import re
import ssl
import time
import json
import select
import socket
import threading
from .app import *
from .ssh_statistic import *


class server_tunnel(threading.Thread):
    def __init__(self, socket_accept, tunnel_type, silent=False):
        super(server_tunnel, self).__init__()

        self.socket_client, (self.client_host, self.client_port) = socket_accept
        self.tunnel_type = tunnel_type
        self.silent = silent

        self.server_name_indication = open(real_path('/../config/server-name-indication.txt')).read().strip()
        self.payload = open(real_path('/../config/payload.txt')).read().strip()
        self.config = json.loads(open(real_path('/../config/config.json')).read())

        self.do_handshake_on_connect = True
        self.buffer_size = 65535
        self.timeout = 3
        self.daemon = True

    def log(self, value):
        if not self.silent: log(value, status='[G1]INFO')

    def log_replace(self, value):
        if not self.silent: log_replace(value)

    def log_exception(self, value):
        log_exception(value, status='[R1]INFO')

    def extract_client_request(self):
        self.client_request = self.socket_client.recv(self.buffer_size).decode('charmap')
        result = re.findall(r'(([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+):([0-9]+))', self.client_request)
        result = result[0] if len(result) else ''
        if not result:
            self.log('[R1]Target host and port not found')
            return False
        self.host, self.port = result[1], int(result[3])
        return True

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
        self.log('Payload:\n\n{payload}\n'.format(
            payload=self.payload_decode(payload_encode).decode('charmap')
            .replace('\r', '').strip('\n\n')
            .replace('\n' * 6 + '[split]', '\n\n----- SPLIT -----\n\n')
            .replace('\n' * 5 + '[split]', '\n\n----- SPLIT -----\n\n')
            .replace('\n' * 4 + '[split]', '\n\n----- SPLIT -----\n\n')
            .replace('\n' * 3 + '[split]', '\n\n----- SPLIT -----\n\n')
            .replace('\n' * 2 + '[split]', '\n\n----- SPLIT -----\n\n')
            .replace('\n' * 1 + '[split]', '\n\n----- SPLIT -----\n\n')
            .replace('\n' * 0 + '[split]', '\n\n----- SPLIT -----\n\n')
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
            if timeout == 120: break

    def proxy_handler(self):
        loop = 0
        while True:
            if loop == 1: self.log('Replacing response')
            response = self.socket_tunnel.recv(self.buffer_size).decode('charmap')
            if not response: break
            response_status = response.replace('\r', '').split('\n')[0]
            if re.match(r'HTTP/1\.(0|1) 200 (OK|Connection established)', response_status):
                self.log('Response: {response}'.format(response=response_status))
                self.handler()
            else:
                self.log('Response:\n\n{response}\n'.format(response=response.replace('\r', '').split('\n\n')[0]))
                self.socket_tunnel.sendall(b'HTTP/1.0 Connection established\r\n\r\n')
                loop = loop + 1

    # Direct -> SSH
    def tunnel_type_0(self):
        try:
            self.socket_tunnel.connect((self.host, int(self.port)))
            self.send_payload(self.payload)
            self.handler()
        except socket.timeout:
            pass
        except socket.error:
            pass
        except Exception as exception:
            self.log_exception(exception)
        finally:
            self.socket_tunnel.close()
            self.socket_client.close()

    # Direct -> SSH (SSL/TLS)
    def tunnel_type_1(self):
        try:
            self.socket_tunnel.connect((self.host, int(self.port)))
            self.log('Server name indication: {server_hostname}'.format(server_hostname=self.server_name_indication))
            self.socket_tunnel = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(self.socket_tunnel, server_hostname=self.server_name_indication, do_handshake_on_connect=self.do_handshake_on_connect)
            self.certificate()
            self.handler()
        except socket.timeout:
            pass
        except socket.error:
            pass
        except Exception as exception:
            self.log_exception(exception)
        finally:
            self.socket_tunnel.close()
            self.socket_client.close()

    # HTTP Proxy -> SSH
    def tunnel_type_2(self):
        try:
            self.socket_tunnel.connect((self.config['proxy_host'], int(self.config['proxy_port'])))
            self.send_payload(self.payload)
            self.proxy_handler()
        except socket.timeout:
            pass
        except socket.error:
            pass
        except Exception as exception:
            self.log_exception(exception)
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

        self.log('Connecting to {host} port {port}'.format(host=self.host, port=self.port))

        if not self.tunnel_type :
            pass
        elif self.tunnel_type == '0': self.tunnel_type_0()
        elif self.tunnel_type == '1': self.tunnel_type_1()
        elif self.tunnel_type == '2': self.tunnel_type_2()




