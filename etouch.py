#!/usr/bin/python3
# -!- encoding:utf8 -!-
#------------------------------------------------------------------------------
#   IMPORTS
#------------------------------------------------------------------------------
import sys
from datetime import date
#------------------------------------------------------------------------------
#   FUNCTIONS
#------------------------------------------------------------------------------
def build_header(comment_char, filename, separator_char='~', author=''):
    h_separator=separator_char*(79-len(comment_char))
    date_str=date.today().strftime('%Y-%m-%d')
    header="""{0}{1}
{0} file:    {2}
{0} date:    {3}
{0} author:  {4}
{0} purpose:
{0}
{0}{1}\n""".format(comment_char, h_separator, 
    filename, date_str, author)
    return header

def touch_c_header(filename):
    filename_h=filename.replace(' ','_').replace('.','_').upper()
    with open(filename, 'w') as f:
        f.write(build_header('//', filename))
        f.write('#ifndef _{}_\n'.format(filename_h))
        f.write('#define _{}_\n\n'.format(filename_h))
        f.write('#endif /*_{}_*/\n'.format(filename_h))
    return True

def touch_c_source(filename):
    basename=filename.split('.')[0]
    with open(filename, 'w') as f:
        f.write(build_header('//', filename))
        if basename!='main':
            f.write('#include "{}.h"\n'.format(basename))
    return True

def touch_cpp_header(filename):
    touch_c_header(filename)
    return True

def touch_cpp_source(filename):
    touch_c_source(filename)
    return True

def touch_py_file(filename):
    h_separator='#{}\n'.format('='*79)
    with open(filename, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('# -!- encoding: utf8 -!-\n')
        f.write(build_header('#', filename))
        f.write(h_separator)
        f.write('#  IMPORTS\n')
        f.write(h_separator)
        f.write('\n')
        f.write(h_separator)
        f.write('#  FUNCTIONS/CLASSES\n')
        f.write(h_separator)
        f.write('\n')
        f.write(h_separator)
        f.write('#  MAIN SCRIPT\n')
        f.write(h_separator)
        f.write('\n')
    return False

def touch_asm_file(filename):
    basename = filename.split('.')[0]
    with open(filename, 'w') as f:
        f.write(build_header(';', filename))
        f.write('[SECTION .text]\nglobal _start\n\n_start:')

def touch_default(filename):
    with open(filename, 'w') as f:
        f.close()
    return True
#------------------------------------------------------------------------------
#   GLOBALS
#------------------------------------------------------------------------------
touch_funcs={
    'h':touch_c_header,
    'c':touch_c_source,
    'hpp':touch_cpp_header,
    'cpp':touch_cpp_source,
    'py':touch_py_file,
    'asm':touch_asm_file
}
#------------------------------------------------------------------------------
#   MAIN
#------------------------------------------------------------------------------
if len(sys.argv) < 2:
    print('usage: etouch <filename> ...')
else:
    for i in range(1, len(sys.argv)):
        fn = sys.argv[i]
        if '.' in fn:
            ext = fn.split('.')[-1]
            func = touch_funcs.get(ext)
            if func is None:
                touch_default(fn)
            else:
                func(fn)
        else:
            touch_default(fn)
