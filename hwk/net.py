# -*- coding: utf-8 -*-

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

import os
import re
import sys

from hwk import udev
from hwk import utils


_LINUX_SYS_CLASS_NET_DIR = '/sys/class/net'
_INFO_HELP = """Network subsystem
===============================================================================
`hwk.net.Info` attributes:

nics (list of `hwk.net.NIC` objects)

  A list of objects describing the network interface controllers on the system

  `hwk.net.NIC` attributes:

  name (string)

    Name of the network controller according to the system, e.g. 'wls1' or
    'enp0s25'

  mac_address (string)

    The MAC address of the NIC, as reported by the system

  model (string)

    String describing the processor model, if known

  vendor (string)

    The processor vendor, if known
"""


class Info(object):
    """Object describing the network information about a system."""

    def __init__(self):
        self.nics = []

    def __repr__(self):
        return "net (%d NICs)" % (
            len(self.nics),
        )

    def describe(self):
        return _INFO_HELP


class NIC(object):

    def __init__(self, name):
        self.name = name
        self.mac = None
        self.model = None
        self.vendor = None

    def __repr__(self):
        vendor_str = ''
        if self.vendor is not None:
            vendor_str = ' [' + self.vendor.strip() + ']'
        model_str = ''
        if self.model is not None:
            model_str = ' - ' + self.model.strip()
        return "NIC %s%s%s" % (
            self.name,
            vendor_str,
            model_str,
        )


def info():
    """Returns a `hwk.net.Info` object containing information on the network
    subsystem, or None if the information could not be determined.
    """
    try:
        return {
            "linux2": _linux_info,
        }[sys.platform]()
    except KeyError:
        return None


@utils.memoize
def _linux_info():
    nics = []
    for filename in os.listdir(_LINUX_SYS_CLASS_NET_DIR):
        # Ignore loopback...
        if filename == 'lo':
            continue

        udev_path = _LINUX_SYS_CLASS_NET_DIR + '/' + filename
        d_info = udev.device_properties(udev_path)

        nic_name = d_info.get('ID_NET_NAME', d_info.get('ID_NET_NAME_PATH'))

        nic = NIC(nic_name)

        mac = d_info.get('ID_NET_NAME_MAC')
        if mac is not None:
            # udev reports MAC addresses for network controllers in the form
            # "{type}x[a-f0-9]12", where {type} is a two-letter code for the
            # type of device. For example, here is what udev reports for an
            # ethernet and a wireless network controller:
            #
            # ID_NET_NAME_MAC=enxe06995034837
            # ID_NET_NAME_MAC=wlx1c7ee5299a06
            nic.mac = mac[-12:]

        nic.vendor = d_info.get('ID_VENDOR_FROM_DATABASE')
        nic.model = d_info.get('ID_MODEL_FROM_DATABASE')
        nics.append(nic)

    res = Info()
    res.nics = nics
    return res

