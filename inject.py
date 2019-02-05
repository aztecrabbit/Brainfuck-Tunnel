import os
import app
import json


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    config = json.loads(open(real_path('/config/config.json')).read())
    tunnel_type = str(config['tunnel_type_external'])
    inject_host = str(config['inject_host_external'])
    inject_port = int(config['inject_port_external'])

    app.server((inject_host, inject_port), tunnel_type).run()

if __name__ == '__main__':
    main()
