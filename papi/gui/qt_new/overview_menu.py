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

from papi.ui.gui.qt_new.overview import Ui_Overview
from papi.gui.qt_new.create_plugin_dialog import CreatePluginDialog
from PySide.QtGui import QMainWindow, QStandardItem, QStandardItemModel
from papi.constants import PLUGIN_PCP_IDENTIFIER, PLUGIN_DPP_IDENTIFIER, PLUGIN_VIP_IDENTIFIER, PLUGIN_IOP_IDENTIFIER
from papi.constants import PLUGIN_ROOT_FOLDER_LIST
from PySide.QtCore import *

from yapsy.PluginManager import PluginManager


class OverviewPluginMenu(QMainWindow, Ui_Overview):

    def __init__(self, callback_functions, parent=None):
        super(OverviewPluginMenu, self).__init__(parent)
        self.setupUi(self)
        self.dgui = None

        self.callback_functions = callback_functions

        self.setWindowTitle("OverviewMenu")


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


        self.pluginTree.clicked.connect(self.pluginItemChanged)


    def setDGui(self, dgui):
        self.dgui = dgui

    def pluginItemChanged(self, index):
        dplugin = self.pluginTree.model().data(index, Qt.UserRole)

        if dplugin is None:
            return

        self.unameEdit.setText(dplugin.uname)
        self.usedpluginEdit.setText(dplugin.plugin_identifier)
        self.stateEdit.setText(dplugin.state)
        self.typeEdit.setText(dplugin.type)
        self.alivestateEdit.setText(dplugin.alive_state)

        # dblock_ids = dplugin.get_dblocks()
        #
        # # self.bloc
        # #
        # # for dblock_id in dblock_ids:
        # #     dblock = dblock_ids[dblock_id]
        # #     block_item = QTreeWidgetItem(dblock_root)
        # #     block_item.dblock = dblock
        # #     block_item.setText(self.get_column_by_name("BLOCK"), dblock.name)
        # #
        # #     # ---------------------------
        # #     # Add Subscribers of DBlock
        # #     # ---------------------------
        # #
        # #     subscriber_ids = dblock.get_subscribers()
        # #
        # #     for subscriber_id in subscriber_ids:
        # #         subscriber_item = QTreeWidgetItem(block_item)
        # #
        # #         subscriber = self.dgui.get_dplugin_by_id(subscriber_id)
        # #
        # #         subscriber_item.setText(self.get_column_by_name("SUBSCRIBER"), str(subscriber.uname))



    def show_create_plugin_dialog(self):
        index = self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)

        if item is not None:
            self.plugin_create_dialog.set_plugin(item)

            self.plugin_create_dialog.show()

    def showEvent(self, *args, **kwargs):
        dplugin_ids = self.dgui.get_all_plugins()

        #Add DPlugins in QTree

        for dplugin_id in dplugin_ids:
            dplugin = dplugin_ids[dplugin_id]

            # ------------------------------
            # Sort DPluginItem in TreeWidget
            # ------------------------------
            plugin_item = PaPITreeItem(dplugin, dplugin.uname)

            if dplugin.type == PLUGIN_VIP_IDENTIFIER:
                self.visual_root.appendRow(plugin_item)
            if dplugin.type == PLUGIN_IOP_IDENTIFIER:
                 self.io_root.appendRow(plugin_item)
            if dplugin.type == PLUGIN_DPP_IDENTIFIER:
                self.dpp_root.appendRow(plugin_item)
            if dplugin.type == PLUGIN_PCP_IDENTIFIER:
                self.pcp_root.appendRow(plugin_item)

            # plugin_item.dplugin = dplugin
            # plugin_item.setText(self.get_column_by_name("PLUGIN"), str(dplugin.uname) )
            #
            # # -------------------------------
            # # Set amount of blocks and parameters as meta information
            # # -------------------------------
            # dparameter_names = dplugin.get_parameters()
            # dblock_ids = dplugin.get_dblocks()
            #
            # plugin_item.setText(self.get_column_by_name("#PARAMETERS"), str(len(dparameter_names.keys())))
            # plugin_item.setText(self.get_column_by_name("#BLOCKS"), str(len(dblock_ids.keys())))
