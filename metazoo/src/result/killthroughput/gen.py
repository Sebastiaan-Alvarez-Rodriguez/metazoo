import matplotlib.pyplot as plt

from result.killthroughput.reader import Reader
import result.util.storer as storer
import util.fs as fs
import util.location as loc


# We process killthroughput experiment results here
def killthroughput(logdir, large, no_show, store_fig, filetype):
    reader = Reader(fs.join(loc.get_metazoo_results_dir(), logdir))
    
    # Reads all log files, and adds numbers from same timestamps together in a handy one-liner
    frame = list(map(lambda *x: sum(x), *[reader.read_ops(x) for x in range(reader.num_files)]))

    fig, ax = plt.subplots()
    ax.plot([x*0.3 for x in range(len(frame))], frame, color='tab:blue')
    
    time = 300
    nr_kills = 7
    nap_time = 300 / (nr_kills+1)

    killpoints = [(1+x)*nap_time for x in range(nr_kills)]
    ax.scatter(killpoints, [frame[int(x*(1.0/0.3))] for x in killpoints], color='tab:red', marker='o', s=400)

    ax.set(xlabel='time (s)', ylabel='ops per 300ms', title='Throughput initial experiment')
    ax.grid()

    fig.tight_layout()

    if store_fig:
        storer.store('kill-throughput', logdir, filetype, plt)

    if not no_show:
        plt.show()