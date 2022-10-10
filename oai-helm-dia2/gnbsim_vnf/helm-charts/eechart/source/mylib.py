##
# Copyright 2022 Telefonica Investigacion y Desarrollo, S.A.U.
# This file is part of OSM
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
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact with: nfvlabs@tid.es
##

import logging
import asyncio
import asyncssh
import time


from mysql.connector import connect, Error

logger = logging.getLogger("osm_ee.vnf")


async def ssh_exec(host: str, user: str, command: str
                           ) -> (int, str):
    """
        Execute a remote command via SSH.
    """

    try:
        async with asyncssh.connect(host,
                                    username=user,
                                    known_hosts=None) as conn:
            logger.debug("Executing command '{}'".format(command))
            result = await conn.run(command)
            logger.debug("Result: {}".format(result))
            return result.exit_status, result.stderr
    except Exception as e:
        logger.error("Error: {}".format(repr(e)))
        return -1, str(e)


def mysql_query(host: str, user: str, password: str, retries: int, query: str
                           ) -> (int, str):
    """
        Execute a query to a MySQL database.
    """

    text = ""
    logger.debug("Host: '{}', user: '{}', password: '{}', query: '{}'".format(host, user, password, query))
    for i in range(0, retries):
        try:
            with connect(
                host=host,
                user=user,
                password=password,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    for (db) in cursor:
                        logger.debug(db)
                        text = text + str(db[0]) + ", "
                    return 0, text[0:len(text)-2]
        except Error as e:
            text = str(e)
            logger.debug("Error: {}".format(e))
            time.sleep(3)
            continue

    return -1, text
