import os
import app
import time
import json
import threading


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    config = json.loads(open(real_path('/config/config.json')).read())
    tunnel_type = str(config['tunnel_type'])
    inject_host = str("127.0.0.1")
    inject_port = int("9080")
    socks5_port = str("2080")

    app.server((inject_host, inject_port), tunnel_type, silent=False).start()

    ssh_clients = app.ssh_clients(tunnel_type, inject_host, inject_port, socks5_ports=[socks5_port])
    ssh_clients.accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))

    while True:
        try:
            app.ssh_statistic('clear')
            threading.Thread(target=ssh_clients.ssh_client, args=(ssh_clients.unique, socks5_port, )).start()
            ssh_clients.unique += 1
            time.sleep(60*60*24*12)
        except KeyboardInterrupt:
            pass
        finally:
            ssh_clients.all_disconnected_listener()
            with app.lock:
                again = input('\n:: '); print()
                if again == 'n': break 


if __name__ == '__main__':
    main()

