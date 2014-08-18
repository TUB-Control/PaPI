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

        dbl_1 = DBlock(dpl_2,1,5)
        dbl_1.id = 3
        dbl_2 = DBlock(dpl_2,1,5)
        dbl_2.id = 4

        #Check: subscribe DBlocks
        self.assertTrue(dpl_1.subscribe(dbl_1))
        self.assertTrue(dpl_1.subscribe(dbl_2))

        self.assertFalse(dpl_1.subscribe(dbl_1))
        self.assertFalse(dpl_1.subscribe(dbl_2))

        #Check: count of subscribtions
        self.assertEqual(len(dpl_1.get_subscribtions().keys()), 2)
        #Check: count of subscribers
        self.assertEqual(len(dbl_1.get_subscribers().keys()), 1)
        self.assertEqual(len(dbl_1.get_subscribers().keys()),1)

        #Check: unsubscribe DBlock
        self.assertTrue(dpl_1.unsubscribe(dbl_1))

        #Check: count of subscribtions
        self.assertEqual(len(dpl_1.get_subscribtions().keys()), 1)
        #Check: count of subscribers
        self.assertEqual(len(dbl_1.get_subscribers().keys()), 0)
        self.assertEqual(len(dbl_2.get_subscribers().keys()), 1)


        pass

    def test_parameters(self):
        dpl_1 = DPlugin()
        dpl_1.id = 1

        dp_1 = DParameter(1)
        dp_1.id = 2
        dp_2 = DParameter(2)
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

        dbl_1 = DBlock(dpl_1, 1, 5, 'Block1')

        dbl_2 = DBlock(dpl_1, 1, 5, 'Block2')

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