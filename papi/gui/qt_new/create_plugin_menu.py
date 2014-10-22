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
from papi.gui.qt_new.item import PaPITreeItem, RootItem, PaPItreeModel

__author__ = 'knuths'

from papi.ui.gui.qt_new.create import Ui_Create
from papi.gui.qt_new.create_plugin_dialog import CreatePluginDialog
from PySide.QtGui import QMainWindow, QStandardItem, QStandardItemModel

from papi.constants import PLUGIN_ROOT_FOLDER_LIST
from PySide.QtCore import *

from yapsy.PluginManager import PluginManager


class CreatePluginMenu(QMainWindow, Ui_Create):

    def __init__(self, gui_api, parent=None):
        super(CreatePluginMenu, self).__init__(parent)
        self.setupUi(self)
        self.dgui = gui_api.gui_data

        self.gui_api = gui_api

        self.subscriberID = None
        self.targetID = None
        self.blockName = None
        self.setWindowTitle("Add Plugin")

        self.plugin_manager = PluginManager()
        self.plugin_path = "../plugin/"

        self.plugin_manager.setPluginPlaces(
            PLUGIN_ROOT_FOLDER_LIST
        )
        self.setWindowTitle('Available Plugins')

        model = PaPItreeModel()
        model.setHorizontalHeaderLabels(['Name'])

        self.pluginTree.setModel(model)
        self.pluginTree.setUniformRowHeights(True)

        self.visual_root = RootItem('ViP')
        self.io_root = RootItem('IOP')
        self.dpp_root = RootItem('DPP')
        self.pcp_root = RootItem('PCP')

        model.appendRow(self.visual_root)
        model.appendRow(self.io_root)
        model.appendRow(self.dpp_root)
        model.appendRow(self.pcp_root)

        self.configuration_inputs = {}

        self.pluginTree.clicked.connect(self.pluginItemChanged)

        self.plugin_create_dialog = CreatePluginDialog(self.gui_api)
        self.createButton.clicked.connect(self.show_create_plugin_dialog)


    def pluginItemChanged(self, index):
        item = self.pluginTree.model().data(index, Qt.UserRole)

        if item is None:
            return

        self.nameEdit.setText(item.name)
        self.authorEdit.setText(item.author)
        self.descriptionText.setText(item.description)
        self.pathEdit.setText(item.path)



    def show_create_plugin_dialog(self):
        index = self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)

        if item is not None:
            self.plugin_create_dialog.set_plugin(item)

            self.plugin_create_dialog.show()

    def showEvent(self, *args, **kwargs):
        self.plugin_manager.collectPlugins()
        for pluginfo in self.plugin_manager.getAllPlugins():

            plugin_item = PaPITreeItem(pluginfo, pluginfo.name)

            if '/visual/' in pluginfo.path:
                self.visual_root.appendRow(plugin_item)
            if '/io/' in pluginfo.path:
                self.io_root.appendRow(plugin_item)
            if '/dpp/' in pluginfo.path:
                self.dpp_root.appendRow(plugin_item)
            if '/pcp/' in pluginfo.path:
                self.pcp_root.appendRow(plugin_item)

    def closeEvent(self, *args, **kwargs):
        self.plugin_create_dialog.close()