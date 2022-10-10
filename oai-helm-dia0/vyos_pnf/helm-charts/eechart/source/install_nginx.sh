#!/usr/bin/env bash

set -eux
sudo -s <<EOF
apt update
apt install -y nginx
systemctl status nginx
EOF

