from collections import defaultdict
import matplotlib.pyplot as plt 
import numpy as np 

from result.throughput.assembler import Assembler
from result.throughput.reader import Reader
import result.util.storer as storer 
from result.util.tabler import table_open
import util.fs as fs
import util.location as loc 
from util.printer import *

def throughput(logdir, large, no_show, store_fig, filetype, original):
    seconds = 5
    if original:
        printe('not implemented yet')
    else:
        path = fs.join(loc.get_metazoo_results_dir(), logdir)
        assembler = Assembler(path)
        frames = [(x[0][0], [n for _, n in x]) for x in zip(*list(assembler.read_ops()))]
        
        percentiles = [1, 25, 50, 75, 99]
        print('Horizontal: percentiles\nVertical: Read ratios')
        with table_open(len(percentiles)+1) as table:
            table.write_elem('-')
            table.write_elems(percentiles)
            for x in frames:
                table.write_elem(x[0])
                nparr = np.array(x[1]) #Convert to np-array once instead of for every column
                for y in percentiles:
                    table.write_elem(np.percentile(nparr, y, interpolation='nearest'))

        data = [x for _, x in frames]
        ticks = ['']
        ticks.extend([x for x, _ in frames])
        #frame = ((x[0][0], sum(n for _, n in x)) for x in zip(*[reader.read_ops(x) for x in range(reader.num_files)]))
        fig, ax = plt.subplots()
        ax.boxplot(data)
        plt.xticks(np.arange(len(ticks)+1), labels=ticks)

        # axes = [None for x in range(5)]
        # axes[0] = plt.subplot(231)
        # axes[0].tick_params(axis='y', direction='in', pad=-40)
        # axes[1] = plt.subplot(232, sharex=axes[0])
        # axes[1].tick_params(axis='y', direction='in', pad=-40)
        # axes[2] = plt.subplot(233, sharex=axes[0])
        # axes[2].tick_params(axis='y', direction='in', pad=-40)
        # axes[3] = plt.subplot(234)
        # axes[3].tick_params(axis='y', direction='in', pad=-40)
        # axes[4] = plt.subplot(235, sharex=axes[3])
        # axes[4].tick_params(axis='y', direction='in', pad=-40)
        # for i, x in enumerate(data):
        #     axes[i].boxplot(x)
        
        ax.set(yscale='log', xlabel='Read Ratio', ylabel='Operations per Second', title='throughput')

    if store_fig:
       storer.store('throughput', logdir, filetype, plt)

    if not no_show:
        plt.show()