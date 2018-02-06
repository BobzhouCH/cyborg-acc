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

import pecan
from pecan import rest
from six.moves import http_client
import wsme
from wsme import types as wtypes

from cyborg.api.controllers import base
from cyborg.api.controllers import link
from cyborg.api.controllers.v1 import types
from cyborg.api import expose
from pecan import expose as pexpose
from cyborg.common import policy
from cyborg import objects
from cyborg.api.controllers.v1 import utils as api_utils
from cyborg.common import exception

from oslo_log import log as logging

LOG = logging.getLogger(__name__)

class Port(base.APIBase):
    """API representation of a port.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of
    a port.
    """

    uuid = types.uuid
    computer_id = types.uuid
    phy_port_name = wtypes.text
    pci_slot = wtypes.text
    product_id = wtypes.text
    vendor_id = wtypes.text
    is_used = wtypes.IntegerType()
    accelerator_id = types.uuid
    bind_instance_id = types.uuid
    bind_port_id = types.uuid
    device_type = wtypes.text

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        self.fields = []
        for field in objects.Port.fields:
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, rpc_acc):
        port = Port(**rpc_acc.as_dict())
        url = pecan.request.public_url
        port.links = [
            link.Link.make_link('self', url, 'ports',
                                port.uuid),
            link.Link.make_link('bookmark', url, 'ports',
                                port.uuid, bookmark=True)
            ]

        return port



class PortCollection(base.APIBase):
    """API representation of a collection of ports."""

    ports = [Port]
    """A list containing port objects"""

    @classmethod
    def convert_with_links(cls, rpc_ports):
        collection = cls()
        collection.ports = [Port.convert_with_links(obj_port)
                                   for obj_port in rpc_ports]
        return collection


class PortPatchType(types.JsonPatchType):

    _api_base = Port

    @staticmethod
    def internal_attrs():
        defaults = types.JsonPatchType.internal_attrs()
        return defaults + ['/computer_id', '/phy_port_name', '/pci_slot',
                             '/vendor_id', '/product_id']


class PortsControllerBase(rest.RestController):
    _resource = None
    def _get_resource(self, uuid):
        self._resource = objects.Port.get(pecan.request.context, uuid)
        return self._resource


class BindPortController(PortsControllerBase):
    # url path: /v1/ports/bind/{uuid}

    @expose.expose(Port, body=types.jsontype)
    def put(self, uuid, patch):
        """bind a existing port to a logical neutron port.
        : param uuid: UUID of a port.
        : param patch: a json type to apply to this port.
        """
        context = pecan.request.context
        obj_port = self._resource or self._get_resource(uuid)
        # object with user modified properties.
        mod_port = objects.Port(context, **patch)

        # update fields used in bind.
        obj_port["accelerator_id"] = mod_port["accelerator_id"]
        obj_port["bind_instance_id"] = mod_port["bind_instance_id"]
        obj_port["bind_port_id"] = mod_port["bind_port_id"]
        obj_port["is_used"] = mod_port["is_used"]
        obj_port["device_type"] = mod_port["device_type"]

        LOG.debug(obj_port)
        new_port = pecan.request.conductor_api.port_update(context, obj_port)
        return Port.convert_with_links(new_port)

class UnBindPortController(PortsControllerBase):
    # url path: /v1/ports/bind/{uuid}

    @expose.expose(Port, body=types.jsontype)
    def put(self, uuid):
        """unbind a existing port, set some areas to null in DB.
        : param uuid: UUID of a port.
        : param patch: a json type to apply to this port.
        """
        context = pecan.request.context
        obj_port = self._resource or self._get_resource(uuid)

        # update fields used in unbind.
        obj_port["accelerator_id"] = None
        obj_port["bind_instance_id"] = None
        obj_port["bind_port_id"] = None
        obj_port["is_used"] = 0
        obj_port["device_type"] = None

        new_port = pecan.request.conductor_api.port_update(context, obj_port)
        return Port.convert_with_links(new_port)


class PortsController(PortsControllerBase):
    """REST controller for Ports.
       url path: /v2.0/ports/
    """
    bind = BindPortController()
    unbind = UnBindPortController()

    @policy.authorize_wsgi("cyborg:port", "create", False)
    @expose.expose(Port, body=types.jsontype,
                   status_code=http_client.CREATED)
    def post(self, port):
        """Create a new port.

        :param port: an port within the request body.
        """
        context = pecan.request.context
        rpc_port = objects.Port(context, **port)
        new_port = pecan.request.conductor_api.port_create(
            context, rpc_port)
        # Set the HTTP Location Header
        pecan.response.location = link.build_url('ports',
                                                 new_port.uuid)
        return Port.convert_with_links(new_port)

    #@policy.authorize_wsgi("cyborg:port", "get")
    @expose.expose(Port, types.uuid)
    def get_one(self, uuid):
        """Retrieve information about the given uuid port.
        : param uuid: UUID of a port.
        """
        rpc_port = self._get_resource(uuid)
        if rpc_port == None:
            return pecan.abort(404, detail='The uuid Not Found.')
        else:
            return  Port.convert_with_links(rpc_port)

    @expose.expose(PortCollection, int, types.uuid, wtypes.text,
                   wtypes.text, types.boolean)
    def get_all(self, limit = None, marker = None, sort_key='id',
                sort_dir='asc'):
        """Retrieve a list of ports.
        : param limit: Optional, to determine the maximum number of
        ports to return.
        : param marker: Optional, to display a list of ports after
        this marker.
        : param sort_dir: Optional, to return a list of ports with this
        sort direction.
        : param all_tenants: Optional, allows administrators to see the
        ports owned by all tenants, otherwise only the ports
        associated with the calling tenant are included in the response."""

        context = pecan.request.context
        marker_obj = None;
        if marker:
            marker_obj = objects.Port.get(context, marker)

        rpc_ports = objects.Port.list(
                context, limit, marker_obj, sort_key, sort_dir)

        return PortCollection.convert_with_links(rpc_ports)

    #@policy.authorize_wsgi("cyborg:port", "update")
    @expose.expose(Port, types.uuid, body=[PortPatchType])
    def put(self, uuid, patch):
        """Update an port's property.
        : param uuid: UUID of a port.
        : param patch: a json PATCH document to apply to this port.
        """
        obj_port = self._resource or self._get_resource(uuid)
        try:
            api_port = Port(**api_utils.apply_jsonpatch(obj_port.as_dict(), patch))
        except api_utils.JSONPATCH_EXCEPTIONS as e:
            raise  exception.PatchError(patch=patch, reason=e)

        #update only the fields that have changed.
        for field in objects.Port.fields:
            try:
                patch_val = getattr(api_port, field)
            except AttributeError:
            # Ignore fields that aren't exposed in the API
                continue

            if patch_val == wtypes.Unset:
                patch_val = None
            if obj_port[field] != patch_val:
                obj_port[field] = patch_val

        context = pecan.request.context
        new_port = pecan.request.conductor_api.port_update(context, obj_port)
        return Port.convert_with_links(new_port)


    #@policy.authorize_wsgi("cyborg:port", "delete")
    @expose.expose(None, types.uuid, status_code=http_client.NO_CONTENT)
    def delete(self, uuid):
        """Delete a port.
        :param uuid: UUID of the port."""

        rpc_port = self._resource or self._get_resource(uuid)
        if rpc_port == None:
            status_code = http_client.NOT_FOUND
        context = pecan.request.context
        pecan.request.conductor_api.port_delete(context, rpc_port)







