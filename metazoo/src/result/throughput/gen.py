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
        #TODO: one-line?
        frame = defaultdict(int)
        for x in range(reader.num_files):
            for ratio, ops in reader.read_ops(x):
                frame[ratio] += ops

        fig, ax = plt.subplots()
        for x in frame:
            ax.scatter(x, frame[x] / seconds, color='tab:green', marker='o', size=400)
        ax.set(xlabel='Read Ratio', ylabel='Operations per Second', title='throughput')

    if store_fig:
       storer.store('throughput', logdir, filetype, plt)

    if not no_show:
        plt.show()