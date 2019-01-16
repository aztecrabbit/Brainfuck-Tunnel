import os
import ssl
import sys
import socket
import datetime
import threading


lock = threading.RLock()

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

def log(value, log_datetime=False, lf=False):
    with lock:
        datetime_value = '[{value}] '.format(value=datetime.datetime.now().strftime('%H:%M:%S')) if log_datetime else ''
        print(colors('[G1]{datetime}{value}[CC]{lf}'.format(datetime=datetime_value, value=value, lf='\n' if lf else '')))

def log_replace(value, log_datetime=False):
    with lock:
        datetime_value = '[{value}] '.format(value=datetime.datetime.now().strftime('%H:%M:%S')) if log_datetime else ''
        sys.stdout.write(colors('[G1]{datetime}{value}[CC]{cr}'.format(datetime=datetime_value, value=value, cr='\r')))
        sys.stdout.flush()

def log_exception(value):
    log('[R1]Exception: {value}'.format(value=value))

def main():
    server_name_indications = []
    host = str('74.125.24.100')
    port = int('443')

    for i in range(len(sys.argv)):
        if i == 0: continue
        server_name_indications.append(sys.argv[i])

    for i in range(len(server_name_indications)):
        try:
            server_name_indication = server_name_indications[i]
            socket_tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_tunnel.settimeout(5)
            log('Connecting to {host} port {port}'.format(host=host, port=port))
            socket_tunnel.connect((host, port))
            log('Server name indication: {server_hostname}'.format(server_hostname=server_name_indication))
            socket_tunnel = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(socket_tunnel, server_hostname=server_name_indication, do_handshake_on_connect=True)
            log('Certificate:\n\n{certificate}'.format(certificate=ssl.DER_cert_to_PEM_cert(socket_tunnel.getpeercert(True))))
            log('Connection established')
            log('Connected')
        except socket.timeout:
            log('[R1]Connection timeout')
            log('Disconnected')
        except socket.error:
            log('[R1]Connection closed')
            log('Disconnected')
        except Exception as exception:
            log_exception(exception)
            log('Disconnected')
        finally:
            socket_tunnel.close()

if __name__ == '__main__':
    main()