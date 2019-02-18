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
        inject_host = str(config['inject_host_external'])
        inject_port = int(config['inject_port_external'])
    except KeyError: app.json_error(config_file); return
    
    app.log('Inject set to {} port {}'.format(inject_host, inject_port))

    ssh_clients = app.ssh_clients((inject_host, inject_port), external=True)
    ssh_clients.accounts = app.generate_accounts(app.convert_hostnames(real_path('/database/accounts.json')))

    app.log('Type debug for debugging log')
    app.log('Type exit to exit')

    while True:
        try:
            ssh_clients.debug = False
            exit = False

            command = app.str_input('\n:: ', newline=True)
            if command == 'exit':
                exit = True
                break
            if command == 'debug':
                ssh_clients.debug = True

            try:
                config_file = real_path('/config/config.json')
                config = json.loads(open(config_file).read())
                ssh_clients.socks5_port_list = app.filter_array(config['socks5_port_list_external'])
            except KeyError: app.json_error(config_file); continue

            if len(ssh_clients.socks5_port_list) == 0: ssh_clients.socks5_port_list.append('1080')

            app.ssh_statistic('clear')
            for socks5_port in ssh_clients.socks5_port_list:
                thread = threading.Thread(target=ssh_clients.ssh_client, args=(ssh_clients.unique, socks5_port, ))
                thread.daemon = True
                thread.start()
            time.sleep(60*60*24*30*12)
        except KeyboardInterrupt:
            pass
        finally:
            if not exit:
                ssh_clients.unique += 1
                ssh_clients.all_disconnected_listener()

if __name__ == '__main__':
    main()
