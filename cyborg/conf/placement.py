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

from oslo_config import cfg

from cyborg.common.i18n import _

opts = [
    cfg.StrOpt('region_name',
               help=_('Name of placement region to use. Useful if keystone '
                      'manages more than one region.')),
    cfg.StrOpt('endpoint_type',
               default='public',
               choices=['public', 'admin', 'internal'],
               help=_('Type of the placement endpoint to use.  This endpoint '
                      'will be looked up in the keystone catalog and should '
                      'be one of public, internal or admin.')),
    cfg.BoolOpt('insecure',
                default=False,
                help="""
                        If true, the vCenter server certificate is not verified.
                        If false, then the default CA truststore is used for
                        verification. Related options:
                        * ca_file: This option is ignored if "ca_file" is set.
                        """),
    cfg.StrOpt('cafile',
               default=None,
               help="""
                       Specifies the CA bundle file to be used in verifying the
                       vCenter server certificate.
                       """),
    cfg.StrOpt('certfile',
               default=None,
               help="""
                       Specifies the certificate file to be used in verifying
                       the vCenter server certificate.
                       """),
    cfg.StrOpt('keyfile',
               default=None,
               help="""
                       Specifies the key file to be used in verifying the vCenter
                       server certificate.
                       """),
    cfg.IntOpt('timeout',
               default=None,
               help=_('Timeout for inactive connections (in seconds)')),
]

opt_group = cfg.OptGroup(name='placement',
                         title='Options for the nova placement sync service')


def register_opts(conf):
    conf.register_opts(opts, group=opt_group)