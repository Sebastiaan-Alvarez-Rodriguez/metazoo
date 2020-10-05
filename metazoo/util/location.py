import util.fs as fs

#################### MetaZoo directories ####################

def get_dep_dir():
    return fs.join(fs.abspath(), 'deps')

#################### Zookeeper directories ####################
def get_zookeeper_dir():
    return fs.join(fs.dirname(fs.abspath()), 'zookeeper-release-3.3.0')

def get_build_dir():
    return fs.join(get_zookeeper_dir(), 'build')

def get_cfg_dir():
    return fs.join(get_zookeeper_dir(), 'conf')

def get_bin_dir():
    return fs.join(get_zookeeper_dir(), 'bin')

def get_lib_dir():
    return fs.join(get_zookeeper_dir(), 'src', 'java', 'lib')

def get_build_lib_dir():
    return fs.join(get_build_dir(), 'lib')

#################### Ant directories ####################
def get_ant_loc_dep():
    return fs.join(get_dep_dir(), 'ant')

def get_ant_loc_bin():
    return fs.join(get_ant_loc_dep(), 'bin', 'ant')



#################### Remote directories ####################
def get_remote_dir():
    return '/var/scratch/ddps2009/'

def get_remote_prj_dir():
    return fs.join(get_remote_dir(), 'zookeeper')