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

                    open(file, 'w').write(str(download) + ' ' + str(upload))
                log_replace('Down: {download} Up: {upload}'.format(download=download, upload=upload))
            except FileNotFoundError:
                open(file, 'w')
                continue
            except RuntimeError:
                pass
            except Exception as exception:
                log_exception(exception)
            break
