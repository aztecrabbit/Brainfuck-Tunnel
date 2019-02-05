import os
import app
import time


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    app.log('Exporting SSH Accounts', status='INFO')

    accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))
    data  = open(real_path('/app/data/banners.txt')).read()

    for account in accounts:
        name = account['name']
        host = account['host']
        hostname = account['hostname']
        username = account['username']
        password = account['password']
        data += '\n'
        data += 'name     : {}\n'.format(name.upper())
        data += 'host     : {}\n'.format(host)
        data += 'hostname : {}\n'.format(hostname)
        data += 'username : {}\n'.format(username)
        data += 'password : {}\n'.format(password)

    open(real_path('/storage/accounts.txt'), 'w').write(data)

    app.log('Exporting SSH Accounts Complete', status='INFO')
    
    try:
        app.log('\nCtrl-C to Exit', log_datetime=False, status=None)
        time.sleep(60*60*24)
    except KeyboardInterrupt:
        pass
    finally: pass

if __name__ == '__main__':
    main()
