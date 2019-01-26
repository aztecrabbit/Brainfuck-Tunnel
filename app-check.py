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
    inject_port = int("8010")
    socks5_port = str("2083")

    app.server((inject_host, inject_port), tunnel_type, silent=False).start()

    ssh_clients = app.ssh_clients(tunnel_type, inject_host, inject_port, socks5_port=[socks5_port])
    ssh_clients.accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))

    while True:
        app.ssh_statistic('clear')
        ssh_request = ssh_clients.ssh_request(socks5_port)
        ssh_request.start()
        thread = threading.Thread(target=ssh_clients.ssh_client, args=(socks5_port, ))
        thread.daemon = True
        thread.start()

        try:
            ssh_clients.connected_listener()
        except KeyboardInterrupt:  pass

        ssh_request.stop()
        ssh_clients.disconnected(socks5_port)

        while True:
            if len(ssh_clients._connected) == 0:
                time.sleep(2.500)
                break


if __name__ == '__main__':
    main()

