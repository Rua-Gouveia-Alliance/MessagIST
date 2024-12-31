#!/bin/bash

# interfaces (replace if needed)
EXT_IF="eth0"   # DMZ zone interface
INT_IF="eth1"   # Internal interface

SERVICE_FILE=/etc/systemd/system/init-natfirewall2-setup.service

# ensure the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: Please run the script as root (with sudo)."
    exit 1
fi

# configure IPv4
ip addr add 192.168.1.1/24 dev $EXT_IF
ip link set dev $EXT_IF up
ip addr add 192.168.2.254/24 dev $INT_IF
ip link set dev $INT_IF up

# configure default gateway
ip route add default via 192.168.1.254 dev $EXT_IF

# configure DNS
echo "nameserver 8.8.8.8" | tee /etc/resolv.conf
echo "nameserver 8.8.4.4" | tee -a /etc/resolv.conf

# disable IPv6
echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6
echo 1 > /proc/sys/net/ipv6/conf/default/disable_ipv6
echo 1 > /proc/sys/net/ipv6/conf/lo/disable_ipv6

# enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.ip_forward=1

# flush existing iptables rules
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X

# configure default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# allow established and related traffic
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# NAT for subnet 192.168.2.0/24
iptables -A FORWARD -s 192.168.2.0/24 -o $EXT_IF -j ACCEPT
iptables -t nat -A POSTROUTING -s 192.168.2.0/24 -o $EXT_IF -j MASQUERADE

# allow dmz-internalserver traffic to internal server
iptables -A FORWARD -p tcp -s 192.168.1.2 -d 192.168.2.1 --dport 5001 -j ACCEPT
iptables -t nat -A PREROUTING -p tcp --dport 5001 -j DNAT --to-destination 192.168.2.1:5001

# create systemd service for running this script at boot time
if [ ! -f "$SERVICE_FILE" ]; then
    echo "[Unit]
Description=NATFirewall 2 Server Setup
After=network.target

[Service]
ExecStart=/bin/bash $(realpath "$0")
Type=oneshot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE
fi

# enable the service
systemctl enable init-natfirewall2-setup
