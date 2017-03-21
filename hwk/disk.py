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

# Information from the following sources was used in this module:
# - http://www.tldp.org/HOWTO/Partition-Mass-Storage-Definitions-Naming-HOWTO/x99.html
# - https://www.debian.org/releases/wheezy/amd64/apcs04.html.en

import math
import gzip
import os
import re
import sys

from hwk import utils


_SECTOR_SIZE = 512
_MB = 1024 * 1024
_LINUX_SYS_BLOCK_DIR = '/sys/block'
_INFO_HELP = """Disk subsystem
===============================================================================
`hwk.disk.Info` attributes:

total_size_bytes (int)

  Number of bytes of physical disk storage available to the system

disks (list of `hwk.disk.Disk` objects)

  A list of objects describing disks that the host system knows about
"""


class Info(object):
    """Object describing the memory information about a system."""

    def __init__(self):
        self.total_size_bytes = None
        self.disks = []

    def __repr__(self):
        tsb = 'unknown'
        if self.total_size_bytes is not None:
            tsb = math.floor(self.total_size_bytes / _MB)
            tsb = str(tsb) + ' MB'
        return "disk (%d disks, %s total size)" % (len(self.disks), tsb)

    def describe(self):
        return _INFO_HELP


class Disk(object):
    """Object describing a hard disk."""

    def __init__(self, name, uuid=None, size_bytes=None, bus_type=None):
        self.name = name
        self.uuid = uuid
        self.size_bytes = size_bytes
        self.bus_type = bus_type

    def __repr__(self):
        uuid_str = ''
        if self.uuid is not None:
            uuid_str = ' - ' + self.uuid
        return "%s (%d MB) [%s]%s" % (
            self.name,
            math.floor((self.size_bytes or 0) / _MB),
            self.bus_type,
            uuid_str,
        )


def disks():
    """Returns a list of `hwk.disk.Disk` objects that describe all disk devices
    the host system knows about.
    """
    try:
        return {
            "linux2": _linux_disks,
        }[sys.platform]()
    except KeyError:
        return None


def _linux_disks():
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
        size_bytes = _linux_disk_size_bytes(filename)

        d = Disk(name=filename, bus_type=bus_type, size_bytes=size_bytes)
        res.append(d)

    return res


def disk_size_bytes(disk_name):
    """Returns the total physical storage capacity of specified disk in
    bytes or None if the information could not be determined.
    """
    try:
        return {
            "linux2": _linux_disk_size_bytes,
        }[sys.platform](disk_name)
    except KeyError:
        return None


def _linux_disk_size_bytes(disk_name):
    # In Linux, we could use the fdisk, lshw or blockdev commands to grab disk
    # size information, however all of these utilities require root privileges
    # to run. We can instead find the number of 512-byte sectors for disk
    # devices by examining the contents of /sys/block/$DEVICE/size and
    # calculate the physical bytes accordingly.
    path = os.path.join(_LINUX_SYS_BLOCK_DIR, disk_name, 'size')
    if os.path.exists(path):
        return int(open(path, 'rb').read()) * _SECTOR_SIZE
    return 0


def total_size_bytes():
    """Returns the total physical storage capacity of attached disks in
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
    return sum(d.size_bytes for d in _linux_disks())


def info():
    """Returns a `MemoryInfo` object containing information on the memory
    available to the system, or None if the information could not be
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
    res.disks = _linux_disks()
    return res
