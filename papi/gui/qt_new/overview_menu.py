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

from papi.gui.qt_new.item import PaPITreeItem, PaPIRootItem, PaPITreeModel
from papi.gui.qt_new.item import DPluginTreeModel, DParameterTreeModel, DBlockTreeModel
from papi.gui.qt_new.item import DPluginTreeItem, DBlockTreeItem, DParameterTreeItem, DSignalTreeItem

from papi.ui.gui.qt_new.overview import Ui_Overview

from PySide.QtGui import QMainWindow, QStandardItem, QMenu, QAbstractItemView, QAction, QStandardItemModel
from papi.constants import PLUGIN_PCP_IDENTIFIER, PLUGIN_DPP_IDENTIFIER, PLUGIN_VIP_IDENTIFIER, PLUGIN_IOP_IDENTIFIER, \
    PLUGIN_STATE_DEAD, PLUGIN_STATE_STOPPED, PLUGIN_STATE_PAUSE, PLUGIN_STATE_RESUMED, PLUGIN_STATE_START_SUCCESFUL

from PySide.QtCore import *
from PySide.QtGui import QLineEdit

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

        self.dpluginModel = DPluginTreeModel()
        self.dpluginModel.setHorizontalHeaderLabels(['Name'])

        self.pluginTree.setModel(self.dpluginModel)
        self.pluginTree.setUniformRowHeights(True)

        self.visual_root = PaPIRootItem('ViP')
        self.io_root = PaPIRootItem('IOP')
        self.dpp_root = PaPIRootItem('DPP')
        self.pcp_root = PaPIRootItem('PCP')

        self.dpluginModel.appendRow(self.visual_root)
        self.dpluginModel.appendRow(self.io_root)
        self.dpluginModel.appendRow(self.dpp_root)
        self.dpluginModel.appendRow(self.pcp_root)

        # -----------------------------------
        # Build structure of parameter tree
        # -----------------------------------

        self.dparameterModel = DParameterTreeModel()
        self.dparameterModel.setHorizontalHeaderLabels(['Name'])
        self.parameterTree.setModel(self.dparameterModel)
        self.parameterTree.setUniformRowHeights(True)
        self.dparameterModel.dataChanged.connect(self.data_changed_parameter_model)

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
        self.pluginTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pluginTree.customContextMenuRequested.connect(self.open_context_menu_dplugin_tree)

        self.blockTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.blockTree.customContextMenuRequested.connect(self.open_context_menu_block_tree)

        self.parameterTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parameterTree.customContextMenuRequested.connect(self.open_context_menu_parameter_tree)

        self.subscribersTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subscribersTree.customContextMenuRequested.connect(self.open_context_menu_subscriber_tree)

        self.subscriptionsTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subscriptionsTree.customContextMenuRequested.connect(self.open_context_menu_subscription_tree)

        # ----------------------------------
        # Add Actions
        # ----------------------------------
        self.actionRefresh.triggered.connect(self.refresh_action)

        self.clear()

    def clear(self):
        """
        This function will clear this window.
        :return:
        """
        self.bModel.clear()
        self.dparameterModel.clear()
        self.subscriberModel.clear()
        self.subscriptionModel.clear()
        self.unameEdit.setText('')
        self.usedpluginEdit.setText('')
        self.stateEdit.setText('')
        self.typeEdit.setText('')
        self.alivestateEdit.setText('')

        self.bModel.setHorizontalHeaderLabels(['Name'])
        self.dparameterModel.setHorizontalHeaderLabels(['Name', 'Value'])
        self.subscriberModel.setHorizontalHeaderLabels(['Subscriber'])
        self.subscriptionModel.setHorizontalHeaderLabels(['Subscription'])

    def plugin_item_changed(self, index):
        """
        Used to display all known information for a DPlugin which is
        accessible in the pluginTree by its index.
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
            # Add Signals of this DBlock
            # -------------------------

            for signal in dblock.get_signals():
                signal_item = DSignalTreeItem(signal)
                block_item.appendRow(signal_item)

            # ----------------------------------
            # Add Subscribers of this DBlock
            # ----------------------------------

            subscriber_ids = dblock.get_subscribers()

            for subscriber_id in subscriber_ids:
                subscriber = self.dgui.get_dplugin_by_id(subscriber_id)
                subscriber_item = DPluginTreeItem(subscriber)

                block_item = DBlockTreeItem(dblock)

                subscriber_item.appendRow(block_item)

                self.subscriberModel.appendRow(subscriber_item)

        # -------------------------
        # Add all Subscriptions
        # for this plugin
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

                for signal_uname in subscription.get_signals():

                    signal_item = QStandardItem(signal_uname)

                    dblock_sub_item.appendRow(signal_item)

        # --------------------------
        # Add DParameters
        # --------------------------

        dparameter_names = dplugin.get_parameters()
        for dparameter_name in dparameter_names:
            dparameter = dparameter_names[dparameter_name]
            dparameter_item = DParameterTreeItem(dparameter)
            self.dparameterModel.appendRow(dparameter_item)
            self.parameterTree.resizeColumnToContents(0)
            self.parameterTree.resizeColumnToContents(1)

        self.blockTree.expandAll()
        self.parameterTree.expandAll()

        # http://srinikom.github.io/pyside-docs/PySide/QtGui/QAbstractItemView.html \
        # #PySide.QtGui.PySide.QtGui.QAbstractItemView.SelectionMode
        self.blockTree.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Sort Models
        self.bModel.sort(0)
        self.dparameterModel.sort(0)

    # noinspection PyUnresolvedReferences
    def open_context_menu_dplugin_tree(self, position):
        """
        This callback function is called to create a context menu
        for the dplugin tree
        :param position:
        :return:
        """
        index = self.pluginTree.indexAt(position)

        if index.isValid() is False:
            return None

        if self.pluginTree.isIndexHidden(index):
            return

        dplugin = self.pluginTree.model().data(index, Qt.UserRole)

        menu = QMenu('Remove')

        action = QAction('Remove DPlugin', self)
        menu.addAction(action)

        action.triggered.connect(lambda p=dplugin.id: self.gui_api.do_delete_plugin(p))

        menu.exec_(self.pluginTree.viewport().mapToGlobal(position))

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

        if self.blockTree.isIndexHidden(index):
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
        isSignal = False
        menu = None
        action = None

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
            isSignal = True

        # ----------------------------------
        # Get necessary objects for this subscription
        # ----------------------------------

        if not isSignal:
            dblock = self.subscriptionsTree.model().data(index, Qt.UserRole)
            dplugin = self.subscriptionsTree.model().data(index.parent(), Qt.UserRole)
            action = QAction('Remove Subscriber', self)
        else:
            action = QAction('Remove Signal', self)
            dblock = self.subscriptionsTree.model().data(index.parent(), Qt.UserRole)
            dplugin = self.subscriptionsTree.model().data(index.parent().parent(), Qt.UserRole)


        # ----------------------------------
        # Create context menu
        # ----------------------------------

        menu = QMenu()
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

        menu = QMenu()
        menu.addMenu(sub_menu)

        menu.exec_(self.parameterTree.viewport().mapToGlobal(position))

    def add_pcp_subscription_action(self, dplugin: DPlugin, dparameter: DParameter, dplugin_pcp: DPlugin,
                                    dblock_pcp: DBlock):
        """
        This function is used to create a subscription for a process control plugin.
        :param dplugin: Subscriber of a pcp plugin
        :param dparameter: Parameter of the subscriber which should be controlled by the pcp plugin.
        :param dplugin_pcp: The pcp plugin
        :param dblock_pcp: Block of the pcp plugin which is used to control the subscriber's parameter.
        :return:
        """

        self.gui_api.do_subscribe(dplugin.id, dplugin_pcp.id, dblock_pcp.name, [], dparameter.name)
        pass

    def add_subscription_action(self, dplugin_uname):
        """

        :param dplugin_uname:
        :return:
        """

        signals = []

        dplugin = self.gui_api.gui_data.get_dplugin_by_uname(dplugin_uname)

        indexes = self.blockTree.selectedIndexes()

        for index in indexes:
            if index.isValid():
                signal = self.blockTree.model().data(index, Qt.UserRole)
                signals.append(signal.uname)

        index_dblock = index.parent()

        dblock = self.blockTree.model().data(index_dblock, Qt.UserRole)

        index = self.pluginTree.currentIndex()

        dplugin_source = self.pluginTree.model().data(index, Qt.UserRole)


        self.gui_api.do_subscribe(dplugin.id, dplugin_source.id, dblock.name, signals)

    def remove_subscriber_action(self, subscriber: DPlugin, dblock: DBlock):
        """

        :param subscriber:
        :param dblock:
        :return:
        """
        index = self.pluginTree.currentIndex()

        source = self.pluginTree.model().data(index, Qt.UserRole)

        self.gui_api.do_unsubscribe_uname(subscriber.uname, source.uname, dblock.name, [])

    def refresh_action(self, new_dplugin: DPlugin=None):
        """
        Used to refresh the overview menu view.
        :param new_dplugin: New dplugin which should be added in self.dpluginTreev.
        :return:
        """

        # -----------------------------------------
        # case: no DPlugin was added or removed
        #       e.g. parameter was changed
        # -----------------------------------------

        index = self.pluginTree.currentIndex()
        self.pluginTree.clicked.emit(index)

        # -----------------------------------------
        # case: remove already deleted plugins
        # -----------------------------------------

        self.visual_root.clean()
        self.dpp_root.clean()
        self.io_root.clean()
        self.pcp_root.clean()

        # -----------------------------------------
        # case: a DPlugin was added
        # -----------------------------------------

        if new_dplugin is not None:
            plugin_item = DPluginTreeItem(new_dplugin)
            if new_dplugin.type == PLUGIN_VIP_IDENTIFIER:
                if not self.visual_root.hasItem(new_dplugin):
                    self.visual_root.appendRow(plugin_item)
            if new_dplugin.type == PLUGIN_IOP_IDENTIFIER:
                if not self.io_root.hasItem(new_dplugin):
#                plugin_item = DPluginTreeItem(new_dplugin)
                    self.io_root.appendRow(plugin_item)
            if new_dplugin.type == PLUGIN_DPP_IDENTIFIER:
                if not self.dpp_root.hasItem(new_dplugin):
                    self.dpp_root.appendRow(plugin_item)
            if new_dplugin.type == PLUGIN_PCP_IDENTIFIER:
                if not self.pcp_root.hasItem(new_dplugin):
                    self.pcp_root.appendRow(plugin_item)

    def cancel_subscription_action(self, source: DPlugin, dblock: DBlock):
        """
        Action called to cancel a subscription of the current selected dplugin.
        :param source:
        :param dblock:
        :return:
        """
        index = self.pluginTree.currentIndex()
        subscriber = self.pluginTree.model().data(index, Qt.UserRole)

        self.gui_api.do_unsubscribe_uname(subscriber.uname, source.uname, dblock.name, [])

    def showEvent(self, *args, **kwargs):
        """
        ShowEvent of this class.
        :param args:
        :param kwargs:
        :return:
        """
        dplugin_ids = self.dgui.get_all_plugins()

        for dplugin_id in dplugin_ids:
            dplugin = dplugin_ids[dplugin_id]
            # ------------------------------
            # Sort DPluginItem in TreeWidget
            # ------------------------------
            plugin_item = DPluginTreeItem(dplugin)

            if dplugin.type == PLUGIN_VIP_IDENTIFIER:
                self.visual_root.appendRow(plugin_item)
            if dplugin.type == PLUGIN_IOP_IDENTIFIER:
                self.io_root.appendRow(plugin_item)
            if dplugin.type == PLUGIN_DPP_IDENTIFIER:
                self.dpp_root.appendRow(plugin_item)
            if dplugin.type == PLUGIN_PCP_IDENTIFIER:
                self.pcp_root.appendRow(plugin_item)

    def play_button_callback(self):
        """
        Callback function for the play button.
        :return:
        """
        index = self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)
        if item is not None:
            self.gui_api.do_resume_plugin_by_id(item.id)
            self.playButton.setDisabled(True)
            self.pauseButton.setDisabled(False)
            self.stopButton.setDisabled(False)

    def pause_button_callback(self):
        """
        Function pause_button_callback

        :return:
        """
        index = self.pluginTree.currentIndex()
        item = self.pluginTree.model().data(index, Qt.UserRole)
        if item is not None:
            self.pauseButton.setDisabled(True)
            self.playButton.setDisabled(False)
            self.gui_api.do_pause_plugin_by_id(item.id)

    def stop_start_button_callback(self):
        """
        Function stop_start_button_callback

        :return:
        """
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()