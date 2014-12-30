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

from PySide.QtGui import QMainWindow, QTreeWidgetItem, QTableWidgetItem
from PySide.QtCore import Qt

from papi.ui.gui.qt_dev.manager import Ui_Manager
from papi.yapsy.PluginManager import PluginManager
from papi.constants import PLUGIN_PCP_IDENTIFIER, PLUGIN_DPP_IDENTIFIER, PLUGIN_VIP_IDENTIFIER, PLUGIN_IOP_IDENTIFIER


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

        self.treePlugin.currentItemChanged.connect(self.plugin_item_changed)
        self.treeBlock.currentItemChanged.connect(self.block_item_changed)
        #self.tableParameter.cellChanged.connect(self.parameterCellChanged)
        # ----------------------------------------
        # Create Root Elements for TreeWidget
        # ----------------------------------------
        self.visual_root = QTreeWidgetItem(self.treePlugin)
        self.visual_root.setText(self.get_column_by_name("PLUGIN"), '[ViP]')
        self.io_root = QTreeWidgetItem(self.treePlugin)
        self.io_root.setText(self.get_column_by_name("PLUGIN"), '[IOP]')
        self.dpp_root = QTreeWidgetItem(self.treePlugin)
        self.dpp_root.setText(self.get_column_by_name("PLUGIN"), '[DPP]')
        self.pcb_root = QTreeWidgetItem(self.treePlugin)
        self.pcb_root.setText(self.get_column_by_name("PLUGIN"), '[PCB]')
        self.dgui = None

#        self.subscribeButton.clicked.connect(self.subscribe_action)

        # ---------------------------------
        # Search for PCP Plugins
        # ---------------------------------

        self.plugin_manager = PluginManager()
        self.plugin_path = "../plugin/"

        self.plugin_manager.setPluginPlaces(
            [
                # self.plugin_path + "visual", 'plugin/visual',
                # self.plugin_path + "io", 'plugin/io',
                # self.plugin_path + "dpp", 'plugin/dpp',
                self.plugin_path + "pcp", 'plugin/pcp'
            ]
        )

        # myAction = QAction('RechtsKLick', self)
        # self.setContextMenuPolicy(Qt.ActionsContextMenu)
        #
        # self.addAction(myAction)
        #
        # myAction.triggered.connect( lambda  : self.contextMenu(self.treePlugin.currentItem()))


    # def contextMenu(self, item):
    #     if hasattr(item, 'object'):
    #         print(item.object)
    #     print('itemContextMenu')

    # def add_plugin(self):
    #     AddPlu = AddPlugin()
    #     AddPlu.setDGui(self.dgui)
    #     AddPlu.show()
    #     AddPlu.raise_()
    #     AddPlu.activateWindow()
    #     r = AddPlu.exec_()
    #
    #     if r == 1 :
    #         self.callback_functions['do_create_plugin'](AddPlu.plugin_name, AddPlu.plugin_uname)
    #
    #     print("ReturnCode ", str(r))

    # def add_subscribtion(self):
    #
    #     AddSub = AddSubscriber()
    #     AddSub.setDGui(self.dgui)
    #     AddSub.show()
    #     AddSub.raise_()
    #     AddSub.activateWindow()
    #     r = AddSub.exec_()
    #
    #     if r == 1 :
    #         subscriber_id = AddSub.subscriberID
    #         target_id = AddSub.targetID
    #         block_name = AddSub.blockName
    #
    #         self.callback_functions['do_subscribe'](subscriber_id, target_id, block_name)
    #
    #     print("ReturnCode " , str(r))

#     def subscribe_action(self):
#         item = self.treePlugin.currentItem()
#         if hasattr(item, 'object'):
#             print(item.object)
#             sub_id = item.object.id
#             target_id = int(self.target_id.text())
#             block_name = str(self.block_name.text())
# #            print(sub_id + " - " + target_id + " - " + block_name)
#             self.callback_functions['do_subscribe'](sub_id, target_id, block_name)
#
#         print('itemCreate')

    def plugin_item_changed(self, item):
        """
        Function is called when a new item/plugin is selected
        :param item:
        :return:
        """
        self.clean()

        # ------------------------------
        # Remove slot for signal cellChanged
        # if possible
        # ------------------------------
        try:
            self.tableParameter.cellChanged.disconnect(self.parameterCellChanged)
        except:
            pass

        if hasattr(item, 'dplugin'):

            dplugin = item.dplugin



            # ------------------------------
            # Add Meta information of DPlugin
            # ------------------------------
            self.le_ID.setText(str(dplugin.id))
            self.le_Type.setText(str(dplugin.type))

            # ------------------------------
            # Add DBlocksItem for DPluginItem
            # ------------------------------
            dblock_root = self.treeBlock

            dblock_ids = dplugin.get_dblocks()

            for dblock_id in dblock_ids:
                dblock = dblock_ids[dblock_id]
                block_item = QTreeWidgetItem(dblock_root)
                block_item.dblock = dblock
                block_item.setText(self.get_column_by_name("BLOCK"), dblock.name)

                # ---------------------------
                # Add Subscribers of DBlock
                # ---------------------------

                subscriber_ids = dblock.get_subscribers()

                for subscriber_id in subscriber_ids:
                    subscriber_item = QTreeWidgetItem(block_item)

                    subscriber = self.dgui.get_dplugin_by_id(subscriber_id)

                    subscriber_item.setText(self.get_column_by_name("SUBSCRIBER"), str(subscriber.uname))

            # ------------------------------
            # Add DParameterItem for DPluginItem
            # ------------------------------

            dparameter_table = self.tableParameter

            dparameter_names = dplugin.get_parameters()

            row = 0

            dparameter_table.setRowCount(len(dparameter_names.keys()))

            for dparameter_name in dparameter_names:

                dparameter = dparameter_names[dparameter_name]
                # ---------------------
                # Set Parameter Name
                # ---------------------
                parameter_item_name = QTableWidgetItem( str(dparameter.name) )
                parameter_item_name.setFlags( Qt.ItemIsSelectable and not Qt.ItemIsEditable and Qt.ItemIsEnabled)
                dparameter_table.setItem(row, 0, parameter_item_name)

                # ---------------------
                # Set PCPs in table
                # ---------------------
#                 combo_box = QComboBox()
#
#                 #TODO: Erzeugt Fehler, da objekte beim Wechsel von Plugins geloescht werden.
#                 # combo_box.currentIndexChanged.connect( lambda : self.combo_box_parameter_changed(dplugin, dparameter, combo_box))
# #
#                 dparameter_table.setCellWidget(row, 1, combo_box)
#
#                 self.plugin_manager.collectPlugins()
#
#                 combo_box.addItem("None", None)
#
#                 for pluginfo in self.plugin_manager.getAllPlugins():
#
#                     combo_box.addItem(pluginfo.name, pluginfo)

                # ---------------------
                # Set Current Value in table
                # ---------------------
                parameter_item_value = QTableWidgetItem( str(dparameter.value) )
                parameter_item_value.dplugin = dplugin
                parameter_item_value.dparameter = dparameter
                dparameter_table.setItem(row, 2, parameter_item_value)

                # ---------------------------------
                # Add slot for signal cellChanged
                # ---------------------------------

                self.tableParameter.cellChanged.connect(self.parameterCellChanged)

                row+=1

    def parameterCellChanged(self, row, column):
        """
        This function is always called when
        an (text)-item within the table is changed
        :param row:
        :param column:
        :return:
        """
        # -----------------------------------------------
        # Only interested in changes of the third column
        # -----------------------------------------------
        if column == 0:
            return 0

        item = self.tableParameter.item(row, column)
        nvalue = item.text()

        self.callback_functions['do_set_parameter'](item.dplugin.uname, item.dparameter.name, float(nvalue))

        #print('Parameter Change Request for ' + item.dparameter.name + " of Plugin " + item.dplugin.uname + " Value: " + str(nvalue))

    # def combo_box_parameter_changed(self, dplugin, dparameter, box):
    #     """
    #     This function is always called when
    #     an item within a combox box is changed
    #
    #     :param dplugin:
    #     :param dparameter:
    #     :param box:
    #     :return:
    #     """
    #     # if dplugin == None or dparameter == None or box == None:
    #     #     return 0
    #
    #     dparameter_name = dparameter.name
    #     index = box.currentIndex()
    #
    #     pcp = box.itemData(index)
    #
    #     if pcp is None:
    #         return 0
    #
    #     config={
    #         'dplugin_id' : {},
    #         'default' : {},
    #         'name' : {}
    #     }
    #
    #     config['dplugin_id']['value']= str(dplugin.id)
    #     config['default']['value']= str(dparameter.default)
    #     config['name']['value'] = dparameter_name
    #
    #
    #     self.callback_functions['do_create_plugin'](pcp.name, dparameter.name + "_" + pcp.name, config=config)
    #
    #     # if pcp is not None:
    #     #     print('GUI:Manager: PCP Change Request for Parameter ' + dparameter.name + " of Plugin " + dplugin.uname + " PCB " + pcp.name )
    #     # else:
    #     #     print('GUI:Manager: PCP Change Request for Parameter ' + dparameter.name + " of Plugin " + dplugin.uname + " PCB None " )
    #     # pass

    def block_item_changed(self, item):
        self.treeSignal.clear()

        if hasattr(item, 'dblock'):
            dblock = item.dblock

            signals = dblock.get_signals()

            for signal in signals:
                print(signal)
                signal_item = QTreeWidgetItem(self.treeSignal)
                signal_item.setText(self.get_column_by_name("SIGNAL"), signal)

    def showEvent(self, *args, **kwargs):
        dplugin_ids = self.dgui.get_all_plugins()

        #Add DPlugins in QTree

        for dplugin_id in dplugin_ids:
            dplugin = dplugin_ids[dplugin_id]

            # ------------------------------
            # Sort DPluginItem in TreeWidget
            # ------------------------------

            if dplugin.type == PLUGIN_VIP_IDENTIFIER:
                plugin_item = QTreeWidgetItem(self.visual_root)
            if dplugin.type == PLUGIN_IOP_IDENTIFIER:
                plugin_item = QTreeWidgetItem(self.io_root)
            if dplugin.type == PLUGIN_DPP_IDENTIFIER:
                plugin_item = QTreeWidgetItem(self.dpp_root)
            if dplugin.type == PLUGIN_PCP_IDENTIFIER:
                plugin_item = QTreeWidgetItem(self.pcb_root)

            plugin_item.dplugin = dplugin
            plugin_item.setText(self.get_column_by_name("PLUGIN"), str(dplugin.uname) )

            # -------------------------------
            # Set amount of blocks and parameters as meta information
            # -------------------------------
            dparameter_names = dplugin.get_parameters()
            dblock_ids = dplugin.get_dblocks()

            plugin_item.setText(self.get_column_by_name("#PARAMETERS"), str(len(dparameter_names.keys())))
            plugin_item.setText(self.get_column_by_name("#BLOCKS"), str(len(dblock_ids.keys())))

    def clean(self):
        """
        This function is called to remove old values in form fields or similar
        :return:
        """

        #------------------
        # Remove content in form fields
        #------------------

        self.le_ID.setText("")
        self.le_Type.setText("")
        self.le_Path.setText("")

        #------------------
        # Remove items in parameter tree
        #------------------

        self.treeBlock.clear()

        #------------------
        # Remove items in block tree
        #------------------

        self.treeSignal.clear()

        self.tableParameter.clear()

        #self.treeParameter.clear()

        #self.tableParameter.clear()

    def hideEvent(self, *args, **kwargs):
        """
        This event is used to clear the TreeWidget
        :param args:
        :param kwargs:
        :return:
        """

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

    def resizeEvent(self, event):
        h = event.size().height()
        w = event.size().width()


    def get_column_by_name(self, name):
        """
        Returns column number by name
        :param name:
        :return:
        """
        if name == "PLUGIN":
            return 0

        if name == "#PARAMETERS":
            return 1

        if name == "#BLOCKS":
            return 2

        if name == "SUBSCRIBER":
            return 1

        if name == "BLOCK":
            return 0

        if name == "PARAMETER":
            return 0

        if name == "SIGNAL":
            return 0
