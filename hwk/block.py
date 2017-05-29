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
import subprocess
import sys

from hwk import udev
from hwk import units
from hwk import utils


_SECTOR_SIZE = 512
_LINUX_SYS_BLOCK_DIR = '/sys/block/'
_LINUX_SYS_CLASS_BLOCK_DIR = '/sys/class/block/'
_INFO_HELP = """Block device subsystem
===============================================================================
`hwk.block.Info` attributes:

total_size_bytes (int)

  Number of bytes of physical disk storage available to the system

disks (list of `hwk.block.Disk` objects)

  A list of objects describing disk block devices that the host system knows
  about

  `hwk.block.Device` attributes:

  name (string)

    The name of the disk provided by the system, e.g. '/dev/sda'

  size_bytes (int)

    Storage capacity of the disk

  bus_type (string)

    'IDE' or 'SCSI'

  vendor (string)

    Device vendor, if known

  serial_no (string)

    Serial number of the device, if known

  partitions (list of `hwk.block.Partition` objects)

    A list of partitions on this particular block device

partitions (list of `hwk.block.Partition` objects)

  A list of objects describing partitions on disks that the host system knows
  about.

  `hwk.block.Partition` attributes:

  disk (`hwk.block.Disk` object)

    The disk object that the partition belongs to

  name (string)

    The name of the partition provided by the system, e.g. '/dev/sda1'

  size_bytes (int)

    Storage capacity of the partition

  type (string)

    A string indicating the filesystem format/type of the partition, e.g.
    'swap' or 'ext4'

  mount_point (string)

    Indicates where, if any, the partition is mounted in the system

  uuid (string)

    Optional string identifier for the partition. Can be either a UUID or a
    shorter identifier for older partition types (like MS-DOS)

  label (string)

    Optional string label for the partition

  is_readonly (bool)

    True if the partition is marked read-only
"""


class Info(object):
    """Object describing the block device information about a system."""

    def __init__(self):
        self.total_size_bytes = None
        self.disks = []

    def __repr__(self):
        tsb = 'unknown'
        if self.total_size_bytes is not None:
            tsb = math.floor(self.total_size_bytes / units.MB)
            tsb = str(tsb) + ' MB'
        return "block (%d disk block devices, %s total size)" % (
            len(self.disks),
            tsb,
        )

    def describe(self):
        return _INFO_HELP


class Disk(object):
    """Object describing a disk block device."""

    def __init__(self, name, size_bytes=None, bus_type=None, vendor=None,
                 serial_no=None):
        self.name = name
        self.size_bytes = size_bytes
        self.bus_type = bus_type
        self.vendor = vendor
        self.serial_no = serial_no
        self.partitions = []

    def __repr__(self):
        vendor_str = ''
        if self.vendor is not None:
            vendor_str = ' ' + self.vendor
        serial_str = ''
        if self.serial_no is not None:
            serial_str = ' - SN #' + self.serial_no
        return "/dev/%s (%d MB) [%s]%s%s" % (
            self.name,
            math.floor((self.size_bytes or 0) / units.MB),
            self.bus_type,
            vendor_str,
            serial_str,
        )


class Partition(object):
    """Object describing a partition of a disk block device."""

    def __init__(self, disk, name=None, label=None, uuid=None, size_bytes=None,
                 type=None, is_readonly=None, mount_point=None):
        self.disk = disk
        self.name = name
        self.uuid = uuid
        self.label = label
        self.mount_point = mount_point
        self.size_bytes = size_bytes
        self.type = type
        self.is_readonly = is_readonly

    def __repr__(self):
        type_str = ''
        if self.type is not None:
            type_str = " [" + self.type + "]"
        mount_str = ''
        if self.mount_point is not None:
            mount_str = ' mounted@' + self.mount_point
        uuid_str = ''
        if self.uuid is not None:
            uuid_str = ' - ' + self.uuid
        return "/dev/%s (%d MB) [%s]%s%s" % (
            self.name,
            math.floor((self.size_bytes or 0) / units.MB),
            type_str,
            mount_str,
            uuid_str,
        )


def disks():
    """Returns a list of `hwk.block.Disk` objects that describe all disk devices
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
    # filesystem and the udev database instead.
    res = []
    for filename in os.listdir(_LINUX_SYS_BLOCK_DIR):
        # Hard drives start with an 's' or an 'h' (for SCSI and IDE) followed
        # by a 'd'
        if not (filename[0] in ('s', 'h') and filename[1] == 'd'):
            continue

        bus_type = 'SCSI' if filename[0] == 's' else 'IDE'
        size_bytes = _linux_disk_size_bytes(filename)

        udev_path = _LINUX_SYS_CLASS_BLOCK_DIR + filename
        d_info = udev.device_properties(udev_path)

        d = Disk(name=filename, bus_type=bus_type, size_bytes=size_bytes)
        d.vendor = d_info.get('ID_VENDOR')
        d.serial_no = d_info.get('ID_SERIAL')

        d.partitions = _linux_partitions_on_disk(d)

        res.append(d)

    return res


def _linux_partitions_on_disk(disk):
    res = []
    dev_name = disk.name
    disk_dir = _LINUX_SYS_BLOCK_DIR + dev_name
    for filename in os.listdir(disk_dir):
        if not filename.startswith(dev_name):
            continue

        udev_path = _LINUX_SYS_CLASS_BLOCK_DIR + filename
        d_info = udev.device_properties(udev_path)

        p = Partition(disk, name=filename)
        p.type = d_info.get('ID_FS_TYPE')
        p.label = d_info.get('ID_FS_LABEL')
        p.uuid = d_info.get('ID_FS_UUID')
        p.mount_point = _linux_partition_mount_point(filename)
        p.size_bytes = _linux_partition_size_bytes(filename)
        res.append(p)
    return res


def _linux_partition_mount_point(part_name):
    """Given a partition name, returns the mount point for the partition, or
    None if not mounted.
    """
    if not part_name.startswith('/dev'):
        part_name = '/dev/' + part_name
    cmd = ['findmnt', part_name, '--noheadings', '--output', 'TARGET']
    try:
        out = subprocess.check_output(cmd)
        return out.strip()
    except subprocess.CalledProcessError:
        # Not mounted...
        return None


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


def _linux_partition_size_bytes(part_name):
    # In Linux, we could use the fdisk, lshw or blockdev commands to grab disk
    # size information, however all of these utilities require root privileges
    # to run. We can instead find the number of 512-byte sectors for disk
    # disks by examining the contents of /sys/block/$DEVICE/$PARTITION/size and
    # calculate the physical bytes accordingly.
    if part_name.startswith('/dev'):
        part_name = part_name[5:]  # Strip the /dev/
    disk_name = part_name[0:3]
    path = os.path.join(_LINUX_SYS_BLOCK_DIR, disk_name, part_name, 'size')
    if os.path.exists(path):
        return int(open(path, 'rb').read()) * _SECTOR_SIZE
    return 0


def _linux_disk_size_bytes(disk_name):
    # In Linux, we could use the fdisk, lshw or blockdev commands to grab disk
    # size information, however all of these utilities require root privileges
    # to run. We can instead find the number of 512-byte sectors for disk
    # disks by examining the contents of /sys/block/$DEVICE/size and
    # calculate the physical bytes accordingly.
    path = os.path.join(_LINUX_SYS_BLOCK_DIR, disk_name, 'size')
    if os.path.exists(path):
        return int(open(path, 'rb').read()) * _SECTOR_SIZE
    return 0


def total_size_bytes():
    """Returns the total physical storage capacity of attached disks in bytes
    or None if the information could not be determined.
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
    """Returns a `hwk.block.Info` object containing information on the disk
    block devices available to the system, or None if the information could not
    be determined.
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
