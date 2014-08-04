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
from papi.buffer.manager import Manager

__author__ = 'knuths'

import unittest

from multiprocessing import Array


class TestDBufferManager(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_array_size(self):

        array_1 = Manager.get_shared_array([[5, 100], [2, 1000]])
        array_2 = Manager.get_shared_array([[2, 10]])
        array_3 = Manager.get_shared_array([[2, 10], [3, 20], [4, 40]])

        # check length
        self.assertEqual(len(array_1), 25006)
        self.assertEqual(len(array_2), 203)
        self.assertEqual(len(array_3), 2409)
        # check attributes
        self.assertEqual(array_1[0], 100*10)
        self.assertEqual(array_1[1], 5)
        self.assertEqual(array_1[2], 0)
        self.assertEqual(array_1[5003], 1000*10)
        self.assertEqual(array_1[5004], 2)
        self.assertEqual(array_1[5005], 0)

        self.assertEqual(array_2[0], 10*10)
        self.assertEqual(array_2[1], 2)
        self.assertEqual(array_2[2], 0)

        self.assertEqual(array_3[0], 10*10)
        self.assertEqual(array_3[1], 2)
        self.assertEqual(array_3[2], 0)

        self.assertEqual(array_3[203], 20*10)
        self.assertEqual(array_3[204], 3)
        self.assertEqual(array_3[205], 0)

        self.assertEqual(array_3[806], 40*10)
        self.assertEqual(array_3[807], 4)
        self.assertEqual(array_3[808], 0)

    def test_init(self):

        array_1 = Manager.get_shared_array([[2, 10]])
        array_2 = Manager.get_shared_array([[5, 100],[2, 1000]])
        array_3 = Manager.get_shared_array([[2, 10], [3, 20], [4, 40]])
        array_4 = Manager.get_shared_array([[2, 10], [3, 20], [4, 40], [5, 50]])
        array_5 = Manager.get_shared_array([[2, 10], [3, 20], [4, 40], [5, 50], [2, 1000]])

        bm_1 = Manager(array_1)
        bm_2 = Manager(array_2)
        bm_3 = Manager(array_3)
        bm_4 = Manager(array_4)
        bm_5 = Manager(array_5)

        self.assertEqual(len(bm_1.get_all_groups().keys()), 1)
        self.assertEqual(len(bm_2.get_all_groups().keys()), 2)
        self.assertEqual(len(bm_3.get_all_groups().keys()), 3)
        self.assertEqual(len(bm_4.get_all_groups().keys()), 4)
        self.assertEqual(len(bm_5.get_all_groups().keys()), 5)

    def test_add_data(self):
        array_1 = Manager.get_shared_array([[2,1]])

        bm_1 = Manager(array_1)

        self.assertTrue(bm_1.add_data(1, [1, 1]))

        self.assertEqual(array_1[3],1)
        self.assertEqual(array_1[13],1)

        self.assertTrue(bm_1.add_data(1, [1, 2]))
        self.assertTrue(bm_1.add_data(1, [3, 4]))
        self.assertTrue(bm_1.add_data(1, [5, 6]))

        self.assertEqual(array_1[4], 1)
        self.assertEqual(array_1[14], 2)

        self.assertEqual(array_1[5], 3)
        self.assertEqual(array_1[15], 4)

        self.assertEqual(array_1[6], 5)
        self.assertEqual(array_1[16], 6)

        self.assertTrue(bm_1.add_data(1, [7, 8]))
        self.assertTrue(bm_1.add_data(1, [9, 10]))
        self.assertTrue(bm_1.add_data(1, [11, 12]))
        self.assertTrue(bm_1.add_data(1, [13, 14]))
        self.assertTrue(bm_1.add_data(1, [15, 16]))
        self.assertTrue(bm_1.add_data(1, [17, 18]))

        #Check if overflow works

        self.assertEqual(array_1[12], 17)
        self.assertEqual(array_1[22], 18)


        self.assertTrue(bm_1.add_data(1, [19, 20]))


        self.assertTrue(bm_1.add_data(1, [21, 22]))

        self.assertEqual(array_1[3], 19)
        self.assertEqual(array_1[13], 20)

        self.assertEqual(array_1[4], 21)
        self.assertEqual(array_1[14], 22)


