#!/usr/bin/env python3
import os
import re
import sys
import enum
import pathlib
import argparse
import binascii
import subprocess

DEBUG = False
HEX_RE = re.compile(r'^[0-9a-f]{2}$')

class OutputFormat(enum.Enum):
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

def pdbg(msg):
    if DEBUG:
        sys.stderr.write(msg+'\n')

def run_cmd(cmd, **kwargs):
    pcmd = ' '.join(cmd)
    pdbg(f"running: {pcmd}")
    return subprocess.check_output(cmd, **kwargs)

def generate(asm_src, bin_fmt):
    tmp = pathlib.Path(f'/tmp/mksc-{os.urandom(8).hex()}.o')
    run_cmd(['nasm', '-f', bin_fmt, '-o', str(tmp), str(asm_src)])
    dat = run_cmd(['objdump', '-d', str(tmp)])
    tmp.unlink()
    return dat

def extract(objdump):
    hstr = ''
    for l in objdump.split('\n'):
        l = l.replace('\t', ' ').strip()
        if not l:
            continue
        parts = [e for e in filter(lambda x: HEX_RE.match(x), l.split(' '))]
        hstr += ''.join(parts)
    return bytearray(binascii.unhexlify(hstr))

def parse_args():
    p = argparse.ArgumentParser(description="Making shellcode creation easy!")
    p.add_argument('asm_src', type=pathlib.Path, help="ASM source file")
    p.add_argument('--debug', action='store_true', help="Increase script verbosity")
    p.add_argument('--format',
                   choices=[fmt.value for fmt in OutputFormat],
                   default=OutputFormat.PrintF,
                   type=OutputFormat,
                   help="Output format")
    p.add_argument('--bin-fmt', default='elf64', help="Binary format to produce")
    p.add_argument('--pad-byte', type=int, default=0x90, help="Padding byte to add at the end if necessary")
    p.add_argument('--expected-size', type=int, default=-1, help="Payload size required at the end")
    p.add_argument('--extra-suffix', help="Payload raw suffix")
    p.add_argument('--extra-prefix', help="Payload raw prefix")
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    DEBUG = args.debug
    dat = generate(args.asm_src, args.bin_fmt)
    pdbg(dat.decode())
    dat = extract(dat.decode())
    pad_size = args.expected_size - len(dat)
    if pad_size < 0 and args.expected_size > 0:
        pdbg(f"warning: shellcode size ({len(dat)}) exceeds expected size")
    if pad_size > 0:
        dat += pad_size * bytearray([args.pad_byte])
    if args.extra_suffix:
        dat += args.extra_suffix.encode()
    if args.extra_prefix:
        dat = args.extra_prefix.encode() + dat
    dat = bytes(dat)
    OUTPUT_FMT_MAP[args.format](dat)

