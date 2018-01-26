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

import pecan
from pecan import rest
from six.moves import http_client
import wsme
from wsme import types as wtypes

from cyborg.api.controllers import base
from cyborg.api.controllers import link
from cyborg.api.controllers.v1 import types
from cyborg.api import expose
from cyborg.common import policy
from cyborg import objects
from cyborg.api.controllers.v1 import utils as api_utils
from cyborg.common import exception

from oslo_log import log as logging

LOG = logging.getLogger(__name__)

class Accelerator(base.APIBase):
    """API representation of a accelerator.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of
    a accelerator.
    """

    uuid = types.uuid
    name = wtypes.text
    description = wtypes.text
    project_id = types.uuid
    user_id = types.uuid
    device_type = wtypes.text
    acc_type = wtypes.text
    acc_capability = wtypes.text
    vendor_id = wtypes.text
    product_id = wtypes.text
    remotable = wtypes.IntegerType()

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        self.fields = []
        for field in objects.Accelerator.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, rpc_acc):
        accelerator = Accelerator(**rpc_acc.as_dict())
        url = pecan.request.public_url
        accelerator.links = [
            link.Link.make_link('self', url, 'accelerators',
                                accelerator.uuid),
            link.Link.make_link('bookmark', url, 'accelerators',
                                accelerator.uuid, bookmark=True)
            ]

        return accelerator



class AcceleratorCollection(base.APIBase):
    """API representation of a collection of accelerators."""

    accelerators = [Accelerator]
    """A list containing accelerator objects"""

    @classmethod
    def convert_with_links(cls, rpc_accs):
        collection = cls()
        collection.accelerators = [Accelerator.convert_with_links(obj_acc)
                                   for obj_acc in rpc_accs]
        return collection


class AcceleratorPatchType(types.JsonPatchType):

    _api_base = Accelerator

    @staticmethod
    def internal_attrs():
        defaults = types.JsonPatchType.internal_attrs()
        return defaults + ['/project_id', '/user_id', '/device_type',
                           '/acc_type', '/acc_capability', '/vendor_id',
                           '/product_id', '/remotable']


class AcceleratorsControllerBase(rest.RestController):
    _resource = None
    def _get_resource(self, uuid):
        self._resource = objects.Accelerator.get(pecan.request.context, uuid)
        return self._resource


class AcceleratorsController(AcceleratorsControllerBase):
    """REST controller for Accelerators."""

    #@policy.authorize_wsgi("cyborg:accelerator", "create", False)
    @expose.expose(Accelerator, body=types.jsontype,
                   status_code=http_client.CREATED)
    def post(self, accelerator):
        """Create a new accelerator.

        :param accelerator: an accelerator within the request body.
        """
        context = pecan.request.context
        rpc_acc = objects.Accelerator(context, **accelerator)
        new_acc = pecan.request.conductor_api.accelerator_create(
            context, rpc_acc)
        # Set the HTTP Location Header
        pecan.response.location = link.build_url('accelerators',
                                                 new_acc.uuid)
        return Accelerator.convert_with_links(new_acc)

    #@policy.authorize_wsgi("cyborg:accelerator", "get")
    @expose.expose(Accelerator, types.uuid)
    def get_one(self, uuid):
        """Retrieve information about the given uuid acceleratior.
        : param uuid: UUID of an accelerator.
        """

        # add if the accelerator does not exist a '404 Not Found' must be returned
        rpc_acc = self._get_resource(uuid)
        if rpc_acc == None:
            return pecan.abort(404, detail='The uuid Not Found.')
        else:
            return  Accelerator.convert_with_links(rpc_acc)


    @expose.expose(AcceleratorCollection, int, types.uuid, wtypes.text,
                   wtypes.text, types.boolean)
    def get_all(self, limit = None, marker = None, sort_key='id',
                sort_dir='asc', all_tenants=None):
        """Retrieve a list of accelerators.
        : param limit: Optional, to determine the maximum number of
        accelerators to return.
        : param marker: Optional, to display a list of accelerators after
        this marker.
        : param sort_dir: Optional, to return a list of accelerators with this
        sort direction.
        : param all_tenants: Optional, allows administrators to see the
        accelerators owned by all tenants, otherwise only the accelerators
        associated with the calling tenant are included in the response."""

        context = pecan.request.context
        project_only = True
        if context.is_admin and all_tenants:
            project_only = False

        marker_obj = None;
        if marker:
            marker_obj = objects.Accelerator.get(context, marker)

        rpc_accs = objects.Accelerator.list(
                context, limit, marker_obj, sort_key, sort_dir, project_only)

        return AcceleratorCollection.convert_with_links(rpc_accs)

    #@policy.authorize_wsgi("cyborg:accelerator", "update")
    @expose.expose(Accelerator, types.uuid, body=[AcceleratorPatchType])
    def put(self, uuid, patch):
        """Update an accelerator's property.
        : param uuid: UUID of an accelerator.
        : param patch: a json PATCH document to apply to this accelerator.
        """
        rpc_acc = self._resource or self._get_resource(uuid)
        try:
            api_acc = Accelerator(**api_utils.apply_jsonpatch(rpc_acc.as_dict(), patch))
        except api_utils.JSONPATCH_EXCEPTIONS as e:
            raise  exception.PatchError(patch=patch, reason=e)



        #update only the fields thart have changed.
        for field in objects.Accelerator.fields:
            try:
                patch_val = getattr(api_acc, field)
            except AttributeError:
            # Ignore fields that aren't exposed in the API
                continue

            if patch_val == wtypes.Unset:
                patch_val = None
            if rpc_acc[field] != patch_val:
                rpc_acc[field] = patch_val

        context = pecan.request.context
        new_acc = pecan.request.conductor_api.accelerator_update(context, rpc_acc)
        return Accelerator.convert_with_links(new_acc)

    #@policy.authorize_wsgi("cyborg:accelerator", "delete")
    @expose.expose(None, types.uuid, status_code=http_client.NO_CONTENT)
    def delete(self, uuid):
        """Delete an accelerator.
        :param uuid: UUID of the accelerator."""

        rpc_acc = self._resource or self._get_resource(uuid)

        LOG.info("test")

        if rpc_acc == None:
            status_code=http_client.NOT_FOUND

        context = pecan.request.context
        pecan.request.conductor_api.accelerator_delete(context, rpc_acc)

