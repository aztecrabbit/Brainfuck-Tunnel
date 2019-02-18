import os
import app
import json


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    try:
        config_file = real_path('/config/config.json')
        config = json.loads(open(config_file).read())
        tunnel_type = str(config['tunnel_type'])
        inject_host = str(config['inject_host'])
        inject_port = int(config['inject_port'])
        socks5_port_list = app.filter_array(config['socks5_port_list'])
    except KeyError: app.json_error(config_file); return

    if len(socks5_port_list) == 0: socks5_port_list.append('1080')

    log_connecting = True if len(socks5_port_list) > 1 else False
    quiet = True if len(socks5_port_list) > 1 else False

    app.server((inject_host, inject_port), quiet=quiet).start()

    ssh_clients = app.ssh_clients((inject_host, inject_port), socks5_port_list, log_connecting=log_connecting)
    ssh_clients.accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))
    ssh_clients.start()

if __name__ == '__main__':
    main()
