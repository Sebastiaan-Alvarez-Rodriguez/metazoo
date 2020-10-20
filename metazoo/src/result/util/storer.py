import matplotlib.pyplot as plt

import util.location as loc
import util.fs as fs

def supported_filetypes():
    generator = (x for x in plt.figure().canvas.get_supported_filetypes())
    plt.clf()
    plt.close()
    return generator

def filetype_is_supported(extension):
    return str(extension).strip().lower() in supported_filetypes()

def store(dirname, filename, filetype, plotlike, **kwargs):
    fs.mkdir(loc.get_metazoo_graphs_dir(), dirname, exist_ok=True)
    plotlike.savefig(fs.join(loc.get_metazoo_graphs_dir(), dirname, '{}.{}'.format(filename, filetype)), **kwargs)