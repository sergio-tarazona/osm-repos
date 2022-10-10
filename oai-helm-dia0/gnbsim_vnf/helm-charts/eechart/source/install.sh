#!/bin/bash
##
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##

echo "Updating operating system"
apt-get update

# Install ansible libraries
echo "Installing ansible"
apt-get install -y software-properties-common
apt-add-repository --yes --update ppa:ansible/ansible
apt install -y ansible

# Install library to execute command remotely by ssh
echo "Installing asynssh"
python3 -m pip install asyncssh

# Install ping system command
apt install -y iputils-ping

# Install HTTP python library
python3 -m pip install requests

# Install MySQL library
python3 -m pip install mysql-connector-python
