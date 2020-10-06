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
