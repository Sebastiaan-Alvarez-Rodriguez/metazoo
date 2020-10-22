# In this fiile, we provide functions to
# install and interact with Apache Ant

from pathlib import Path
import urllib.request
import zipfile

import util.fs as fs
import util.location as loc
from util.printer import *


# Check if Ant is installed in deps/ant
def ant_available():
    return fs.isdir(loc.get_ant_loc_dep()) and fs.isfile(loc.get_ant_loc_bin())


#installs Ant
def install():
    if ant_available():
        return True

    depsloc = loc.get_ant_loc_dep()
    fs.mkdir(depsloc, exist_ok=True)
    print('Installing ant in {0}'.format(depsloc))

    ziploc = fs.join(depsloc, 'ant.zip')
    Path(ziploc).touch()

    for x in range(5):
        fs.rm(ziploc)
        url = 'https://downloads.apache.org//ant/binaries/apache-ant-1.10.9-bin.zip'
        print('[{0}]Fetching ant from {1}'.format(x, url))
        urllib.request.urlretrieve(url, ziploc)

        try:
            with zipfile.ZipFile(ziploc, 'r') as zip_ref:
                zip_ref.extractall(depsloc)
            break
        except zipfile.BadZipFile as e:
            if x == 4:
                printe('Could not download zip file correctly')
                return False
            elif x == 0:
                printw('Bad zipfile detected. Retrying...')

    apache_ant = 'apache-ant-1.10.9'
    tmploc = fs.join(depsloc, apache_ant)
    for path in fs.ls(tmploc, full_paths=True):
        fs.mv(path, depsloc)
    fs.rm(depsloc, apache_ant)
    fs.rm(ziploc)

    print('installing complete')
    return True






