import os
import app
import time
import json


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    try:
        ssh_create = app.ssh_create()
        ssh_create.accounts = app.generate_accounts(json.loads(open(real_path('/database/accounts.json')).read())['accounts'])
        ssh_create.start()
        app.log('\nCtrl-C to Exit', log_datetime=False, status=None)
        time.sleep(60*60*24)
    except KeyboardInterrupt:
        pass
    finally: print()

if __name__ == '__main__':
    main()
