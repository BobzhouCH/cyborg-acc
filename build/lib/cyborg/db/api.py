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

"""Base classes for storage engines."""

import abc

from oslo_config import cfg
from oslo_db import api as db_api
import six


_BACKEND_MAPPING = {'sqlalchemy': 'cyborg.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF,
                                backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    # accelerator
    @abc.abstractmethod
    def accelerator_create(self, context, values):
        """Create a new accelerator."""

    @abc.abstractmethod
    def accelerator_get(self, context, uuid):
        """Get requested accelerator."""

    @abc.abstractmethod
    def accelerator_list(self, context, limit, marker, sort_key, sort_dir, project_only):
        """Get requested list accelerators."""

    @abc.abstractmethod
    def accelerator_update(self, context, uuid, values):
        """Update an accelerator."""

    @abc.abstractmethod
    def accelerator_destory(self, context, uuid):
        """Delete an accelerator."""

    #ports
    @abc.abstractmethod
    def port_create(self, context, values):
        """Create a new port."""

    @abc.abstractmethod
    def port_get(self, context, uuid):
        """Get requested port."""

    @abc.abstractmethod
    def port_list(self, context, limit, marker, sort_key, sort_dir):
        """Get requested list ports."""

    @abc.abstractmethod
    def port_update(self, context, uuid, values):
        """Update a port."""

    @abc.abstractmethod
    def port_destory(self, context, uuid):
        """Delete a port."""