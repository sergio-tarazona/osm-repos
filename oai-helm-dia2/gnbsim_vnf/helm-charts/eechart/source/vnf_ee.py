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
    
    # This method implements the "run_script" primitive. Uncomment and modify it if a primitive requires executing a user
    # script in the VDU. It needs "file" parameter (script's file to run, must be in "source" directory)
    # and optionally "parameters" (command-line arguments for script).
    async def run_script(self, id, params):
        self.logger.debug("Execute action run_script, params: '{}'".format(params))
        self._check_required_params(params, ["file"])

        command = "bash " + self.SSH_SCRIPT + " " + self.config_params["ssh-hostname"] + " " + self.config_params["ssh-username"] + " " + params["file"]
        if "parameters" in params:
            command += " \"" + params.get("parameters", "") + "\""
        self.logger.debug("Command: '{}'".format(command))
        return_code, stdout, stderr = await util_ee.local_async_exec(command)
        if return_code != 0:
            yield "ERROR", "return code {}: {}".format(return_code, stderr.decode())
        else:
            yield "OK", stdout.decode()

    # This method implements the "copy_files" primitive. Uncomment and modify it if a primitive requires
    # to copy files to a VNF. It needs file name parameter (file must be in "source" directory).

    async def copy_files(self, id, params):
        self.logger.debug("Execute action copy_files, params: '{}'".format(params))
        self._check_required_params(params, ["file"])

        command= "scp" + " -o StrictHostKeyChecking=no /app/EE/osm_ee/vnf/" + params["file"] + " " + self.config_params["ssh-username"] + "@" + self.config_params["ssh-hostname"] + ":" + params["file"]  
        self.logger.debug("Command: '{}'".format(command))
        return_code, stdout, stderr = await util_ee.local_async_exec(command)
        if return_code != 0:
            yield "ERROR", "return code {}: {}".format(return_code, stderr.decode())
        else:
            yield "OK", stdout.decode()

    # This method implements the "gnbsim_up" primitive. Uncomment and modify it if you need a primitive that
    # starts up the gnbsim to test 5G OAI Core. It only needs "file" parameter, in this case use gnbsim.
    async def gnbsim_up(self, id, params):
        self.logger.debug("Execute action gnbsim_up, params: '{}'".format(params))

        self._check_required_params(params, ["file"])
        command = "docker-compose -f docker-compose-gnbsim.yaml up -d" + " " + params["file"]
        return_code, description = await mylib.ssh_exec(self.config_params["ssh-hostname"], self.config_params["ssh-username"], command)
        if return_code != 0:
            yield "ERROR", description
        else:
            yield "OK", description
    
    # This method implements the "gnbsim_down" primitive. Uncomment and modify it if you need a primitive that
    # stops the gnbsim for testing 5G OAI Core. It only needs "file" parameter, in this case use gnbsim.
    async def gnbsim_down(self, id, params):
        self.logger.debug("Execute action gnbsim_down, params: '{}'".format(params))

        self._check_required_params(params, ["file"])
        command = "docker-compose -f docker-compose-gnbsim.yaml down"
        return_code, description = await mylib.ssh_exec(self.config_params["ssh-hostname"], self.config_params["ssh-username"], command)
        if return_code != 0:
            yield "ERROR", description
        else:
            yield "OK", description

    # This method implements the "send_command" primitive. Uncomment and modify it if you need a primitive that
    # sends any command to the VM through SSH. It only needs "file" parameter which contains the command to send.
    async def send_command(self, id, params):
        self.logger.debug("Execute action send_command, params: '{}'".format(params))

        self._check_required_params(params, ["file"])
        command = params["file"]
        return_code, description = await mylib.ssh_exec(self.config_params["ssh-hostname"], self.config_params["ssh-username"], command)
        if return_code != 0:
            yield "ERROR", description
        else:
            yield "OK", description


    # Static method that verifies whether a parameter exists in the map
    @staticmethod
    def _check_required_params(params, required_params):
        for required_param in required_params:
            if required_param not in params:
                raise VnfException("Missing required param: {}".format(required_param))

