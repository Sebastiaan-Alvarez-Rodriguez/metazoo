# Ask the user to provide an integer value, with optional min and max values
def ask_int(question, minval=None, maxval=None):
    while True:
        try:
            val = input(str(question)+' ').strip()
            val_cast = int(val)
            if minval != None and val_cast < minval:
                print('Input is too small')
                continue
            if maxval != None and val_cast > maxval:
                print('Input is too large')
                continue
            return val_cast
        except Exception as e:
            print('Input "{0}" is not a number. Try again'.format(val))


# Ask user for a boolean value
def ask_bool(question):
    while True:
        val = input(str(question)+' ').strip().lower()
        if val in ('y', 'yes', 't', 'true') :
            return True
        elif val in ('n', 'no', 'f', 'false'):
            return False
        else:
            print('Input "{0}" could not be interpreted as a boolean. Try again'.format(val))

# Ask user for a string, possibly with confirmation
def ask_string(question, confirm=False, empty_ok=False):
    while True:
        val = input(str(question)+' ').strip()
        if not empty_ok and len(val)==0:
            print('You should provide an empty string!')
        elif (confirm and ask_bool('Your choice: "{}". Are you absolutely sure this is correct?'.format(val))) or not confirm:
            return val

# Ask user to pick one of the displayed options.
# Returns integer index of picked item
def ask_pick(question, options: list):
    while True:
        for idx, x in enumerate(options):
            print('[{}] - {}'.format(idx, x))
        try:
            val = input(str(question)+' ').strip()
            val_cast = int(val)
            if val_cast < 0:
                print('Input is too small')
                continue
            if val_cast >= len(options):
                print('Input is too large')
                continue
            return val_cast
        except Exception as e:
            print('Input "{0}" is not a number. Try again'.format(val))