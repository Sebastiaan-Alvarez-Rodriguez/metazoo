import time
import fcntl
import os
import signal


# Remove
def listener_dir_remove(directory):
    # signal.signal(signal.SIGIO, handler)
    fd = os.open(directory,  os.O_RDONLY)
    # fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
    fcntl.fcntl(fd, fcntl.F_NOTIFY, 0)


# Sets watch on directory. Watch must take parameters (signum, frame).
# Signum is the signal received from the file descriptor (SIGIO)
# Frame is None most of the time
def listener_dir_create(directory, oncreate):
    signal.signal(signal.SIGIO, oncreate)
    fd = os.open(directory, os.O_RDONLY)
    fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
    fcntl.fcntl(fd, fcntl.F_NOTIFY, fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)


# https://stackoverflow.com/a/473471
# Signal list: https://github.com/python/cpython/blob/master/Modules/fcntlmodule.c
# Signal tutorial: https://www.tutorialspoint.com/unix_system_calls/fcntl.htm
# FNAME = "/HOME/TOTO/FILETOWATCH"

# def handler(signum, frame):
#     print('File {} modified'.format(FNAME))

# signal.signal(signal.SIGIO, handler)
# fd = os.open(FNAME,  os.O_RDONLY)
# fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
# fcntl.fcntl(fd, fcntl.F_NOTIFY, fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)

# while True:
#     time.sleep(10000)