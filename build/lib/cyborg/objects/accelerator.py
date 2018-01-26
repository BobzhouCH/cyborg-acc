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

from oslo_log import log as logging
from oslo_versionedobjects import base as object_base

from cyborg.db import api as dbapi
from cyborg.objects import base
from cyborg.objects import fields as object_fields

LOG = logging.getLogger(__name__)

@base.CyborgObjectRegistry.register
class Accelerator(base.CyborgObject, object_base.VersionedObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'uuid': object_fields.UUIDField(nullable=False),
        'name': object_fields.StringField(nullable=False),
        'description': object_fields.StringField(nullable=True),
        'project_id': object_fields.UUIDField(nullable=True),
        'user_id': object_fields.UUIDField(nullable=True),
        'device_type': object_fields.StringField(nullable=False),
        'acc_type': object_fields.StringField(nullable=False),
        'acc_capability': object_fields.StringField(nullable=False),
        'vendor_id': object_fields.StringField(nullable=False),
        'product_id': object_fields.StringField(nullable=False),
        'remotable': object_fields.IntegerField(nullable=False),
    }

    def __init__(self, *args, **kwargs):
        super(Accelerator, self).__init__(*args, **kwargs)

    def create(self, context=None):
        """Create an Accelerator record in the DB."""
        values = self.obj_get_changes()
        db_acc= self.dbapi.accelerator_create(context, values)
        self._from_db_object(self, db_acc)

    @classmethod
    def get(cls, context, uuid):
        """Find a DB Accelerator and return an Ojb Accelerator."""
        db_acc = cls.dbapi.accelerator_get(context, uuid)
        obj_acc = cls._from_db_object(cls(context), db_acc)
        return obj_acc

    @classmethod
    def list(cls, context, limit, marker, sort_key, sort_dir, project_only):
        """Return a list of Accelerator objects."""
        db_accs = cls.dbapi.accelerator_list(context, limit, marker, sort_key,
                                             sort_dir, project_only)
        obj_accs = cls._from_db_object_list(context, db_accs)
        return obj_accs

    def save(self, context):
        """Update an Accelerator record in the DB."""
        updates = self.obj_get_changes()
        db_acc = self.dbapi.accelerator_update(context, self.uuid, updates)
        self._from_db_object(self, db_acc)

    def destory(self, context):
        """Delete the Accelerator record from the DB."""
        self.dbapi.accelerator_destory(context, self.uuid)
        self.obj_reset_changes()
