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
"""


class Info(object):
    """Object describing the CPU information about a system."""

    def __init__(self):
        self.total_cores = None
        self.total_threads = None

    def __repr__(self):
        return "cpu (%s cores, %s threads)" % (
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
        cpus.append(cpu)

    res = Info()
    res.total_cores = sum(c.cores for c in cpus)
    res.total_threads = sum(c.threads for c in cpus)
    res.cpus = cpus
    return res
