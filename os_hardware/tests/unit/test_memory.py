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

import mock

from os_hardware import memory

from os_hardware.tests.unit import base


class TestMemory(base.TestCase):

    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.listdir')
    @mock.patch('sys.platform', 'linux2')
    def test_supported_page_sizes_linux(self, listdir_mock,
            is_dir_mock):
        listdir_mock.return_value = [
            'hugepages-2048kb',
            'hugepages-1048576kb',
        ]
        page_sizes = memory.supported_page_sizes()

        expected = set([2048, 1048576])
        self.assertEqual(expected, page_sizes)

        listdir_mock.assert_called_once_with('/sys/kernel/mm/hugepages')
