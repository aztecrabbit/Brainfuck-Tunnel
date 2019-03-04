import re
import ssl
import time
import json
import random
import select
import socket
import threading
from .app           import *
from .default       import *
from .ssh_statistic import *


class server_tunnel(threading.Thread):
    def __init__(self, socket_accept, force_tunnel_type=None, external=False, quiet=False):
        super(server_tunnel, self).__init__()

        self.socket_client, (self.client_host, self.client_port) = socket_accept
        self.force_tunnel_type = force_tunnel_type
        self.external = external
        self.quiet = quiet

        self.server_name_indication = open(real_path('/../config/server-name-indication.txt')).readlines()[0].strip()
        self.tunnel_type = ''
        self.proxies = []
        self.payload = ''
        self.config = {}

        self.do_handshake_on_connect = True
        self.buffer_size = 65535
        self.timeout = 3
        self.daemon = True

    def force_log(self, value, status='INFO', status_color='[G1]'):
        log(value, status=status, status_color=status_color)

    def log(self, value, status='INFO', status_color='[G1]'):
        if not self.quiet: log(value, status=status, status_color=status_color)

    def log_error(self, value, status='INFO'):
        self.force_log('[R1]{}'.format(value), status=status, status_color='[R1]')

    def log_external(self, value, status='INFO', status_color='[G1]'):
        if self.external: self.log(value, status=status, status_color=status_color)

    def extract_client_request(self):
        self.client_request = self.socket_client.recv(self.buffer_size).decode('charmap')
        result = re.findall(r'(([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+):([0-9]+))', self.client_request)
        result = result[0] if len(result) else ''
        if not result:
            self.log('[R1]Target host and port not found', status_color='[R1]')
            return False
        self.host, self.port = result[1], int(result[3])
        return True

    def get_host_port(self, value):
        value = re.findall(r'(([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+)(:(\d+))?)', value)
        value = value[0] if len(value) else []
        value_host = value[1] if len(value) >= 2 and value[1] else ''
        value_port = value[4] if len(value) >= 5 and value[4] else '80'

        return (value_host, int(value_port)) if value_host and value_port else ''

    def get_proxy(self):
        data_proxies = filter_array(open(real_path('/../config/proxies.txt')).readlines())
        data_proxies = filter_array('\n'.join(data_proxies).split('---')[0].splitlines())
        for proxy in data_proxies:
            proxy = self.get_host_port(proxy)
            if proxy: self.proxies.append(proxy)

        if len(self.proxies):
            self.proxy_host, self.proxy_port = random.choice(self.proxies)

        return True if len(self.proxies) else False

    def get_payload(self):
        data_payload = filter_array(open(real_path('/../config/payload.txt')).readlines())
        data_payload = filter_array('\n'.join(data_payload).split('---')[0].splitlines())
        for value in data_payload:
            value = value.strip()
            if value and not value.startswith('#'):
                self.payload += value

        return self.payload

    def payload_decode(self, payload):
        payload = payload.replace('[real_raw]', '[raw][crlf][crlf]')
        payload = payload.replace('[raw]', '[method] [host_port] [protocol]')
        payload = payload.replace('[method]', 'CONNECT')
        payload = payload.replace('[host_port]', '[host]:[port]')
        payload = payload.replace('[host]', str(self.host))
        payload = payload.replace('[port]', str(self.port))
        payload = payload.replace('[protocol]', 'HTTP/1.0')
        payload = payload.replace('[user-agent]', 'User-Agent: Chrome/1.1.3')
        payload = payload.replace('[keep-alive]', 'Connection: Keep-Alive')
        payload = payload.replace('[close]', 'Connection: Close')
        payload = payload.replace('[crlf]', '[cr][lf]')
        payload = payload.replace('[lfcr]', '[lf][cr]')
        payload = payload.replace('[cr]', '\r')
        payload = payload.replace('[lf]', '\n')

        return payload.encode()

    def send_payload(self, payload_encode = ''):
        payload_encode = payload_encode if payload_encode else '[method] [host_port] [protocol][crlf][crlf]'
        self.log('Payload: \n\n{}\n'.format(('|   ' + self.payload_decode(payload_encode).decode())
            .replace('\r', '')
            .replace('[split]', '$lf\n')
            .replace('\n', '\n|   ')
            .replace('$lf', '\n')
        ))
        payload_split = payload_encode.split('[split]')
        for i in range(len(payload_split)):
            if i > 0: time.sleep(0.200)
            self.socket_tunnel.sendall(self.payload_decode(payload_split[i]))

    def certificate(self):
        self.log('Certificate:\n\n{certificate}'.format(certificate=ssl.DER_cert_to_PEM_cert(self.socket_tunnel.getpeercert(True))))

    def convert_response(self, response):
        response = response.replace('\r', '').rstrip() + '\n\n'

        if response.startswith('HTTP'):
            response = '\n\n|   {}\n'.format(response.replace('\n', '\n|   '))
        else:
            response = '[W2]\n\n{}\n'.format(re.sub(r'\s+', ' ', response.replace('\n', '[CC][Y1]\\n[W2]')))

        return response

    def handler(self):
        sockets = [self.socket_tunnel, self.socket_client]
        timeout = 0
        self.socket_client.sendall(b'HTTP/1.0 200 Connection established\r\n\r\n')
        self.log('Connection established')
        while True:
            timeout += 1
            socket_io, _, errors = select.select(sockets, [], sockets, 3)
            if errors: break
            if socket_io:
                for socket in socket_io:
                    try:
                        data = socket.recv(self.buffer_size)
                        if not data: break
                        if socket is self.socket_tunnel:
                            self.socket_client.sendall(data)
                            if self.quiet != 'full': ssh_statistic('download')
                        elif socket is self.socket_client:
                            self.socket_tunnel.sendall(data)
                            if self.quiet != 'full': ssh_statistic('upload')
                        timeout = 0
                    except: break
            if timeout == 30: break

    def proxy_handler(self):
        x = 0
        while True:
            if x == 1: self.log('Replacing response')
            response = self.socket_tunnel.recv(self.buffer_size).decode('charmap')
            if not response: break
            response_status = response.replace('\r', '').split('\n')[0]
            if re.match(r'HTTP/\d(\.\d)? 200 .+', response_status):
                self.log('Response: {}'.format(self.convert_response(response)))
                self.handler()
                break
            else:
                self.log('Response: {}'.format(self.convert_response(response)))
                self.socket_tunnel.sendall(b'HTTP/1.0 200 Connection established\r\nConnection: keep-alive\r\n\r\n')
                x += 1

    # Direct -> SSH
    def tunnel_type_0(self):
        try:
            self.log('Connecting to {host} port {port}'.format(host=self.host, port=self.port))
            self.socket_tunnel.connect((self.host, int(self.port)))
            self.send_payload(self.get_payload())
            self.handler()
        except socket.timeout:
            self.log_external('Connection timeout', status_color='[R1]')
        except socket.error:
            self.log_external('Connection closed', status_color='[R1]')
        finally:
            self.socket_tunnel.close()
            self.socket_client.close()

    # Direct -> SSH (SSL/TLS)
    def tunnel_type_1(self):
        try:
            self.log('Connecting to {host} port {port}'.format(host=self.host, port=self.port))
            self.socket_tunnel.connect((self.host, int(self.port)))
            self.log('Server name indication: {server_hostname}'.format(server_hostname=self.server_name_indication))
            self.socket_tunnel = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(self.socket_tunnel, server_hostname=self.server_name_indication, do_handshake_on_connect=self.do_handshake_on_connect)
            self.certificate()
            self.handler()
        except socket.timeout:
            self.log_external('Connection timeout', status_color='[R1]')
        except socket.error:
            self.log_external('Connection closed', status_color='[R1]')
        finally:
            self.socket_tunnel.close()
            self.socket_client.close()

    # HTTP Proxy -> SSH
    def tunnel_type_2(self):
        try:
            if self.get_proxy() == False:
                self.log_error('Connecting to remote proxy error (remote proxy not found)')
                return
            self.log('Connecting to remote proxy {proxy_host} port {proxy_port}'.format(proxy_host=self.proxy_host, proxy_port=self.proxy_port))
            self.socket_tunnel.connect((self.proxy_host, self.proxy_port))
            self.log('Connecting to {host} port {port}'.format(host=self.host, port=self.port))
            self.send_payload(self.get_payload())
            self.proxy_handler()
        except socket.timeout:
            self.log_external('Connection timeout', status_color='[R1]')
        except socket.error:
            self.log_external('Connection closed', status_color='[R1]')
        finally:
            self.socket_tunnel.close()
            self.socket_client.close()

    def run(self):
        self.socket_tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_tunnel.settimeout(self.timeout)

        try:
            self.config_file = real_path('/../config/config.json')
            self.config = json.loads(open(self.config_file).read())
            self.tunnel_type = self.config['tunnel_type'] if not self.external else self.config['tunnel_type_external']
            if not self.tunnel_type or int(self.tunnel_type) >= 3: raise KeyError
        except KeyError:
            json_error(self.config_file)
            self.socket_tunnel.close()
            self.socket_client.close()
            return

        if not self.extract_client_request():
            self.log_error('Client request error (target host and port not found)')
            self.socket_tunnel.close()
            self.socket_client.close()
            return

        if self.force_tunnel_type is not None:
            self.tunnel_type = self.force_tunnel_type

        if not self.tunnel_type :
            pass
        elif self.tunnel_type == '0': self.tunnel_type_0()
        elif self.tunnel_type == '1': self.tunnel_type_1()
        elif self.tunnel_type == '2': self.tunnel_type_2()
