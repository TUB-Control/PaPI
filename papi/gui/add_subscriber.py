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

from papi.ui.gui.add_subscriber import Ui_AddSubscriber
from PySide.QtGui import QDialog, QAbstractButton, QDialogButtonBox
from PySide.QtGui import QTreeWidgetItem
from papi.constants import PLUGIN_PCP_IDENTIFIER

class AddSubscriber(QDialog, Ui_AddSubscriber):

    def __init__(self, callback_functions, parent=None):
        super(AddSubscriber, self).__init__(parent)
        self.setupUi(self)
        self.dgui = None

        self.treeSubscriber.currentItemChanged.connect(self.subscriberItemChanged)
        self.treeTarget.currentItemChanged.connect(self.targetItemChanged)
        self.treeBlock.currentItemChanged.connect(self.blockItemChanged)

        self.buttonBox.clicked.connect(self.button_clicked)

        self.subscriberID = None
        self.targetID = None
        self.blockName = None
        self.signalName = None
        self.signalIndex = []
        self.setWindowTitle("Create Subscribtion")

        self.callback_functions = callback_functions

    def setDGui(self, dgui):
        self.dgui = dgui

    def getDGui(self):
        """

        :return:
        :rtype DGui:
        """
        return self.dgui

    def subscriberItemChanged(self, item):
        self.treeTarget.clear()
        if hasattr(item, 'dplugin'):

            subscriber = self.treeSubscriber.currentItem().dplugin

            dplugin_ids = self.dgui.get_all_plugins()

            for dplugin_id in dplugin_ids:
                dplugin = dplugin_ids[dplugin_id]

                # ------------------------------
                # Sort DPluginItem in TreeWidget of Subscriber and Target
                # ------------------------------

                if subscriber.id is not dplugin_id and len(dplugin.get_dblocks()) is not 0 and dplugin.type != PLUGIN_PCP_IDENTIFIER:

                    target_item = QTreeWidgetItem(self.treeTarget)

                    target_item.dplugin = dplugin
                    target_item.setText(0, str(dplugin.uname) )

    def targetItemChanged(self, item):

        self.treeBlock.clear()

        if hasattr(item, 'dplugin'):
            dplugin = item.dplugin
            dblock_ids = dplugin.get_dblocks()

            for dblock_id in dblock_ids:
                dblock = dblock_ids[dblock_id]
                block_item = QTreeWidgetItem(self.treeBlock)
                block_item.dblock = dblock
                block_item.setText(0, dblock.name)

    def blockItemChanged(self, item):
        self.treeSignal.clear()

        if hasattr(item, 'dblock'):
            dblock = item.dblock

            signal_names = dblock.get_signals()

            for signal_name in signal_names:
                signal_item = QTreeWidgetItem(self.treeSignal)
                signal_item.setText(0, signal_name)

    def showEvent(self, *args, **kwargs):

        self.treeSubscriber.clear()
        self.treeTarget.clear()
        self.treeBlock.clear()

        dplugin_ids = self.dgui.get_all_plugins()

        for dplugin_id in dplugin_ids:
            dplugin = dplugin_ids[dplugin_id]

            # ------------------------------
            # Sort DPluginItem in TreeWidget of Subscriber and Target
            # ------------------------------

            if dplugin.type != PLUGIN_PCP_IDENTIFIER:

                subscriber_item = QTreeWidgetItem(self.treeSubscriber)

                subscriber_item.dplugin = dplugin
                subscriber_item.setText(0, str(dplugin.uname) )

                # # -------------------------------
                # # Set amount of blocks and parameters as meta information
                # # -------------------------------
                # dblock_ids = dplugin.get_dblocks()
                #
                # plugin_item.setText(self.get_column_by_name("#BLOCKS"), str(len(dblock_ids.keys())))

    def button_clicked(self, button : QAbstractButton):

        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ApplyRole:

            subscriber_item = self.treeSubscriber.currentItem()
            target_item = self.treeTarget.currentItem()
            block_item = self.treeBlock.currentItem()
            signal_item = self.treeSignal.currentItem()

            self.subscriberID = subscriber_item.dplugin.id
            self.targetID = target_item.dplugin.id
            self.blockName = block_item.dblock.name

            self.signalIndex = []

            for item in self.treeSignal.selectedItems():
                signalName = item.text(0)

                index = block_item.dblock.get_signals().index(signalName)

                self.signalIndex.append(index)

            button.setFocus()

            self.callback_functions['do_subscribe'](self.subscriberID, self.targetID, self.blockName, self.signalIndex)