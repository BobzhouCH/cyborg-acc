# Copyright 2018 Huawei Technologies Co.,LTD.
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

import datetime

import mock
import netaddr
from oslo_db import exception as db_exc
from oslo_serialization import jsonutils
from oslo_utils import timeutils
from oslo_context import context

from cyborg import db
from cyborg.common import exception
from cyborg import objects
from cyborg.objects import base
from cyborg import tests as test
from cyborg.tests.unit import fake_accelerator
from cyborg.tests.unit import fake_deployable
from cyborg.tests.unit.objects import test_objects
from cyborg.tests.unit.db.base import DbTestCase


class _TestDeployableObject(DbTestCase):
    @property
    def fake_deployable(self):
        db_deploy = fake_deployable.fake_db_deployable(id=2)
        return db_deploy

    @property
    def fake_accelerator(self):
        db_acc = fake_accelerator.fake_db_acceleraotr(id=2)
        return  db_acc

    def test_create(self, mock_create):
        db_acc = self.fake_accelerator
        acc = objects.Accelerator(context=self.context,
                                  **db_acc)
        acc.create(self.context)
        acc_get = objects.Accelerator.get(self.context, acc.uuid)

        db_dpl = self.fake_deployable
        dpl = objects.Deployable(context=self.context,
                                 **db_dpl)
        dpl.accelerator_id = acc_get.id
        dpl.create(self.context)
        self.assertEqual(db_dpl['uuid'], dpl.uuid)



    def test_get(self):
        db_acc = self.fake_accelerator
        acc = objects.Accelerator(context=self.context,
                                  **db_acc)
        acc.create(self.context)
        acc_get = objects.Accelerator.get(self.context, acc.uuid)
        db_dpl = self.fake_deployable
        dpl = objects.Deployable(context=self.context,
                                 **db_dpl)

        dpl.accelerator_id = acc_get.id
        dpl.create(self.context)
        dpl_get = objects.Deployable.get(self.context, dpl.uuid)
        self.assertEqual(dpl_get.uuid, dpl.uuid)

    def test_get_by_filter(self):
        db_acc = self.fake_accelerator
        acc = objects.Accelerator(context=self.context,
                                  **db_acc)
        acc.create(self.context)
        acc_get = objects.Accelerator.get(self.context, acc.uuid)
        db_dpl = self.fake_deployable
        dpl = objects.Deployable(context=self.context,
                                 **db_dpl)

        dpl.accelerator_id = acc_get.id
        dpl.create(self.context)
        query = {"uuid": dpl['uuid']}
        dpl_get_list = objects.Deployable.get_by_filter(self.context, query)

        self.assertEqual(dpl_get_list[0].uuid, dpl.uuid)

    def test_save(self):
        db_acc = self.fake_accelerator
        acc = objects.Accelerator(context=self.context,
                                  **db_acc)
        acc.create(self.context)
        acc_get = objects.Accelerator.get(self.context, acc.uuid)
        db_dpl = self.fake_deployable
        dpl = objects.Deployable(context=self.context,
                                 **db_dpl)

        dpl.accelerator_id = acc_get.id
        dpl.create(self.context)
        dpl.host = 'test_save'
        dpl.save(self.context)
        dpl_get = objects.Deployable.get(self.context, dpl.uuid)
        self.assertEqual(dpl_get.host, 'test_save')

    def test_destroy(self):
        db_acc = self.fake_accelerator
        acc = objects.Accelerator(context=self.context,
                                  **db_acc)
        acc.create(self.context)
        acc_get = objects.Accelerator.get(self.context, acc.uuid)
        db_dpl = self.fake_deployable
        dpl = objects.Deployable(context=self.context,
                                 **db_dpl)

        dpl.accelerator_id = acc_get.id
        dpl.create(self.context)
        self.assertEqual(db_dpl['uuid'], dpl.uuid)
        dpl.destroy(self.context)
        self.assertRaises(exception.DeployableNotFound,
                          objects.Deployable.get, self.context,
                          dpl.uuid)


class TestDeployableObject(test_objects._LocalTest,
                           _TestDeployableObject):
    def _test_save_objectfield_fk_constraint_fails(self, foreign_key,
                                                   expected_exception):

        error = db_exc.DBReferenceError('table', 'constraint', foreign_key,
                                        'key_table')
        # Prevent lazy-loading any fields, results in InstanceNotFound
        deployable = fake_deployable.fake_deployable_obj(self.context)
        fields_with_save_methods = [field for field in deployable.fields
                                    if hasattr(deployable, '_save_%s' % field)]
        for field in fields_with_save_methods:
            @mock.patch.object(deployable, '_save_%s' % field)
            @mock.patch.object(deployable, 'obj_attr_is_set')
            def _test(mock_is_set, mock_save_field):
                mock_is_set.return_value = True
                mock_save_field.side_effect = error
                deployable.obj_reset_changes(fields=[field])
                deployable._changed_fields.add(field)
                self.assertRaises(expected_exception, deployable.save)
                deployable.obj_reset_changes(fields=[field])
            _test()