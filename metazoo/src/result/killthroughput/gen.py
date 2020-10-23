import matplotlib.pyplot as plt
import numpy as np

from result.killthroughput.reader import Reader
from result.killthroughput.identifier import Identifier
import result.util.storer as storer
import util.fs as fs
import util.location as loc


# We process killthroughput experiment results here
def killthroughput(logdir, large, no_show, store_fig, filetype):
    '''
        ith-experiment:
            experiment_logs/kills.log
            0.log
            1.log
            .
            .
            .
            255.log
    '''
    '''
        # STEP 1: bepalen van events per log: FOLLOWER_KILL or LEADER_KILL
        # STEP 2: verdelen van frames in: event bins
        # STEP 3: voor elke stap in bins ('bin1[i][j]', met i = lognr, j = step)
            # STEP 3a: bereken 25th, 50th, 75th percentile 
        # STEP 4: plot, 50th percentiles as lines, 25th and 75th as areas around lines
        IDEA: 
            frame = [ops for all clients]
            list with booleans, indicating if an event is LEADER_KILL or not
            leader = [True, False, True, ... , False]

            bin_leader = [e0[ops], e1[ops], e2[ops], ...]
            bin_follower = [e0[ops], e1[ops], ...]
    
            med_leader = [med(ei[ops0]), med(ei[ops1])] (same for 25th and 75th)
            plot med_leader etc
    '''
    reader = Reader(fs.join(loc.get_metazoo_results_dir(), logdir))
    identifier = Identifier(fs.join(loc.get_metazoo_results_dir(), logdir))

    # Reads all log files, and adds numbers from same timestamps together in a handy one-liner
    frame = list(map(lambda *x: sum(x), *[reader.read_ops(x) for x in range(reader.num_files)]))
    leaders = identifier.identify_leaders()

    time = 300
    log_time = 0.3
    nr_kills = 7
    nap_time = time / (nr_kills+1)
    bin_sizes = nap_time / log_time

    if len(leaders) != nr_kills:
        raise RuntimeError('kill logs is ill-formatted, please provide {} lines'.format(nr_kills))

    killers = [int((1+x)*bin_sizes) for x in range(nr_kills)]
    radius = bin_sizes // 2
    bin_leader = []
    bin_follower = []
    for i, kill in enumerate(killers):
        event = [frame[i] for i in range(i - radius, i + radius)]
        if leaders[i]:
            bin_leader.append(event)
        else:
            bin_follower.append(event)

    med_leader = []
    med_follower = []
    up_leader = []
    up_follower = []
    low_leader = []
    low_follower = []

    for i in range(int(2*radius)):
        leaders = [event[i] for event in bin_leader]
        followers = [event[i] for event in bin_follower]
        med_follower.append(np.percentile(leaders, 50))
        up_follower.append(np.percentile(leaders, 75))
        low_follower.append(np.percentile(leaders, 25))
        med_leader.append(np.percentile(followers, 50))
        up_leader.append(np.percentile(followers, 75))
        low_leader.append(np.percentile(followers, 25))

    fig, ax = plt.subplots()


    
    #ax.plot([x*0.3 for x in range(len(frame))], frame, color='tab:blue')


    #killpoints = [(1+x)*nap_time for x in range(nr_kills)]
    #ax.scatter(killpoints, [frame[int(x*(1.0/0.3))] for x in killpoints], color='tab:red', marker='o', s=400)

    #ax.set(xlabel='time (s)', ylabel='ops per 300ms', title='Throughput initial experiment')
    #ax.grid()

    fig.tight_layout()

    #if store_fig:
    #    storer.store('kill-throughput', logdir, filetype, plt)

    if not no_show:
        plt.show()