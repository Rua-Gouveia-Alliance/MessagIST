#!/bin/bash

# TODO: configure ssl for postgres

# change if needed
DB_IF="eth0"   # Network interface
DB_USER="messagist"
DB_PASSWORD="messagist"

SERVICE_FILE=/etc/systemd/system/init-postgresdbserver.service

# ensure the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: Please run the script as root (with sudo)."
    exit 1
fi

# configure IPv4
ip addr add 192.168.2.2/24 dev $DB_IF
ip link set dev $DB_IF up

# configure default gateway
ip route add default via 192.168.2.254 dev $DB_IF

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

# allow traffic only from the MessagIST server
iptables -A INPUT -p tcp -s 192.168.2.1 --dport 5432 -j ACCEPT

# check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    apt-get update
    apt-get install -y postgresql postgresql-client
fi
systemctl enable --now postgresql

# create default user if not exists
sudo -u postgres psql <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_roles WHERE rolname = '$DB_USER'
   ) THEN
      CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD' CREATEDB;
   END IF;
END
\$do\$;

REVOKE ALL PRIVILEGES ON DATABASE postgres FROM $DB_USER;
EOF

# create systemd service for running this script at boot time
if [ ! -f "$SERVICE_FILE" ]; then
    echo "[Unit]
Description=MessagIST Server Setup
After=network.target

[Service]
ExecStart=/bin/bash $(realpath "$0")
Type=oneshot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE
fi

# enable the service
systemctl enable --now init-postgresdbserver
