import os
import app
import time


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    try:
        app.log('Exporting SSH Accounts')

        accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))
        data = open(real_path('/app/data/banners.txt')).read() + '\n'

        for account in accounts:
            name = account['name']
            host = account['host']
            hostname = account['hostname']
            username = account['username']
            password = account['password']
            data += 'name     : {}\n'.format(name.upper())  + \
                    'host     : {}\n'.format(host)          + \
                    'hostname : {}\n'.format(hostname)      + \
                    'username : {}\n'.format(username)      + \
                    'password : {}{}'.format(password, '\n\n')

        open(real_path('/storage/ssh-accounts.txt'), 'w').write(data.strip() + '\n')

        app.log('Exporting SSH Accounts Complete \n')
    except KeyboardInterrupt: pass

if __name__ == '__main__':
    main()
