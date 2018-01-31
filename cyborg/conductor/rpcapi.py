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

"""Client side of the conductor RPC API."""

from oslo_config import cfg
import oslo_messaging as messaging

from cyborg.common import constants
from cyborg.common import rpc
from cyborg.objects import base as objects_base


CONF = cfg.CONF


class ConductorAPI(object):
    """Client side of the conductor RPC API.

    API version history:

    |    1.0 - Initial version.

    """

    RPC_API_VERSION = '1.0'

    def __init__(self, topic=None):
        super(ConductorAPI, self).__init__()
        self.topic = topic or constants.CONDUCTOR_TOPIC
        target = messaging.Target(topic=self.topic,
                                  version='1.0')
        serializer = objects_base.CyborgObjectSerializer()
        self.client = rpc.get_client(target,
                                     version_cap=self.RPC_API_VERSION,
                                     serializer=serializer)

    def accelerator_create(self, context, acc_obj):
        """Signal to conductor service to create an accelerator.

        :param context: request context.
        :param acc_obj: a created (but not saved) accelerator object.
        :returns: created accelerator object.
        """
        cctxt = self.client.prepare(topic=self.topic, server=CONF.host)
<<<<<<< HEAD
        return cctxt.call(context, 'accelerator_create', values=acc_obj)
=======
        #return cctxt.call(context, 'accelerator_create', values=acc_obj)
        return cctxt.call(context, 'accelerator_create', acc_obj=acc_obj)
>>>>>>> 8f919f6ea81c906f84a06047e0eb262adaaa235a
