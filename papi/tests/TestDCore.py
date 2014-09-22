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
from papi.data.DCore import DPlugin, DBlock


class TestDCore(unittest.TestCase):

    def setUp(self):
        self.dcore = DCore()

    def test_create_id(self):
        id_1 = self.dcore.create_id()
        id_2 = self.dcore.create_id()

        self.assertNotEqual(id_1, id_2)

    def test_add_plugin(self):

        pl_id_1 = self.dcore.create_id()
        pl_id_2 = self.dcore.create_id()

        self.dcore.add_plugin(None, 1, None, None, None, pl_id_1)
        self.dcore.add_plugin(None, 2, None, None, None, pl_id_2)

        dp_1 = self.dcore.get_dplugin_by_id(pl_id_1)

        self.assertTrue(isinstance(dp_1, DPlugin))

        self.assertEqual(dp_1.id, pl_id_1)
        dp_2 = self.dcore.get_dplugin_by_id(pl_id_2)
        self.assertTrue(isinstance(dp_2, DPlugin))
        self.assertEqual(dp_2.id, pl_id_2)

        self.assertEqual(self.dcore.get_dplugins_count(), 2)

        self.assertTrue(self.dcore.rm_dplugin(dp_1.id))

        self.assertEqual(self.dcore.get_dplugins_count(), 1)

    def test_rm_dplugin(self):
        #Create dplugins
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_2 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        #Create dblocks
        d_bl_1 = DBlock(None, 0, 0, 'Block_1')
        d_bl_2 = DBlock(None, 0, 0, 'Block_2')

        #assign dblocks to DPlugin d_pl_1
        d_pl_1.add_dblock(d_bl_1)
        d_pl_1.add_dblock(d_bl_2)

        #create subscribtions

        self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_1.name)
        self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_2.name)

        self.assertEqual(len(d_pl_2.get_subscribtions()[d_pl_1.id]), 2)
        self.assertEqual(len(d_bl_1.get_subscribers()), 1)
        self.assertEqual(len(d_bl_2.get_subscribers()), 1)

        self.dcore.rm_dplugin(d_pl_1.id)

        #Check if DPlugin d_pl_1 is missing

        self.assertFalse(self.dcore.get_dplugin_by_id(d_pl_1.id))

        #Check if all subscribtions were canceled

        self.assertEqual(len(d_pl_2.get_subscribtions().keys()), 0)
        self.assertEqual(len(d_bl_1.get_subscribers()), 0)
        self.assertEqual(len(d_bl_2.get_subscribers()), 0)

        pass

    def test_get_dplugin_by_id(self):
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        self.dcore.get_dplugin_by_id(d_pl_1.id)
        self.assertEqual(d_pl_1.id, self.dcore.get_dplugin_by_id(d_pl_1.id).id)

    def test_get_dplugin_by_uname(self):
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_2 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_3 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        d_pl_1.uname = "Test1"
        d_pl_2.uname = "Test2"
        d_pl_3.uname = "Test3"

        self.assertEqual("Test1", self.dcore.get_dplugin_by_uname("Test1").uname)
        self.assertEqual("Test2", self.dcore.get_dplugin_by_uname("Test2").uname)
        self.assertEqual("Test3", self.dcore.get_dplugin_by_uname("Test3").uname)

        self.assertIsNone(self.dcore.get_dplugin_by_uname("Test4"))

    def test_get_all_plugins(self):
        self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        self.assertEqual(len(self.dcore.get_all_plugins().keys()), 4)

    def test_subscribe(self):
        #Create dplugins
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_2 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        #Create dblocks
        d_bl_1 = DBlock(None, 0, 0, 'Block_1')
        d_bl_2 = DBlock(None, 0, 0, 'Block_2')


        #assign dblocks to DPlugin d_pl_1
        d_pl_1.add_dblock(d_bl_1)
        d_pl_1.add_dblock(d_bl_2)

        self.assertTrue(self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_1.name))
        self.assertTrue(self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_2.name))


        self.assertTrue(d_pl_2.id in d_bl_1.get_subscribers())
        self.assertTrue(d_pl_2.id in d_bl_2.get_subscribers())


    def test_unsubscribe(self):
        #Create dplugins
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_2 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        #Create dblocks
        d_bl_1 = DBlock(None, 0, 0, 'Block_1')
        d_bl_2 = DBlock(None, 0, 0, 'Block_2')


        #assign dblocks to DPlugin d_pl_1
        d_pl_1.add_dblock(d_bl_1)
        d_pl_1.add_dblock(d_bl_2)

        self.assertTrue(self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_1.name))
        self.assertTrue(self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_2.name))

        self.dcore.unsubscribe(d_pl_2.id, d_pl_1.id, d_bl_1.name)
        self.dcore.unsubscribe(d_pl_2.id, d_pl_1.id, d_bl_2.name)

        self.assertFalse(d_pl_2.id in d_bl_1.get_subscribers())
        self.assertFalse(d_pl_2.id in d_bl_1.get_subscribers())
        self.assertEqual(len(d_bl_2.get_subscribers()),0)


    def test_unsubscribe_all(self):
        #Create dplugins
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_2 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        #Create dblocks
        d_bl_1 = DBlock(None, 0, 0, 'Block_1')
        d_bl_2 = DBlock(None, 0, 0, 'Block_2')

        #assign dblocks to DPlugin d_pl_1
        d_pl_1.add_dblock(d_bl_1)
        d_pl_1.add_dblock(d_bl_2)

        self.assertTrue(self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_1.name))
        self.assertTrue(self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_2.name))

        self.assertEqual(len(d_pl_2.get_subscribtions()[d_pl_1.id].keys()), 2)

        self.dcore.unsubscribe_all(d_pl_2.id)

        self.assertNotIn(d_pl_1.id, d_pl_2.get_subscribtions())

        pass

    def test_rm_all_subscribers(self):
        #Create dplugins
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_2 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_3 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        #Create dblocks
        d_bl_1 = DBlock(None, 0, 0, 'Block_1')
        d_bl_2 = DBlock(None, 0, 0, 'Block_2')

        #assign dblocks to DPlugin d_pl_1
        d_pl_1.add_dblock(d_bl_1)
        d_pl_1.add_dblock(d_bl_2)

        self.assertTrue(self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_1.name))
        self.assertTrue(self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_2.name))
        self.assertTrue(self.dcore.subscribe(d_pl_3.id, d_pl_1.id, d_bl_1.name))
        self.assertTrue(self.dcore.subscribe(d_pl_3.id, d_pl_1.id, d_bl_2.name))

        self.assertEqual(len(d_bl_1.get_subscribers()), 2)
        self.assertEqual(len(d_bl_2.get_subscribers()), 2)

        self.dcore.rm_all_subscribers(d_pl_1.id)

        self.assertEqual(len(d_bl_1.get_subscribers()), 0)
        self.assertEqual(len(d_bl_2.get_subscribers()), 0)

        pass

    def test_subscribe_signals(self):
        #Create dplugins
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_2 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_3 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        #Create dblocks
        d_bl_1 = DBlock(None, 0, 0, 'Block1')
        d_bl_2 = DBlock(None, 0, 0, 'Block2')

        #assign dblocks to DPlugin d_pl_1
        d_pl_1.add_dblock(d_bl_1)
        d_pl_1.add_dblock(d_bl_2)

        self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_1.name)
        self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_2.name)
        self.dcore.subscribe(d_pl_3.id, d_pl_1.id, d_bl_1.name)
        self.dcore.subscribe(d_pl_3.id, d_pl_1.id, d_bl_2.name)


        self.assertTrue(self.dcore.subscribe_signals(d_pl_2.id, d_pl_1.id, d_bl_1.name, [1, 2, 3]))

        self.assertTrue(self.dcore.subscribe_signals(d_pl_2.id, d_pl_1.id, d_bl_2.name, [6, 4, 5]))

        self.assertTrue(self.dcore.subscribe_signals(d_pl_3.id, d_pl_1.id, d_bl_1.name, [9]))

        self.assertTrue(self.dcore.subscribe_signals(d_pl_3.id, d_pl_1.id, d_bl_2.name, [17,19,18]))


        subscription = d_pl_2.get_subscribtions()[d_pl_1.id][d_bl_1.name]

        self.assertIn(1, subscription.get_signals())
        self.assertIn(2, subscription.get_signals())
        self.assertIn(3, subscription.get_signals())

        subscription = d_pl_3.get_subscribtions()[d_pl_1.id][d_bl_2.name]

        self.assertIn(19, subscription.get_signals())
        self.assertIn(17, subscription.get_signals())
        self.assertIn(18, subscription.get_signals())

        subscription = d_pl_3.get_subscribtions()[d_pl_1.id][d_bl_1.name]

        self.assertIn(9, subscription.get_signals())


    def test_unsubscribe_signals(self):
        #Create dplugins
        d_pl_1 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_2 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())
        d_pl_3 = self.dcore.add_plugin(None, 1, None, None, None, self.dcore.create_id())

        #Create dblocks
        d_bl_1 = DBlock(None, 0, 0, 'Block1')
        d_bl_2 = DBlock(None, 0, 0, 'Block2')

        #assign dblocks to DPlugin d_pl_1
        d_pl_1.add_dblock(d_bl_1)
        d_pl_1.add_dblock(d_bl_2)

        self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_1.name)
        self.dcore.subscribe(d_pl_2.id, d_pl_1.id, d_bl_2.name)
        self.dcore.subscribe(d_pl_3.id, d_pl_1.id, d_bl_1.name)
        self.dcore.subscribe(d_pl_3.id, d_pl_1.id, d_bl_2.name)


        self.dcore.subscribe_signals(d_pl_2.id, d_pl_1.id, d_bl_1.name, [1, 2, 3])
        self.dcore.subscribe_signals(d_pl_2.id, d_pl_1.id, d_bl_2.name, [6, 4, 5])
        self.dcore.subscribe_signals(d_pl_3.id, d_pl_1.id, d_bl_1.name, [9])
        self.dcore.subscribe_signals(d_pl_3.id, d_pl_1.id, d_bl_2.name, [17,19,18])

        self.assertTrue(self.dcore.unsubscribe_signals(d_pl_2.id, d_pl_1.id, d_bl_1.name, [1, 2]))

        subscription = d_pl_2.get_subscribtions()[d_pl_1.id][d_bl_1.name]

        self.assertNotIn(1, subscription.get_signals())
        self.assertNotIn(2, subscription.get_signals())
        self.assertIn(3, subscription.get_signals())

        self.assertEqual(len(d_bl_1.get_subscribers()), 2)

        self.assertTrue(self.dcore.unsubscribe_signals(d_pl_2.id, d_pl_1.id, d_bl_1.name, [3]))

        self.assertEqual(len(d_bl_1.get_subscribers()), 1)

if __name__ == "__main__":
    unittest.main();