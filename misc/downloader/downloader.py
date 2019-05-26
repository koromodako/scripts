#!/usr/bin/env python3
# -!- encoding:utf8 -!-
# ------------------------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------------------------
from os import urandom
from pathlib import Path, PurePosixPath
from asyncio import (
    CancelledError,
    get_event_loop,
    create_task,
    gather,
    Queue,
    Lock,
)
from datetime import datetime
from argparse import ArgumentParser
from yarl import URL
from aiohttp import ClientSession
# ------------------------------------------------------------------------------
# GLOBALS
# ------------------------------------------------------------------------------
__major__ = 1
__minor__ = 0
__patch__ = 0
__version__ = f'{__major__}.{__minor__}.{__patch__}'
__banner__ = r'''
 ____                      _                 _
|  _ \  _____      ___ __ | | ___   __ _  __| | ___ _ __
| | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
| |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |
|____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   v{}

'''.format(__version__)
URL_QUEUE = Queue()
PRINT_LOCK = Lock()
WORKER_TASKS = []
CHUNK_SIZE = 65536  # 64k
# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------
async def log(lvl, msg):
    '''Display a message
    '''
    async with PRINT_LOCK:
        tmstp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        print(f"({tmstp})[{lvl}]: {msg}")

async def worker_log(lvl, msg, worker_id=None):
    '''Display a worker message
    '''
    if worker_id:
        msg = f"{worker_id} - {msg}"
    await log(lvl, msg)

async def info(msg, worker_id=None):
    '''Display an information message
    '''
    await worker_log('INF', msg, worker_id)

async def error(msg, worker_id=None):
    '''Display an error message
    '''
    await worker_log('ERR', msg, worker_id)

def filepath_for(url, resp, output_dir):
    '''[summary]
    '''
    content_disp = resp.content_disposition
    if content_disp and content_disp.filename:
        filename = PurePosixPath(content_disp.filename)
    else:
        filename = PurePosixPath(PurePosixPath(URL(url).path).name)
    filepath = output_dir.joinpath(filename)
    ctr = 1
    while filepath.exists():
        ext = ''.join(filename.suffixes)
        basename = filename.name.replace(ext, '')
        filename_candidate = PurePosixPath(f'{basename}.{ctr}{ext}')
        filepath = output_dir.joinpath(filename_candidate)
        ctr += 1
    return filepath

async def download_from_url(url, output_dir):
    '''Download file from url
    '''
    async with ClientSession(raise_for_status=True) as sess:
        async with sess.get(url) as resp:
            filepath = filepath_for(url, resp, output_dir)
            with filepath.open('wb') as fp:
                while True:
                    chunk = await resp.content.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    fp.write(chunk)
    return filepath

async def worker_routine(worker_id, output_dir):
    '''Represent a monitoring worker
    '''
    while True:
        # get next url out of the queue
        url = await URL_QUEUE.get()
        if url is None:
            await info("exiting gracefully", worker_id)
            break
        # download url
        await info(f"downloading url: {url}", worker_id)
        try:
            filepath = await download_from_url(url, output_dir)
        except Exception as exc:
            await error(f"an exception occured while downloading '{url}': {exc}", worker_id)
        else:
            await info(f"'{url}' content stored in {filepath}", worker_id)
        # notify the queue that the url has been processed
        URL_QUEUE.task_done()

def url_from_file(url_file):
    '''Yield URL from file
    '''
    with url_file.open() as fp:
        for url in fp:
            url = url.strip()
            if not url:
                continue
            yield url

async def parallel_download(url_file, output_dir, workers=4):
    '''Perform downloads in parallel using workers
    '''
    for url in url_from_file(args.url_file):
        await info(f"scheduling url: {url}")
        await URL_QUEUE.put(url)
    # check if queue is empty before starting
    if URL_QUEUE.empty():
        await error(f"no url to download, exiting.")
        return
    # create download directory if missing
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True)
    # create N workers to process the queue concurrently
    await info(f"spawning {workers} workers...")
    for k in range(workers):
        WORKER_TASKS.append(create_task(worker_routine(f'worker-{k}', output_dir)))
    # await queue to be processed entirely
    await info(f"waiting for urls to be downloaded...")
    try:
        await URL_QUEUE.join()
    except CancelledError:
        await error("tasks cancelled.")
    # terminate workers
    await info(f"terminating workers...")
    for _ in WORKER_TASKS:
        await URL_QUEUE.put(None)
    # await workers termination
    await info(f"waiting for workers to terminate...")
    await gather(*WORKER_TASKS, return_exceptions=True)
    await info(f"exiting.")

def parse_args():
    '''[summary]
    '''
    parser = ArgumentParser(description="Downloads multiple files using given url file.")
    parser.add_argument('--workers', '-w', type=int, default=4, help="Number of workers.")
    parser.add_argument('--output-dir', '-o', type=Path, default=Path(), help="Directory where files should be placed.")
    parser.add_argument('url_file', type=Path, help="URL file.")
    return parser.parse_args()
# ------------------------------------------------------------------------------
# SCRIPT
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print(__banner__)
    args = parse_args()
    loop = get_event_loop()
    loop.run_until_complete(parallel_download(args.url_file,
                                              args.output_dir,
                                              args.workers))
    loop.close()
