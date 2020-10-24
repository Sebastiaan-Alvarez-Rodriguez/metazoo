import matplotlib.pyplot as plt
import numpy as np

from result.faulttolerance.assembler import Assembler
import result.util.storer as storer
import util.fs as fs
import util.location as loc


# We process faulttolerance experiment results here
def faulttolerance(logdir, large, no_show, store_fig, filetype):
    assembler = Assembler(fs.join(loc.get_metazoo_results_dir(), logdir))

    # Reads all log files, and adds numbers from same timestamps together in a handy one-liner
    frames = list(assembler.read_ops())
    leader_kills = list(assembler.identify_leaders())

    time = 300
    log_time = 0.3                        # Amount of seconds between every log moment
    nr_kills = 7
    nap_time = time / (nr_kills+1)        # Amount of seconds between every 2 kills
    kill_idx_dists = nap_time / log_time  # Amount of indices between every 2 kills

    for kill in leader_kills:
        if len(kill) != nr_kills:
            raise RuntimeError('kill-logs is ill-formated, please provide {} lines'.format(nr_kills))
    if len(leader_kills) != len(frames):
        raise RuntimeError('Missing leader kill info (or frames)')

    kill_idxs = [int((1+x)*kill_idx_dists) for x in range(nr_kills)] #All kill starting indices
    radius = int(kill_idx_dists // 2) # We want a window with this radius for each kill
    bin_leader = []
    bin_follower = []
    for i, kill in enumerate(kill_idxs):
        for frame, leader_kill in zip(frames, leader_kills):
            event = [frame[j] for j in range(kill - radius, kill + radius)]
            if leader_kill[i]:
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
        med_leader.append(np.percentile(leaders, 50))
        up_leader.append(np.percentile(leaders, 75))
        low_leader.append(np.percentile(leaders, 25))
        med_follower.append(np.percentile(followers, 50))
        up_follower.append(np.percentile(followers, 75))
        low_follower.append(np.percentile(followers, 25))

    fig, ax = plt.subplots()

    # for i, kill in enumerate(kill_idxs):
    #     event = [frame[i] for i in range(i - radius, i + radius)]
    #     ax.plot([x*0.3 for x in range(-radius, radius)], event, color='tab:red')

    x_points = [x*log_time for x in range(-radius, radius)]

    ax.plot(x_points, (1/log_time)*np.array(med_leader), color='tab:red')
    ax.vlines(x_points, (1/log_time)*np.array(low_leader), (1/log_time)*np.array(up_leader), color='tab:red', alpha=0.6, zorder=0)
    ax.plot(x_points, (1/log_time)*np.array(med_follower), color='tab:green')
    ax.vlines(x_points, (1/log_time)*np.array(low_follower), (1/log_time)*np.array(up_follower), color='tab:green', alpha=0.6, zorder=0)
    ax.set(xlabel='Time (seconds)', ylabel='Operations per Second', title='Operations per second around Kill Events')


    # ax.plot([x*0.3 for x in range(len(frame))], frame, color='tab:blue')
    # killpoints_leader = [(1+x)*nap_time for x in range(nr_kills) if leader_kills[x]]
    # killpoints_follower = [(1+x)*nap_time for x in range(nr_kills) if not leader_kills[x]]
    # ax.scatter(killpoints_leader, [frame[int(x*(1.0/0.3))] for x in killpoints_leader], color='tab:red', marker='o', s=400)
    # ax.scatter(killpoints_follower, [frame[int(x*(1.0/0.3))] for x in killpoints_follower], color='tab:green', marker='o', s=400)

    #killpoints = [(1+x)*nap_time for x in range(nr_kills)]


    #ax.set(xlabel='time (s)', ylabel='ops per 300ms', title='Throughput initial experiment')
    #ax.grid()

    fig.tight_layout()

    # if store_fig:
    #    storer.store('kill-throughput', logdir, filetype, plt)

    if not no_show:
        plt.show()