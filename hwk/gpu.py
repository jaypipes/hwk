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
import sys

from hwk import udev
from hwk import utils

_LINUX_SYS_BUS_PCI_DEVICES_DIR = '/sys/bus/pci/devices/'
_INFO_HELP = """GPU subsystem
===============================================================================
`hwk.gpu.Info` attributes:

gpus (list of `hwk.gpu.GPU` objects)

  A list of objects describing the physical graphical processing units

  `hwk.gpu.GPU` attributes:

  bus_type (string)

    Device bus used. Currently only 'pci'

  address (string)

    GPU's device address (if bus_type is 'pci', this will be the complete PCI
    address

  driver (string)

    The kernel device driver used for this GPU, if known

  model (string)

    String describing the processor model, if known

  vendor (string)

    The processor vendor, if known

  vendor_id (string)

    The ID of the vendor in hexadecimal, if known, e.g. '0x8086' or '0x168c'
"""


class Info(object):
    """Object describing the graphical processing units in a system."""

    def __init__(self):
        self.gpus = []

    def __repr__(self):
        return "gpu (%d physical GPUs)" % (
            len(self.gpus),
        )

    def describe(self):
        return _INFO_HELP


class GPU(object):

    def __init__(self):
        self.model = None
        self.vendor = None
        self.bus_type = None
        self.address = None
        self.driver = None

    def __repr__(self):
        vendor_str = ''
        if self.vendor is not None:
            vendor_str = ' [' + self.vendor.strip() + ']'
        model_str = ''
        if self.model is not None:
            model_str = ' (' + self.model.strip() + ')'
        return "GPU @%s:%s%s%s" % (
            self.bus_type,
            self.address,
            vendor_str,
            model_str,
        )


def info():
    """Returns a `hwk.gpu.Info` object containing information on the GPUs
    available to the system, or None if the information could not be
    determined.
    """
    try:
        return {
            "linux2": _linux_info,
        }[sys.platform]()
    except KeyError:
        return None


@utils.memoize
def _linux_info():
    gpus = []
    cmd = ['lspci', '-D']
    out = subprocess.check_output(cmd).strip()
    for line in out.split('\n'):
        if not 'VGA' in line:
            # TODO(jaypipes): Figure out if there are any GPUs that do **NOT**
            # indicate they are a VGA-compatible controller...
            continue
        # Matching lines look like:
        # 0000:03:00.0 VGA compatible controller: NVIDIA Corporation GF114\
        # [GeForce GTX 560 Ti] (rev a1)
        pci_address = line[:12]
        udev_path = _LINUX_SYS_BUS_PCI_DEVICES_DIR + pci_address
        d_info = udev.device_properties(udev_path)

        gpu = GPU()
        gpu.address = pci_address
        gpu.bus_type = 'pci'

        gpu.vendor = d_info.get('ID_VENDOR_FROM_DATABASE')
        pci_id = d_info.get('PCI_ID')
        if pci_id is not None:
            vendor_id, product_id = pci_id.split(':')
            vendor_id = '0x%s' % vendor_id.lower()
            gpu.vendor_id = vendor_id
        gpu.model = d_info.get('ID_MODEL_FROM_DATABASE')
        gpu.driver = d_info.get('DRIVER')
        gpus.append(gpu)

    res = Info()
    res.gpus = gpus
    return res
