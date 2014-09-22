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

from papi.data.DPlugin import DPlugin, DBlock, DSubscription
from papi.data.DParameter import DParameter


class TestDSusbcription(unittest.TestCase):

    def setUp(self):
        pass

    def test_attach_signal(self):
        dblock = DBlock(None,1,10,'SinMit_f1',['t','f1_1'])

        subscription = DSubscription(dblock, [1,2,3])

        self.assertTrue(subscription.attach_signal(4))

        self.assertIn(4, subscription.get_signals())

        self.assertFalse(subscription.attach_signal(1))

    def test_remove_signal(self):
        dblock = DBlock(None,1,10,'SinMit_f1',['t','f1_1'])

        subscription = DSubscription(dblock, [1,2,3])

        self.assertTrue(subscription.remove_signal(1))

        self.assertNotIn(1, subscription.get_signals())

        self.assertTrue(subscription.attach_signal(1))