#!/usr/bin/env python3
import os
import re
import sys
from enum import Enum
from logging import basicConfig, getLogger, INFO, DEBUG
from pathlib import Path
from argparse import ArgumentParser
from binascii import unhexlify
from subprocess import check_output

basicConfig(format='(%(name)s)[%(levelname)7s]: %(message)s', level=DEBUG)
app_log = getLogger('mksc')
app_log.setLevel(INFO)

HEX_RE = re.compile(r'^[0-9a-f]{2}$')

class OutputFormat(Enum):
    Raw = 'raw'
    PrintF = 'printf'
    Python = 'python'

def raw_out(data):
    sys.stdout.buffer.write(data)

def printf_out(data):
    hdata = str(data)[2:-1]
    print(f'printf "{hdata}"')

def python_out(data):
    hdata = str(data)[2:-1]
    print(f'python3 -c "import sys;sys.stdout.buffer.write(b\'{hdata}\')"')

OUTPUT_FMT_MAP = {
    OutputFormat.Raw: raw_out,
    OutputFormat.PrintF: printf_out,
    OutputFormat.Python: python_out,
}

def run_cmd(cmd, **kwargs):
    pcmd = ' '.join(cmd)
    app_log.debug(f"running: {pcmd}")
    return check_output(cmd, **kwargs)

def generate(dist_dir, asm_path, bin_fmt):
    dist_dir.mkdir(parents=True, exist_ok=True)
    obj_path = dist_dir.joinpath(f'{asm_path.stem}.obj')
    bin_path = dist_dir.joinpath(f'{asm_path.stem}.bin')
    hex_path = dist_dir.joinpath(f'{asm_path.stem}.hex')
    app_log.info("creating object from assembly...")
    run_cmd(['nasm', '-f', bin_fmt, '-o', str(obj_path), str(asm_path)])
    app_log.info("creating executable from object...")
    run_cmd(['ld', '-o', str(bin_path), str(obj_path)])
    app_log.info("creating objdump from object...")
    dat = run_cmd(['objdump', '-d', str(obj_path)])
    hex_path.write_bytes(dat)
    return dat

def extract(objdump):
    app_log.info("extracting shellcode from objdump...")
    hstr = ''
    for line in objdump.split('\n'):
        line = line.replace('\t', ' ').strip()
        if not line:
            continue
        parts = [elt for elt in filter(lambda x: HEX_RE.match(x), line.split(' '))]
        hstr += ''.join(parts)
    return bytearray(unhexlify(hstr))

def parse_args():
    p = ArgumentParser(description="Making shellcode creation easy!")
    p.add_argument('asm_path', type=Path, help="ASM source file")
    p.add_argument('--debug', action='store_true', help="Increase script verbosity")
    p.add_argument('--format',
                   choices=[fmt.value for fmt in OutputFormat],
                   default=OutputFormat.PrintF,
                   type=OutputFormat,
                   help="Output format")
    p.add_argument('--bin-fmt', default='elf64', help="Binary format to produce")
    p.add_argument('--pad-byte', type=int, default=0x90, help="Padding byte to add at the end if necessary")
    p.add_argument('--dist-dir', default=Path('mksc.dist'), type=Path, help="Distribution directory")
    p.add_argument('--expected-size', type=int, default=-1, help="Payload size required at the end")
    p.add_argument('--hex-suffix', help="Payload hex-encoded suffix")
    p.add_argument('--hex-prefix', help="Payload hex-encoded prefix")
    return p.parse_args()

def app(args):
    # generate required elements from assembly source file
    dat = generate(args.dist_dir,
                   args.asm_path,
                   args.bin_fmt)
    # extract shellcode from objdump output
    dat = extract(dat.decode())
    # perform padding if required
    pad_size = args.expected_size - len(dat)
    if pad_size < 0 and args.expected_size > 0:
        app_log.warning(f"warning: shellcode size ({len(dat)}) exceeds expected size")
    if pad_size > 0:
        dat += pad_size * bytearray([args.pad_byte])
    # append hex-encoded suffix
    if args.hex_suffix:
        dat += unhexlify(args.hex_suffix)
    # prepend hex-encoded prefix
    if args.hex_prefix:
        dat = unhexlify(args.hex_prefix) + dat
    dat = bytes(dat)
    app_log.info("printing payload:")
    OUTPUT_FMT_MAP[args.format](dat)

if __name__ == '__main__':
    # parse command line arguments
    args = parse_args()
    if args.debug:
        app_log.setLevel(DEBUG)
    app(args)
