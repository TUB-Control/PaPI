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

from papi.ui.gui.add_plugin import Ui_AddPlugin
from PySide.QtGui import QDialog, QAbstractButton, QDialogButtonBox
from PySide.QtGui import QTreeWidgetItem
from yapsy.PluginManager import PluginManager

class AddPlugin(QDialog, Ui_AddPlugin):

    def __init__(self, callback_function, parent=None):
        super(AddPlugin, self).__init__(parent)
        self.setupUi(self)
        self.dgui = None

        self.callback_functions = callback_function

        self.treePlugin.currentItemChanged.connect(self.pluginItemChanged)


        self.buttonBox.clicked.connect(self.button_clicked)

        self.subscriberID = None
        self.targetID = None
        self.blockName = None
        self.setWindowTitle("Add Plugin")

        self.plugin_manager = PluginManager()
        self.plugin_path = "../plugin/"

        self.plugin_manager.setPluginPlaces(
            [
                self.plugin_path + "visual", 'plugin/visual',
                self.plugin_path + "io", 'plugin/io',
                self.plugin_path + "dpp", 'plugin/dpp'
            ]
        )
        self.setWindowTitle('Available Plugins')


        self.visual_root = QTreeWidgetItem(self.treePlugin)
        self.visual_root.setText(0, 'ViP')
        self.io_root = QTreeWidgetItem(self.treePlugin)
        self.io_root.setText(0, 'IOP')
        self.dpp_root = QTreeWidgetItem(self.treePlugin)
        self.dpp_root.setText(0, 'DPP')
        self.pcb_root = QTreeWidgetItem(self.treePlugin)
        self.pcb_root.setText(0, 'PCB')

        self.plugin_uname = None
        self.plugin_name = None

    def setDGui(self, dgui):
        self.dgui = dgui

    def getDGui(self):
        """

        :return:
        :rtype DGui:
        """
        return self.dgui

    def pluginItemChanged(self, item):
        if hasattr(item, 'pluginfo'):
            pluginfo = item.pluginfo

            self.le_path.setText(pluginfo.path)

            pass

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
            if '/pcp/' in pluginfo.path:
                plugin_item = QTreeWidgetItem(self.pcb_root)

            if plugin_item is not None:
                plugin_item.pluginfo = pluginfo
                plugin_item.setText(0, pluginfo.name)

    def button_clicked(self, button : QAbstractButton):

        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ApplyRole:

            plugin_item = self.treePlugin.currentItem()

            self.plugin_name = plugin_item.pluginfo.name
            self.plugin_uname = self.le_uname.text()

            self.callback_functions['do_create_plugin'](self.plugin_name, self.plugin_uname)

            self.le_uname.setText('')