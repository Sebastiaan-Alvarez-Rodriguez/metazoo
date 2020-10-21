import argparse
import sys

import util.location as loc
import util.fs as fs


def subparser(registrar):
    resultparser = registrar.add_parser('results', help='Build all kinds of graphs (use results -h to see more...)')
    group = resultparser.add_mutually_exclusive_group()
    group.add_argument('-kt', '--kill-throughput', nargs=1, metavar='timestamp', dest='killthroughput', help='Build kill_throughput graph, reading from metazoo/results/<timestamp>')
    resultparser.add_argument('-l', '--large', help='Forces to generate large graphs, with large text', action='store_true')
    resultparser.add_argument('-ns', '--no-show', dest='no_show', help='Do not show generated graph (useful on servers without xorg forwarding)', action='store_true')
    resultparser.add_argument('-s', '--store', help='Store generated graph (in /metazoo/graphs/<graph_name>/<timestamp>.<type>)', action='store_true')
    resultparser.add_argument('-t', '--type', nargs=1, help='Preferred storage type (default=pdf)', default='pdf')

def result_args_set(args):
    return hasattr(args, 'killthroughput')

def results(parser, args):
    if not importer.library_exists('matplotlib'):
        print('Cannot work with results. Matplotlib is not available!')
        return

    if args.store and args.type is None:
        parser.error('--store (-st) requires --type (-t)')
        return
    import result.util.storer as storer
    if args.store and not storer.filetype_is_supported(args.type):
        parser.error('--type only supports filetypes: '+', '.join(storer.supported_filetypes()))
        return

    if not fs.isdir(loc.get_metazoo_results_dir()):
        print('[FAILURE] You have no experiment results directory "{}". Run experiments to get some data first.'.format(log.get_metazoo_results_dir()))
    fargs = [args.large, args.no_show, args.store, args.type]
    if args.killthroughput:
        import result.killthroughput.gen as kgen
        kgen.killthroughput(args.killthroughput[0], *fargs)
