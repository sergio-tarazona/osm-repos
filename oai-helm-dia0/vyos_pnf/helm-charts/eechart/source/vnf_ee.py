##
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

import asyncio
import asyncssh
import requests
import logging
import os

from osm_ee.exceptions import VnfException

import osm_ee.util.util_ee as util_ee
import osm_ee.util.util_ansible as util_ansible
import osm_ee.vnf.mylib as mylib

class VnfEE:
    
    PLAYBOOK_PATH = "/app/EE/osm_ee/vnf"
    SSH_SCRIPT = "/app/EE/osm_ee/vnf/run_ssh.sh"

    def __init__(self, config_params):
        self.logger = logging.getLogger('osm_ee.vnf')
        self.config_params = config_params

    # config method saves SSH access parameters (host and username) for future use by other methods.
    # It is mandatory in any case.
    async def config(self, id, params):
        self.logger.debug("Execute action config, params: {}".format(params))
        # Config action is special, params are merged with previous config calls
        self.config_params.update(params)
        required_params = ["ssh-hostname"]
        self._check_required_params(self.config_params, required_params)
        yield "OK", "Configured"
    
    # This method implements the "ansible_playbook" primitive. Uncomment and modify it if a primitive requires
    # executing an Ansible Playbook. It needs "playbook-name" parameter (playbook file, must be in "source" directory).
    async def ansible_playbook(self, id, params):
        self.logger.debug("Execute action ansible_playbook, params: '{}'".format(params))

        try:
            self._check_required_params(params, ["playbook-name"])
            params["ansible_user"] = self.config_params["ssh-username"]
            params["ansible_password"] = self.config_params["ssh-password"]
            inventory = self.config_params["ssh-hostname"] + ","
            playbook = self.PLAYBOOK_PATH + "/" + params["playbook-name"]
            os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
            return_code, stdout, stderr = await util_ansible.execute_playbook(playbook, inventory, params)
            status = "OK" if return_code == 0 else "ERROR"
            yield status, stdout + stderr
        except Exception as e:
            self.logger.debug("Error executing ansible playbook: {}".format(repr(e)))
            yield "ERROR", str(e)

    # Static method that verifies whether a parameter exists in the map
    @staticmethod
    def _check_required_params(params, required_params):
        for required_param in required_params:
            if required_param not in params:
                raise VnfException("Missing required param: {}".format(required_param))

