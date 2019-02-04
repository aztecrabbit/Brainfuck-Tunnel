import socket
import threading
from .app           import *
from .server_tunnel import *


class server(threading.Thread):
    def __init__(self, inject_host_port, tunnel_type, quiet=False):
        super(server, self).__init__()

        self.inject_host, self.inject_port = self.inject_host_port = inject_host_port
        self.tunnel_type = tunnel_type
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.daemon = True
        self.quiet = quiet

    def log(self, value, status='[G1]INFO'):
        log(value, status=status)

    def run(self):
        try:
            self.server.bind(self.inject_host_port)
            self.server.listen(True)
            self.log('[G1]Inject running on {inject_host} port {inject_port}'.format(inject_host=self.inject_host, inject_port=self.inject_port))

            if self.tunnel_type == '0':
                self.log('Tunnel Type: Direct -> SSH')
            elif self.tunnel_type == '1':
                self.log('Tunnel Type: Direct -> SSH (SSL/TLS)')
            elif self.tunnel_type == '2':
                self.log('Tunnel Type: HTTP Proxy -> SSH')

            while True:
                try:
                    server_tunnel(self.server.accept(), self.tunnel_type, self.quiet).start()
                except KeyboardInterrupt: pass
        except OSError as oserror:
            if not oserror:
                message = 'Something error'
            elif 'Cannot assign requested address' in str(oserror):
                message = 'Change host and relaunch this program for better experience'
            elif 'Address already in use' in str(oserror):
                message = 'Change port and relaunch this program for better experience'
            else:
                message = str(oserror)
            self.log('Inject not running on {inject_host} port {inject_port} because port used by another programs'.format(inject_host=self.inject_host, inject_port=self.inject_port), status='[R1]INFO')
            self.log('{message}'.format(message=message))
            self.log('SSH Running')
