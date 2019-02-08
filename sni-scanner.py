import re
import app
import ssl
import socket


def log(value, status='INFO', status_color='[G1]'):
    app.log(value, status=status, status_color=status_color)

def main():
    log('Type hostname to scan that hostname (example: goo.gl fb.me etc)')
    log('Type exit to exit\n')

    host = str('74.125.24.100')
    port = int('443')

    while True:
        server_name_indications = app.str_input(':: ', newline=True)
        server_name_indications = app.filter_array(re.sub(r'\s+', ' ', server_name_indications).split(' '))

        if len(server_name_indications) and server_name_indications[0] == 'exit':
            break

        for server_name_indication in server_name_indications:
            try:
                if server_name_indication == 'exit': print(':: exit'); return
                socket_tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_tunnel.settimeout(3)
                log('Connecting to {host} port {port}'.format(host=host, port=port))
                socket_tunnel.connect((host, port))
                log('Server name indication: {server_hostname}'.format(server_hostname=server_name_indication))
                socket_tunnel = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(socket_tunnel, server_hostname=server_name_indication, do_handshake_on_connect=True)
                certificate = ssl.DER_cert_to_PEM_cert(socket_tunnel.getpeercert(True)).splitlines()
                certificate = '\n'.join(certificate[:13] + certificate[-13:])
                log('Certificate: \n\n{}\n'.format(certificate))
                log('Connection established')
                log('[Y1]Connected', status_color='[Y1]')
            except socket.timeout:
                log('[R1]Connection timeout', status_color='[R1]')
            except socket.error:
                log('[R1]Connection closed', status_color='[R1]')
            finally:
                socket_tunnel.close(); print()

if __name__ == '__main__':
    main()
