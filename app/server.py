import socket
import threading
from .app           import *
from .server_tunnel import *


class server(threading.Thread):
    def __init__(self, inject_host_port, external=False, quiet=False):
        super(server, self).__init__()

        self.inject_host, self.inject_port = self.inject_host_port = inject_host_port
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.external = external
        self.quiet = quiet

        self.daemon = True

    def log(self, value, status='INFO', status_color='[G1]'):
        log(value, status=status, status_color=status_color)

    def run(self):
        try:
            self.socket_server.bind(self.inject_host_port)
            self.socket_server.listen(True)
            self.log('Inject running on {inject_host} port {inject_port}'.format(inject_host=self.inject_host, inject_port=self.inject_port))
            while True:
                try:
                    server_tunnel(self.socket_server.accept(), self.external, self.quiet).start()
                except KeyboardInterrupt: pass
        except OSError:
            self.log('Inject not running on {inject_host} port {inject_port} because port used by another programs'.format(inject_host=self.inject_host, inject_port=self.inject_port), status_color='[R1]')
