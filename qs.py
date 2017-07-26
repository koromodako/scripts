#!/usr/bin/env python3
# -!- encoding:utf8 -!-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: shellcode.py
#    date: 2017-07-26
#  author: paul.dautry
# purpose:
#   Quick Search is a command line tool aiming at opening a webrowser quickly
#   with the page i'm looking for loaded without having to click everywhere to
#   get there
# license:
#   GPLv3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
#-------------------------------------------------------------------------------
import sys
from subprocess import call
from urllib.parse import quote_plus
#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------
_BOOKMARKS_ = {
    'github': 'https://github.com/pdautry',
    'regex101': 'https://regex101.com/',
    'pythondoc': 'https://docs.python.org/3.5/library/index.html'
}
_OPTIONS_ = ['-s', '-b', '-bl']
#-------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------
def build_search_string():
    search_str = ''
    for i in range(2, len(sys.argv)):
         search_str += sys.argv[i] + ' '
    return quote_plus(search_str.strip())

def check_min_args(num):
    if len(sys.argv) < num:
        print('Missing arguments.')
        exit(1)
        
def main():
    if len(sys.argv) < 2 or sys.argv[1] not in _OPTIONS_:
        print('usage : qs ( -b <bookmark> | -s <search_string> | -bl)')
    else:
        opt = sys.argv[1]
        if opt == '-b':
            check_min_args(3)
            url = _BOOKMARKS_.get(sys.argv[2], None)
            if url:
                call(['firefox --new-tab ' + url + ' &> /dev/null &'], shell=True)
            else:
                print('No bookmark found.')
        elif opt == '-bl':
            print('Bookmarks:')
            for b in _BOOKMARKS_.keys():
                print('    + ' + b)
        elif opt == '-s':
            check_min_args(3)
            call(['firefox --new-tab https://duckduckgo.com/?q=' + build_search_string() + ' &> /dev/null &'], shell=True)
        else:
            print('Unknown option.')
#-------------------------------------------------------------------------------
# SCRIPT
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
