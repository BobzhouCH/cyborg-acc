"""
Cyborg SPDK driver modules implementation.
"""

import socket
from cyborg.accelerator.common import exception
from cyborg.accelerator.drivers.modules import generic
from oslo_log import log as logging
from oslo_config import cfg
from oslo_concurrency import processutils as putils
from cyborg.common.i18n import _
from cyborg.accelerator import configuration
from cyborg.db.sqlalchemy import api

LOG = logging.getLogger(__name__)

accelerator_opts = [
    cfg.StrOpt('spdk_conf_file',
               default='/etc/cyborg/spdk.conf',
               help=_('SPDK conf file to use for the SPDK driver in Cyborg;')),

    cfg.StrOpt('device_type',
               default='NVMe',
               help=_('Default backend device type: NVMe')),

    cfg.IntOpt('queue',
               default=8,
               help=_('Default number of queues')),

    cfg.IntOpt('iops',
               default=1000,
               help=_('Default number of iops')),

    cfg.IntOpt('bandwidth:',
               default=800,
               help=_('Default bandwidth')),

    cfg.BoolOpt('remoteable:',
                default=False,
                help=_('remoteable is false by default'))

]

CONF = cfg.CONF
CONF.register_opts(accelerator_opts, group=configuration.SHARED_CONF_GROUP)

try:
    import py_spdk
except ImportError:
    py_spdk = None


class SPDKDRIVER(generic.GENERICDRIVER):
    def __init__(self, execute=putils.execute, *args, **kwargs):
        super(SPDKDRIVER, self).__init__(execute, *args, **kwargs)
        self.configuration.append_config_values(accelerator_opts)
        self.hostname = socket.gethostname()
        self.driver_type = self.configuration\
                               .safe_get('accelerator_backend_name') or 'SPDK'
        self.device_type = self.configuration.safe_get('device_type')
        self.dbconn = api.get_backend()

    def initialize_connection(self, accelerator, connector):
        return py_spdk.initialize_connection(accelerator, connector)

    def validate_connection(self, connector):
        return py_spdk.initialize_connection(connector)

    def destory_db(self):
        if self.dbconn is not None:
            self.dbconn.close()

    def discover_driver(self, driver_type):
        HAVE_SPDK = None
        if HAVE_SPDK:
            values = {'acc_type': self.driver_type}
            self.dbconn.accelerator_create(None, values)

    def install_driver(self, driver_id, driver_type):
        accelerator = self.dbconn.accelerator_query(None, driver_id)
        if accelerator:
            self.initialize_connection(accelerator, None)
            self.do_setup()
            ctrlr = self.get_controller()
            nsid = self.get_allocated_nsid(ctrlr)
            self.attach_instance(nsid)
        else:
            msg = (_("Could not find %s accelerator") % driver_type)
            raise exception.InvalidAccelerator(msg)

    def uninstall_driver(self, driver_id, driver_type):
        ctrlr = self.get_controller()
        nsid = self.get_allocated_nsid(ctrlr)
        self.detach_instance(nsid)
        pass

    def driver_list(self, driver_type):
        return self.dbconn.accelerator_query(None, driver_type)

    def update(self, driver_type):
        pass

    def attach_instance(self, instance_id):
        self.add_ns()
        self.attach_and_detach_ns()
        pass

    def detach_instance(self, instance_id):
        self.delete_ns()
        self.detach_and_detach_ns()
        pass

    def get_controller(self):
        return self.ctrlr

    '''list controllers'''

    def display_controller_list(self):
        pass

    '''create namespace'''

    def add_ns(self):
        pass

    '''delete namespace'''

    def delete_ns(self):
        pass

    '''attach namespace to controller'''

    def attach_and_detach_ns(self):
        pass

    '''detach namespace from controller'''

    def detach_and_detach_ns(self):
        pass

    '''	format namespace or controller'''

    def format_nvm(self):
        pass

    def get_allocated_nsid(self, ctrl):
        return self.nsid
