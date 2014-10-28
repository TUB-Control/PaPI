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

from papi.gui.qt_new.item import PaPITreeItem, PaPIRootItem, PaPITreeModel
from papi.gui.qt_new.item import DPluginTreeModel, DParameterTreeModel, DBlockTreeModel
from papi.gui.qt_new.item import DPluginTreeItem, DBlockTreeItem, DParameterTreeItem

from papi.ui.gui.qt_new.overview import Ui_Overview

from PySide.QtGui import QMainWindow, QStandardItem, QMenu, QAbstractItemView, QAction, QStandardItemModel
from papi.constants import PLUGIN_PCP_IDENTIFIER, PLUGIN_DPP_IDENTIFIER, PLUGIN_VIP_IDENTIFIER, PLUGIN_IOP_IDENTIFIER, \
    PLUGIN_STATE_DEAD, PLUGIN_STATE_STOPPED, PLUGIN_STATE_PAUSE, PLUGIN_STATE_RESUMED, PLUGIN_STATE_START_SUCCESFUL

from PySide.QtCore import *
from papi.data.DPlugin import DPlugin, DBlock, DParameter


class OverviewPluginMenu(QMainWindow, Ui_Overview):
    """
    This class is used to create an extra window which is used to display all created plugins.
    The information are taken by the corresponding DPlugin-Object of a plugin. By this window a user is able to
    create and cancel subscriptions.
    """

    def __init__(self, gui_api, parent=None):
        super(OverviewPluginMenu, self).__init__(parent)
        self.setupUi(self)
        self.dgui = gui_api.gui_data

        self.gui_api = gui_api

        self.setWindowTitle("OverviewMenu")

        # ----------------------------------
        # Build structure of plugin tree
        # ----------------------------------

        self.model = DPluginTreeModel()
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

        self.pModel = DParameterTreeModel()
        self.pModel.setHorizontalHeaderLabels(['Name'])
        self.parameterTree.setModel(self.pModel)
        self.parameterTree.setUniformRowHeights(True)
        self.pModel.dataChanged.connect(self.data_changed_parameter_model)

        # -----------------------------------
        # Build structure of block tree
        # -----------------------------------

        self.bModel = DBlockTreeModel()
        self.bModel.setHorizontalHeaderLabels(['Name'])
        self.blockTree.setModel(self.bModel)
        self.blockTree.setUniformRowHeights(True)


        # -----------------------------------
        # Build structure of subscriber tree
        # -----------------------------------

        self.subscriberModel = PaPITreeModel()
        self.subscriberModel.setHorizontalHeaderLabels(['Subscriber'])
        self.subscribersTree.setModel(self.subscriberModel)
        self.subscribersTree.setUniformRowHeights(True)

        # -----------------------------------
        # Build structure of subscriptions tree
        # -----------------------------------

        self.subscriptionModel = PaPITreeModel()
        self.subscriptionModel.setHorizontalHeaderLabels(['Subscription'])
        self.subscriptionsTree.setModel(self.subscriptionModel)
        self.subscriptionsTree.setUniformRowHeights(True)

        # -----------------------------------
        # signal/slots
        # -----------------------------------
        self.playButton.clicked.connect(self.play_button_callback)
        self.pauseButton.clicked.connect(self.pause_button_callback)
        self.stopButton.clicked.connect(self.stop_start_button_callback)
        self.pluginTree.clicked.connect(self.plugin_item_changed)

        # ----------------------------------
        # Add context menu
        # ----------------------------------
        self.blockTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.blockTree.customContextMenuRequested.connect(self.open_context_menu_block_tree)

        self.parameterTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parameterTree.customContextMenuRequested.connect(self.open_context_menu_parameter_tree)

        self.subscribersTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subscribersTree.customContextMenuRequested.connect(self.open_context_menu_subscriber_tree)

        self.subscriptionsTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subscriptionsTree.customContextMenuRequested.connect(self.open_context_menu_subscription_tree)

        self.clear()

    def clear(self):
        """
        This function will clear this window.
        :return:
        """
        self.bModel.clear()
        self.pModel.clear()
        self.subscriberModel.clear()
        self.subscriptionModel.clear()
        self.unameEdit.setText('')
        self.usedpluginEdit.setText('')
        self.stateEdit.setText('')
        self.typeEdit.setText('')
        self.alivestateEdit.setText('')

        self.bModel.setHorizontalHeaderLabels(['Name'])
        self.pModel.setHorizontalHeaderLabels(['Name', 'Value'])
        self.subscriberModel.setHorizontalHeaderLabels(['Subscriber'])
        self.subscriptionModel.setHorizontalHeaderLabels(['Subscription'])

    def plugin_item_changed(self, index):
        """
        Used to display all known information for a DPlugin which is
        accessible in the pluginTree by index.
        :param index: Current selected index
        :return:
        """

        dplugin = self.pluginTree.model().data(index, Qt.UserRole)

        self.clear()

        if dplugin is None:
            self.tabWidget.setDisabled(True)
            return
        self.tabWidget.setDisabled(False)

        # ------------------------------------
        # Get all needed dplugin information
        # ------------------------------------

        self.unameEdit.setText(dplugin.uname)
        self.usedpluginEdit.setText(dplugin.plugin_identifier)
        self.stateEdit.setText(dplugin.state)
        self.typeEdit.setText(dplugin.type)
        self.alivestateEdit.setText(dplugin.alive_state)

        if dplugin.type != PLUGIN_PCP_IDENTIFIER:
            self.pauseButton.setDisabled(False)
            self.playButton.setDisabled(False)
            self.stopButton.setDisabled(False)
        else:
            self.pauseButton.setDisabled(True)
            self.playButton.setDisabled(True)
            self.stopButton.setDisabled(True)

        if dplugin.alive_state != PLUGIN_STATE_DEAD:
            if dplugin.state == PLUGIN_STATE_PAUSE:
                self.pauseButton.setDisabled(True)
            if dplugin.state == PLUGIN_STATE_STOPPED:
                self.pauseButton.setDisabled(True)
                self.playButton.setDisabled(True)
                self.stopButton.setText('START')
            if dplugin.state == PLUGIN_STATE_RESUMED:
                self.playButton.setDisabled(True)
            if dplugin.state == PLUGIN_STATE_START_SUCCESFUL:
                self.playButton.setDisabled(True)
                self.stopButton.setText('STOP')

        # ---------------------------
        # Add DBlocks
        # ---------------------------

        dblock_ids = dplugin.get_dblocks()

        for dblock_id in dblock_ids:
            dblock = dblock_ids[dblock_id]

            block_item = DBlockTreeItem(dblock)
            self.bModel.appendRow(block_item)

            # -------------------------
            # Add Signals
            # -------------------------

            signal_names = dblock.get_signals()

            for signal_index in range(len(signal_names)):
                if signal_index != 0:
                    signal_name = signal_names[signal_index]
                    signal_item = PaPITreeItem(signal_index, signal_name)
                    block_item.appendRow(signal_item)

            # for signal_name in signal_names:
            #     signal_item = PaPITreeItem(signal_name, signal_name)
            #     signals_item.appendRow(signal_item)

            # -------------------------
            # Add Subscribers
            # -------------------------

            subscriber_ids = dblock.get_subscribers()

            for subscriber_id in subscriber_ids:
                subscriber = self.dgui.get_dplugin_by_id(subscriber_id)
                subscriber_item = DPluginTreeItem(subscriber)

                block_item = DBlockTreeItem(dblock)

                subscriber_item.appendRow(block_item)

                self.subscriberModel.appendRow(subscriber_item)




        # -------------------------
        # Add Subscriptions
        # -------------------------

        dplugin_sub_ids = dplugin.get_subscribtions()

        for dplugin_sub_id in dplugin_sub_ids:

            dblock_names = dplugin_sub_ids[dplugin_sub_id]
            dplugin_sub = self.gui_api.gui_data.get_dplugin_by_id(dplugin_sub_id)
            dplugin_sub_item = DPluginTreeItem(dplugin_sub)
            self.subscriptionModel.appendRow(dplugin_sub_item)

            for dblock_name in dblock_names:

                dblock_sub = dplugin_sub.get_dblock_by_name(dblock_name)
                dblock_sub_item = DBlockTreeItem(dblock_sub)
                dplugin_sub_item.appendRow(dblock_sub_item)

                subscription = dblock_names[dblock_name]
                signals = subscription.get_signals()

                for signal in signals:
                    signal_item = QStandardItem(str(signal))
                    dblock_sub_item.appendRow(signal_item)


        # --------------------------
        # Add DParameters
        # --------------------------

        dparameter_names = dplugin.get_parameters()
        for dparameter_name in dparameter_names:
            dparameter = dparameter_names[dparameter_name]
            dparameter_item = DParameterTreeItem(dparameter)
            self.pModel.appendRow(dparameter_item)
            self.parameterTree.resizeColumnToContents(0)
            self.parameterTree.resizeColumnToContents(1)

        self.blockTree.expandAll()
        self.parameterTree.expandAll()

        # http://srinikom.github.io/pyside-docs/PySide/QtGui/QAbstractItemView.html \
        # #PySide.QtGui.PySide.QtGui.QAbstractItemView.SelectionMode
        self.blockTree.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def open_context_menu_block_tree(self, position):
        """
        This callback function is called to create a context menu
        for the block tree
        :param position:
        :return:
        """

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
                    action.triggered.connect(lambda p=dplugin.uname: self.add_subscription_action(p))

            menu = QMenu()
            menu.addMenu(sub_menu)

            menu.exec_(self.blockTree.viewport().mapToGlobal(position))

    def open_context_menu_subscriber_tree(self, position):
        """
        This callback function is called to create a context menu
        for the subscriper tree
        :param position:
        :return:
        """
        index = self.subscribersTree.indexAt(position)

        if index.isValid() is False:
            return None

        if index.parent().isValid() is False:
            return None

        if self.subscribersTree.isIndexHidden(index):
            return

        dblock = self.subscribersTree.model().data(index, Qt.UserRole)
        dplugin = self.subscribersTree.model().data(index.parent(), Qt.UserRole)

        menu = QMenu('Remove')

        action = QAction('Remove Subscriber', self)
        menu.addAction(action)

        action.triggered.connect(lambda p=dblock, m=dplugin: self.remove_subscriber_action(m, p))

        menu.exec_(self.subscribersTree.viewport().mapToGlobal(position))

    def open_context_menu_subscription_tree(self, position):
        """
        This callback function is called to create a context menu
        for the subscription tree
        :param position:
        :return:
        """
        index = self.subscriptionsTree.indexAt(position)

        # ----------------------------------
        # Open no context menu if invalid
        # ----------------------------------

        if index.isValid() is False:
            return None

        # ----------------------------------
        # Open no context menu for parent
        # ----------------------------------

        if index.parent().isValid() is False:
            return None

        # ----------------------------------
        # Open no context menu for hidden objects
        # ----------------------------------

        if self.subscriptionsTree.isIndexHidden(index):
            return None

        # ----------------------------------
        # Open no context menu for signals
        # ----------------------------------

        if not index.child(0, 0).isValid():
            return None


        # ----------------------------------
        # Get necessary objects for this subscription
        # ----------------------------------

        dblock = self.subscriptionsTree.model().data(index, Qt.UserRole)
        dplugin = self.subscriptionsTree.model().data(index.parent(), Qt.UserRole)

        # ----------------------------------
        # Create context menu
        # ----------------------------------

        menu = QMenu()

        action = QAction('Remove Subscriber', self)
        menu.addAction(action)

        action.triggered.connect(lambda p=dblock, m=dplugin: self.cancel_subscription_action(m, p))

        menu.exec_(self.subscriptionsTree.viewport().mapToGlobal(position))

    def open_context_menu_parameter_tree(self, position):
        """
        This callback function is called to create a context menu
        for the parameter tree
        :param position:
        :return:
        """
        index = self.parameterTree.indexAt(position)

        if index.isValid() is False:
            return None

        if self.parameterTree.isIndexHidden(index):
            return

        dparameter = self.parameterTree.model().data(index, Qt.UserRole)
        dplugin = self.pluginTree.model().data(self.pluginTree.currentIndex(), Qt.UserRole)

        sub_menu = QMenu('Control by')

        dplugin_ids = self.dgui.get_all_plugins()

        for dplugin_id in dplugin_ids:
            dplugin_pcp = dplugin_ids[dplugin_id]

            if dplugin_pcp.type == PLUGIN_PCP_IDENTIFIER:
                # action = QAction(self.tr(dplugin.uname), self)
                # sub_menu.addAction(action)

                pcp_menu = QMenu(self.tr(dplugin_pcp.uname))
                sub_menu.addMenu(pcp_menu)

                dblock_pcp_ids = dplugin_pcp.get_dblocks()

                for dblock_pcp_id in dblock_pcp_ids:
                    dblock_pcp = dblock_pcp_ids[dblock_pcp_id]
                    action = QAction(self.tr(dblock_pcp.name), self)
                    pcp_menu.addAction(action)

                    action.triggered.connect(lambda p1=dplugin, p2=dparameter, p3=dplugin_pcp, p4=dblock_pcp:
                                             self.add_pcp_subscription_action(p1, p2, p3, p4))


                    #     action.triggered.connect(lambda p=dplugin.uname: self.add_subscription_action(p))
                    #     self.gui_api.do
                    #
                    # print(self.pluginID)
                    # print(self.pcpID)
                    # print(self.pcpBlock)
                    # print(self.parameter)
                    #
                    # self.callback_functions['do_subscribe'](self.pluginID, self.pcpID, self.pcpBlock.name , [], self.parameter.name)

        menu = QMenu()
        menu.addMenu(sub_menu)

        menu.exec_(self.parameterTree.viewport().mapToGlobal(position))

    def add_pcp_subscription_action(self, dplugin: DPlugin, dparameter: DParameter, dplugin_pcp:DPlugin,
                                    dblock_pcp:DBlock, ):

        # print(dplugin.uname)
        # print(dparameter.name)
        # print(dplugin_pcp.uname)
        # print(dblock_pcp.name)

        self.gui_api.do_subscribe(dplugin.id, dplugin_pcp.id, dblock_pcp.name, [], dparameter.name)
        pass

    def add_subscription_action(self, dplugin_uname):
        """

        :rtype :
        """

        subscriber_id = None
        source_id = None
        block_name = None
        signals = []

        dplugin = self.gui_api.gui_data.get_dplugin_by_uname(dplugin_uname)

        indexes = self.blockTree.selectedIndexes()

        print('Add Subscription for ' + dplugin.uname)
        print('There are ' + str(len(indexes)) + " signals to subscribe")
        for index in indexes:
            if index.isValid():
                signal_index = self.blockTree.model().data(index, Qt.UserRole)
                signals.append(signal_index)

        index_dblock = index.parent()

        dblock = self.blockTree.model().data(index_dblock, Qt.UserRole)

        index = self.pluginTree.currentIndex()

        dplugin_source = self.pluginTree.model().data(index, Qt.UserRole)

        self.gui_api.do_subscribe(dplugin.id, dplugin_source.id, dblock.name, signals)

    def remove_subscriber_action(self, subscriber: DPlugin, dblock: DBlock):

        index = self.pluginTree.currentIndex()

        source = self.pluginTree.model().data(index, Qt.UserRole)

        self.gui_api.do_unsubscribe_uname(subscriber.uname, source.uname, dblock.name, [])

        self.pluginTree.clicked.emit(index)

    def cancel_subscription_action(self, source: DPlugin, dblock: DBlock):
        print('Cancel ' + dblock.name + ' from' + str(source.id))

        index = self.pluginTree.currentIndex()
        subscriber = self.pluginTree.model().data(index, Qt.UserRole)

        self.gui_api.do_unsubscribe_uname(subscriber.uname, source.uname, dblock.name, [])

    def showEvent(self, *args, **kwargs):
        dplugin_ids = self.dgui.get_all_plugins()

        #Add DPlugins in QTree

        for dplugin_id in dplugin_ids:
            dplugin = dplugin_ids[dplugin_id]

            # ------------------------------
            # Sort DPluginItem in TreeWidget
            # ------------------------------
            plugin_item = DPluginTreeItem(dplugin)
            # print('Change Editable')
            # print(plugin_item.isEditable())
            #
            # plugin_item.setEditable(False)
            # print(plugin_item.isEditable())
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
        index = self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)
        if item is not None:
            self.gui_api.do_resume_plugin_by_id(item.id)
            self.playButton.setDisabled(True)
            self.pauseButton.setDisabled(False)
            self.stopButton.setDisabled(False)

    def pause_button_callback(self):
        index = self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)
        if item is not None:
            self.pauseButton.setDisabled(True)
            self.playButton.setDisabled(False)
            self.gui_api.do_pause_plugin_by_id(item.id)

    def stop_start_button_callback(self):
        index = self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)
        if item is not None:
            if self.stopButton.text() == 'STOP':
                self.gui_api.do_stopReset_pluign(item.id)
                self.stopButton.setText('START')
                self.pauseButton.setDisabled(True)
                self.playButton.setDisabled(True)
                self.stopButton.setDisabled(False)

            else:
                self.gui_api.do_start_plugin(item.id)
                self.stopButton.setText('STOP')
                self.pauseButton.setDisabled(False)
                self.playButton.setDisabled(False)
                self.stopButton.setDisabled(False)

    def data_changed_parameter_model(self, index, n):
        """
        This function is called when a dparameter value is changed by editing the 'value'-column.
        :param index: Index of current changed dparameter
        :param n: None
        :return:
        """

        dparameter = self.parameterTree.model().data(index, Qt.UserRole)
        index = self.pluginTree.currentIndex()

        dplugin = self.pluginTree.model().data(index, Qt.UserRole)

        self.gui_api.do_set_parameter(dplugin.id, dparameter.name, dparameter.value)
