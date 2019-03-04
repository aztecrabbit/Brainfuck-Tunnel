import os
import app
import json
import queue
import random
import threading
import subprocess


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def log(value, status_color='[G1]'):
    app.log(value, status=None, status_color=status_color)

class thread(threading.Thread):
    def __init__(self, queue_accounts, proxy_command):
        super(thread, self).__init__()

        self.queue_accounts = queue_accounts
        self.proxy_command = proxy_command
        self.daemon = True

    def log(self, value, status_color='[G1]'):
        log(value, status_color=status_color)

    def run(self):
        while True:
            account = self.queue_accounts.get()
            results_1 = self.connect(account, '80')
            results_2 = self.connect(account, '443')
            self.log('{hostname:.<56} {results_1} {results_2}'.format(
                hostname='[Y1]{} '.format(account['hostname'].replace('.', '[G1].')),
                results_1=results_1,
                results_2=results_2
            ))
            self.queue_accounts.task_done()
            
            if self.queue_accounts.qsize() == 0: break

    def connect(self, account, port):
        hostname = account['hostname']
        username = account['username']
        password = account['password']
        proxy_command = ''
        if port == '443':
            proxy_command = '-o ProxyCommand="{}"'.format(self.proxy_command.format(
                inject_host='127.0.0.1',
                inject_port='3313'
            ))

        response = subprocess.Popen(
            ('sshpass -p "{password}" ssh -v {hostname} -p {port} -l "{username}" ' + '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {proxy_command}').format(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                proxy_command=proxy_command
            ),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        for line in response.stdout:
            line = line.decode().lstrip(r'(debug1|Warning):').strip() + '\r'

            # self.log(line, status_color='[G2]')

            if 'pledge: ' in line:
                return '[G1]200'

            elif 'Permission denied' in line:
                return '[R1]200'

            elif 'Connection timed out' in line:
                return '[Y2]ERR'

            elif 'Connection closed' in line or 'Connection refused' in line or 'Connection reset' in line or 'connection abort' in line:
                return '[R2]ERR'

        return '   '

def main():
    try:
        config_file = real_path('/config/config.json')
        config = json.loads(open(config_file).read())
        proxy_command = config['proxy_command']
        if str(proxy_command.strip()) == '': raise KeyError
    except KeyError: app.json_error(config_file); return False

    data_accounts = json.loads(open(real_path('/database/accounts.json')).read())['accounts']
    data_deleted_accounts = {}

    for name, value in data_accounts.items():
        data_deleted_accounts[name] = []
        for i in range(len(value)):
            account = data_accounts[name][i]
            if app.check_hostname(account['hostname']) == False:
                data_accounts[name][i]['hostname'].replace('#', '')
                data_deleted_accounts[name].append(data_accounts[name][i])
                data_accounts[name][i] = ''

    json_authentications = json.loads(open(real_path('/database/authentications.json')).read())['authentications']
    data_authentications = []

    for i in range(len(json_authentications)):
        data_authentications.append([{'username': json_authentications[i]['username'], 'password': json_authentications[i]['username']}])

    accounts = app.generate_accounts(data_accounts, data_authentications=random.choice(data_authentications))
    queue_accounts = queue.Queue()
    threads = 10

    app.server((str('127.0.0.1'), int('3313')), force_tunnel_type='1', quiet='full').start()

    for account in accounts:
        queue_accounts.put(account)

    for i in range(threads):
        thread(queue_accounts, proxy_command).start()

    queue_accounts.join()

    print()

    deleted_accounts = app.generate_accounts(data_deleted_accounts, data_authentications=[{'username': 'rabbit', 'password': 'rabbit'}])
    queue_deleted_accounts = queue.Queue()

    for deleted_account in deleted_accounts:
        queue_deleted_accounts.put(deleted_account)

    for i in range(threads):
        thread(queue_deleted_accounts, proxy_command).start()

    queue_deleted_accounts.join()


if __name__ == '__main__':
    main()