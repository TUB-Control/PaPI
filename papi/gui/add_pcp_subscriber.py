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

class AddPCPSubscriber(QDialog, Ui_AddSubscriber):

    def __init__(self, callback_functions, parent=None):
        super(AddPCPSubscriber, self).__init__(parent)
        self.setupUi(self)
        self.dgui = None

        self.treeSubscriber.currentItemChanged.connect(self.subscriberItemChanged)
        self.treeTarget.currentItemChanged.connect(self.targetItemChanged)
        self.treeBlock.currentItemChanged.connect(self.blockItemChanged)

        self.treeSubscriber.setHeaderLabel('PCP')
        self.treeTarget.setHeaderLabel('PCP_BLOCK')
        self.treeBlock.setHeaderLabel('Plugin')
        self.treeSignal.setHeaderLabel('Parameter')

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

            dplugin = item.dplugin
            dblock_ids = dplugin.get_dblocks()

            print(dplugin.type)

            for dblock_id in dblock_ids:
                dblock = dblock_ids[dblock_id]
                block_item = QTreeWidgetItem(self.treeTarget)
                block_item.dblock = dblock
                block_item.setText(0, dblock.name)
                block_item.dplugin = dplugin

    def targetItemChanged(self, item):

        self.treeBlock.clear()

        if hasattr(item, 'dplugin'):

            subscriber = self.treeSubscriber.currentItem().dplugin

            dplugin_ids = self.dgui.get_all_plugins()

            for dplugin_id in dplugin_ids:
                dplugin = dplugin_ids[dplugin_id]

                # ------------------------------
                # Sort DPluginItem in TreeWidget of Subscriber and Target
                # ------------------------------

                if subscriber.id is not dplugin_id and len(dplugin.get_parameters()) is not 0:

                    target_item = QTreeWidgetItem(self.treeBlock)

                    target_item.dplugin = dplugin
                    target_item.setText(0, str(dplugin.uname) )


    def blockItemChanged(self, item):
        self.treeSignal.clear()

        if hasattr(item, 'dplugin'):
            dplugin = item.dplugin
            dparameters = dplugin.get_parameters()

            for dparameter_key in dparameters:
                dparameter = dparameters[dparameter_key]
                parameter_item = QTreeWidgetItem(self.treeSignal)
                parameter_item.dparameter = dparameter
                parameter_item.setText(0, dparameter.name)


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

            self.pcpID = subscriber_item.dplugin.id
            self.pcpBlock = target_item.dblock

            self.pluginID = block_item.dplugin.id


            self.parameter = signal_item.dparameter


            button.setFocus()
            print(self.pluginID)
            print(self.pcpID)
            print(self.pcpBlock)
            print(self.parameter)

            self.callback_functions['do_subscribe'](self.pluginID, self.pcpID, self.pcpBlock.name , [], self.parameter.name)