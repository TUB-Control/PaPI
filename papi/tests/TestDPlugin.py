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
from papi.data.DCore import DPlugin


class TestDPlugin(unittest.TestCase):

    def setUp(self):
        pass

    def test_add_subscriber(self):

        dp_1 = DPlugin()
        dp_2 = DPlugin()
        dp_1.id = 1
        dp_2.id = 2

        self.assertEqual(len(dp_1.get_subscribers().keys()), 0)
        dp_1.add_subscriber(dp_2)
        self.assertEqual(len(dp_1.get_subscribers().keys()), 1)

    def test_subscribe(self):
        pass

    def test_rm_subscriber(self):

        dp_1 = DPlugin()
        dp_2 = DPlugin()
        dp_1.id = 1
        dp_2.id = 2

        dp_1.add_subscriber(dp_2)

        dp_2.add_subscriber(dp_1)

        self.assertEqual(len(dp_1.get_subscribers().keys()),1)
        self.assertEqual(len(dp_2.get_subcribtions().keys()),1)

        dp_1.rm_subscriber(dp_2)

        self.assertEqual(len(dp_1.get_subscribers().keys()),0)
        self.assertEqual(len(dp_2.get_subcribtions().keys()),0)

        self.assertEqual(len(dp_2.get_subscribers().keys()),1)
        self.assertEqual(len(dp_1.get_subcribtions().keys()),1)

    def test_unsubscribe(self):
        pass



if __name__ == "__main__":
    unittest.main();