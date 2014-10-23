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
from papi.gui.qt_new.item import PaPITreeItem, PaPIRootItem, PaPItreeModel

__author__ = 'knuths'

from papi.ui.gui.qt_new.overview import Ui_Overview
from papi.gui.qt_new.create_plugin_dialog import CreatePluginDialog
from PySide.QtGui import QMainWindow, QStandardItem, QStandardItemModel, QMenu, QAbstractItemView, QAction
from papi.constants import PLUGIN_PCP_IDENTIFIER, PLUGIN_DPP_IDENTIFIER, PLUGIN_VIP_IDENTIFIER, PLUGIN_IOP_IDENTIFIER
from papi.constants import PLUGIN_ROOT_FOLDER_LIST
from PySide.QtCore import *
from papi.data.DPlugin import DPlugin, DBlock

from yapsy.PluginManager import PluginManager


class OverviewPluginMenu(QMainWindow, Ui_Overview):

    def __init__(self, gui_api, parent=None):
        super(OverviewPluginMenu, self).__init__(parent)
        self.setupUi(self)
        self.dgui = gui_api.gui_data

        self.gui_api = gui_api

        self.setWindowTitle("OverviewMenu")

        # ----------------------------------
        # Build structure of plugin tree
        # ----------------------------------

        self.model = PaPItreeModel()
        self.model.setHorizontalHeaderLabels(['Name'])

        self.pluginTree.setModel(self.model)
        self.pluginTree.setUniformRowHeights(True)

        self.visual_root = PaPIRootItem('ViP')
        self.io_root = PaPIRootItem('IOP')
        self.dpp_root = PaPIRootItem('DPP')
        self.pcp_root = PaPIRootItem('PCP')

        self.model.appendRow(self.visual_root)
        self.model.appendRow(self.io_root)
        self.model.appendRow(self.dpp_root)
        self.model.appendRow(self.pcp_root)

        # -----------------------------------
        # Build structure of parameter tree
        # -----------------------------------

        self.pModel = PaPItreeModel()
        self.pModel.setHorizontalHeaderLabels(['Name'])
        self.parameterTree.setModel(self.pModel)
        self.parameterTree.setUniformRowHeights(True)

        # -----------------------------------
        # Build structure of block tree
        # -----------------------------------

        self.bModel = PaPItreeModel()
        self.bModel.setHorizontalHeaderLabels(['Name'])
        self.blockTree.setModel(self.bModel)
        self.blockTree.setUniformRowHeights(True)

        # -----------------------------------
        # signal/slots
        # -----------------------------------
        self.playButton.clicked.connect(self.play_button_callback)
        self.pauseButton.clicked.connect(self.pause_button_callback)
        self.stopButton.clicked.connect(self.stop_start_button_callback)
        self.pluginTree.clicked.connect(self.pluginItemChanged)

        # ----------------------------------
        # Add context menu
        # ----------------------------------
        self.blockTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.blockTree.customContextMenuRequested.connect(self.open_context_menu_block_tree)


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

        self.bModel.clear()
        self.pModel.clear()

        self.bModel.setHorizontalHeaderLabels(['Name'])
        self.pModel.setHorizontalHeaderLabels(['Name'])

        # ---------------------------
        # Add DBlocks
        # ---------------------------

        dblock_ids = dplugin.get_dblocks()

        for dblock_id in dblock_ids:
            dblock = dblock_ids[dblock_id]

            block_item = PaPITreeItem(dblock, dblock.name)
            self.bModel.appendRow(block_item)

            # -------------------------
            # Add Signals
            # -------------------------
            signals_item = PaPIRootItem('Signals')
            block_item.appendRow(signals_item)

            signal_names = dblock.get_signals()

            for signal_name in signal_names:
                signal_item = PaPITreeItem(None, signal_name)
                signals_item.appendRow(signal_item)

            #signals_item.setSelectable(True)


            # -------------------------
            # Add Subscriber
            # -------------------------
            subscribers_item = PaPIRootItem('Subscribers')

            block_item.appendRow(subscribers_item)
            subscriber_ids = dblock.get_subscribers()

            for subscriber_id in subscriber_ids:
                subscriber = self.dgui.get_dplugin_by_id(subscriber_id)
                subscriber_item = PaPITreeItem(subscriber, subscriber.uname)
                subscribers_item.appendRow(subscriber_item)

        # --------------------------
        # Add DParameters
        # --------------------------

        dparameter_names = dplugin.get_parameters()
        for dparameter_name in dparameter_names:
            dparameter = dparameter_names[dparameter_name]
            dparameter_item = PaPITreeItem(dparameter, dparameter_name)
            self.pModel.appendRow(dparameter_item)

            dparameter_item_value = PaPITreeItem(dparameter, str(dparameter.value))
            self.pModel.appendColumn([dparameter_item_value])
            self.parameterTree.resizeColumnToContents(0)
            self.parameterTree.resizeColumnToContents(1)


        self.blockTree.expandAll()
        self.parameterTree.expandAll()

        # http://srinikom.github.io/pyside-docs/PySide/QtGui/QAbstractItemView.html \
        # #PySide.QtGui.PySide.QtGui.QAbstractItemView.SelectionMode
        self.blockTree.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def show_create_plugin_dialog(self):
        index = self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)

        if item is not None:
            self.plugin_create_dialog.set_plugin(item)

            self.plugin_create_dialog.show()

    def open_context_menu_block_tree(self, position):
        '''

        :param position:
        :return:
        '''

        index = self.blockTree.indexAt(position)

        if index.isValid() is False:
            return None

        if self.pluginTree.isIndexHidden(index):
            return

        item = self.blockTree.model().data(index, Qt.UserRole)

        if isinstance(item, DPlugin) or isinstance(item, DBlock):
            return

        index_sel = self.pluginTree.currentIndex()
        dplugin_sel = self.pluginTree.model().data(index_sel, Qt.UserRole)

        if dplugin_sel is not None:

            sub_menu = QMenu('Add Subscription')
            dplugin_ids = self.dgui.get_all_plugins()

            for dplugin_id in dplugin_ids:
                dplugin = dplugin_ids[dplugin_id]

                if dplugin_sel.id != dplugin_id:
                    action = QAction(self.tr(dplugin.uname), self)
                    sub_menu.addAction(action)
                    dplugin_uname = dplugin.uname
                    action.triggered.connect(lambda: self.add_subscription_action(self.tr(dplugin_uname)))

            menu = QMenu()
            menu.addMenu(sub_menu)

            menu.exec_(self.blockTree.viewport().mapToGlobal(position))

    def add_subscription_action(self, dplugin_uname):
        """

        :rtype :
        """

        dplugin = self.gui_api.gui_data.get_dplugin_by_uname(dplugin_uname)
        indexes = self.blockTree.selectedIndexes()

        print('Add Subscriotion for ' + dplugin.uname)
        print('There are ' + str(len(indexes)) + " signals to subscribe")
        for index in indexes:
            pass

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

    def play_button_callback(self):
        index=self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)
        if item is not None:
            self.gui_api.do_resume_plugin_by_id(item.id)

    def pause_button_callback(self):
        index=self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)
        if item is not None:
            self.pauseButton.setDisabled(True)
            #self.gui_api.do_pause_plugin_by_id(item.id)

    def stop_start_button_callback(self):
        index=self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)
        if item is not None:
            if self.stopButton.text() == 'STOP':
                self.gui_api.do_stopReset_pluign(item.id)
                self.stopButton.setText('START')
                #self.pauseButton.setDisabled(True)
                #self.playButton.setDisabled(True)

            else:
                self.gui_api.do_start_plugin(item.id)
                self.stopButton.setText('START')
                #self.pauseButton.setDisabled(False)
                #self.playButton.setDisabled(False)
