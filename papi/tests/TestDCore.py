#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""

__author__ = 'knuths'

import unittest

from papi.data.DCore import DCore
from papi.plugin.TestPL1 import TestPl1
from papi.data.DCore import DPlugin


class TestDCore(unittest.TestCase):

    def setUp(self):
        self.dcore = DCore()

    def test_add_pl_process(self):


        pl = None

        self.dcore.add_plugin(None, 1, None, None, pl, 10)
        self.dcore.add_plugin(None, 2, None, None, pl, 11)

        dp_1 = self.dcore.get_dplugin_by_id(10)

        self.assertTrue(isinstance(dp_1, DPlugin))

        self.assertEqual(dp_1.id, 10)
        dp_2 = self.dcore.get_dplugin_by_id(11)
        self.assertTrue(isinstance(dp_2, DPlugin))
        self.assertEqual(dp_2.id, 11)

        self.assertEqual(self.dcore.get_dplugins_count(),2)

        self.dcore.rm_dplugin(dp_1)

        self.assertEqual(self.dcore.get_dplugins_count(),1)

        self.assertTrue(isinstance(self.dcore.dbg_get_first_dplugin(),DPlugin))


    def test_add_subscriber(self):
        self.dcore.add_plugin(None, 1, None, None, None, 10)
        self.dcore.add_plugin(None, 1, None, None, None, 11)

        dp_1 = self.dcore.get_dplugin_by_id(10)
        dp_2 = self.dcore.get_dplugin_by_id(11)

        self.assertEqual(len(dp_1.get_subscribers().keys()), 0)
        dp_1.add_subscriber(dp_2)
        self.assertEqual(len(dp_1.get_subscribers().keys()), 1)

if __name__ == "__main__":
    unittest.main();