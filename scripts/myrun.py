import sys, getopt
import os

def main(argv):
    nrnodes = -1
    coreaffinity = -1
    maxnrnodes = 24
    minnrnodes = -1
    try:
        opts, args = getopt.getopt(argv, 'hn:c:')
    except getopt.GetoptError:
        print('myrun.py -n <number of nodes>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('myrun.py -n <number of nodes> -c <core affinity>')
        elif opt in ('-n'):
            nrnodes = int(arg)
            if nrnodes < minnrnodes or nrnodes > maxnrnodes:
                print('number of nodes should be between [{}, {}]'.format(minnrnodes, maxnrnodes))
                nrnodes = -1
        elif opt in ('-c'):
            coreaffinity = int(arg)
            if coreaffinity < 1 or coreaffinity > 8:
                print('Only can set core affinity to 1, 2, or 4')
                coreaffinity = -1

    while nrnodes == -1: 
        print('How many nodes do you want to allocate?')
        nrnodes = int(input('').strip())
        if nrnodes < minnrnodes or nrnodes > maxnrnodes:
            print('number of nodes should be between [{}, {}]'.format(minnrnodes, maxnrnodes))
            nrnodes = -1

    while coreaffinity == -1:
        val = input('Set a core affinity (or press enter to pick default [1]): ')
        if len(val) == 0:
            coreaffinity = 1
        else:
            coreaffinity = int(val)
            if coreaffinity < 1 or coreaffinity > 8:
                print('Only can set core affinity to 1, 2, or 4')
                coreaffinity = -1

    command = 'prun -np {} -{} python3 test.py'.format(nrnodes, coreaffinity)
    os.system(command)


if __name__ == '__main__':
    main(sys.argv[1:])