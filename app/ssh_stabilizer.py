import time
import requests
import threading


class ssh_stabilizer(threading.Thread):
    def __init__(self, socks5_port):
        super(ssh_stabilizer, self).__init__()

        self.socks5_port = socks5_port
        self.daemon = True
        self._stop = False
        self.start()

    def stop(self):
        self._stop = True

    def task(self, socks5_port):
        while not self._stop:
            time.sleep(15.000)
            try:
                requests.request('HEAD', 'http://141.0.11.241', proxies={'http': 'socks5h://127.0.0.1:{}'.format(socks5_port), 'https': 'socks5h://127.0.0.1:{}'.format(socks5_port)}, timeout=3, allow_redirects=False)
            except Exception as exception: pass

    def run(self):
        threads = []

        for socks5_port in self.socks5_port:
            threads.append(threading.Thread(target=self.task, args=(socks5_port, )))

        for thread in threads:
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

        threads = []