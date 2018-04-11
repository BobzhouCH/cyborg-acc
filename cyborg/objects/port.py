# Copyright 2018 Lenovo Research Co.,LTD.
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

from oslo_log import log as logging
from oslo_versionedobjects import base as object_base

from cyborg.db import api as dbapi
from cyborg.objects import base
from cyborg.objects import fields as object_fields

LOG = logging.getLogger(__name__)

@base.CyborgObjectRegistry.register
class Port(base.CyborgObject, object_base.VersionedObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=False),
        'computer_node': object_fields.UUIDField(nullable=False),
        'phy_port_name': object_fields.StringField(nullable=True),
        'pci_slot': object_fields.StringField(nullable=True),
        'product_id': object_fields.StringField(nullable=True),
        'vendor_id': object_fields.StringField(nullable=False),
        'is_used': object_fields.IntegerField(nullable=False),
        'accelerator_id': object_fields.UUIDField(nullable=True),
        'bind_instance_id': object_fields.UUIDField(nullable=True),
        'bind_port_id': object_fields.UUIDField(nullable=True),
        'device_type': object_fields.StringField(nullable=True),
    }

    def __init__(self, *args, **kwargs):
        super(Port, self).__init__(*args, **kwargs)

    def create(self, context=None):
        """Create an Port record in the DB, this can be used by cyborg-agents
        to auto register physical port of network cards."""
        values = self.obj_get_changes()
        db_port= self.dbapi.port_create(context, values)
        self._from_db_object(self, db_port)

    @classmethod
    def get(cls, context, uuid):
        """Find a DB Port and return an Ojb Port."""
        db_port = cls.dbapi.port_get(context, uuid)
        obj_port = cls._from_db_object(cls(context), db_port)
        return obj_port

    @classmethod
    def get(cls, context, phy_port_name, pci_slot, computer_node):
        """Return a list of Port objects."""
        db_port = cls.dbapi.port_get(context, phy_port_name=phy_port_name,
                                     pci_slot=pci_slot, computer_node=computer_node)
        if db_port:
            obj_port = cls._from_db_object(cls(context), db_port)
            return obj_port
        else:
            return None

    @classmethod
    def list(cls, context, limit, marker, sort_key, sort_dir):
        """Return a list of Port objects."""
        db_ports = cls.dbapi.port_list(context, limit, marker, sort_key,
                                             sort_dir)
        obj_ports = cls._from_db_object_list(context, db_ports)
        return obj_ports

    def save(self, context):
        """Update a Port record in the DB."""
        updates = self.obj_get_changes()
        db_port = self.dbapi.port_update(context, self.uuid, updates)
        self._from_db_object(self, db_port)

    def destory(self, context):
        """Delete the Port record in the DB."""
        self.dbapi.port_destory(context, self.uuid)
        self.obj_reset_changes()
