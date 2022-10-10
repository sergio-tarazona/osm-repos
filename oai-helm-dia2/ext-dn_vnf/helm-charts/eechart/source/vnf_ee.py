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

    # This method implements the "ansible_playbook" primitive. Uncomment and modify it if a primitive requires
    # executing an Ansible Playbook. It needs "playbook-name" parameter (playbook file, must be in "source" directory).
    # async def ansible_playbook(self, id, params):
    #     self.logger.debug("Execute action ansible_playbook, params: '{}'".format(params))

    #     try:
    #         self._check_required_params(params, ["playbook-name"])
    #         params["ansible_user"] = self.config_params["ssh-username"]
    #         inventory = self.config_params["ssh-hostname"] + ","
    #         playbook = self.PLAYBOOK_PATH + "/" + params["playbook-name"]
    #         os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
    #         return_code, stdout, stderr = await util_ansible.execute_playbook(playbook, inventory, params)
    #         status = "OK" if return_code == 0 else "ERROR"
    #         yield status, stdout + stderr
    #     except Exception as e:
    #         self.logger.debug("Error executing ansible playbook: {}".format(repr(e)))
    #         yield "ERROR", str(e)

    # This method implements the "ping" primitive. Uncomment and modify it if a primitive requires
    # executing a local command (such as ping) on EE. It uses "ssh-hostname" as ping destination.
    # async def ping(self, id, params):
    #     self.logger.debug("Execute action ping, params: '{}'".format(params))

    #     command = "ping -c 3 " + self.config_params["ssh-hostname"]
    #     return_code, stdout, stderr = await util_ee.local_async_exec(command)
    #     if return_code != 0:
    #         yield "ERROR", "return code {}: {}".format(return_code, stderr.decode())
    #     else:
    #         yield "OK", stdout.decode()

    # This method implements the "http_check" primitive. Uncomment and modify it if a primitive requires
    # executing embedded python code on VfnEE class. It requests "http://<ssh-hostname>/" using a HTTP library.
    # async def http_check(self, id, params):
    #     self.logger.debug("Execute action http_check, params: '{}'".format(params))

    #     try:
    #         session = requests.Session()
    #         url = 'http://' + self.config_params["ssh-hostname"]
    #         self.logger.debug("HTTP GET {}...".format(url))
    #         req = session.get(url)
    #         self.logger.debug("{}".format(req.text))
    #         if req.status_code == 200:
    #             yield "OK", req.text
    #         else:
    #             yield "ERROR", req.text
    #     except Exception as e:
    #         self.logger.error("HTTP error: {}".format(repr(e)))
    #         yield "ERROR", str(e)

    # This method implements the "touch" primitive. Uncomment and modify it if you need a primitive that
    # imports a user-defined python library. It only needs "file" parameter for creating it in VDU via SSH.
    # async def touch(self, id, params):
    #     self.logger.debug("Execute action touch, params: '{}'".format(params))
    #
    #     self._check_required_params(params, ["file"])
    #     command = "touch" + " " + params["file"]
    #     return_code, description = await mylib.ssh_exec(self.config_params["ssh-hostname"], self.config_params["ssh-username"], command)
    #     if return_code != 0:
    #         yield "ERROR", description
    #     else:
    #         yield "OK", description

    # This method implements the "gnbsim_up" primitive. Uncomment and modify it if you need a primitive that
    # starts up the gnbsim to test 5G OAI Core. It only needs "file" parameter, in this case use gnbsim.
    async def ext_dn_up(self, id, params):
        self.logger.debug("Execute action gnbsim_up, params: '{}'".format(params))

        self._check_required_params(params, ["file"])
        command = "docker-compose up -d oai-ext-dn"
        return_code, description = await mylib.ssh_exec(self.config_params["ssh-hostname"], self.config_params["ssh-username"], command)
        if return_code != 0:
            yield "ERROR", description
        else:
            yield "OK", description
    
    # This method implements the "gnbsim_down" primitive. Uncomment and modify it if you need a primitive that
    # stops the gnbsim for testing 5G OAI Core. It only needs "file" parameter, in this case use gnbsim.
    async def ext_dn_down(self, id, params):
        self.logger.debug("Execute action gnbsim_down, params: '{}'".format(params))

        self._check_required_params(params, ["file"])
        command = "docker-compose down"
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

    # This method implements the "check_database" primitive. Uncomment and modify it if a primitive requires
    # accessing to a service provided by a helm subchart. Access parameters are read from environment variables
    # async def check_database(self, id, params):
    #     self.logger.debug("Execute action check_database, params: '{}'".format(params))

    #     host = os.getenv('mysql_host')
    #     user = os.getenv('mysql_user')
    #     password = os.getenv('mysql_password')
    #     retries = 3
    #     query = "SHOW DATABASES"
    #     return_code, description = mylib.mysql_query(host, user, password, retries, query)
    #     if return_code != 0:
    #         yield "ERROR", description
    #     else:
    #         yield "OK", description


    # Static method that verifies whether a parameter exists in the map
    @staticmethod
    def _check_required_params(params, required_params):
        for required_param in required_params:
            if required_param not in params:
                raise VnfException("Missing required param: {}".format(required_param))

