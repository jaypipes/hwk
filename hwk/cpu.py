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
    cores = 0
    threads = 0
    cpu_info = open('/proc/cpuinfo', 'rb').readlines()
    for line in cpu_info:
        if line.strip() == '':
            continue
        key, value = line.split(':')
        key = key.strip()
        if key == 'cpu cores':
            cores = int(value.strip())
        if key == 'siblings':
            threads = int(value.strip())

    res = Info()
    res.total_cores = cores
    res.total_threads = threads
    return res
