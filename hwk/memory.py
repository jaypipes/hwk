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
import gzip
import os
import re
import sys

from hwk import utils


_INFO_HELP = """Memory subsystem
===============================================================================
`hwk.memory.Info` attributes:

total_physical_bytes (int)

  Number of bytes of physical RAM available to the system

total_usable_bytes (int)

  Number of bytes usable by the system (physical bytes minus a few bits
  reserved for system and the resident kernel size)

supported_page_sizes (set of int)

  A set of ints indicating memory page sizes the system can utilize, in bytes
"""


class Info(object):
    """Object describing the memory information about a system."""

    def __init__(self):
        self.total_physical_bytes = None
        self.total_usable_bytes = None
        self.supported_page_sizes = None

    def __repr__(self):
        tpb = 'unknown'
        if self.total_physical_bytes is not None:
            tpb = math.floor(self.total_physical_bytes / (1024 * 1024))
            tpb = str(tpb) + ' MB'
        tub = 'unknown'
        if self.total_usable_bytes is not None:
            tub = math.floor(self.total_usable_bytes / (1024 * 1024))
            tub = str(tub) + ' MB'
        return "memory (%s physical, %s usable)" % (tpb, tub)

    def describe(self):
        return _INFO_HELP


def supported_page_sizes():
    """Returns a set() containing the memory page sizes, in KB, supported by
    the host, or None if the page sizes could not be determined.
    """
    try:
        return {
            "linux2": _linux_supported_page_sizes,
        }[sys.platform]()
    except KeyError:
        return None


@utils.memoize
def _linux_supported_page_sizes():
    # In Linux, /sys/kernel/mm/hugepages contains a directory per page size
    # supported by the kernel. The directory name corresponds to the pattern
    # 'hugepages-{pagesize}kb'
    hp_dir = '/sys/kernel/mm/hugepages'
    return set([int(parts.split('-')[1][0:-2]) for parts in os.listdir(hp_dir)
                if os.path.isdir(os.path.join(hp_dir, parts))])


def total_physical_bytes():
    """Returns the total physical memory in bytes or None if the information
    could not be determined.
    """
    try:
        return {
            "linux2": _linux_total_physical_bytes,
        }[sys.platform]()
    except KeyError:
        return None


# System log lines will look similar to the following:
# ... kernel: [0.000000] Memory: 24633272K/25155024K ...
_SYSLOG_MEM_LINE_RE = re.compile(r'Memory:\s+\d+K\/(\d+)K')

@utils.memoize
def _linux_total_physical_bytes():
    # In Linux, the total physical memory can be determined by looking at the
    # output of dmidecode, however dmidecode requires root privileges to run,
    # so instead we examine the system logs for startup information containing
    # total physical memory and cache the results of this.
    def _find_physical_kb(line):
        matched = _SYSLOG_MEM_LINE_RE.search(line)
        if matched:
            return int(matched.group(1)) * 1024
        return None

    log_dir = '/var/log'
    log_files = sorted([
        filename for filename in os.listdir(log_dir)
        # /var/log will contain a file called syslog and 0 or more files called
        # syslog.$NUMBER or syslog.$NUMBER.gz containing system log records. We
        # search each, stopping when we match a system log record line that
        # contains physical memory information.
        if filename.startswith('syslog')
    ])

    for filename in log_files:
        unzip = filename.endswith('.gz')
        if unzip:
            opener = gzip.open
        else:
            opener = open

        path = os.path.join(log_dir, filename)
        with opener(path, 'rb') as f:
            for line in f.readlines():
                size = _find_physical_kb(line)
                if size is not None:
                    return size
    return None


def info():
    """Returns a `hwk.memory.Info` object containing information on the memory
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
    # In Linux, /proc/meminfo contains a set of memory-related amounts, with
    # lines looking like the following:
    #
    # $ cat /proc/meminfo
    # MemTotal:       24677596 kB
    # MemFree:        21244356 kB
    # MemAvailable:   22085432 kB
    # ...
    # HugePages_Total:       0
    # HugePages_Free:        0
    # HugePages_Rsvd:        0
    # HugePages_Surp:        0
    # ...
    #
    # It's worth noting that /proc/meminfo returns exact information, not
    # "theoretical" information. For instance, on the above system, I have 24GB
    # of RAM but MemTotal is indicating only around 23GB. This is because
    # MemTotal contains the exact amount of *usable* memory after accounting
    # for the kernel's resident memory size and a few reserved bits. For more
    # information, see:
    #
    #  https://www.kernel.org/doc/Documentation/filesystems/proc.txt
    mem_filepath = '/proc/meminfo'
    meminfo_lines = open(mem_filepath, 'rb').readlines()
    values = {}
    for line in meminfo_lines:
        parts = line.split()
        key = parts[0].strip(': ')
        value = int(parts[1].strip())
        in_kb = (len(parts) == 3 and parts[2].strip() == 'kB')
        if in_kb:
            value = value * 1024
        values[key] = value

    res = Info()
    res.supported_page_sizes = _linux_supported_page_sizes()
    res.total_physical_bytes = _linux_total_physical_bytes()
    res.total_usable_bytes = values['MemTotal']
    return res
