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
from papi.data.DCore import DCore


class TestCore(unittest.TestCase):

    def setUp(self):
        self.dcore = DCore()
        pass

    def test_add_susbcribers(self):

        dbl = DBlock(None, 1,5)
        dbl.id = 1

        dpl_1 = DPlugin()
        dpl_1.id = 2
        dpl_2 = DPlugin()
        dpl_2.id = 3

        self.assertTrue(dbl.add_subscribers(dpl_1))
        self.assertTrue(dbl.add_subscribers(dpl_2))

        self.assertEqual(len(dbl.get_subscribers().keys()),2)

    def test_rm_subscribers(self):
        dbl = DBlock(None, 1,5)
        dbl.id = 1

        dpl_1 = DPlugin()
        dpl_1.id = 2
        dpl_2 = DPlugin()
        dpl_2.id = 3

        dbl.add_subscribers(dpl_1)
        dbl.add_subscribers(dpl_2)

        self.assertEqual(len(dbl.get_subscribers().keys()),2)

        dbl.rm_subscribers(dpl_1)

        self.assertEqual(len(dbl.get_subscribers().keys()),1)

        dbl.rm_subscribers(dpl_2)

        self.assertEqual(len(dbl.get_subscribers().keys()),0)

        self.assertFalse(dbl.rm_subscribers(dpl_1))


