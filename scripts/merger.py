import sys
import os
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), '../metazoo/src'))

import util.fs as fs 
from util.printer import *

def get_results_dir():
    return fs.join('..', 'metazoo', 'results')

def insert(src, dst):
    src_path = fs.join(get_results_dir(), src)
    if not fs.isdir(src_path):
        raise RuntimeError('Cannot find directory {}'.format(src_path))
    dst_path = fs.join(get_results_dir(), dst)
    if not fs.isdir(dst_path):
        raise RuntimeError('Cannot find directory {}'.format(dst_path))

    visited_dirs = []
    for directory in fs.ls(src_path, only_dirs=True, full_paths=True):
        if directory in visited_dirs:
            raise RuntimeError('Visiting directory {} twice. Should not happen!'.format(directory))
        visited_dirs.append(directory)
        for src_file in fs.ls(directory, only_files=True, full_paths=True):
            if src_file.endswith('.log') and fs.basename(src_file).split('.')[-2].isnumeric():
                line = None
                with open(src_file, 'r') as f: # Read 90% r/w point
                    line = f.readlines()[0]
                dst_file = src_file.replace(src, dst)
                
                dst_lines = None
                with open(dst_file, 'r') as f: # Read 0,25,50,75,100 r/w point
                    dst_lines = f.readlines()
                dst_lines.insert(4, line) # Add 90 r/w point between 75 and 100
                with open(dst_file, 'w') as f:
                    for l in dst_lines:
                        f.write(l)



def main():
    insert('throughput_90_13', 'results_13_throughput')


if __name__ == '__main__':
    main()