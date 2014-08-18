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


import sys
import time

from PySide.QtGui import QMainWindow, QApplication, QListWidgetItem, QTreeWidgetItem

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
        self.plugin_path = "../plugin/"



        self.plugin_manager.setPluginPlaces([self.plugin_path + "visual", 'plugin/visual', self.plugin_path + "io", 'plugin/io', self.plugin_path + "dpp", 'plugin/dpp' ])
        self.setWindowTitle('Available Plugins')


        self.listPlugin.currentItemChanged.connect(self.itemChanged)

        self.visual_root = QTreeWidgetItem(self.listPlugin)
        self.visual_root.setText(0, 'Visual')
        self.io_root = QTreeWidgetItem(self.listPlugin)
        self.io_root.setText(0, 'IO')
        self.dpp_root = QTreeWidgetItem(self.listPlugin)
        self.dpp_root.setText(0, 'DPP')

    def itemChanged(self):
        print('itemChanged')

    def showEvent(self, *args, **kwargs):
        self.plugin_manager.collectPlugins()
        for pluginfo in self.plugin_manager.getAllPlugins():

            plugin_item = None

            if '/visual/' in pluginfo.path:
                plugin_item = QTreeWidgetItem(self.visual_root)
            if '/io/' in pluginfo.path:
                plugin_item = QTreeWidgetItem(self.io_root)
            if '/dpp/' in pluginfo.path:
                plugin_item = QTreeWidgetItem(self.dpp_root)

            plugin_item.setText(0, pluginfo.name)
            plugin_item.setText(1, pluginfo.path)



            # plugins = QTreeWidgetItem(self.listPlugin)
            # plugins.setText(0, pluginfo.name)
            # plugins.setText(1, pluginfo.path)

        # for pluginfo in self.plugin_manager.getAllPlugins():
        #     print('Plugin: ')
        #     print(pluginfo.name)
        #     newItem = QListWidgetItem()
        #     newItem.setText(pluginfo.name)
        #     self.listPlugin.insertItem(0, newItem)

    def hideEvent(self, *args, **kwargs):
        #print(self.listPlugin.topLevelItemCount())


        item = self.io_root.child(0)

        while( item is not None ):
            self.io_root.removeChild(item)
            item = self.io_root.child(0)

        item = self.visual_root.child(0)

        while( item is not None ):
            self.visual_root.removeChild(item)
            item = self.visual_root.child(0)
