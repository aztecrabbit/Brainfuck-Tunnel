from os              import system, name
from sys             import version, exit
from .app            import *
from .default        import *
from .server         import *
from .server_tunnel  import *
from .ssh_clients    import *
from .ssh_create     import *


def main():
    print('\n\n\n\n')
    system('cls' if name == 'nt' else 'clear')
    print(colors('[G1]{banners}'.format(banners=open(real_path('/data/banners.txt')).read())))
    if version[0] == '2':
        log('For Python 3 Only!\n', status='[R1]INFO')
        exit()

main()