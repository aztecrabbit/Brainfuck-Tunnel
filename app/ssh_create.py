import os
import re
import time
import json
import requests
import threading
from .app  import *
from bs4   import BeautifulSoup

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


class ssh_create(object):
    def __init__(self, verbose=False):
        super(ssh_create, self).__init__()

        self.hostname_empty_serverid = set()
        self.hostname_serverid = []
        self.data_create_ssh = json.loads(open(real_path('/../database/servers.json')).read())['servers']
        self.queue_accounts = Queue()
        self.queue_threads = 20
        self.accounts = []
        self.verbose = verbose

        self._created = 0
        self._total = 0

    def log(self, value, status=None):
        log(value, status=status)

    def log_replace(self, value, log_datetime=False):
        log_replace(value, log_datetime=log_datetime)

    def log_exception(self, value, status=None):
        log_exception(value, status=status)

    def get_cookies(self, browser):
        return requests.utils.dict_from_cookiejar(browser.cookies)

    def created(self):
        self._created += 1

    def total(self):
        return self._total - self._created

    def create(self, data, account):
        serverid = account['serverid']
        hostname = account['hostname']
        username = account['username'].replace(data['replace-username'], '')
        password = account['password'].replace(data['replace-password'], '')
        HEAD = 'http://{name}{head}'.format(name=data['name'], head=data['head'].format(serverid=serverid))
        POST = 'http://{name}{post}'.format(name=data['name'], post=data['post'])
        i = 0
        x = 2

        while True:
            try:
                time.sleep(0.200)
                loop, i = 0, i + 1
                results = '{username_hostname:.<48} '.format(username_hostname='[Y1]'+username+'[G1]@'+hostname+' ')
                browser = requests.session()
                response = browser.request('HEAD', HEAD, timeout=10)
                time.sleep(0.200)
                response = browser.request('POST', POST,
                    data={'serverid': serverid, 'username': username, 'password': password},
                    headers={'Referer': POST},
                    cookies=self.get_cookies(browser),
                    timeout=15
                )
                if not response.text:
                    results = results + '[C1]200'
                elif 'Username already exist' in response.text:
                    results = results + '[Y1]200'
                elif 'has been successfully created' in response.text:
                    results = results + '[G1]200'
                elif 'Account maximum' in response.text:
                    results = results + '[R1]200'
                else:
                    results = results + '[R1]' + str(response.text)
            except requests.exceptions.Timeout:
                results = results + '[R1]ERR'
                if i < x: loop = 1
            except requests.exceptions.ConnectionError:
                results = results + '[R2]ERR'
                if i < x: loop = 1
            except Exception as exception:
                results = results + '[R1]Exception: ' + str(exception)
            finally:
                self.log(results[:-7] + '[R2]END' if i == x else results)
            if loop:
                self.log_replace('[Y1]{}'.format(self.total()), log_datetime=False)
                continue
            self.created()
            self.log_replace('[Y1]{}'.format(self.total()), log_datetime=False)
            break

    def update_serverid_thread(self, data):
        while True:
            try:
                response = requests.request('GET', 'http://{name}{page}'.format(name=data['name'], page=data['page']), timeout=10)
                response = BeautifulSoup(response.text, 'html.parser')
                self.log('[G1]{name:.<44} [G1]200'.format(name=data['name']+' [G1]'))
                for element in response.find_all(attrs={'class': data['pattern-class']}):
                    hostname = re.findall(r'{}'.format(data['pattern-hostname'].format(hostname=r'([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+)')), str(element))
                    serverid = re.findall(r'{}'.format(data['pattern-serverid'].format(serverid=r'([0-9]+)')), str(element))
                    hostname = hostname[0][0] if len(hostname) and len(hostname[0]) else ''
                    serverid = serverid[0] if len(serverid) else ''

                    if not hostname or not serverid:
                        hostname_available = False
                        for account in self.accounts:
                            if hostname and hostname == account['hostname']:
                                hostname_available = True
                                break
                        if hostname_available or self.verbose:
                            self.log('[R1]{hostname:.<44} [R1]{serverid} {verbose}'.format(
                                    hostname=(hostname if hostname else '(empty hostname)') + ' [G1]',
                                    serverid=(serverid if serverid else '(empty serverid)'),
                                    verbose=('(verbose)' if self.verbose else '')
                                )
                            )
                        continue
                    
                    if self.verbose:
                        self.log('[G1]{hostname:.<40} [Y1]{serverid}'.format(
                                hostname=hostname + ' ',
                                serverid=serverid
                            )
                        )

                    self.hostname_serverid.append({
                        'hostname': hostname,
                        'serverid': serverid
                    })
            except requests.exceptions.Timeout:
                self.log('[R1]{name:.<44} [R1]ERR'.format(name=data['name']+' [G1]'))
                continue
            except requests.exceptions.ConnectionError:
                self.log('[R1]{name:.<44} [R2]END'.format(name=data['name']+' [G1]'))
            except Exception as exception:
                self.log_exception(exception)
            break

    def update_serverid(self):
        self.log('Updating serverid')

        threads = []

        for data in self.data_create_ssh:
            name_available = False
            for account in self.accounts:
                if account['name'] == data['name']:
                    name_available = True
                    break
            if name_available: threads.append(threading.Thread(target=self.update_serverid_thread, args=(data, )))

        for thread in threads:
            time.sleep(0.200)
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

        for i in range(len(self.accounts)):
            for data in self.hostname_serverid:
                hostname = data['hostname']
                serverid = data['serverid']
                if hostname == self.accounts[i]['hostname']:
                    self.accounts[i]['serverid'] = serverid

        self.hostname_serverid = []
        self.log('Updating serverid complete')

    def create_thread(self):
        while True:
            time.sleep(0.200)
            account = self.queue_accounts.get()
            for data in self.data_create_ssh:
                if data['name'] == account['name']:
                    self.create(data, account)
                    break
            if self.queue_accounts.task_done() is None and self.queue_accounts.qsize() == 0:
                break

    def start(self):
        if len(self.accounts) >= 1:
            self.update_serverid()

            for account in self.accounts:
                if account.get('serverid'):
                    self.queue_accounts.put(account)
                    continue
                self.hostname_empty_serverid.add(account['hostname'])

            self._total = self.queue_accounts.qsize()

            for hostname in self.hostname_empty_serverid:
                self.log('[R1]{hostname:.<44} [R1](empty serverid)'.format(hostname=hostname+' [G1]'))

            value = '[G1]Creating {} ssh accounts'.format(self._total)
            self.log(value + ' ' * 8)
            self.log_replace('[Y1]{}'.format(self.total()), log_datetime=False)

            for i in range(self.queue_threads):
                thread = threading.Thread(target=self.create_thread)
                thread.daemon = True
                thread.start()

            self.queue_accounts.join()
            self.accounts = []

            self.log(value + ' complete')

