#!/bin/bash

# interfaces (replace if needed)
DMZ_IF="eth0"   # Network interface

SERVICE_FILE=/etc/systemd/system/init-dmzserver.service

# ensure the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: Please run the script as root (with sudo)."
    exit 1
fi

# configure IPv4
ip addr add 192.168.1.2/24 dev $DMZ_IF
ip link set dev $DMZ_IF up

# configure default gateway
ip route add default via 192.168.1.254 dev $EXT_IF

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

# create systemd service for running this script at boot time
if [ ! -f "$SERVICE_FILE" ]; then
    echo "[Unit]
Description=DMZ Server Setup
After=network.target

[Service]
ExecStart=/bin/bash $(realpath "$0")
Type=oneshot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE
fi

# enable the service
systemctl enable init-dmzserver
