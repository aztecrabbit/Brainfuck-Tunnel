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

        self.hostname_serverid = []
        self.data_create_ssh = json.loads(open(real_path('/../database/servers.json')).read())['servers']
        self.queue_accounts = Queue()
        self.queue_threads = 20
        self.accounts = []
        self._created = 0
        self.verbose = verbose

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
        return len(self.accounts) - self._created

    def create(self, data, account):
        serverid = account['serverid']
        hostname = account['hostname']
        username = account['username'].replace(data['replace-username'], '')
        password = account['password'].replace(data['replace-password'], '')
        HEAD = 'http://{name}{head}'.format(name=data['name'], head=data['head'].format(serverid=serverid))
        POST = 'http://{name}{post}'.format(name=data['name'], post=data['post'])

        loop = 0
        while True:
            try:
                if loop >= 1: self.log(results)
                if loop == 3: break
                results = '[Y1]{username_hostname:.<48} '.format(username_hostname=username+'[G1]@'+hostname+' ')
                browser = requests.session()
                browser.request('HEAD', HEAD, timeout=10)
                response = browser.request('POST', POST,
                    data={'serverid': serverid, 'username': username, 'password': password},
                    headers={'Referer': POST},
                    cookies=self.get_cookies(browser),
                    timeout=15
                )
                if not response.text:
                    results = results + '[R1]No response'
                    loop = loop + 1
                    continue
                elif 'Username already exist' in response.text:
                    results = results + '[Y1]200'
                elif 'has been successfully created' in response.text:
                    results = results + '[G1]200'
                elif 'Account maximum' in response.text:
                    results = results + '[R1]200'
                else:
                    results = results + '[R1]' + str(response.text)
            except requests.exceptions.Timeout:
                results = results + '[R1]ERR '
                loop = loop + 1
                continue
            except requests.exceptions.ConnectionError:
                results = results + '[R2]ERR '
                loop = loop + 1
                continue
            except Exception as exception:
                results = results + '[R1]Exception: ' + str(exception)
            self.created()
            self.log(results)
            self.log_replace('[Y1]{}'.format(self.total()), log_datetime=False)
            break

    def update_serverid_thread(self, data):
        while True:
            try:
                response = requests.request('GET', 'http://{name}{page}'.format(name=data['name'], page=data['page']), timeout=10)
                response = BeautifulSoup(response.text, 'html.parser')
                for element in response.find_all(attrs={'class': data['pattern-class']}):
                    hostname = re.findall(r'{}'.format(data['pattern-hostname'].format(hostname=r'([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+)')), str(element))
                    serverid = re.findall(r'{}'.format(data['pattern-serverid'].format(serverid=r'([0-9]+)')), str(element))
                    hostname = hostname[0][0] if len(hostname) and len(hostname[0]) else ''
                    serverid = serverid[0] if len(serverid) else ''

                    if not hostname or not serverid:
                        hostname_available = False
                        for account in self.accounts:
                            if not hostname and hostname == account['hostname']:
                                hostname_available = True
                                break
                        if hostname_available or self.verbose:
                            self.log('[R1]{hostname:.<48} [R1]{serverid}{verbose}'.format(hostname=(hostname if hostname else '(empty hostname)') + ' [G1]', serverid=(serverid if serverid else '(empty serverid)') + ' ', verbose='[R1](verbose)' if self.verbose else ''))
                        continue
                    
                    if self.verbose:
                       self.log('[G1]{hostname:.<48} [G1]{serverid}'.format(hostname=(hostname if hostname else '(empty hostname)') + ' [G1]', serverid=(serverid if serverid else '(empty serverid)') + ' '))

                    self.hostname_serverid.append({
                        'hostname': hostname,
                        'serverid': serverid
                    })
            except requests.exceptions.Timeout:
                self.log('[R1]Connection timeout')
                continue
            except requests.exceptions.ConnectionError:
                self.log('[R1]Connection closed')
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
            account = self.queue_accounts.get()
            for data in self.data_create_ssh:
                if data['name'] == account['name']:
                    self.create(data, account)
                    break
            self.queue_accounts.task_done()
            if self.queue_accounts.qsize() == 0: break

    def start(self):
        if len(self.accounts) >= 1:
            message = '[G1]Creating {len_accounts} ssh accounts'.format(len_accounts=len(self.accounts))
            self.log(message + ' ' * 8)

            self.update_serverid()

            for account in self.accounts:
                if account.get('serverid'):
                    self.queue_accounts.put(account)

            for i in range(self.queue_threads):
                threading.Thread(target=self.create_thread).start()

            self.queue_accounts.join()

            self.accounts = []
            self.log('{message} complete'.format(message=message))

