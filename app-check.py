import os
import app
import time
import json
import threading


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    try:
        config_file = real_path('/config/config.json')
        config = json.loads(open(config_file).read())
        inject_host = str('127.0.0.1')
        inject_port = int('9080')
        socks5_port = str('2080')
        socks5_port_list = [socks5_port]
    except KeyError: app.json_error(config_file); return

    app.server((inject_host, inject_port)).start()

    ssh_clients = app.ssh_clients(inject_host, inject_port, socks5_port_list, http_requests_enable=False, log_connecting=False)
    ssh_clients.accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))

    while True:
        try:
            app.ssh_statistic('clear')
            threading.Thread(target=ssh_clients.ssh_client, args=(ssh_clients.unique, socks5_port, )).start()
            ssh_clients._connected.add(socks5_port)
            ssh_clients.unique += 1
            ssh_clients.all_disconnected_listener()
        except KeyboardInterrupt:
            pass
        finally:
            try:
                if ssh_clients.all_disconnected() == False: ssh_clients.all_disconnected_listener()
                if app.str_input('\n:: ', newline=True) == 'exit': break
            except KeyboardInterrupt: break


if __name__ == '__main__':
    main()
