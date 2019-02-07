import os
import sys
import time
import signal
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

def log(value, log_datetime=True, status='INFO', status_color='[G1]'):
    with lock:
        datetime_value = '[{value}] '.format(value=datetime.datetime.now().strftime('%H:%M:%S')) if log_datetime else ''
        status = '' if status == None else '[P1]:: {status_color}{status:>4} [P1]:: '.format(status=status, status_color=status_color)
        print(colors('[G1]{datetime}{status}[G1]{value}[CC]'.format(datetime=datetime_value, status=status, value=value)))

def log_replace(value, log_datetime=False, status=None):
    datetime_value = '[{value}] '.format(value=datetime.datetime.now().strftime('%H:%M:%S')) if log_datetime else ''
    status = '' if status == None else '[P1]:: [G1]{status:>4} [P1]:: '.format(status=status)
    sys.stdout.write(colors('[G1]{datetime}{status}[G1]{value}[CC]{cr}'.format(datetime=datetime_value, status=status, value=value, cr='\r')))
    sys.stdout.flush()

def log_exception(value, log_datetime=True, status=''):
    log('[R1]Exception: {value}'.format(value=value), log_datetime=log_datetime, status=status)
