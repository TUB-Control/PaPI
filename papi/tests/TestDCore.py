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

from multiprocessing import Process, Queue
from papi.data.DCore import DCore
from papi.plugin.plot import Plot

class TestDCore(unittest.TestCase):

    def setUp(self):
        self.dcore = DCore()

    def test_add_pl_process(self):

        p = Process()
        queue = Queue()
        pl = Plot()

        self.dcore.add_plugin(p, 5, queue, None, pl, 10 )

        dp = self.dcore.get_dplugin_by_id(5)

       # self.assertTrue()

if __name__ == "__main__":
    unittest.main();