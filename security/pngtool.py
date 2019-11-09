#!/usr/bin/env python3
from zlib import crc32, compress
from pathlib import Path
from logging import basicConfig, getLogger, INFO
from argparse import ArgumentParser
from construct import (
    Int32ub,
    Struct,
    Bytes,
    Const,
    Byte,
    this
)

basicConfig(format='(%(name)s)[%(levelname)7s]: %(message)s', level=INFO)
app_log = getLogger('pngtool')
app_log.setLevel(INFO)

CRITICAL_CHUNKS = [
    'IHDR',
    'PLTE',
    'IDAT',
    'IEND',
]

ANCILLARY_CHUNKS = [
    'bKGD',
    'cHRM',
    'gAMA',
    'hIST',
    'pHYs',
    'sBIT',
    'tEXt',
    'tIME',
    'tRNS',
    'zTXt',
]

PNGHeader = Struct(
    'signature' / Const(bytes([137, 80, 78, 71, 13, 10, 26, 10])),
)

PNGChunk = Struct(
    'length' / Int32ub,
    'type' / Bytes(4),
    'data' / Bytes(this.length),
    'crc' / Int32ub,
)

class PNGFile:
    '''Represent a PNG file
    '''
    def __init__(self, png_path):
        '''Constructor
        '''
        self._chunks = []
        app_log.info(f"parsing {png_path}")
        data = png_path.read_bytes()
        offset = 0
        self._header = PNGHeader.parse(data[offset:offset+PNGHeader.sizeof()])
        offset += PNGHeader.sizeof()
        app_log.debug(f"header:\n{self._header}")
        while True:
            remaining = data[offset:]
            if not remaining:
                break
            chk = PNGChunk.parse(remaining)
            offset += 12 + chk.length
            app_log.debug(f"chunk:\n{chk}")
            self._chunks.append(chk)
            if data[offset:] and chk.type.decode() == 'IEND':
                self._remaining = data[offset:]
                app_log.warning("data found after IEND chunk!")

    def __str__(self):
        '''String representation of PNGFile
        '''
        text = "PNGFile(\n"
        text += "header:\n"
        text += str(self._header)
        text += "\n"
        text += "chunks:\n"
        for chk in self._chunks:
            text += str(chk)
            text += "\n"
        text += ")"
        return text

    @property
    def header(self):
        '''PNG header
        '''
        return self._header

    @property
    def chunks(self):
        '''PNG chunks
        '''
        return self._chunks

    def insert(self, index, chk_type, data):
        '''Insert a chunk
        '''
        app_log.info(f"inserting new chunk: {chk_type}")
        chk_data = Bytes(4).build(chk_type.encode())
        chk_data += data
        chk_data += Int32ub.build(png_crc(chk_data))
        chk_data = Int32ub.build(len(data)) + chk_data
        chk = PNGChunk.parse(chk_data)
        self._chunks.insert(index, chk)

    def save(self, filepath):
        '''Save PNG to filepath
        '''
        app_log.info(f"saving PNG to: {filepath}")
        with filepath.open('wb') as png:
            png.write(self._header.signature)
            for chk in self._chunks:
                png.write(Int32ub.build(chk.length))
                png.write(chk.type)
                png.write(chk.data)
                png.write(Int32ub.build(chk.crc))

def png_crc(data):
    '''Compute CRC32
    '''
    return crc32(data) & 0xffffffff

def png_check_crc(chk):
    '''Determine PNG chunk CRC validity
    '''
    return png_crc(chk.type + chk.data) == chk.crc

def png_check_type(chk):
    '''Determine PNG chunk type category
    '''
    chk_type = chk.type.decode()
    if chk_type in CRITICAL_CHUNKS:
        return 'critical'
    if chk_type in ANCILLARY_CHUNKS:
        return 'ancillary'
    return None

def png_dissect(png_path):
    '''Dissect a PNG file
    '''
    pngf = PNGFile(png_path)
    print("header:")
    print(pngf.header)
    print("chunks:")
    for chk in pngf.chunks:
        print(chk)
        print("    check result:")
        category = png_check_type(chk)
        type_result = f'known ({category})' if category else 'unknown!'
        print(f"     - chunk type is {type_result}")
        valid_crc = png_check_crc(chk)
        print(f"     - chunk CRC is {'' if valid_crc else 'in'}valid")

def dissect_cmd(args):
    '''Implement 'dissect' command
    '''
    png_dissect(args.png_path)

def insert_cmd(args):
    '''Implement 'insert' command
    '''
    pngf = PNGFile(args.png_path)
    pngf.insert(args.index, args.type, args.chunk_path.read_bytes())
    print(pngf)
    answer = input("Do you want to save this png? [y/n]: ")
    if answer.lower() in ['yes', 'y']:
        pngf.save(args.output_path)

def app():
    '''App entry point
    '''
    parser = ArgumentParser(description="PNG Format Manipulation Toolkit")
    parser.add_argument('png_path', type=Path, help="PNG file to manipulate")
    # - subparsers
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True
    # -- dissect
    dissect = subparsers.add_parser('dissect', help="Dissect a PNG file")
    dissect.set_defaults(func=dissect_cmd)
    # -- insert
    insert = subparsers.add_parser('insert', help="Insert a chunk in a PNG file")
    insert.add_argument('index', type=int, help="Insert chunk at this index")
    insert.add_argument('type', help="Chunk type")
    insert.add_argument('chunk_path', type=Path, help="File containing chunk data to insert")
    insert.add_argument('output_path', type=Path, help="New PNG to create")
    insert.set_defaults(func=insert_cmd)
    # - parse args
    args = parser.parse_args()
    try:
        args.func(args)
    except:
        app_log.exception("Unhandled exception caught! Details below.")

if __name__ == '__main__':
    app()
