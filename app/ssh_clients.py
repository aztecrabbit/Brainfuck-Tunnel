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
from .default        import *
from .ssh_create     import *
from .ssh_statistic  import *
from .http_requests  import *


class ssh_clients(object):
    
    _connected = set()

    def __init__(self, inject_host_port, socks5_port_list=[], external=False, http_requests_enable=True, log_connecting=True, dynamic_port_forwarding=True):
        super(ssh_clients, self).__init__()

        self.inject_host, self.inject_port = self.inject_host_port = inject_host_port
        self.dynamic_port_forwarding = dynamic_port_forwarding
        self.http_requests_enable = http_requests_enable
        self.socks5_port_list = socks5_port_list
        self.log_connecting = log_connecting
        self.external = external

        self.http_requests = http_requests(self.socks5_port_list, self.http_requests_enable)
        self.proxy_command = ''
        self.accounts = []
        self.unique = 0
        self.daemon = True
        self.debug = False

    def log(self, value, status='INFO', status_color='[G1]'):
        log(value, status=status, status_color=status_color)

    def log_debug(self, value, status='DBUG', status_color='[G2]'):
        if self.debug: log(value, status=status, status_color=status_color)

    def connected(self, socks5_port):
        self._connected.add(socks5_port)
        if len(self._connected) >= len(self.socks5_port_list):
            self.log('Connected', status='all', status_color='[Y1]')
            self.http_requests = http_requests(self.socks5_port_list, self.http_requests_enable)
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
                self.log('Disconnected', status='all', status_color='[R1]')
                break

    def get_config(self):
        try:
            self.config_file = real_path('/../config/config.json')
            self.config = json.loads(open(self.config_file).read())
            self.tunnel_type = self.config['tunnel_type'] if not self.external else self.config['tunnel_type_external']
            self.proxy_command = self.config['proxy_command']
            if not self.tunnel_type or int(self.tunnel_type) >= 3: raise KeyError
            if str(self.proxy_command.strip()) == '': raise KeyError
        except KeyError: json_error(self.config_file); return False

    def start(self):
        if self.get_config() is not None: return

        if len(self.socks5_port_list) == 0:
            self.socks5_port_list.append('1080')

        while True:
            try:
                ssh_statistic('clear')
                for socks5_port in self.socks5_port_list:
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

            if self.get_config() is not None:
                self.disconnected(socks5_port)
                break

            dynamic_port_forwarding = '-CND {}'.format(socks5_port) if self.dynamic_port_forwarding else ''
            proxy_command = self.proxy_command

            account = random.choice(self.accounts)
            host = account['host']
            port = '443' if self.tunnel_type == '1' else '80'
            hostname = account['hostname']
            username = account['username']
            password = account['password']

            if self.log_connecting == True:
                self.log('[G1]Connecting to {hostname} port {port}{end}'.format(hostname=hostname, port=port, end='  '*4), status=socks5_port)
            
            response = subprocess.Popen(
                (
                    'sshpass -p "{password}" ssh -v {dynamic_port_forwarding} {host} -p {port} -l "{username}" ' + '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ProxyCommand="{proxy_command}"'.format(
                        proxy_command=proxy_command
                    )
                ).format(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    inject_host=self.inject_host,
                    inject_port=self.inject_port,
                    dynamic_port_forwarding=dynamic_port_forwarding
                ),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

            for line in response.stdout:
                line = line.decode().lstrip(r'(debug1|Warning):').strip() + '\r'

                self.log_debug(line)

                if 'pledge: proc' in line:
                    self.connected(socks5_port)

                elif 'Permission denied' in line:
                    self.log('Access Denied', status=socks5_port, status_color='[R1]')

                elif 'Connection closed' in line:
                    self.log_debug('Connection closed', status=socks5_port, status_color='[R1]')

                elif 'Could not request local forwarding' in line:
                    self.log('Port used by another programs', status=socks5_port, status_color='[R1]')
                    unique -= 1
                    break

            self.disconnected(socks5_port)
