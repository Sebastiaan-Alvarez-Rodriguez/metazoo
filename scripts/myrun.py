import sys, getopt
import os

def main(argv):
	nrnodes = -1
	maxnrnodes = 24
	minnrnodes = 1
	try:
		opts, args = getopt.getopt(argv, 'hn:')
	except getopt.GetoptError:
		print('myrun.py -n <number of nodes>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('myrun.py -n <number of nodes>')
		elif opt in ('-n'):
			nrnodes = int(arg)
			if nrnodes < minnrnodes or nrnodes > maxnrnodes:
				print('number of nodes should be between [{}, {}]'.format(minnrnodes, maxnrnodes))
				nrnodes = -1

	while nrnodes == -1: 
		print('How many nodes do you want to allocate?')
		nrnodes = int(input('').strip())
		if nrnodes < minnrnodes or nrnodes > maxnrnodes:
				print('number of nodes should be between [{}, {}]'.format(minnrnodes, maxnrnodes))
				nrnodes = -1
			

	command = 'prun -np ' + str(nrnodes) + ' -1 python3 test.py'
	os.system(command)


if __name__ == '__main__':
	main(sys.argv[1:])