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
import sys

from hwk import cpu
from hwk import utils

_LINUX_SYS_DEVICES_SYSTEM_NODE_DIR = '/sys/devices/system/node/'
_INFO_HELP = """Topology information
===============================================================================
`hwk.topology.Info` attributes:

architecture (string)

  A string indicating the overall architecture of the system topology (e.g.
  'NUMA' or 'SMP')

nodes (list of `hwk.topology.Node` objects)

  A list of objects representing one or more processors, memory banks (caches)
  and the bus/interconnect between them.

  `hwk.topology.Node` attributes:

  id (int)

    0-based index of the node within the system

  processor_set (set of int)

    A set of integers representing the logical processors that are associated
    with this node. For example, assume a dual Intel® Xeon® Processor E5-4650
    v2 system. Each E5-4650 processor has 10 cores with 2 hardware threads per
    core, giving 40 total logical processors in the system.  Suppose the system
    reported the second Xeon processor's (NUMA node) cores (and their thread
    siblings) as logical processors 10-19 and 31-39, the value of processor_set
    would be set([10,11,12,13,14,15,16,17,18,19,31,32,33,34,35,36,37,38,39]).
"""


class Info(object):
    """Object describing the physical topology of a system."""

    def __init__(self):
        self.architecture = None
        self.nodes = None

    def __repr__(self):
        return "topology %s (%d nodes)" % (
            self.architecture,
            len(self.nodes),
        )

    def describe(self):
        return _INFO_HELP


class Node(object):

    def __init__(self, node_id):
        self.id = int(node_id)
        self.processor_set = set()

    def __repr__(self):
        return "Node %d" % (
            self.id,
        )


def node_processor_set(node_id):
    """Returns a set of ints representing the logical processor IDs associated
    with the supplied NUMA node.
    """
    try:
        return {
            "linux2": _linux_node_processor_set,
        }[sys.platform](node_id)
    except KeyError:
        return None


@utils.memoize
def _linux_node_processor_set(node_id):
    # The /sys/devices/node/nodeX/cpumask file contains a hexadecimal string
    # that indicates which of the logical processors on the system are
    # associated with node X
    path = os.path.join(
        _LINUX_SYS_DEVICES_SYSTEM_NODE_DIR,
        'node' + str(node_id),
        'cpumap',
    )
    cpumap = utils.hextoi(open(path, 'rb').read())
    num_cpus = cpu.total_threads()
    return set(x for x in range(num_cpus) if cpumap & (1 << x))


def info():
    """Returns a `hwk.topology.Info` object containing information on the
    physical topology in the system, or None if the information could not be
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
    nodes = []
    for filename in os.listdir(_LINUX_SYS_DEVICES_SYSTEM_NODE_DIR):
        if filename.startswith('node'):
            node_id = filename[4:]
            node = Node(node_id)
            node.processor_set = _linux_node_processor_set(node_id)
            nodes.append(node)

    res = Info()
    res.architecture = 'NUMA' if len(nodes) > 1 else 'SMP'
    res.nodes = nodes
    return res
