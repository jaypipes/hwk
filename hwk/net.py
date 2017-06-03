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
import subprocess
import platform

import six

from hwk import udev


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

  bus_type (string):

    The bus type used by the NIC, if known, e.g. 'pci'

  driver (string)

    The kernel network driver, if known, e.g. 'e1000e' or 'ath9k'

  mac_address (string)

    The MAC address of the NIC, as reported by the system

  model (string)

    String describing the NIC model, if known

  vendor (string)

    The NIC vendor, if known

  vendor_id (string)

    The ID of the vendor in hexadecimal, if known, e.g. '0x8086' or '0x168c'

  enabled_features (set of string)

    The set of features the NIC supports and has enabled, e.g.
    'rx-vlan-offload', 'tx-gso-partial', etc
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
        self.bus_type = None
        self.driver = None
        self.mac = None
        self.model = None
        self.vendor = None
        self.vendor_id = None
        self.enabled_features = set()

    def __repr__(self):
        vendor_str = ''
        if self.vendor is not None:
            vendor_str = ' [' + self.vendor.strip().decode('utf8') + ']'
        model_str = ''
        if self.model is not None:
            model_str = ' - ' + self.model.strip().decode('utf8')
        return "NIC %s%s%s" % (
            self.name,
            vendor_str,
            model_str,
        )


def _linux_nic_features(nic_name):
    cmd = ['ethtool', '-k', nic_name]
    try:
        out = subprocess.check_output(cmd)
        # The output of `ethtool -k <nic>` looks like the following:
        # $ ethtool -k enp0s25
        # Features for enp0s25:
        # rx-checksumming: on
        # tx-checksumming: on
        #         tx-checksum-ipv4: off [fixed]
        #         tx-checksum-ip-generic: on
        #         tx-checksum-ipv6: off [fixed]
        #         tx-checksum-fcoe-crc: off [fixed]
        #         tx-checksum-sctp: off [fixed]
        # scatter-gather: on
        #         tx-scatter-gather: on
        #         tx-scatter-gather-fraglist: off [fixed]
        # tcp-segmentation-offload: on
        #         tx-tcp-segmentation: on
        #         tx-tcp-ecn-segmentation: off [fixed]
        #         tx-tcp-mangleid-segmentation: off
        #         tx-tcp6-segmentation: on
        # udp-fragmentation-offload: off [fixed]
        # generic-segmentation-offload: on
        # generic-receive-offload: on
        # large-receive-offload: off [fixed]
        # rx-vlan-offload: on
        # tx-vlan-offload: on
        # ntuple-filters: off [fixed]
        # receive-hashing: on
        # highdma: on [fixed]
        # rx-vlan-filter: off [fixed]
        # vlan-challenged: off [fixed]
        # tx-lockless: off [fixed]
        # netns-local: off [fixed]
        # tx-gso-robust: off [fixed]
        # tx-fcoe-segmentation: off [fixed]
        # tx-gre-segmentation: off [fixed]
        # tx-gre-csum-segmentation: off [fixed]
        # tx-ipxip4-segmentation: off [fixed]
        # tx-ipxip6-segmentation: off [fixed]
        # tx-udp_tnl-segmentation: off [fixed]
        # tx-udp_tnl-csum-segmentation: off [fixed]
        # tx-gso-partial: off [fixed]
        # tx-sctp-segmentation: off [fixed]
        # fcoe-mtu: off [fixed]
        # tx-nocache-copy: off
        # loopback: off [fixed]
        # rx-fcs: off
        # rx-all: off
        # tx-vlan-stag-hw-insert: off [fixed]
        # rx-vlan-stag-hw-parse: off [fixed]
        # rx-vlan-stag-filter: off [fixed]
        # l2-fwd-offload: off [fixed]
        # busy-poll: off [fixed]
        # hw-tc-offload: off [fixed]
        all_features = set()
        enabled = set()
        for line in out.split(six.b('\n'))[1:]:
            line = line.decode('utf8')
            parts = line.split(':')
            if len(parts) != 2:
                continue
            feature = parts[0].strip()
            on_str = parts[1].strip().split(' ')[0]
            on = on_str == 'on'
            all_features.add(feature)
            if on:
                enabled.add(feature)
        return all_features, enabled
    except subprocess.CalledProcessError:
        return None


def nic_features(nic_name):
    """Given a NIC name, returns two sets of strings.  None if not mounted. The
    first set are all the features, the second are all features that are
    enabled.
    """
    return {
        "Linux": _linux_nic_features,
    }[platform.system()](nic_name)


def _linux_net_device_mac_address(dev):
    # Instead of use udevadm, we can get the device's MAC address by examing
    # the /sys/class/net/$DEVICE/address file in sysfs. However, for devices
    # that have addr_assign_type != 0, return None since the MAC address is
    # random.
    try:
        aat_path = os.path.join(
            _LINUX_SYS_CLASS_NET_DIR,
            dev,
            'addr_assign_type',
        )
        aat = int(open(aat_path, 'r').read().strip())
        if aat != 0:
            return None
        addr_path = os.path.join(_LINUX_SYS_CLASS_NET_DIR, dev, 'address')
        return open(addr_path, 'r').read().strip()
    except IOError:
        return None


def info():
    """Returns a `hwk.net.Info` object containing information on the network
    subsystem, or None if the information could not be determined.
    """
    return {
        "Linux": _linux_info,
    }[platform.system()]()


def _linux_info():
    nics = []
    for filename in os.listdir(_LINUX_SYS_CLASS_NET_DIR):
        # Ignore loopback...
        if filename == 'lo':
            continue

        net_path = os.path.join(_LINUX_SYS_CLASS_NET_DIR, filename)
        dest = os.readlink(net_path)
        if 'virtio' in dest:
            # Don't bother using udevadm for virtual devices... we'll get an
            # error "query needs a valid device specified by --path= or
            # --name="
            d_info = {}
        else:
            udev_path = _LINUX_SYS_CLASS_NET_DIR + '/' + filename
            d_info = udev.device_properties(udev_path)

        nic = NIC(filename)

        nic.mac = _linux_net_device_mac_address(filename)
        nic.vendor = d_info.get('ID_VENDOR_FROM_DATABASE')
        nic.vendor_id = d_info.get('ID_VENDOR_ID')
        nic.model = d_info.get('ID_MODEL_FROM_DATABASE')
        nic.bus_type = d_info.get('ID_BUS')
        nic.driver = d_info.get('ID_NET_DRIVER')
        features = _linux_nic_features(filename)
        if features is not None:
            nic.enabled_features = features[1]
        nics.append(nic)

    res = Info()
    res.nics = nics
    return res
