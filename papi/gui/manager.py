#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universitšt Berlin,
Fakultšt IV - Elektrotechnik und Informatik,
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


import sys
import time

from PySide.QtGui import QMainWindow, QApplication

import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore

from papi.ui.gui.manager import Ui_Manager
from yapsy.PluginManager import PluginManager

class Manager(QMainWindow, Ui_Manager):
    def __init__(self, plugin_type, parent=None):
        super(Manager, self).__init__(parent)
        self.setupUi(self)
        self.plugin_type = plugin_type

        self.plugin_manager = PluginManager()

        if self.plugin_type == 'visual':
            self.plugin_manager.setPluginPlaces(["plugin/visual"])
            self.setWindowTitle('Visual Plugins')
        if self.plugin_type == 'io':
            self.plugin_manager.setPluginPlaces(["plugin/io"])
            self.setWindowTitle('IO Plugins')
        if self.plugin_type == 'parameter':
            self.plugin_manager.setPluginPlaces(["plugin/parameter"])
            self.setWindowTitle('Parameter Plugins')
