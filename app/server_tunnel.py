import re
import ssl
import time
import json
import random
import select
import socket
import threading
from .app           import *
from .ssh_statistic import *


class server_tunnel(threading.Thread):
    def __init__(self, socket_accept, tunnel_type, quiet):
        super(server_tunnel, self).__init__()

        self.socket_client, (self.client_host, self.client_port) = socket_accept
        self.tunnel_type = tunnel_type
        self.quiet = quiet

        self.server_name_indication = open(real_path('/../config/server-name-indication.txt')).readlines()[0].strip()
        self.proxies = []
        self.config = json.loads(open(real_path('/../config/config.json')).read())

        self.do_handshake_on_connect = True
        self.buffer_size = 65535
        self.timeout = 3
        self.daemon = True

    def log(self, value, status='INFO', status_color='[G1]'):
        if not self.quiet: log(value, status=status, status_color=status_color)

    def log_replace(self, value):
        if not self.quiet: log_replace(value)

    def log_exception(self, value):
        log_exception(value, status='[R1]INFO')

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
        result = re.findall(r'(([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+):([0-9]+))', value)
        result = result[0] if len(result) else []
        result = (result[1], int(result[3])) if len(result) else ''

        return result

    def get_proxy(self):
        data_proxies = open(real_path('/../config/proxies.txt')).read().split('---')[0].splitlines()
        data_proxies = filter_array(data_proxies)
        for data_proxy in data_proxies:
            proxy = self.get_host_port(data_proxy)
            if proxy: self.proxies.append(proxy)
        if len(self.proxies) == 0:
            return False
        random.shuffle(self.proxies)
        self.proxy_host, self.proxy_port = self.proxies[random.randint(0, len(self.proxies)-1)]
        return True

    def payload(self):
        payload = ''

        for value in open(real_path('/../config/payload.txt')).read().split('---')[0].splitlines():
            value = value.strip()
            if value and not value.startswith('#'):
                payload = payload + value

        return payload

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

        return payload.encode('charmap')

    def send_payload(self, payload_encode = ''):
        payload_encode = payload_encode if payload_encode else '[method] [host_port] [protocol][crlf][crlf]'
        self.log('Payload: \n\n{payload}\n'.format(
            payload=('|   ' + self.payload_decode(payload_encode).decode('charmap'))
                .replace('\r', '')
                .replace('[split]', '$lf\n')
                .replace('\n', '\n|   ')
                .replace('$lf', '\n')
        ))
        payload_splits = payload_encode.split('[split]')
        for i in range(len(payload_splits)):
            if i > 0: time.sleep(0.200)
            payload = payload_splits[i]
            payload = self.payload_decode(payload)
            self.socket_tunnel.sendall(payload)

    def certificate(self):
        self.log('Certificate:\n\n{certificate}'.format(certificate=ssl.DER_cert_to_PEM_cert(self.socket_tunnel.getpeercert(True))))

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
                        if not data:
                            break
                        if socket is self.socket_tunnel:
                            self.socket_client.sendall(data)
                            ssh_statistic('download')
                        elif socket is self.socket_client:
                            self.socket_tunnel.sendall(data)
                            ssh_statistic('upload')
                        timeout = 0
                    except: break
            if timeout == 30: break

    def convert_response(self, response):
        if response.startswith('HTTP'):
            response = '\n\n|   {}\n'.format(response.replace('\r', '').split('\n\n')[0].replace('\n', '\n|   '))

        else:
            response = '[W2]\n\n{}\n'.format(re.sub(
                r'\s+', ' ', response.replace('\r', '[CC][Y1]\\r[W2]').replace('\n', '[CC][Y1]\\n[W2]')
            ))

        return response

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
                self.socket_tunnel.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
                x += 1

    # Direct -> SSH
    def tunnel_type_0(self):
        try:
            self.log('Connecting to {host} port {port}'.format(host=self.host, port=self.port))
            self.socket_tunnel.connect((self.host, int(self.port)))
            self.send_payload(self.payload())
            self.handler()
        except socket.timeout:
            pass
        except socket.error:
            pass
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
            pass
        except socket.error:
            pass
        finally:
            self.socket_tunnel.close()
            self.socket_client.close()

    # HTTP Proxy -> SSH
    def tunnel_type_2(self):
        try:
            if self.get_proxy() == False: return
            self.log('Connecting to remote proxy {proxy_host} port {proxy_port}'.format(proxy_host=self.proxy_host, proxy_port=self.proxy_port))
            self.socket_tunnel.connect((self.proxy_host, self.proxy_port))
            self.log('Connecting to {host} port {port}'.format(host=self.host, port=self.port))
            self.send_payload(self.payload())
            self.proxy_handler()
        except socket.timeout:
            pass
        except socket.error:
            pass
        finally:
            self.socket_tunnel.close()
            self.socket_client.close()

    def run(self):
        self.socket_tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_tunnel.settimeout(self.timeout)

        if not self.extract_client_request():
            self.socket_tunnel.close()
            self.socket_client.close()
            return

        if not self.tunnel_type :
            pass
        elif self.tunnel_type == '0': self.tunnel_type_0()
        elif self.tunnel_type == '1': self.tunnel_type_1()
        elif self.tunnel_type == '2': self.tunnel_type_2()
