#!/usr/bin/env python3
import re
from pathlib import Path
from logging import basicConfig, getLogger, DEBUG
from argparse import ArgumentParser
from binascii import unhexlify

DEBUG = False
INSTR_RE = re.compile(r'^(?P<offset>[0-9a-f]+):\s+(?P<data>([0-9a-f]{4}\s)+).*')
STRING_RE = re.compile(r'^(?P<offset>[0-9a-f]+):\s+"(?P<data>[^"]+).*')

basicConfig(
    format="(%(name)s)[%(levelname)7s]: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=DEBUG
)
app_log = getLogger("app")

def str2offset(offset):
    return int(offset, 16)

def concat_dat(dat):
    return unhexlify(dat.replace(' ', ''))

def null_term_str(string):
    return string.encode() + b'\x00'

def extract(objdump_file):
    '''Extract binary elements from a formated file
    '''
    bin_parts = []
    with objdump_file.open('r') as odf:
        for line in odf:
            instr_match = INSTR_RE.match(line)
            if instr_match:
                offset = str2offset(instr_match.group('offset'))
                data = concat_dat(instr_match.group('data'))
                bin_parts.append((offset, data))
                continue
            string_match = STRING_RE.match(line)
            if string_match:
                offset = str2offset(string_match.group('offset'))
                data = null_term_str(string_match.group('data'))
                bin_parts.append((offset, data))
                continue
    return bin_parts

def build_raw_bin(bin_parts, output_file):
    '''Build a binary from bin_parts
    '''
    last_elt = bin_parts[-1]
    bin_size = last_elt[0] + len(last_elt[1])
    app_log.info(f"binary size: {bin_size} bytes")
    with output_file.open('wb') as opf:
        for offset, data in bin_parts:
            opf.seek(offset, 0)
            opf.write(data)

def parse_args():
    '''Parse command line arguments
    '''
    p = ArgumentParser(description="Create a raw binary from microcorr objdump style")
    p.add_argument('objdump_file', type=Path)
    p.add_argument('output_file', type=Path)
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    bin_parts = extract(args.objdump_file)
    build_raw_bin(bin_parts, args.output_file)
    # Open the binary using MSP430X 32bits in Ghidra
