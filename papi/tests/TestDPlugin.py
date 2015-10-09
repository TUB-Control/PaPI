#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""



import unittest

from papi.data.DPlugin import DPlugin, DBlock
from papi.data.DParameter import DParameter


class TestDPlugin(unittest.TestCase):

    def setUp(self):
        pass

    def test_subscribtions(self):
        dpl_1 = DPlugin()
        dpl_1.id = 1
        dpl_2 = DPlugin()
        dpl_2.id = 2

        dbl_1 = DBlock('DBlock1')
        dbl_1.id = 3
        dbl_1.dplugin_id = dpl_2.id

        dbl_2 = DBlock('DBlock2')
        dbl_2.id = 4
        dbl_2.dplugin_id = dpl_2.id

        dpl_2.add_dblock(dbl_1)
        dpl_2.add_dblock(dbl_2)

        #Check: subscribe DBlocks
        self.assertTrue(dpl_1.subscribe(dbl_1))
        self.assertTrue(dpl_1.subscribe(dbl_2))

        self.assertFalse(dpl_1.subscribe(dbl_1))
        self.assertFalse(dpl_1.subscribe(dbl_2))

        #Check: count of subscribtions
        self.assertEqual(len(dpl_1.get_subscribtions()[dpl_2.id].keys()), 2)

        #Check: unsubscribe DBlock
        self.assertTrue(dpl_1.unsubscribe(dbl_1))

        #Check: count of subscribtions
        self.assertEqual(len(dpl_1.get_subscribtions().keys()), 1)
        #Check: count of subscribtions
        self.assertEqual(len(dpl_1.get_subscribtions()[dpl_2.id].keys()), 1)

    def test_parameters(self):
        dpl_1 = DPlugin()
        dpl_1.id = 1

        dp_1 = DParameter(1, 'parameter1')
        dp_1.id = 2
        dp_2 = DParameter(2, 'parameter2')
        dp_2.id = 3

        #check: add Parameter
        self.assertTrue(dpl_1.add_parameter(dp_1))
        self.assertTrue(dpl_1.add_parameter(dp_2))

        self.assertFalse(dpl_1.add_parameter(dp_1))
        self.assertFalse(dpl_1.add_parameter(dp_2))

        #Check: count of parameters

        self.assertEqual(len(dpl_1.get_parameters().keys()), 2)

        #Check: rm parameter

        self.assertTrue(dpl_1.rm_parameter(dp_1))
        self.assertEqual(len(dpl_1.get_parameters().keys()), 1)
        self.assertTrue(dpl_1.rm_parameter(dp_2))
        self.assertEqual(len(dpl_1.get_parameters().keys()), 0)

    def test_dblocks(self):
        dpl_1 = DPlugin()
        dpl_1.id = 1

        dbl_1 = DBlock('Block1')
        dbl_1.dplugin_id = dpl_1.id

        dbl_2 = DBlock('Block2')
        dbl_2.dplugin_id = dpl_1.id

        #check: add Parameter
        self.assertTrue(dpl_1.add_dblock(dbl_1))
        self.assertTrue(dpl_1.add_dblock(dbl_2))

        self.assertFalse(dpl_1.add_dblock(dbl_1))
        self.assertFalse(dpl_1.add_dblock(dbl_2))

        #Check: count of parameters

        self.assertEqual(len(dpl_1.get_dblocks().keys()), 2)

        #Check: rm parameter

        self.assertTrue(dpl_1.rm_dblock(dbl_1))
        self.assertEqual(len(dpl_1.get_dblocks().keys()), 1)
        self.assertTrue(dpl_1.rm_dblock(dbl_2))
        self.assertEqual(len(dpl_1.get_dblocks().keys()), 0)

if __name__ == "__main__":
    unittest.main();