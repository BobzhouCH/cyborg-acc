# Copyright 2018 Intel, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""
Cyborg FPGA driver implementation.
"""

from cyborg.accelerator.drivers.fpga import utils


VENDOR_MAPS = {"0x8086": "intel"}


class FPGADriver(object):
    """Base class for FPGA drivers.
       This is just a virtual FPGA drivers interface.
       Vendors should implement their specific drivers.
    """

    @classmethod
    def create(cls, vendor, *args, **kwargs):
        for sclass in cls.__subclasses__():
            vendor = VENDOR_MAPS.get(vendor, vendor)
            if vendor == sclass.VENDOR:
                return sclass(*args, **kwargs)
        raise LookupError("Not find the FPGA driver for vendor %s" % vendor)

    def __init__(self, *args, **kwargs):
        pass

    def discover(self):
        raise NotImplementedError()

    def program(self, device_path, image):
        raise NotImplementedError()

    @classmethod
    def discover_vendors(cls):
        return utils.discover_vendors()