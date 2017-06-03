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

from hwk import net

from hwk.tests.functional import base


class TestNet(base.TestCase):

    def test_info(self):
        info = net.info()
        nics = info.nics

        for nic in nics:
            self.assertTrue(0 < len(nic.name))

    def test_nic_features(self):

        info = net.info()
        for nic in nics:
            all_f, enabled_f = net.nic_features(nic.name)
            self.assertTrue(0 < len(all_f))
            self.assertTrue(len(enabled_f) < len(all_f))
