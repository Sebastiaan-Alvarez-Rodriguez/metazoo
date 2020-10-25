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
    path = fs.join(loc.get_metazoo_results_dir(), logdir)

    if large: 
        fontsize = 16
        font = {
            'family' : 'DejaVu Sans',
            'weight' : 'bold',
            'size'   : fontsize
        }
        plt.rc('font', **font)


    if original:
        printe('not implemented yet')
        runs = sorted(list(fs.ls(path, only_dirs=True, full_paths=True)))
        servers = []
        for run in runs:
            reader = Reader(run)
            servers.append((x[0][0], sum(n for _, n in x)) for x in zip(*[reader.read_ops(x) for x in range(reader.num_files)]))
        fig, ax = plt.subplots()
        colors = ['r', 'lime', 'b', 'magenta', 'cyan']
        numbers = ['3', '5', '7', '9', '13']
        linestyles = ('solid', 'dashed', 'dotted', (0, (1,1)), 'dashdot')
        for server, color, i, linestyle in zip(servers, colors, numbers, linestyles):
            ax.plot([x for x,_ in server], [x for _, x in server], color=color, linestyle=linestyle, label='{} servers'.format(i))

    else:  
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
        fig, ax = plt.subplots()
        bplot = ax.boxplot(data, patch_artist=True)
        plt.setp(bplot['boxes'], color='lightgreen')
        plt.setp(bplot['boxes'], edgecolor='black')
        plt.setp(bplot['medians'], color='forestgreen')
        plt.xticks(np.arange(len(ticks)+1), labels=ticks)
        
        ax.set(yscale='log', xlabel='Read Ratio', ylabel='Operations per Second', title='Throughput')

    fig.tight_layout()
    if large:
        fig.set_size_inches(8, 6)

    if store_fig:
       storer.store('throughput', logdir, filetype, plt)

    if large:
        plt.rcdefaults()

    if not no_show:
        plt.show()