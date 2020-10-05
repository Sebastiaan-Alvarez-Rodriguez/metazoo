import util.location as loc
import util.fs as fs
import urllib.request
import zipfile
from pathlib import Path


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
    if not fs.exists(ziploc):
        url = 'https://downloads.apache.org//ant/binaries/apache-ant-1.10.9-bin.zip'
        urllib.request.urlretrieve(url, ziploc)

    with zipfile.ZipFile(ziploc, 'r') as zip_ref:
        zip_ref.extractall(depsloc)

    apache_ant = 'apache-ant-1.10.9'
    tmploc = fs.join(depsloc, apache_ant)
    for path in fs.ls(tmploc, full_paths=True):
        fs.mv(path, depsloc)
    fs.rm(depsloc, apache_ant)
    fs.rm(ziploc)

    print('installing complete')
    return True






