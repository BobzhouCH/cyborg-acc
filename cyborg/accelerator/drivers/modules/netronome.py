"""
Cyborg Netronome driver modules implementation.
"""
import os
import json

from cyborg.accelerator.drivers.modules import generic

from oslo_log import log as logging

LOG = logging.getLogger(__name__)

class NETRONOMEDRIVER(generic.GENERICDRIVER):
    def __init__(self, *args, **kwargs):
        super(NETRONOMEDRIVER, self).__init__(*args, **kwargs)
        self.port_name_prefix = 'sdn_v0.'
        self.port_index_max = 59

    def get_available_resource(self):
        port_resource = self._read_config()
        LOG.info('Discover netronome port %s '% (port_resource))

        return port_resource

    def _ovs_port_check(self, port_name):
        for port in self.bridge_port_list:
            if port_name == port.strip():
                return True

        return False


    def _read_config(self):
        '''read tag_config_path tags config file 
        and return direction format variables'''
        self.tag_config_path = '/etc/cyborg/netronome_ports.json'
        if os.path.exists(self.tag_config_path):
            config_file = open(self.tag_config_path, 'r')
        else:
            output = 'There is no %s' % (self.tag_config_path)
            LOG.error('There is no %s' % (self.tag_config_path))
            return

        try:
            buf = config_file.read()
            netronome = json.loads(buf)
        except Exception:
            LOG.error('Failed to read %s' % (self.tag_config_path))

        return netronome['netronome_ports']

    def discover_ports(self):
        port_list = []
        for i in range(0, port_index_max + 1):
            port_name = port_name_prefix + str(i)
            port = dict()
            port["bind_instance"] = None
            port["bind_port"] = None
            port["is_used"] = False
            port["pci_slot"] = os.popen("ethtool -i %s | grep bus-info | cut -d ' ' -f 5" % port_name).read().strip()
            port["port_id"] = i
            port["port_name"] = port_name
            port["product_id"] = "6003"
            port["vender_id"] = "19ee"

            port_list.append(port)
