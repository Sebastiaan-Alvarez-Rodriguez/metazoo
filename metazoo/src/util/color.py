
from enum import Enum
import os

'''
The greater purpose of (functions in) this file is
to convert strings to colored strings, which helps
navigating the commandline interface
'''

'''An enum to specify what color you want your text to be'''
class Color(Enum):
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

# Print given error text
def printwarn(string, color=Color.YEL, end='\n'):
    print(f'Warning: {format(string, color)}', end=end)

def printerr(string, color=Color.RED, end='\n'):
    print(f'Error: {format(string, color)}', end=end)

# Format a string with a color
def format(string, color):
    if os.name == 'posix':
        return f'{color.value}{string}{Color.CLR.value}'
    return string