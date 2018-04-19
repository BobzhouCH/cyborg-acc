# -*- coding: utf-8 -*-

#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pecan
import oslo_messaging as messaging
from oslo_service import periodic_task

from cyborg.accelerator.drivers.modules import netronome
from cyborg.accelerator.drivers.fpga.base import FPGADriver
from cyborg.agent.resource_tracker import ResourceTracker
from cyborg.conductor import rpcapi as conductor_api

from cyborg import objects

from cyborg.conf import CONF
from oslo_log import log as logging


LOG = logging.getLogger(__name__)

class AgentManager(periodic_task.PeriodicTasks):
    """Cyborg Agent manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host=None):
        super(AgentManager, self).__init__(CONF)
        #can only use in the same node, change it to RPC to conductor
        self.conductor_api = conductor_api.ConductorAPI()
        self.topic = topic
        self.host = host or CONF.host
        self.fpga_driver = FPGADriver()
        self._rt = ResourceTracker(host, self.conductor_api)

    def periodic_tasks(self, context, raise_on_error=False):
#        self.update_available_resource(context)
        return self.run_periodic_tasks(context,raise_on_error=raise_on_error)

    def hardware_list(self, context, values):
        """List installed hardware."""
        pass

    def fpga_program(self, context, accelerator, image):
        """Program a FPGA region, image can be a url or local file."""
        #TODO Get image from glance
        # And add claim and rollback logical
        raise NotImplementedError()


    @periodic_task.periodic_task(run_immediately=True)
    def update_available_resource(self,context, startup=True):
        """update all kinds of accelerator resources from their drivers."""
        driver = netronome.NETRONOMEDRIVER()
        port_resource = driver.get_available_resource()
        self.conductor_api.port_bulk_create(context, port_resource)
        self._rt.update_usage(context)
