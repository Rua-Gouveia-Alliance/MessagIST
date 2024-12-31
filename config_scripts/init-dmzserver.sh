#!/bin/bash

# change if needed
DMZ_IF="eth0"   # Network interface
NON_ROOT_USER="serveradmin" # to avoid running the server as root
MESSAGIST_PATH="/home/A61" # location of cloned repo

SERVICE_FILE=/etc/systemd/system/init-dmzserver.service

ENV_NAME="messagist"
ENV_FILE="$MESSAGIST_PATH/messagist/environment.yml"
PROTO_SCRIPT="$MESSAGIST_PATH/messagist/proto.sh"
DMZ_SERVER="$MESSAGIST_PATH/messagist/dmz/DmzServer.py"

# ensure the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: Please run the script as root (with sudo)."
    exit 1
fi

# ensure non_root_user exists
if ! id "$NON_ROOT_USER" &>/dev/null; then
    echo "Error: User $NON_ROOT_USER does not exist."
    exit 1
fi

# configure IPv4
ip addr add 192.168.1.2/24 dev $DMZ_IF
ip link set dev $DMZ_IF up

# configure default gateway
ip route add default via 192.168.1.254 dev $DMZ_IF

# configure DNS
echo "nameserver 8.8.8.8" | tee /etc/resolv.conf
echo "nameserver 8.8.4.4" | tee -a /etc/resolv.conf

# disable IPv6
echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6
echo 1 > /proc/sys/net/ipv6/conf/default/disable_ipv6
echo 1 > /proc/sys/net/ipv6/conf/lo/disable_ipv6

# flush existing iptables rules
iptables -F
iptables -X

# configure default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# allow established and related traffic
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# allow traffic to the DMZ server
iptables -A INPUT -p tcp --dport 5001 -j ACCEPT

# switch to the non-root user for Conda installation and environment setup
sudo -u "$NON_ROOT_USER" bash <<EOF
export PATH="/home/$NON_ROOT_USER/miniconda/bin:\$PATH"
if ! command -v conda &>/dev/null; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p /home/$NON_ROOT_USER/miniconda
    rm /tmp/miniconda.sh
fi
eval "\$(/home/$NON_ROOT_USER/miniconda/bin/conda shell.bash hook)"

if ! conda env list | grep -q "$ENV_NAME"; then
    conda env create -f "$ENV_FILE"
fi

cd "$MESSAGIST_PATH/messagist"
conda run -n "$ENV_NAME" bash "$PROTO_SCRIPT"
EOF

# kill DMZ server processes if already running
if pgrep -f "$DMZ_SERVER" > /dev/null; then
    pkill -f "$DMZ_SERVER"
fi
cd "$MESSAGIST_PATH/messagist/dmz"
sudo -u "$NON_ROOT_USER" conda run -n "$ENV_NAME" python "$DMZ_SERVER" &

# create systemd service for running this script at boot time
if [ ! -f "$SERVICE_FILE" ]; then
    echo "[Unit]
Description=DMZ Server Setup
After=network.target

[Service]
ExecStart=/bin/bash $(realpath "$0")
Restart=always
Type=simple
User=root

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE
fi

# enable the service
systemctl enable --now init-dmzserver
