# The greater purpose of (functions in) this file is
# to convert strings to colored strings, which helps
# navigating the commandline interface


from enum import Enum
import os


class Color(Enum):
    '''An enum to specify what color you want your text to be'''
    RED = '\033[1;31m'
    GRN = '\033[1;32m'
    YEL = '\033[1;33m'
    BLU = '\033[1;34m'
    PRP = '\033[1;35m'
    CAN = '\033[1;36m'
    CLR = '\033[0m'

# Print given text with given color
def printc(string, color, end='\n'):
    print(format(string, color), end=end)

# Print given warning text
def printwarn(string, color=Color.YEL, **kwargs):
    print(f'[WARNING] {format(string, color)}', **kwargs)

# Print given warning text, flushing to terminal.
# Because we flush so many times, we made this shortcut
def printwarnf(string, color=Color.YEL, **kwargs):
    printwarn(string, color, flush=True, **kwargs)


# Print given error text
def printerr(string, color=Color.RED, **kwargs):
    print(f'Error: {format(string, color)}', **kwargs)

# Print given error text, flushing to terminal.
# Because we flush so many times, we made this shortcut
def printerrf(string, color=Color.RED, **kwargs):
    printerr(string, color, flush=True, **kwargs)

# Format a string with a color
def format(string, color):
    if os.name == 'posix':
        return '{}{}{}'.format(color.value, string, Color.CLR.value)
    return string