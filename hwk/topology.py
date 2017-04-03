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

from hwk import utils

_LINUX_SYS_DEVICES_SYSTEM_NODE_DIR = '/sys/devices/system/node/'
_INFO_HELP = """Topology information
===============================================================================
`hwk.topology.Info` attributes:

architecture (string)

  A string indicating the overall architecture of the system topology (e.g.
  'NUMA' or 'SMP')
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

    def __repr__(self):
        return "Node %d" % (
            self.id,
        )


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
            node = Node(filename[4:])
            nodes.append(node)

    res = Info()
    res.architecture = 'NUMA' if len(nodes) > 1 else 'SMP'
    res.nodes = nodes
    return res
