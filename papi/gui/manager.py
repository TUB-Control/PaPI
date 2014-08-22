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

from PySide.QtGui import QMainWindow, QTreeWidgetItem
from PySide import QtGui

from papi.ui.gui.manager import Ui_Manager
from yapsy.PluginManager import PluginManager
from papi.data.DPlugin import DPlugin

class Available(QMainWindow, Ui_Manager):
    def __init__(self, callback_functions, parent=None):
        super(Available, self).__init__(parent)
        self.setupUi(self)

        self.plugin_manager = PluginManager()
        self.plugin_path = "../plugin/"

        self.plugin_manager.setPluginPlaces([self.plugin_path + "visual", 'plugin/visual', self.plugin_path + "io", 'plugin/io', self.plugin_path + "dpp", 'plugin/dpp' ])
        self.setWindowTitle('Available Plugins')

        self.treePlugin.currentItemChanged.connect(self.itemChanged)

        self.callback_functions = callback_functions


        self.visual_root = QTreeWidgetItem(self.treePlugin)
        self.visual_root.setText(self.get_column_by_name("PLUGIN"), 'ViP')
        self.io_root = QTreeWidgetItem(self.treePlugin)
        self.io_root.setText(self.get_column_by_name("PLUGIN"), 'IOP')
        self.dpp_root = QTreeWidgetItem(self.treePlugin)
        self.dpp_root.setText(self.get_column_by_name("PLUGIN"), 'DPP')
        self.pcb_root = QTreeWidgetItem(self.treePlugin)
        self.pcb_root.setText(self.get_column_by_name("PLUGIN"), 'PCB')

        self.createButton.clicked.connect(self.create_action)

    def create_action(self):
        item = self.treePlugin.currentItem()
        if hasattr(item, 'object'):
            print(item.object)

            self.callback_functions['create_plugin'](item.object.name, 'SuperPlot !!')

        print('itemCreate')

        pass



    def itemChanged(self, item):
        # if hasattr(item, 'object'):
        #     print(item.object)
        #
        #     self.callback_functions['create_plugin'](item.object.name, 'SuperPlot !!')

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

            if plugin_item is not None:
                plugin_item.object = pluginfo

                plugin_item.setText(self.get_column_by_name("PLUGIN"), pluginfo.name)
                plugin_item.setText(self.get_column_by_name("PATH"), pluginfo.path)

    def hideEvent(self, *args, **kwargs):
        #print(self.treePlugin.topLevelItemCount())

        item = self.io_root.child(0)

        while( item is not None ):
            self.io_root.removeChild(item)
            item = self.io_root.child(0)

        item = self.visual_root.child(0)

        while( item is not None ):
            self.visual_root.removeChild(item)
            item = self.visual_root.child(0)

        item = self.dpp_root.child(0)

        while( item is not None ):
            self.dpp_root.removeChild(item)
            item = self.dpp_root.child(0)

        item = self.pcb_root.child(0)

        while( item is not None ):
            self.pcb_root.removeChild(item)
            item = self.pcb_root.child(0)

    def get_column_by_name(self, name):
        if name == "PLUGIN":
            return 0
        if name == "TYPE":
            return 1
        if name == "ID":
            return 2
        if name == "PATH":
            return 3

class Overview(QMainWindow, Ui_Manager):
    def __init__(self, callback_functions, parent=None):
        """

        :param dgui:
        :param parent:
        :return:
        """

        super(Overview, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('Overview Plugins')

        self.callback_functions = callback_functions

        #print(self.treePlugin)
        self.treePlugin.currentItemChanged.connect(self.itemChanged)
        #self.treePlugin.setHeaderLabel(1, "ID")
        self.visual_root = QTreeWidgetItem(self.treePlugin)
        self.visual_root.setText(self.get_column_by_name("PLUGIN"), 'ViP')
        self.io_root = QTreeWidgetItem(self.treePlugin)
        self.io_root.setText(self.get_column_by_name("PLUGIN"), 'IOP')
        self.dpp_root = QTreeWidgetItem(self.treePlugin)
        self.dpp_root.setText(self.get_column_by_name("PLUGIN"), 'DPP')
        self.pcb_root = QTreeWidgetItem(self.treePlugin)
        self.pcb_root.setText(self.get_column_by_name("PLUGIN"), 'PCB')
        self.dgui = None

        self.subscribeButton.clicked.connect(self.subscribe_action)


    def subscribe_action(self):
        item = self.treePlugin.currentItem()
        if hasattr(item, 'object'):
            print(item.object)
            sub_id = item.object.id
            target_id = int(self.target_id.text())
            block_name = str(self.block_name.text())
#            print(sub_id + " - " + target_id + " - " + block_name)
            self.callback_functions['subscribe'](sub_id, target_id, block_name)

        print('itemCreate')

    def itemChanged(self, item):
        if hasattr(item, 'object'):
            print(item.object)
        print('itemChanged')

    def showEvent(self, *args, **kwargs):
        dplugin_ids = self.dgui.get_all_plugins()

        #Add DPlugins in QTree

        for dplugin_id in dplugin_ids:
            dplugin = dplugin_ids[dplugin_id]
            print(dplugin.id)

 #           plugin_item = QTreeWidgetItem(self.visual_root)
            print(dplugin.type)

            if dplugin.type == "ViP":
                 plugin_item = QTreeWidgetItem(self.visual_root)
            if dplugin.type == "IOP":
                plugin_item = QTreeWidgetItem(self.io_root)
            if dplugin.type == "DPP":
                plugin_item = QTreeWidgetItem(self.dpp_root)
            if dplugin.type == "PCB":
                plugin_item = QTreeWidgetItem(self.pcb_root)

            plugin_item.object = dplugin
            plugin_item.setText(self.get_column_by_name("PLUGIN"), str(dplugin.uname) )
            plugin_item.setText(self.get_column_by_name("ID"), str(dplugin.id) )


            #Add DBlocks for DPlugin

            dblock_ids = dplugin.get_dblocks()

            dblock_root = QTreeWidgetItem(plugin_item)
            dblock_root.setText(self.get_column_by_name("PLUGIN"), "Blocks")

            for dblock_id in dblock_ids:
                dblock = dblock_ids[dblock_id]
                block_item = QTreeWidgetItem(dblock_root)
                block_item.object = dblock
                block_item.setText(self.get_column_by_name("PLUGIN"), dblock.name)

            #Add DParameter for DPlugin
            dparameter_root = QTreeWidgetItem(plugin_item)
            dparameter_root.setText(self.get_column_by_name("PLUGIN"), "Parameters")

            dparameter_names = dplugin.get_parameters()

            for dparameter_name in dparameter_names:
                dparameter = dparameter_names[dparameter_name]
                parameter_item = QTreeWidgetItem(dparameter_root)
                parameter_item.object = dparameter
                parameter_item.setText(self.get_column_by_name("PLUGIN"), dparameter.name)

    def hideEvent(self, *args, **kwargs):
        #print(self.treePlugin.topLevelItemCount())

        item = self.io_root.child(0)

        while item is not None:
            self.io_root.removeChild(item)
            item = self.io_root.child(0)

        item = self.visual_root.child(0)

        while item is not None:
            self.visual_root.removeChild(item)
            item = self.visual_root.child(0)

        item = self.dpp_root.child(0)

        while item is not None:
            self.dpp_root.removeChild(item)
            item = self.dpp_root.child(0)

        item = self.pcb_root.child(0)

        while item is not None:
            self.pcb_root.removeChild(item)
            item = self.pcb_root.child(0)

    def get_column_by_name(self, name):
        if name == "PLUGIN":
            return 0
        if name == "TYPE":
            return 1
        if name == "ID":
            return 2
        if name == "PATH":
            return 3
