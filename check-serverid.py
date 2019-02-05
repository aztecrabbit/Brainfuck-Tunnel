import os
import app
import json
import threading


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    app.log('Checking serverid', status=None)
    data_create_ssh_temp = [
        {
            "link": "",
            "head": "",
            "post": "",
            "page": "",
            "pattern-class": "",
            "pattern-serverid": "",
            "pattern-hostname": "",
            "replace-username": "",
            "replace-password": ""
        }
    ]

    ssh_create = app.ssh_create(verbose=True)
    ssh_create.accounts = app.generate_accounts(json.loads(open(real_path('/database/accounts.json')).read())['accounts'])
    # ssh_create.data_create_ssh = data_create_ssh_temp
    
    threads = []

    for data in ssh_create.data_create_ssh:
        threads.append(threading.Thread(target=ssh_create.update_serverid_thread, args=(data, )))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    app.log('Checking serverid complete', status=None)

if __name__ == '__main__':
    main()
