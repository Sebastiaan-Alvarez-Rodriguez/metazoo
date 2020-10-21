import datetime
import time

import util.fs as fs
import util.location as loc
import util.ui as ui
# Generate a timestamp for this experiment and return it
def timestamp():
    # Obtain a timestamp for this experiment, and construct needed directories
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H%M%S')
    print('Timestamped experiment, designation {}'.format(timestamp))
    if fs.isdir(loc.get_metazoo_results_dir(), timestamp):
        if ui.ask_bool('Results already contain timestamp {}. Override (Y) or wait (n)?'):
            fs.rm(loc.get_metazoo_results_dir(), timestamp)
        else:
            while datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H%M%S') == timestamp:
                time.sleep(1)
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H%M%S')
            print('New timestamp assigned: {}'.format(timestamp))
    return timestamp