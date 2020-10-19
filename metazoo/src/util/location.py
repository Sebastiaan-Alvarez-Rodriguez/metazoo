import util.fs as fs
from settings.settings import settings_instance as st

#################### MetaZoo directories ####################
def get_metazoo_dep_dir():
    return fs.join(fs.abspath(), 'deps')

def get_metazoo_experiment_dir():
    return fs.join(fs.abspath(), 'experiments')

def get_metazoo_log_dir():
    return fs.join(fs.abspath(), 'logs')


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
    return fs.join(get_metazoo_dep_dir(), 'ant')

def get_ant_loc_bin():
    return fs.join(get_ant_loc_dep(), 'bin', 'ant')


#################### Remote directories ####################
def get_remote_metazoo_parent_dir():
    return st.remote_metazoo_dir

def get_remote_metazoo_dir():
    return fs.join(get_remote_metazoo_parent_dir(), 'zookeeper')

def get_remote_crawlspace_dir():
    return fs.join(st.remote_crawlspace_dir, 'crawlspace')


#################### Node directories ####################
# Because we  will use client logging using plan 2, this should change
# def get_node_log_dir():
#     return '/local/ddps2009/'