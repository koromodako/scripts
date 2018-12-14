#!/usr/bin/env python3
# -!- encoding:utf8 -!-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: shellcode.py
#    date: 2017-07-26
#  author: paul.dautry
# purpose:
#   extract a shellcode from objdump output
# license:
#   GPLv3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
#-------------------------------------------------------------------------------
import sys
from subprocess import check_output
#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------
OBJDUMP = 'objdump'
OBJDUMP_PARAMS = ['-d']
#-------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------
def usage():
    print("""%s [options] <func_name> <executable.elf>

OPTIONS
    --objdump=<objdump-path>
        set objdump command name
    --wrap=<int>
        print shellcode on lines of <int> bytes.
""" % sys.argv[0])
    exit(1)

def objdump(executable):
    cmd = [ OBJDUMP ] + OBJDUMP_PARAMS + [ executable ]
    return check_output(cmd).decode('utf8')

def parse_line(line):
    line = line.split(':')[1].strip()
    sc = ''
    for c in line:
        if c == ' ':
            continue
        elif c == '\t':
            break
        else:
            sc += c
    return sc

def shellcode(dump, function):
    sc = []
    lines = dump.split('\n')
    tag = '<%s>:' % function
    k = 0
    while k < len(lines):
        if tag in lines[k]:
            while k < len(lines):
                line = lines[k].strip()
                if len(line) == 0:
                    break
                sc.append(parse_line(line))
                k += 1
        k += 1
    return sc

def print_shellcode(sc, wrap):
    sc = ''.join(sc) 
    if wrap is None or wrap == 0:
        print(sc)
    else:
        i = 0
        line = ''
        for c in sc:
            if i == wrap * 2:
                print(line)
                i = 0
                line = ''
            line += c
            i += 1
        if len(line) > 0:
            print(line) 

def main():
    global OBJDUMP
    wrap = None
    nop_padding = False
    if len(sys.argv) < 3:
        usage()
    for i in range(1, len(sys.argv)-2):
        arg = sys.argv[i]
        if '--wrap=' in arg:
            wrap = int(arg.split('=')[1])
        elif '--objdump=' in arg:
            OBJDUMP = arg.split('=')[1]
    function = sys.argv[-2]
    executable = sys.argv[-1]
    dump = objdump(executable)
    sc = shellcode(dump, function)
    print_shellcode(sc, wrap)
#-------------------------------------------------------------------------------
# SCRIPT
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
