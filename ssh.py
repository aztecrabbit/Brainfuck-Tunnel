import os
import app
import json
import random


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    config = json.loads(open(real_path('/config/config.json')).read())
    tunnel_type = str(config['tunnel_type_external'])
    inject_host = str(config['inject_host_external'])
    inject_port = int(config['inject_port_external'])
    socks5_port = config['socks5_port_external']

    app.log('Inject set to {inject_host} port {inject_port}'.format(inject_host=inject_host, inject_port=inject_port), status='INFO')

    ssh_clients = app.ssh_clients(tunnel_type, inject_host, inject_port, socks5_port)
    ssh_clients.accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))
    ssh_clients.start()

if __name__ == '__main__':
    main()