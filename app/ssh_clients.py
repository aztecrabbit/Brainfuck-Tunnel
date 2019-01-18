import os
import json
import time
import socket
import random
import requests
import threading
import subprocess
from .app            import *
from .ssh_create     import *
from .ssh_statistic  import *
from .ssh_stabilizer import *


class ssh_clients(object):
    
    _connected = set()

    def __init__(self, tunnel_type, inject_host, inject_port, socks5_port):
        super(ssh_clients, self).__init__()

        self.tunnel_type = tunnel_type
        self.inject_host = inject_host
        self.inject_port = inject_port
        self.socks5_port = socks5_port
        self.accounts = []
        self.unique = 0
        self.daemon = True

    def log(self, value, status=''):
        log(value, status=status)

    def connected(self, socks5_port):
        self._connected.add(socks5_port)

    def disconnected(self, socks5_port):
        if socks5_port in self._connected:
            self._connected.remove(socks5_port)

    def connected_listener(self):
        while True:
            time.sleep(0.200)
            if len(self._connected) == len(self.socks5_port):
                self.log('[Y1]Connected', status='[Y1] all')
                self.disconnected_listener()

    def disconnected_listener(self):
        while True:
            time.sleep(1.000)
            if len(self._connected) != len(self.socks5_port):
                break

    class ssh_request(threading.Thread):
        def __init__(self, socks5_port):
            super(ssh_clients.ssh_request, self).__init__()

            self.socks5_port = socks5_port
            self.daemon = True
            self._stop = False

        def stop(self):
            self._stop = True

        def run(self):
            while not self._stop:
                try:
                    requests.request('HEAD', 'http://141.0.11.241', proxies={'http': 'socks5h://127.0.0.1:{}'.format(self.socks5_port), 'https': 'socks5h://127.0.0.1:{}'.format(self.socks5_port)}, timeout=3, allow_redirects=False)
                    if not self._stop: ssh_clients.connected(ssh_clients, self.socks5_port)
                    break
                except Exception as exception: pass

    def start(self):
        ssh_stabilizer(self.socks5_port)
        while True:
            try:
                while True:
                    time.sleep(0.200)
                    if len(self._connected) == 0: break
                ssh_statistic('clear')
                for socks5_port in self.socks5_port:
                    time.sleep(0.200)
                    threading.Thread(target=self.thread_ssh_client, args=(self.unique, socks5_port, )).start()
                self.connected_listener()
            except KeyboardInterrupt:
                pass
            finally:
                self.unique += 1

    def thread_ssh_client(self, unique, socks5_port):
        while self.unique == unique:
            ssh_request = self.ssh_request(socks5_port)
            ssh_request.start()
            self.ssh_client(socks5_port)
            ssh_request.stop()
            self.disconnected(socks5_port)

    def ssh_client(self, socks5_port):
        subprocess.Popen('rm -rf ~/.ssh/known_hosts', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        random.shuffle(self.accounts)

        account = self.accounts[random.randint(0, len(self.accounts) - 1)]
        host = account['host']
        port = '80' if not self.tunnel_type or self.tunnel_type == '0' or self.tunnel_type == '2' else '443'
        hostname = account['hostname']
        username = account['username']
        password = account['password']

        self.log('[G1]Connecting to {hostname} port {port}{end}'.format(hostname=hostname, port=port, end=' '*8), status='[G1]'+socks5_port)
        response = subprocess.Popen(
            #'sshpass -p "{password}" ssh -CND {socks5_port} {host} -p {port} -l "{username}" -o "ProxyCommand=nc -X CONNECT -x {inject_host}:{inject_port} %h %p"'.format(
            'sshpass -p "{password}" ssh -CND {socks5_port} {host} -p {port} -l "{username}" -o "ProxyCommand=corkscrew {inject_host} {inject_port} %h %p"'.format(
                host=host,
                port=port,
                username=username,
                password=password,
                inject_host=self.inject_host,
                inject_port=self.inject_port,
                socks5_port=socks5_port
            ),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
        ).communicate()[0].decode('utf-8').replace('\r', '').replace('\n', ' ')
        
        if not response:
            response = 'Disconnected'
        elif 'Permission denied' in response:
            response = 'Access Denied'
        elif 'Connection closed' in response:
            response = 'Connection closed'
        elif 'nc: proxy read: Broken pipe' in response:
            response = 'Address not found'
        elif 'no remote_id' in response:
            response = 'Fucking banners'
        elif 'packet_write_wait: Connection to UNKNOWN port' in response:
            response = 'Connection timeout'
        elif 'to the list of known hosts.' in response or 'End of stack trace' in response or 'Connection reset' in response or 'open failed' in response:
            response = 'Disconnected'

        self.log('[R1]{response}'.format(response=response), status='[R1]'+socks5_port)
