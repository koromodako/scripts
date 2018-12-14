#!/usr/bin/env python3
# -!- encoding:utf8 -!-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: projstats.py
#    date: 2017-07-10
#  author: paul.dautry
# purpose:
#       
# license:
#       GPLv3
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   IMPORTS
#-------------------------------------------------------------------------------
import os
import fnmatch
import argparse
#-------------------------------------------------------------------------------
#   CLASSES
#-------------------------------------------------------------------------------
class Statistics(object):
    def __init__(self, verbose,
        exclude_files, exclude_dirs, include_files, include_dirs,
        no_comment):
        super(Statistics, self).__init__()
        # options
        self.verbose = verbose
        self.exclude_files = set(filter(None, exclude_files.split(',')))
        self.exclude_dirs = set(filter(None, exclude_dirs.split(',')))
        self.include_files = set(filter(None, include_files.split(',')))
        self.include_dirs = set(filter(None, include_dirs.split(',')))
        self.no_comment = no_comment
        # statistics
        self.root = None 
        self.extensions = set()
        self.file_cnt = 0
        self.kloc = 0

    def __scan_file(self, fpath, fname):
        if self.verbose:
            print('scanning: %s' % fname)
        self.file_cnt += 1
        if '.' in fname:
            self.extensions.add(fname.split('.')[-1])
        with open(fpath, 'r') as f:
            self.kloc += len(f.read().split('\n'))

    def __include_dirs(self, dirs):
        kept = set()
        for d in dirs:
            for pattern in self.include_dirs:
                if fnmatch.fnmatch(d, pattern):
                    kept.add(d)
                    break
        return kept

    def __exclude_dirs(self, dirs):
        kept = set()
        for d in dirs:
            keep = True
            for pattern in self.exclude_dirs:
                if fnmatch.fnmatch(d, pattern):
                    keep = False
            if keep:
                kept.add(d)
        return kept

    def scan(self, dirpath):
        self.root = dirpath
        for root, dirs, files in os.walk(self.root):
            if self.verbose:
                print('entering: %s' % root)
            # include or exclude dirs
            if len(self.include_dirs) > 0:
                dirs[:] = self.__include_dirs(dirs)
            else:
                dirs[:] = self.__exclude_dirs(dirs) 
            # scan files
            for f in files:
                if len(self.include_files) > 0:
                    for pattern in self.include_files:
                        if fnmatch.fnmatch(f, pattern):
                            self.__scan_file(os.path.join(root, f), f)
                            break
                else:
                    skip = False
                    for pattern in self.exclude_files:
                        if fnmatch.fnmatch(f, pattern):
                            skip = True
                    if not skip:
                        self.__scan_file(os.path.join(root, f), f)

    def print(self):
        print("""
project root directory: %s
statistics:
    + scanned file extensions: %s
    + file count: %s
    + kloc: %s
""" % (
            self.root,
            self.extensions,
            self.file_cnt,
            self.kloc
        ))
#-------------------------------------------------------------------------------
#   FUNCTIONS
#-------------------------------------------------------------------------------
def create_argv_parser():
    parser = argparse.ArgumentParser(usage='%s(prog)s [options] directory',
        add_help=True, allow_abbrev=False, 
        description='A simple tool computing statistics about development project.')
    parser.add_argument('-v', '--verbose', action='store_true', 
        help='increase program verbosity')
    parser.add_argument('--exclude-files', default='', 
        help='comma-separated list of excluded file patterns')
    parser.add_argument('--exclude-dirs', default='', 
        help='comma-separated list of excluded dir. patterns')
    parser.add_argument('--include-files', default='', 
        help='comma-separated list of included file patterns')
    parser.add_argument('--include-dirs', default='', 
        help='comma-separated list of included dir. patterns')
    parser.add_argument('--no-comment', action='store_true', 
        help='ignore comment lines')
    parser.add_argument('directory', help='input director(y|ies)')
    return parser

def usage():
    create_argv_parser().print_help()
    exit(1)

def main():
    parser = create_argv_parser()
    args = parser.parse_args()
    stats = Statistics(
        args.verbose,
        args.exclude_files, args.exclude_dirs, 
        args.include_files, args.include_dirs,
        args.no_comment)
    stats.scan(args.directory)
    stats.print()

#-------------------------------------------------------------------------------
#   SCRIPT
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()