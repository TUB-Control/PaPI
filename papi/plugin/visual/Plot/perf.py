#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
 
Contributors:
Sven Knuth
"""

import sys
import os
import time
import random

sys.path.insert(0,os.path.abspath('../../../../'))

print(sys.path)
import papi.pyqtgraph as pq

from PySide.QtGui import QApplication, QLabel
from PySide import QtCore

import importlib.machinery


def do_fctn(plugin):
    t = plugin.__t__
    data = {}
    for i in range(10):
        data['t'] = [t]
        t += 0.01
        data['signal_1'] = [random.randint(0, 5)]
        data['signal_2'] = [random.randint(10, 15)]
        data['signal_3'] = [random.randint(20, 25)]
        data['signal_4'] = [random.randint(30, 35)]
        data['signal_5'] = [random.randint(40, 45)]


        plugin.execute(data)
        plugin.__t__ = t

    if plugin.__t__ < 10:
        QtCore.QTimer.singleShot(20, lambda : do_fctn(plugin))

imp_path = "Plot.py"
class_name = "Plot"

app = QApplication([])

loader = importlib.machinery.SourceFileLoader(class_name, imp_path)
current_modul = loader.load_module()

plugin = getattr(current_modul, class_name)(debug=True)

# print('1')
# __text_item__ = pq.TextItem(text='', color=(200, 200, 200), anchor=(0, 0))
# print('2')


plugin.debug_papi()

plot_widget = plugin.__plotWidget__

plot_widget.show()

plugin.__t__ = 0

QtCore.QTimer.singleShot(50, lambda : do_fctn(plugin))

app.exec_()


