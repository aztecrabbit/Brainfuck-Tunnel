import os
import app
import json


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    config = json.loads(open(real_path('/config/config.json')).read())
    tunnel_type = str(config['tunnel_type'])
    inject_host = str(config['inject_host'])
    inject_port = int(config['inject_port'])
    socks5_port = config['socks5_port']
    quiet = True if len(socks5_port) > 1 else False

    app.server((inject_host, inject_port), tunnel_type, quiet).start()

    ssh_clients = app.ssh_clients(tunnel_type, inject_host, inject_port, socks5_port)
    ssh_clients.accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))
    ssh_clients.start()

if __name__ == '__main__':
    main()

