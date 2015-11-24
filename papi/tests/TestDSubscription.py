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

from papi.data.DPlugin import DPlugin, DBlock, DSubscription
from papi.data.DSignal import DSignal
from papi.data.DParameter import DParameter
from papi.constants import CORE_TIME_SIGNAL

class TestDSusbcription(unittest.TestCase):

    def setUp(self):
        pass

    def test_attach_signal(self):
        dblock = DBlock('SinMit_f1')
        ds_1 = DSignal(CORE_TIME_SIGNAL)
        ds_2 = DSignal('f1_1')
        dblock.add_signal(ds_1)
        dblock.add_signal(ds_2)

        subscription = DSubscription(dblock)

        self.assertTrue(subscription.add_signal(ds_1))

        self.assertIn(ds_1, subscription.get_signals())

        self.assertFalse(subscription.add_signal(ds_1))

    def test_remove_signal(self):
        dblock = DBlock('SinMit_f1')
        ds_1 = DSignal(CORE_TIME_SIGNAL)
        dblock.add_signal(ds_1)

        subscription = DSubscription(dblock)
        subscription.add_signal(ds_1)
        self.assertTrue(subscription.rm_signal(ds_1))

        self.assertNotIn(ds_1, subscription.get_signals())

        self.assertTrue(subscription.add_signal(ds_1))