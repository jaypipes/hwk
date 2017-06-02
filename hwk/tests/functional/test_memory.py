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

from hwk import memory

from hwk.tests.functional import base


class TestMemory(base.TestCase):

    def test_info(self):
        info = memory.info()
        tub = info.total_usable_bytes
        self.assertTrue(0 < tub)

    def test_total_physical_bytes(self):
        tpb = memory.total_physical_bytes()

        if tpb is not None:
            self.assertTrue(0 < tpb)

    def test_supported_page_sizes(self):
        page_sizes = memory.supported_page_sizes()
        self.assertTrue(0 < len(page_sizes))
