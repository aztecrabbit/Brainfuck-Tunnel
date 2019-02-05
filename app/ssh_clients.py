import os
import sys
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
from .http_requests  import *


class ssh_clients(object):
    
    _connected = set()

    def __init__(self, tunnel_type, inject_host, inject_port, socks5_ports, http_requests_enable=True, log_connecting=True):
        super(ssh_clients, self).__init__()

        self.http_requests_enable = http_requests_enable
        self.log_connecting = log_connecting
        self.http_requests = http_requests(socks5_ports, self.http_requests_enable)
        self.socks5_ports = socks5_ports
        self.tunnel_type = tunnel_type
        self.inject_host = inject_host
        self.inject_port = inject_port
        self.accounts = []
        self.unique = 0
        self.daemon = True

        try:
            self.proxy_command = json.loads(open(real_path('/../config/config.json')).read())['proxy_command']
        except:
            self.proxy_command = ""

    def log(self, value, status='', status_color='[G1]'):
        log(value, status=status, status_color=status_color)

    def connected(self, socks5_port):
        self._connected.add(socks5_port)
        if len(self._connected) == len(self.socks5_ports):
            self.log('[Y1]Connected', status='all', status_color='[Y1]')
            self.http_requests = http_requests(self.socks5_ports, self.http_requests_enable)
            self.http_requests.start()

    def disconnected(self, socks5_port):
        with lock: self.http_requests.stop()
        if socks5_port in self._connected:
            self._connected.remove(socks5_port)
        if len(self._connected) == 0:
            ssh_statistic('clear')

    def all_disconnected(self):
        return True if len(self._connected) == 0 else False

    def all_disconnected_listener(self):
        while True:
            if self.all_disconnected():
                self.log('[R1]Disconnected', status='all', status_color='[R1]')
                break

    def start(self):
        if not self.proxy_command:
            value  = '[R1]Exception:' + ' ' * 24 + '\n\n'
            value += '   File {file} Error!\n'.format(file=real_path('/../config/config.json')).replace('/app/../', '/')
            value += '   Please delete that file or fixing by your-self.\n'
            value += '   Good-luck!\n'
            self.log(value, status='[R1]INFO')
            return

        while True:
            try:
                ssh_statistic('clear')
                for socks5_port in self.socks5_ports:
                    time.sleep(0.025)
                    thread = threading.Thread(target=self.ssh_client, args=(self.unique, socks5_port, ))
                    thread.daemon = True
                    thread.start()
                time.sleep(60*60*24*30*12)
            except KeyboardInterrupt:
                pass
            finally:
                self.unique += 1
                self.all_disconnected_listener()

    def ssh_client(self, unique, socks5_port):
        while self.unique == unique:
            subprocess.Popen('rm -rf ~/.ssh/known_hosts', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

            random.shuffle(self.accounts)

            account = self.accounts[random.randint(0, len(self.accounts) - 1)]
            host = account['host']
            port = '80' if not self.tunnel_type or self.tunnel_type == '0' or self.tunnel_type == '2' else '443'
            hostname = account['hostname']
            username = account['username']
            password = account['password']
            proxy_command = self.proxy_command

            if self.log_connecting == True:
                self.log('[G1]Connecting to {hostname} port {port}{end}'.format(hostname=hostname, port=port, end=' '*8), status=socks5_port)
            
            response = subprocess.Popen(
                ('sshpass -p "{password}" ssh -v -CND {socks5_port} {host} -p {port} -l "{username}" ' + '-o StrictHostKeyChecking=no -o ProxyCommand="{proxy_command}"'.format(
                        proxy_command=proxy_command
                    )
                ).format(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    inject_host=self.inject_host,
                    inject_port=self.inject_port,
                    socks5_port=socks5_port
                ),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

            for line in response.stdout:
                line = line.decode().lstrip('debug1: ').rstrip()

                if 'Authentication succeeded' in line:
                    self.connected(socks5_port)

                elif 'Permission denied' in line:
                    self.log('[R1]Access Denied', status=socks5_port, status_color='[R1]')

                elif 'Connection closed' in line:
                    self.log('[R1]Connection closed', status=socks5_port, status_color='[R1]')

                elif 'Address already in use' in line:
                    self.log('[R1]Port used by another programs', status=socks5_port, status_color='[R1]')

            self.disconnected(socks5_port)
