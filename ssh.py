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
        tunnel_type = str(config['tunnel_type_external'])
        inject_host = str(config['inject_host_external'])
        inject_port = int(config['inject_port_external'])
        socks5_port_list = app.filter_array(config['socks5_port_list_external'])
    except KeyError: app.json_error(config_file); return

    if len(socks5_port_list) == 0:
        socks5_port_list.append('1080')

    app.log('Inject set to {inject_host} port {inject_port}'.format(inject_host=inject_host, inject_port=inject_port), status='INFO')

    ssh_clients = app.ssh_clients(tunnel_type, inject_host, inject_port, socks5_port_list)
    ssh_clients.accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))

    while True:
        try:
            app.ssh_statistic('clear')
            for socks5_port in ssh_clients.socks5_port_list:
                time.sleep(0.025)
                thread = threading.Thread(target=ssh_clients.ssh_client, args=(ssh_clients.unique, socks5_port, ))
                thread.daemon = True
                thread.start()
            time.sleep(60*60*24*30*12)
        except KeyboardInterrupt:
            pass
        finally:
            try:
                ssh_clients.unique += 1
                ssh_clients.all_disconnected_listener()
                if app.str_input('\n:: ', newline=True) == 'exit': return
            except KeyboardInterrupt: return

if __name__ == '__main__':
    main()
