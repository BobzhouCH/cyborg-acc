# Copyright 2017 Huawei Technologies Co.,LTD.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import oslo_messaging as messaging

from cyborg import objects
from cyborg.conf import CONF


from oslo_log import log as logging


LOG = logging.getLogger(__name__)

class ConductorManager(object):
    """Cyborg Conductor manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host=None):
        super(ConductorManager, self).__init__()
        self.topic = topic
        self.host = host or CONF.host

    def periodic_tasks(self, context, raise_on_error=False):
        pass

    def accelerator_create(self, context, acc_obj):
        """Create a new accelerator.

        :param context: request context.
        :param acc_obj: a changed (but not saved) accelerator object.
        :returns: created accelerator object.
        """
        base_options={
            'project_id' : context.tenant,
            'user_id' : context.user
        }
        acc_obj.update(base_options)
        acc_obj.create(context)
        return acc_obj

    def accelerator_update(self, context, acc_obj):
        """Update an accelerator.
        :param context: request context.
        :param acc_obj: an accelerator object to update.
        :return: updated accelerator objects."""

        acc_obj.save(context)
        return acc_obj

    def accelerator_delete(self, context, acc_obj):
        """Delete an accelerator.

        :param context: request context.
        :param acc_obj: an accelerator object to delete."""

        acc_obj.destory(context)


    def port_create(self, context, port_obj):
        """Create a new port.

        :param context: request context.
        :param port_obj: a changed (but not saved) port object.
        :returns: created port object.
        """
        port_obj.create(context)
        return port_obj

    def port_bulk_create(self, context, port_list):
        """Create a new port.

        :param context: request context.
        :param port_list: port list need to be create and save.
        :returns: request result.
        """
        try:
            for port in list(port_list):
                port_obj = objects.Port(context, **port)
                port = self.check_port_exist(context, port_obj)
                if not port:
                    port_obj.create(context)

            LOG.info('Update port resource %s ' % (port_list))
            return True
        except Exception as e:
            LOG.error("Failed to port bulk create with error: %s" % (e))
            LOG.error("Failed to port bulk create: %s" % (port_list))


    def port_update(self, context, port_obj):
        """Update a port.
        :param context: request context.
        :param port_obj: a port object to update.
        :return: updated port objects."""

        port_obj.save(context)
        return port_obj

    def port_delete(self, context, port_obj):
        """Delete a port.

        :param context: request context.
        :param port_obj: a port object to delete."""

        port_obj.destory(context)

    def check_port_exist(self, context, port_obj):
        """Delete a port.
        
        :param port_obj: a port object to delete.
        :returns: True/False exist or not exist.
        """
        return objects.Port.get(context=context, phy_port_name=port_obj.phy_port_name, \
                           pci_slot=port_obj.pci_slot, computer_node=port_obj.computer_node)

