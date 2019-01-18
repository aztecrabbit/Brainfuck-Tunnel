# Brainfuck Tunnel

SSH Tunneling for Dynamic Port Forwarding (Free charge Internet Access)

### Packages

```
openssh
sshpass
python3
corkscrew
python3-pip
```
```
openssh sshpass python3 corkscrew python3-pip
```

### Using Termux on Android?

```
pkg install pip python openssh sshpass corkscrew
```

### Using Cygwin on Windows?

#### 1. apt-cyg

```
wget rawgit.com/transcode-open/apt-cyg/master/apt-cyg -P /bin/; chmod +x /bin/apt-cyg
```

#### 2. required packages

```
apt-cyg install tar curl make openssh python3 autoconf gcc-core corkscrew python3-pip
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

### Configurations

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

| `Name`                               | `Script`
|:------------------------------------ |:--------------------------------------------
| `Inject`                             | `inject.py`
| `SSH Clients`                        | `ssh.py`
| `SNI Scanner`                        | `sni-scanner.py (hostname) (hostname) (etc)`
| `Check Serverid`                     | `check-serverid.py`
| `Create SSH Accounts`                | `create-ssh.py`
| `Export SSH Accounts`                | `export-ssh.py`
| `Inject and SSH Clients`             | `app.py`

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
