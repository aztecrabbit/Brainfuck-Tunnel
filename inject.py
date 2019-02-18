import os
import app
import json


def real_path(file_name):
    return os.path.dirname(os.path.abspath(__file__)) + file_name

def main():
    try:
        config_file = real_path('/config/config.json')
        config = json.loads(open(config_file).read())
        inject_host = str(config['inject_host_external'])
        inject_port = int(config['inject_port_external'])
    except KeyError: app.json_error(config_file); return

    app.server((inject_host, inject_port), external=True).run()

if __name__ == '__main__':
    main()
