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

from hwk import cpu

from hwk.tests.functional import base


class TestCPU(base.TestCase):

    def test_info(self):
        info = cpu.info()
        tc = info.total_cores
        self.assertTrue(0 < tc)

    def test_cpus(self):
        info = cpu.info()
        cpus = info.cpus

        self.assertTrue(0 < len(cpus))

        for c in cpus:
            cores = c.cores
            self.assertTrue(0 < cores)

            threads = c.threads
            self.assertTrue(cores <= threads)

            v = c.vendor
            self.assertIsNotNone(v)

            m = c.model
            self.assertIsNotNone(m)

            fs = c.features
            self.assertTrue(0 < len(fs))

    def test_total_cores(self):
        tc = cpu.total_cores()
        self.assertTrue(0 < tc)

    def test_total_threads(self):
        tc = cpu.total_threads()
        self.assertTrue(0 < tc)
