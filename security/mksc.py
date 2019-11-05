#!/usr/bin/env python3
import os
import re
import sys
from enum import Enum
from logging import basicConfig, getLogger, INFO, DEBUG
from pathlib import Path
from tempfile import NamedTemporaryFile
from argparse import ArgumentParser
from binascii import unhexlify
from subprocess import check_output

basicConfig(format='(%(name)s)[%(levelname)7s]: %(message)s', level=DEBUG)
app_log = getLogger('mksc')
app_log.setLevel(INFO)

NOP_BYTE = b'\x90'
NULL_BYTE = b'\x00'

def run_cmd(cmd, **kwargs):
    app_log.debug(f"running: {cmd}")
    return check_output(cmd, **kwargs)

class ShellCode:
    '''[summary]
    '''

    class NASMFormat(Enum):
        '''From `nasm -hf`

        ELF only for now...
        '''
        #BIN = 'bin'       # flat-form binary files (e.g. DOS .COM, .SYS)
        #ITH = 'ith'       # Intel hex
        #OBJ = 'obj'       # MS-DOS 16-bit/32-bit OMF object files
        #RDF = 'rdf'       # Relocatable Dynamic Object File Format v2.0
        #DBG = 'dbg'       # Trace of all info passed to output stage
        ELF = 'elf'       # ELF (short name for ELF32)
        #WIN = 'win'       # WIN (short name for WIN32)
        #SREC = 'srec'      # Motorola S-records
        #AOUT = 'aout'      # Linux a.out object files
        #AS86 = 'as86'      # Linux as86 (bin86 version 0.3) object files
        #COFF = 'coff'      # COFF (i386) object files (e.g. DJGPP for DOS)
        #IEEE = 'ieee'      # IEEE-695 (LADsoft variant) object file format
        #AOUTB = 'aoutb'     # NetBSD/FreeBSD a.out object files
        ELF32 = 'elf32'     # ELF32 (i386) object files (e.g. Linux)
        ELF64 = 'elf64'     # ELF64 (x86_64) object files (e.g. Linux)
        #WIN32 = 'win32'     # Microsoft Win32 (i386) object files
        #WIN64 = 'win64'     # Microsoft Win64 (x86-64) object files
        #MACHO = 'macho'     # MACHO (short name for MACHO32)
        ELFX32 = 'elfx32'    # ELFX32 (x86_64) object files (e.g. Linux)
        #MACHO32 = 'macho32'   # NeXTstep/OpenStep/Rhapsody/Darwin/MacOS X (i386) object files
        #MACHO64 = 'macho64'   # NeXTstep/OpenStep/Rhapsody/Darwin/MacOS X (x86_64) object files

    class PrintFormat(Enum):
        '''[summary]
        '''
        Raw = 'raw'
        PrintF = 'printf'
        Python = 'python'


    NASM_MODE_MAP = {
        NASMFormat.ELF:     32,
        NASMFormat.ELF32:   32,
        NASMFormat.ELF64:   64,
        NASMFormat.ELFX32:  64
    }

    @classmethod
    def from_hex(cls, hexstr):
        return cls(unhexlify(hexstr))

    def __init__(self, data):
        '''[summary]
        '''
        self._data = bytearray(data)

    @property
    def plain(self):
        '''[summary]
        '''
        return bytes(self._data)

    @property
    def size(self):
        '''[summary]
        '''
        return len(self._data)

    def xored(self, key):
        '''[summary]
        '''
        keyl = len(key)
        return ShellCode(bytearray([self._data[k] ^ key[k % keyl] for k in range(len(self._data))]))

    def save(self, filepath):
        '''[summary]
        '''
        filepath.write_bytes(self._data)
        app_log.info(f"shellcode written to: {filepath}")

    def check(self, bad_bytes=None, max_size=None):
        '''[summary]
        '''
        app_log.info("performing payload checks...")
        ok = True
        # check max size
        size = len(self._data)
        app_log.info(f"shellcode size: {size} bytes")
        if max_size and size > max_size:
            ok = False
            app_log.warning(f"payload bigger than {max_size} bytes ({size}).")
        # check null byte
        indx = self._data.find(NULL_BYTE)
        if indx >= 0:
            ok = False
            app_log.warning(f"payload contains a null byte at {indx}.")
        # check bad bytes if required
        bad_bytes = bad_bytes or []
        for bad_byte in bad_bytes:
            indx = self._data.find(bad_byte)
            if indx < 0:
                continue
            ok = False
            app_log.warning(f"bad byte {bad_byte} found at {indx}")
        if ok:
            app_log.info("payload checks passed.")
        else:
            app_log.warning("payload checks failed.")
        return ok

    def pad(self, pad_byte=NOP_BYTE, expected_size=-1):
        '''[summary]
        '''
        if expected_size <= 0:
            return
        pad_size = expected_size - self.size
        if pad_size > 0:
            self._data += bytearray([args.pad_byte] * pad_size)
        else:
            app_log.warning("pad() called while shellcode was already bigger than expected size.")

    def prefix(self, prefix_bytes):
        '''[summary]
        '''
        if prefix_bytes:
            self._data = bytearray(prefix_bytes) + self._data

    def suffix(self, suffix_bytes):
        '''[summary]
        '''
        if suffix_bytes:
            self._data += bytearray(suffix_bytes)

    def ndisasm(self, bin_fmt):
        '''[summary]
        '''
        lines = []
        with NamedTemporaryFile('wb') as tmpf:
            tmpf.write(self._data)
            tmpf.flush()
            output = run_cmd(['ndisasm', '-b', str(self.NASM_MODE_MAP[bin_fmt]), tmpf.name])
            lines.append("--------------------------[NDISASM]--------------------------")
            for line in output.decode().split('\n'):
                if line:
                    lines.append(line.lower())
            lines.append("-------------------------------------------------------------")
        return '\n'.join(lines)

    def _fmt_raw(self):
        '''[summary]
        '''
        sys.stdout.buffer.write(self.plain)

    def _fmt_printf(self):
        '''[summary]
        '''
        print(f"printf '{str(self.plain)[2:-1]}'")

    def _fmt_python(data):
        '''[summary]
        '''
        print(f"python3 -c 'import sys;sys.stdout.buffer.write(b\"{str(self.plain)[2:-1]}\")'")

    def print(self, print_fmt):
        '''[summary]
        '''
        func = getattr(self, f'_fmt_{print_fmt.value}', None)
        if func:
            app_log.info(f"printing payload ({print_fmt.value} format):")
            func()

def generate(dist_dir, asm_path, bin_fmt):
    if not asm_path.is_file():
        app_log.error(f"{asm_path} is not an assembly file.")
        return
    dist_dir.mkdir(parents=True, exist_ok=True)
    obj_path = dist_dir.joinpath(f'{asm_path.stem}.obj')
    bin_path = dist_dir.joinpath(f'{asm_path.stem}.bin')
    hex_path = dist_dir.joinpath(f'{asm_path.stem}.hex')
    app_log.info("creating object from assembly...")
    run_cmd(['nasm', '-f', bin_fmt.value, '-o', str(obj_path), str(asm_path)])
    app_log.info("creating executable from object...")
    run_cmd(['ld', '-o', str(bin_path), str(obj_path)])
    app_log.info("creating objdump from object...")
    objdmp = run_cmd(['objdump', '-d', str(obj_path)])
    hex_path.write_bytes(objdmp)
    app_log.info(f"objdump written to: {hex_path}")
    return objdmp.decode()

HEX_RE = re.compile(r'[0-9a-f]+:(?P<hexpart>(\s[0-9a-f]{2})+)')

def parse_objdmp(objdmp):
    app_log.info("extracting bytes from objdump output...")
    hexstr = ''
    for line in objdmp.split('\n'):
        line = line.replace('\t', ' ').strip()
        if not line:
            continue
        match = HEX_RE.match(line)
        if not match:
            continue
        hexstr += ''.join(match.group('hexpart').replace(' ', ''))
    return ShellCode.from_hex(hexstr)

def parse_args():
    p = ArgumentParser(description="Making shellcode creation easy!")
    p.add_argument('asm_path', type=Path, help="ASM source file")
    p.add_argument('--debug', action='store_true', help="Increase script verbosity")
    p.add_argument('--bin-fmt',
                   choices=[fmt for fmt in ShellCode.NASMFormat],
                   default=ShellCode.NASMFormat.ELF64,
                   type=ShellCode.NASMFormat,
                   help="Binary format to produce")
    p.add_argument('--print-fmt',
                   choices=[fmt for fmt in ShellCode.PrintFormat],
                   default=ShellCode.PrintFormat.PrintF,
                   type=ShellCode.PrintFormat,
                   help="Output format")
    p.add_argument('--pad-byte', type=int, default=0x90, help="Padding byte to add at the end if necessary")
    p.add_argument('--dist-dir', default=Path('mksc.dist'), type=Path, help="Distribution directory")
    p.add_argument('--xor-bytes', type=unhexlify, help="Hex-encoded bytes of the XOR key")
    p.add_argument('--bad-bytes', type=unhexlify, nargs='+', help="Warn if this hex-encoded bytes are found in payload")
    p.add_argument('--suffix-bytes', type=unhexlify, help="Payload hex-encoded suffix")
    p.add_argument('--prefix-bytes', type=unhexlify, help="Payload hex-encoded prefix")
    p.add_argument('--expected-size', type=int, default=-1, help="Payload size required at the end")
    return p.parse_args()

def app(args):
    # generate required elements from assembly source file
    objdmp = generate(args.dist_dir, args.asm_path, args.bin_fmt)
    if not objdmp:
        return
    # extract shellcode from objdump output
    sc = parse_objdmp(objdmp)
    # perform padding if required
    sc.pad(args.pad_byte, args.expected_size)
    # append hex-encoded suffix
    sc.suffix(args.suffix_bytes)
    # prepend hex-encoded prefix
    sc.prefix(args.prefix_bytes)
    sc.save(args.dist_dir.joinpath(f'{args.asm_path.stem}.shc'))
    print(sc.ndisasm(args.bin_fmt))
    sc.check(args.bad_bytes)
    sc.print(args.print_fmt)
    if args.xor_bytes:
        app_log.info("xoring shellcode...")
        xored_sc = sc.xored(args.xor_bytes)
        xored_sc.check(args.bad_bytes)
        xored_sc.save(args.dist_dir.joinpath(f'{args.asm_path.stem}.xshc'))
        xored_sc.print(args.print_fmt)

if __name__ == '__main__':
    # parse command line arguments
    args = parse_args()
    if args.debug:
        app_log.setLevel(DEBUG)
    app(args)
