# Brainfuck Tunnel

SSH Tunneling for Dynamic Port Forwarding (Free charge Internet Access)


Requirements
------------

#### Packages

    nc (openbsd-version) (be aware if you are installing wrong nc)
    openssh
    sshpass
    python3
    corkscrew
    python3-pip


#### Using Termux on Android?

    $ pkg install pip python openssh sshpass corkscrew


#### Using Cygwin on Windows?

**1. apt-cyg**

    $ wget rawgit.com/transcode-open/apt-cyg/master/apt-cyg -P /bin/; chmod +x /bin/apt-cyg


**2. required packages**

    $ apt-cyg install nc tar curl make openssh python3 autoconf gcc-core corkscrew python3-pip


**3. sshpass**

    $ curl -LO http://downloads.sourceforge.net/sshpass/sshpass-1.06.tar.gz
    $ md5sum sshpass-1.06.tar.gz
    $ tar xvf sshpass-1.06.tar.gz
    $ cd sshpass-1.06
    $ ./configure
    $ make
    $ make install


#### Python 3

    $ python3 -m pip install --upgrade pip
    $ python3 -m pip install -r requirements.txt


Configurations
--------------

Run `app.py` first to export `config.json` to `config/config.json`

**1. Tunel Type**

    0: Direct     -> SSH
    1: Direct     -> SSH (SSL/TLS)
    2: HTTP Proxy -> SSH


**2. SOCKS5 Port**

    "socks5_port_external": [
      "1081",
      "1082",
      "1083"
    ]

    "socks5_port": [
      "1081",
      "1082",
      "1083"
    ]

If `socks5_port_external` or `socks5_port` like that. You will execute 3 SSH Clients.
Add ports to execute more SSH Clients.


**3. Proxy Command**

Please googling for this topic.

    proxy_host: {inject_host}
    proxy_port: {inject_port}


Usage
-----

| `Name`                               | `Script`
|:------------------------------------ |:--------------------------------------------
| `Inject`                             | `inject.py`
| `SSH Clients`                        | `ssh.py`
| `SNI Scanner`                        | `sni-scanner.py (hostname) (hostname) (etc)`
| `Check Serverid`                     | `check-serverid.py`
| `Create SSH Accounts`                | `create-ssh.py`
| `Export SSH Accounts`                | `export-ssh.py`
| `Inject and SSH Clients`             | `app.py`


Note
----

    Ctrl-C to Change Server
    Ctrl-Pause to Exit


Contacts
--------

Facebook Group : [Internet Freedom]


[Internet Freedom]: https://www.facebook.com/groups/171888786834544/
