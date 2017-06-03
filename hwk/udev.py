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

import subprocess

import six


def device_properties(path):
    """Given a device path, e.g. '/sys/class/block/sda', returns a dict of
    properties for the device.
    """
    cmd = ['udevadm', 'info', '-q', 'property', path]
    try:
        out = subprocess.check_output(cmd)
    except subprocess.CalledProcessError:
        return {}

    # Output from udevadm info looks like the following:
    # $ udevadm info -q property /sys/class/block/sda
    # DEVLINKS=/dev/disk/by-id/wwn-0x600508e000000000f8253aac9a1abd0c ...
    # DEVNAME=/dev/sda
    # DEVPATH=/devices/pci0000:00/0000:00:07.0/...
    # DEVTYPE=disk
    # ID_BUS=scsi
    # ID_MODEL=Logical_Volume
    # ID_MODEL_ENC=Logical\x20Volume\x20\x20
    # ID_PART_TABLE_TYPE=dos
    # ID_PART_TABLE_UUID=0000ebf3
    # ID_PATH=pci-0000:04:00.0-scsi-0:1:0:0
    # ID_PATH_TAG=pci-0000_04_00_0-scsi-0_1_0_0
    # ID_REVISION=3000
    # ID_SCSI=1
    # ID_SERIAL=3600508e000000000f8253aac9a1abd0c
    # ID_SERIAL_SHORT=600508e000000000f8253aac9a1abd0c
    # ID_TYPE=disk
    # ID_VENDOR=LSI
    # ID_VENDOR_ENC=LSI\x20\x20\x20\x20\x20
    # ID_WWN=0x600508e000000000
    # ID_WWN_VENDOR_EXTENSION=0xf8253aac9a1abd0c
    # ID_WWN_WITH_EXTENSION=0x600508e000000000f8253aac9a1abd0c
    # MAJOR=8
    # MINOR=0
    # SUBSYSTEM=block
    # TAGS=:systemd:
    # USEC_INITIALIZED=10219204
    res = {}
    for line in six.text_type(out.strip()).split('\n'):
        parts = line.split('=', 1)
        if len(parts) != 2:
            continue
        key = parts[0]
        val = parts[1]
        res[key] = val
    return res
