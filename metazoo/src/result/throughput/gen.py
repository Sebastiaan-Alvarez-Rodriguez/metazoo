from collections import defaultdict
import matplotlib.pyplot as plt 
import numpy as np 

#from result.throughput.assembler import Assembler
from result.throughput.reader import Reader
import result.util.storer as storer 
import util.fs as fs
import util.location as loc 
from util.printer import *

#TODO: current version is for one run only. 
def throughput(logdir, large, no_show, store_fig, filetype, original):
    seconds = 5
    if original:
        printe('not implemented yet')
    else: 
        path = fs.join(loc.get_metazoo_results_dir(), logdir)
        run = next(fs.ls(path, only_dirs=True, full_paths=True))
        reader = Reader(run)
        frame = [(x[0][0], sum(n for _, n in x)) for x in zip(*[reader.read_ops(x) for x in range(reader.num_files)])]
        fig, ax = plt.subplots()
        for ratio, ops in frame: 
            ax.scatter(ratio, ops / seconds, color='tab:green', marker='o')
        ax.set(yscale='log', xlabel='Read Ratio', ylabel='Operations per Second', title='throughput')

    if store_fig:
       storer.store('throughput', logdir, filetype, plt)

    if not no_show:
        plt.show()