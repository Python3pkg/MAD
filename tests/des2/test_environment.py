#!/usr/bin/env python

#
# This file is part of MAD.
#
# MAD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MAD.  If not, see <http://www.gnu.org/licenses/>.
#

from unittest import TestCase

from mad.des2.environment import Environment


class EnvironmentTest(TestCase):

    def test_look_up_bindings_in_parent(self):
        env1 = Environment()
        env1.define("my_var", 4)
        env2 = env1.create_local_environment()
        env3 = env2.create_local_environment()

        self.assertEqual(env3.look_up("my_var"), 4)

    def test_look_up_a_missing_binding(self):
        env1 = Environment()
        env1.define("var1", 5)
        self.assertIsNone(env1.look_up("missing_symbol"))

    def test_look_up_masked_bindings(self):
        env1 = Environment()
        env1.define("my_var", 8)
        env2 = env1.create_local_environment()
        env2.define("my_var", 7)
        env3 = env2.create_local_environment()
        env3.define("my_var", 6)

        self.assertEqual(env1.look_up("my_var"), 8)
        self.assertEqual(env2.look_up("my_var"), 7)
        self.assertEqual(env3.look_up("my_var"), 6)

    # Test creating an environment that is not a child of another environment