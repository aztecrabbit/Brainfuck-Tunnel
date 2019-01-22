import json
import threading
from .app import *


lock = threading.RLock()

class ssh_statistic(threading.Thread):
    def __init__(self, command = ''):
        super(ssh_statistic, self).__init__()

        self.command = command
        self.start()

    def run(self):
        file = real_path('/data/statistic.txt')
        while True:
            try:
                with lock:
                    data = open(file, 'r').read()
                    download, upload = data.split(' ') if len(data.split(' ')) == 2 else (0, 0)

                    if not self.command:
                        return
                    elif self.command == 'download':
                        download = int(download) + 1
                    elif self.command == 'upload':
                        upload = int(upload) + 1
                    elif self.command == 'clear':
                        open(file, 'w').write('0 0')
                        return

                    log_replace('[Y1]Down: {download} Up: {upload}'.format(download=download, upload=upload))
                    open(file, 'w').write(str(download) + ' ' + str(upload))
                    break
            except FileNotFoundError:
                open(file, 'w')
            except RuntimeError:
                break
            except Exception as exception:
                log('[R1]Exception: {exception}'.format(exception=exception), status='[R1]INFO')
                break