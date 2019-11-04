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

NULL_BYTE = b'\x00'

class OutputFormat(Enum):
    Raw = 'raw'
    PrintF = 'printf'
    Python = 'python'

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

NASM_MODE_MAP = {
    NASMFormat.ELF:     32,
    NASMFormat.ELF32:   32,
    NASMFormat.ELF64:   64,
    NASMFormat.ELFX32:  64
}

def raw_out(data):
    sys.stdout.buffer.write(data)

def printf_out(data):
    hdata = str(data)[2:-1]
    print(f'printf "{hdata}"')

def python_out(data):
    hdata = str(data)[2:-1]
    print(f'python3 -c "import sys;sys.stdout.buffer.write(b\'{hdata}\')"')

OUTPUT_FMT_MAP = {
    OutputFormat.Raw:       raw_out,
    OutputFormat.PrintF:    printf_out,
    OutputFormat.Python:    python_out,
}

def run_cmd(cmd, **kwargs):
    pcmd = ' '.join(cmd)
    app_log.debug(f"running: {pcmd}")
    return check_output(cmd, **kwargs)

def ndisasm(shc_path, bin_fmt):
    output = run_cmd(['ndisasm', '-b', str(NASM_MODE_MAP[bin_fmt]), str(shc_path)])
    app_log.info("--------------------------[NDISASM]--------------------------")
    for line in output.decode().split('\n'):
        if line:
            app_log.info(line.lower())
    app_log.info("-------------------------------------------------------------")

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

HEX_RE = re.compile(r'[0-9a-f]+:(?P<bytes>(\s[0-9a-f]{2})+)')

def parse_objdmp(objdmp):
    app_log.info("extracting bytes from objdump output...")
    hstr = ''
    for line in objdmp.split('\n'):
        line = line.replace('\t', ' ').strip()
        if not line:
            continue
        match = HEX_RE.match(line)
        if not match:
            continue
        hstr += ''.join(match.group('bytes').replace(' ', ''))
    shcode = bytearray(unhexlify(hstr))
    return shcode

def xor_encode(shcode, hex_xor):
    key = unhexlify(hex_xor)
    keyl = len(key)
    return bytes([shcode[i] ^ key[i % keyl] for i in range(len(shcode))])

def parse_args():
    p = ArgumentParser(description="Making shellcode creation easy!")
    p.add_argument('asm_path', type=Path, help="ASM source file")
    p.add_argument('--debug', action='store_true', help="Increase script verbosity")
    p.add_argument('--format',
                   choices=[fmt.value for fmt in OutputFormat],
                   default=OutputFormat.PrintF,
                   type=OutputFormat,
                   help="Output format")
    p.add_argument('--bin-fmt',
                   choices=[fmt.value for fmt in NASMFormat],
                   default=NASMFormat.ELF64,
                   type=NASMFormat,
                   help="Binary format to produce")
    p.add_argument('--pad-byte', type=int, default=0x90, help="Padding byte to add at the end if necessary")
    p.add_argument('--dist-dir', default=Path('mksc.dist'), type=Path, help="Distribution directory")
    p.add_argument('--hex-xor', help="Hex representation of the XOR key")
    p.add_argument('--hex-suffix', help="Payload hex-encoded suffix")
    p.add_argument('--hex-prefix', help="Payload hex-encoded prefix")
    p.add_argument('--expected-size', type=int, default=-1, help="Payload size required at the end")
    return p.parse_args()

def app(args):
    # generate required elements from assembly source file
    objdmp = generate(args.dist_dir, args.asm_path, args.bin_fmt)
    if not objdmp:
        return
    # extract shellcode from objdump output
    shcode = parse_objdmp(objdmp)
    # perform padding if required
    pad_size = args.expected_size - len(shcode)
    if pad_size < 0 and args.expected_size > 0:
        app_log.warning(f"warning: shellcode size ({len(shcode)}) exceeds expected size")
    if pad_size > 0:
        shcode += pad_size * bytearray([args.pad_byte])
    # append hex-encoded suffix
    if args.hex_suffix:
        shcode += bytearray(unhexlify(args.hex_suffix))
    # prepend hex-encoded prefix
    if args.hex_prefix:
        shcode = bytearray(unhexlify(args.hex_prefix)) + shcode
    shc_path = args.dist_dir.joinpath(f'{args.asm_path.stem}.shc')
    shc_path.write_bytes(bytes(shcode))
    ndisasm(shc_path, args.bin_fmt)
    app_log.info(f"payload length: {len(shcode)}")
    if NULL_BYTE in shcode:
            app_log.warning("payload contains null bytes.")
    app_log.info(f"raw payload written to: {shc_path}")
    app_log.info("printing payload:")
    OUTPUT_FMT_MAP[args.format](bytes(shcode))
    if args.hex_xor:
        xored_shcode = xor_encode(shcode, args.hex_xor)
        if NULL_BYTE in xored_shcode:
            app_log.warning("xored payload contains null bytes.")
        xshc_path = args.dist_dir.joinpath(f'{args.asm_path.stem}.xshc')
        xshc_path.write_bytes(bytes(xored_shcode))
        app_log.info(f"xored payload written to: {xshc_path}")
        app_log.info("printing xored payload:")
        OUTPUT_FMT_MAP[args.format](bytes(xored_shcode))

if __name__ == '__main__':
    # parse command line arguments
    args = parse_args()
    if args.debug:
        app_log.setLevel(DEBUG)
    app(args)
