import os
import sys
import socket
import datetime
import threading


lock = threading.RLock()

class safe_dict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def colors(value):
    patterns = {
        'CC' : '\033[0m',    'BB' : '\033[1m',
        'D1' : '\033[30;1m', 'D2' : '\033[30;2m',
        'R1' : '\033[31;1m', 'R2' : '\033[31;2m',
        'G1' : '\033[32;1m', 'G2' : '\033[32;2m',
        'Y1' : '\033[33;1m', 'Y2' : '\033[33;2m',
        'B1' : '\033[34;1m', 'B2' : '\033[34;2m',
        'P1' : '\033[35;1m', 'P2' : '\033[35;2m',
        'C1' : '\033[36;1m', 'C2' : '\033[36;2m',
        'W1' : '\033[37;1m', 'W2' : '\033[37;2m'
    }
    for code in patterns:
        value = value.replace('[{code}]'.format(code=code), patterns[code])
    return value

def filter_array(array):
    for i in range(len(array)):
        if array[i].startswith('#'): array[i] = ''

    array = [x for x in array if x]

    return array

def xstrip(value, string=None):
    value = value.strip(string).encode()    \
        .replace(b'\x1b[A', b'')            \
        .replace(b'\x1b[B', b'')            \
        .replace(b'\x1b[C', b'')            \
        .replace(b'\x1b[D', b'')            \
        .decode().strip()
    return value

def app_format(value, align, width, chars = ''):
    value = ('{:' + str(chars) + str(align) + str(width) + '}').format(value)
    return value

def json_shuffle(data):
    keys = list(data.keys())
    random.shuffle(keys)
    data = [(key, data[key]) for key in keys]
    return data

def str_input(value, newline=False):
    with lock:
        string = xstrip(str(input(value)))
        if newline: print()

    return string

def log_format(value, time=True, status=None, status_color=''):
    value_status = ''
    value_time = ''

    if status is not None:
        value_status = '[P1]:: [G1]{}{:>4} [P1]:: '.format(status_color, status)
    
    if time == True:
        value_time = '{}[{}] '.format(status_color, datetime.datetime.now().strftime('%H:%M:%S'))

    return colors(
        '{value_time}{value_status}{status_color}{value}{end}'.format(
            value_time=value_time,
            value_status=value_status,
            status_color=status_color,
            value=value,
            end='[CC]'
        )
    )

def log(value, time=True, status='INFO', status_color='[G1]'):
    with lock:
        print(log_format(value, time=time, status=status, status_color=status_color))

def log_replace(value, time=False, status=None, status_color='[Y1]'):
    sys.stdout.write('\r')
    sys.stdout.write(log_format(value, time=time, status=status, status_color=status_color))
    sys.stdout.write('\r')
    sys.stdout.flush()

def log_exception(value, time=True, status='INFO', status_color='[R1]'):
    log('Exception: {}'.format(value), time=time, status=status, status_color='[R1]')
