#!/usr/bin/env bash

set -eux
sudo -s <<EOF

apt-get -y update
apt-get -y install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get -y update
apt-get -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
groupadd docker
usermod -aG docker ubuntu
newgrp docker

curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

sysctl net.ipv4.conf.all.forwarding=1
iptables -P FORWARD ACCEPT
ip route add 192.168.70.128/26 via 192.168.1.1 dev ens4
ip route add 192.168.18.0/24 via 192.168.1.1 dev ens4

EOF
