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

from hwk import utils


_INFO_HELP = """CPU subsystem
===============================================================================
`hwk.cpu.Info` attributes:

total_cores (int)

  Number of physical CPU cores, not including hardware threads

total_threads (int)

  Number of physical CPU threads

cpus (list of `hwk.cpu.CPU` objects)

  A list of objects describing the physical CPUs

  `hwk.cpu.CPU` attributes:

  id (int)

    0-based index of the processor, according to the system

  cores (int)

    Number of physical cores on the CPU

  threads (int)

    Number of hardware threads on the CPU

  model (string)

    String describing the processor model, if known

  vendor (string)

    The processor vendor, if known

  processor_map (dict)

    A mapping of each of this CPU's cores to a set of system processor IDs.

    For example, assume a system has 2 CPUs, each with 4 cores and each core
    has 2 hardware threads. The total number of processors in the system would
    equal 2 x 4 x 2 = 16. Now, let's also assume that the system sees the
    processors 4-7 and 12-15 belonging to the cores on the second CPU, the
    processor_map might look like the following:
    
        {
            0: set([4, 5]),
            1: set([6, 7]),
            2: set([12, 13]),
            3: set([14, 15]),
        }
"""


class Info(object):
    """Object describing the CPU information about a system."""

    def __init__(self):
        self.total_cores = None
        self.total_threads = None
        self.cpus = []

    def __repr__(self):
        return "cpu (%d physical packages, %s cores, %s hardware threads)" % (
            len(self.cpus),
            self.total_cores,
            self.total_threads,
        )

    def describe(self):
        return _INFO_HELP


class CPU(object):

    def __init__(self, proc_id):
        self.cores = None
        self.threads = None
        self.model = None
        self.vendor = None
        self.id = int(proc_id)

    def __repr__(self):
        cores_str = 'unknown #'
        if self.cores is not None:
            cores_str = str(self.cores)
        threads_str = 'unknown #'
        if self.threads is not None:
            threads_str = str(self.threads)
        model_str = ''
        if self.model is not None:
            model_str = '[' + self.model.strip() + ']'
        return "processor %d (%s cores, %s threads)%s" % (
            self.id,
            cores_str,
            threads_str,
            model_str,
        )


def total_cores():
    """Returns the total physical cores or None if the information could not be
    determined.
    """
    try:
        return {
            "linux2": _linux_total_cores,
        }[sys.platform]()
    except KeyError:
        return None


def _linux_total_cores():
    i = info()
    return i.total_cores


def total_threads():
    """Returns the total hardware threads or None if the information could not
    be determined.
    """
    try:
        return {
            "linux2": _linux_total_threads,
        }[sys.platform]()
    except KeyError:
        return None


def _linux_total_threads():
    i = info()
    return i.total_threads


def info():
    """Returns a `hwk.cpu.Info` object containing information on the CPU
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
    cpu_info = open('/proc/cpuinfo', 'rb').readlines()
    cpu_attrs = []
    cur_cpu_attrs = {}
    for line in cpu_info:
        if line.strip() == '':
            cpu_attrs.append(cur_cpu_attrs)
            cur_cpu_attrs = {}
            continue
        key, value = line.split(':')
        key = key.strip()
        cur_cpu_attrs[key] = value

    # Group all processor attrs by physical id, which signifies physical CPU
    cpu_ids = set(c['physical id'] for c in cpu_attrs)
    cpus = []
    for cpu_id in cpu_ids:
        cpu = CPU(cpu_id)
        procs_in_cpu = [c for c in cpu_attrs if c['physical id'] == cpu_id]
        first = procs_in_cpu[0]
        cpu.model = first['model name']
        cpu.vendor = first['vendor_id']
        cpu.cores = int(first['cpu cores'])
        cpu.threads = int(first['siblings'])
        core_ids = set(c['core id'] for c in procs_in_cpu)
        
        # OK, so this looks exceedingly weird, but what we're doing here is
        # finding the zero-based index of the core within the physical
        # package/socket. Turns out that certain vendors return a "core id"
        # value that doesn't align with a zero-based sequential array (looking
        # at you, Intel i7, which returns the core ids {0, 1, 2, 8, 9, 10} for
        # its six cores). So, here we create a map of the core id returned by
        # /proc/cpuinfo to the zero-based index of the core within the physical
        # socket. We determine the zero-based index by examining the processor
        # #s associated with the cores, order them and tie the ordered list
        # index back to the core id.
        ordered_core_ids = [
            c['core id'] for c in procs_in_cpu
        ]
        core_id_index = {
            core_id: ordered_core_ids.index(core_id)
            for core_id in core_ids
        }
        pmap = {
            core_id_index[core_id]: set(
                int(c['processor']) for c in procs_in_cpu
                if c['core id'] == core_id
            ) for core_id in core_ids
        }
        cpu.processor_map = pmap
        cpus.append(cpu)

    res = Info()
    res.total_cores = sum(c.cores for c in cpus)
    res.total_threads = sum(c.threads for c in cpus)
    res.cpus = cpus
    return res
