# Brainfuck Tunnel
SSH Tunneling for Dynamic Port Forwarding (Free charge Internet Access)

### Packages

```
nc
openssh
sshpass
python3
python3-pip
```
```
nc openssh sshpass python3 python3-pip
```

### Using Cygwin? Here we go

#### 1. apt-cyg

```
wget rawgit.com/transcode-open/apt-cyg/master/apt-cyg -P /bin/; chmod +x /bin/apt-cyg
```

#### 2. required packages

```
apt-cyg install nc tar curl make openssh python3 autoconf gcc-core python3-pip
```

#### 3. sshpass

```
curl -LO http://downloads.sourceforge.net/sshpass/sshpass-1.06.tar.gz
md5sum sshpass-1.06.tar.gz
tar xvf sshpass-1.06.tar.gz
cd sshpass-1.06
./configure
make
make install
```
```
curl -LO http://downloads.sourceforge.net/sshpass/sshpass-1.06.tar.gz; md5sum sshpass-1.06.tar.gz; tar xvf sshpass-1.06.tar.gz; cd sshpass-1.06; ./configure; make; make install
```

### SSH Configurations

Edit file `~/.ssh/config` like this:

```
Host *
    StrictHostKeyChecking no
```

If file or folder not found. Copy this command and paste to terminal:

```
mkdir ~/.ssh; echo '' > ~/.ssh/config
cat << 'EOF' > ~/.ssh/config
Host *
    StrictHostKeyChecking no
EOF
cat ~/.ssh/config

```

End command must be Enter. Make sure response from cat command like this:

```
Host *
    StrictHostKeyChecking no
```

### IMPORTANT

```
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### Config

Run `app.py` first to export `config.json` to `config/config.json`

#### 1. Tunel Type

```
0: Direct     -> SSH
1: Direct     -> SSH (SSL/TLS)
2: HTTP Proxy -> SSH
```

#### 2. SOCKS5 Port

```json
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
```

If socks5_port_external or socks5_port like that. You will execute 3 SSH Clients.
SOCKSv5 Dynamic Port Forwarding set to 1081, 1082, and 1083.
Add port to execute more SSH Clients.

### Usage

| `Name`                               | `Command`
|:------------------------------------ |:---------------------------------------------
| `Inject`                             | `python3 inject.py`
| `SSH Clients`                        | `python3 ssh.py`
| `SNI Scanner`                        | `python3 sni-scanner.py (hostname) (hostname)`
| `Check Serverid`                     | `python3 check-serverid.py`
| `Create SSH Accounts`                | `python3 create-ssh.py`
| `Export SSH Accounts`                | `python3 export-ssh.py`
| `Inject and SSH Clients`             | `python3 app.py`

#### Note

```
Ctrl-C to Change Server
Ctrl-Pause to Exit
```

#### Contacts

Facebook Group : [Internet Freedom] <br />
Facebook Account : [Aztec Rabbit]

[Internet Freedom]: https://www.facebook.com/groups/171888786834544/
[Aztec Rabbit]: https://www.facebook.com/aztec.rabbit
