# Copyright 2018 Huawei Technologies Co.,LTD.
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

from cyborg.common import exception
from cyborg.db import api as dbapi
from cyborg.objects import base
from cyborg.objects import fields as object_fields


LOG = logging.getLogger(__name__)


@base.CyborgObjectRegistry.register
class Attribute(base.CyborgObject, object_base.VersionedObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'id': fields.IntegerField(nullable=False),
        'uuid': object_fields.UUIDField(nullable=False),
        'deployable_id': fields.IntegerField(nullable=False),
        'key': object_fields.StringField(nullable=False),
        'value': object_fields.StringField(nullable=False)
    }

    def create(self, context):
        """Create an attribute record in the DB."""
        if self.deployable_id is None:
            raise exception.AttributeInvalid()

        values = self.obj_get_changes()
        db_attr = self.dbapi.attribute_create(context,
                                              self.key,
                                              self.value)
        self._from_db_object(self, db_attr)

    @classmethod
    def get(cls, context, uuid):
        """Find a DB attribute and return an Obj attribute."""
        db_attr = cls.dbapi.attribute_get(context, uuid)
        obj_attr = cls._from_db_object(cls(context), db_attr)
        return obj_attr

    @classmethod
    def attribute_get_by_deployable_uuid(cls, context, deployable_uuid):
        """Get an attribute by deployable uuid."""
        db_attr = cls.dbapi.attribute_get_by_deployable_uuid(context,
                                                             deployable_uuid)
        return cls._from_db_object_list(db_attr, context)

    def save(self, context):
        """Update an attribute record in the DB."""
        updates = self.obj_get_changes()
        db_attr = self.dbapi.attribute_update(context,
                                              self.uuid,
                                              self.key,
                                              self.value)
        self._from_db_object(self, db_attr)

    def destroy(self, context):
        """Delete an attribute from the DB."""
        self.dbapi.attribute_delete(context, self.uuid)
        self.obj_reset_changes()

    def set_key_value_pair(self, set_key, set_value):
        self.key = set_key
        self.value = set_value
