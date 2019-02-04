import time
import requests
import threading
from .app import *


class http_requests(threading.Thread):
    def __init__(self, socks5_ports, enable):
        super(http_requests, self).__init__()

        self.socks5_ports = socks5_ports
        self.enable = enable
        self.daemon = True
        self._stop = True

    def log(self, value, status='INFO', status_color='[G1]'):
        if not self.enable: return
        log(value, status=status, status_color=status_color)

    def stop(self):
        if not self.enable: return
        if self._stop == False: self.log('HTTP Requests stopped')
        self._stop = True

    def run(self):
        if not self.enable: return
        self._stop = False
        self.log('HTTP Requests started')

        threads = []

        for socks5_port in self.socks5_ports:
            threads.append(threading.Thread(target=self.task, args=(socks5_port, )))

        for thread in threads:
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

        threads = []

    def task(self, socks5_port):
        while not self._stop:
            try:
                response = requests.head(
                    url='http://141.0.11.241',
                    proxies={
                        'http': 'socks5h://127.0.0.1:{}'.format(socks5_port),
                        'https': 'socks5h://127.0.0.1:{}'.format(socks5_port)
                    },
                    timeout=5,
                    allow_redirects=False
                )
                self.log('Response: {}'.format(response.status_code), status=socks5_port)
            except requests.exceptions.Timeout:
                self.log('[R1]Response: ERR', status=socks5_port, status_color='[R1]')
            except requests.exceptions.ConnectionError:
                self.log('[R2]Response: ERR', status=socks5_port, status_color='[R2]')
            except Exception as exception:
                pass
            finally: time.sleep(15.000)
