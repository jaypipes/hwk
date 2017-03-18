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


def _linux_supported_page_sizes():
    # In Linux, /sys/kernel/mm/hugepages contains a directory per page size
    # supported by the kernel. The directory name corresponds to the pattern
    # 'hugepages-{pagesize}kb'
    hp_dir = '/sys/kernel/mm/hugepages'
    return set([int(parts.split('-')[1][0:-2]) for parts in os.listdir(hp_dir)
                if os.path.isdir(os.path.join(hp_dir, parts))])
