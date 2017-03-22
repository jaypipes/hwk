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

import math
import os
import sys

from hwk import units
from hwk import utils


_SECTOR_SIZE = 512
_LINUX_SYS_BLOCK_DIR = '/sys/block'
_INFO_HELP = """Block device subsystem
===============================================================================
`hwk.block.Info` attributes:

total_size_bytes (int)

  Number of bytes of physical disk storage available to the system

devices (list of `hwk.block.Device` objects)

  A list of objects describing block devices that the host system knows about.

  `hwk.block.Device` attributes:

  name (string)

    The name of the disk provided by the system, e.g. '/dev/sda1'

  size_bytes (int)

    Storage capacity of the disk

  bus_type (string)

    'IDE' or 'SCSI'
"""


class Info(object):
    """Object describing the block device information about a system."""

    def __init__(self):
        self.total_size_bytes = None
        self.devices = []

    def __repr__(self):
        tsb = 'unknown'
        if self.total_size_bytes is not None:
            tsb = math.floor(self.total_size_bytes / units.MB)
            tsb = str(tsb) + ' MB'
        return "block (%d block devices, %s total size)" % (len(self.devices), tsb)

    def describe(self):
        return _INFO_HELP


class Device(object):
    """Object describing a block device."""

    def __init__(self, name, size_bytes=None, bus_type=None):
        self.name = name
        self.size_bytes = size_bytes
        self.bus_type = bus_type

    def __repr__(self):
        return "%s (%d MB) [%s]" % (
            self.name,
            math.floor((self.size_bytes or 0) / units.MB),
            self.bus_type,
        )


def devices():
    """Returns a list of `hwk.block.Device` objects that describe all disk devices
    the host system knows about.
    """
    try:
        return {
            "linux2": _linux_devices,
        }[sys.platform]()
    except KeyError:
        return None


def _linux_devices():
    # In Linux, we could use the fdisk, lshw or blockdev commands to list disk
    # information, however all of these utilities require root privileges to
    # run. We can get all of this information by examining the /sys/block
    # filesystem instead.
    res = []
    for filename in os.listdir(_LINUX_SYS_BLOCK_DIR):
        # Hard drives start with an 's' or an 'h' (for SCSI and IDE) followed
        # by a 'd'
        if not (filename[0] in ('s', 'h') and filename[1] == 'd'):
            continue

        bus_type = 'SCSI' if filename[0] == 's' else 'IDE'
        size_bytes = _linux_device_size_bytes(filename)

        d = Device(name=filename, bus_type=bus_type, size_bytes=size_bytes)
        res.append(d)

    return res


def device_size_bytes(device_name):
    """Returns the total physical storage capacity of specified disk in
    bytes or None if the information could not be determined.
    """
    try:
        return {
            "linux2": _linux_device_size_bytes,
        }[sys.platform](device_name)
    except KeyError:
        return None


def _linux_device_size_bytes(device_name):
    # In Linux, we could use the fdisk, lshw or blockdev commands to grab disk
    # size information, however all of these utilities require root privileges
    # to run. We can instead find the number of 512-byte sectors for disk
    # devices by examining the contents of /sys/block/$DEVICE/size and
    # calculate the physical bytes accordingly.
    path = os.path.join(_LINUX_SYS_BLOCK_DIR, device_name, 'size')
    if os.path.exists(path):
        return int(open(path, 'rb').read()) * _SECTOR_SIZE
    return 0


def total_size_bytes():
    """Returns the total physical storage capacity of attached devices in
    bytes or None if the information could not be determined.
    """
    try:
        return {
            "linux2": _linux_total_size_bytes,
        }[sys.platform]()
    except KeyError:
        return None


@utils.memoize
def _linux_total_size_bytes():
    return sum(d.size_bytes for d in _linux_devices())


def info():
    """Returns a `hwk.block.Info` object containing information on the block
    devices available to the system, or None if the information could not be
    determined.
    """
    try:
        return {
            "linux2": _linux_info,
        }[sys.platform]()
    except KeyError:
        return None


def _linux_info():
    res = Info()
    res.total_size_bytes = _linux_total_size_bytes()
    res.devices = _linux_devices()
    return res
