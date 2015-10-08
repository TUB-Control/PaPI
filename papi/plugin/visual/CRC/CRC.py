#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

Contributors:
<Stefan Ruppin
"""



from PyQt5.QtCore import *
from PyQt5.QtGui import *

from papi.ui.gui.default.CreateRecording import Ui_CreateRecording
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QComboBox, QStyleOptionButton,\
     QStyledItemDelegate, QStyle, QApplication


from papi.gui.default.item import PaPITreeModel

from papi.plugin.base_classes.vip_base import vip_base

class CreateRecordingConfig(QMainWindow, Ui_CreateRecording):
    def __init__(self, api):
        super(CreateRecordingConfig, self).__init__()
        self.setupUi(self)
        self.api = api

        # -----------------------------------------
        # Initiate first tab: Fields
        # -----------------------------------------

        self.addFieldButton.clicked.connect(self.add_button_triggered)
        self.previewButton.clicked.connect(self.preview_button_triggered)

        self.field_model = CustomFieldModel()
        self.field_model.dataChanged.connect(self.custom_field_edited)
        self.field_model.setHorizontalHeaderLabels(['Field', 'Size', 'Remove'])

        self.customFieldTable.setModel(self.field_model)
        self.customFieldTable.clicked.connect(self.custom_field_table_clicked)
        #self.customFieldTable.itemDelegateForColumn(2, CustomFieldDelegate())

        self.customFieldTable.setItemDelegate(CustomFieldDelegate())
#        self.customFieldTable.setItemDelegateForColumn(2, CustomFieldDelegate())
        # -------------------------------------------

        self.struct_model = StructTreeModel()
        self.structureView.setModel(self.struct_model)
        self.struct_model.setHorizontalHeaderLabels(['Name', 'Size'])
        self.root_struct = StructTreeNode(CustomField('Data', size=''), 0)

        self.struct_model.appendRow(self.root_struct)

        # -----------------------------------------
        # Initiate second tab: Subscription
        # -----------------------------------------

        self.previewButton_sub.clicked.connect(self.preview_sub_button_triggered)

        self.struct_model_sub = StructTreeModel()
        self.struct_model_sub.setHorizontalHeaderLabels(['Name', 'Size'])
        self.structureView_sub.setModel(self.struct_model_sub)

        self.root_struct_sub = StructTreeNode(CustomField('Data', size=''), 0)

        self.root_struct_sub = StructTreeNode(CustomField(), 0)

        self.struct_model_sub.appendRow(self.root_struct_sub)

        self.structureView_sub.expandAll()
        self.structureView_sub.resizeColumnToContents(0)
        self.structureView_sub.resizeColumnToContents(1)

        self.structureView_sub.clicked.connect(self.structureView_sub_item_changed)


        # ---------------------------------------------
        # Internal variables
        # ---------------------------------------------
        self.boxes = []
        #self.selectionGrid.setAlignment(Qt.AlignTop)



    def showEvent(self, *args, **kwargs):
        pass

    def add_button_triggered(self):
        custom_field_item = CustomFieldItem(CustomField())

        self.field_model.appendRow(custom_field_item)
        self.customFieldTable.resizeColumnsToContents()

        for i in range(self.struct_model.rowCount()):
            index = self.struct_model.index(i, 2)
            #print(index)
            button = QPushButton('Remove')
            #self.customFieldTable.setIndexWidget(index, button)

    def preview_button_triggered(self):

        self.struct_model.clear()
        self.struct_model.setHorizontalHeaderLabels(['Name', 'Size'])

        self.root_struct = StructTreeNode(CustomField('Data', size=''), 0)
        self.struct_model.appendRow(self.root_struct)

        for i in range(self.field_model.rowCount()):
            field = self.field_model.item(i).object

            self.root_struct.appendRow(field)

        self.structureView.expandAll()
        self.structureView.resizeColumnToContents(0)
        self.structureView.resizeColumnToContents(1)

    def preview_sub_button_triggered(self):

        self.struct_model_sub.clear()
        self.struct_model_sub.setHorizontalHeaderLabels(['Name', 'Size'])

        self.root_struct_sub = StructTreeNode(CustomField('Data', size=''), 0)
        self.struct_model_sub.appendRow(self.root_struct_sub)

        for i in range(self.field_model.rowCount()):
            field = self.field_model.item(i).object
            self.root_struct_sub.appendRow(field)

        self.structureView_sub.expandAll()
        self.structureView_sub.resizeColumnToContents(0)
        self.structureView_sub.resizeColumnToContents(1)

    def custom_field_table_clicked(self, index):

        if index.isValid() is False:
            return None

        col = index.column()

        if col == 2:
            self.field_model.removeRow(index.row())

        #self.customFieldTable.

    def custom_field_edited(self, index, none):
        print('Edited !!')

    def structureView_sub_item_changed(self, index):
        if index.isValid() is False:
            return None

        item = self.structureView_sub.model().data(index, Qt.UserRole)

        if item is None:
            return


        for i in reversed(range(self.selectionGrid.count())):
                widget = self.selectionGrid.itemAt(i).widget()
                self.selectionGrid.removeWidget(widget)
                widget.setParent(None)

        self.selectionGrid.addWidget(QLabel('Plugin'), 0, 0)
        self.selectionGrid.addWidget(QLabel('Block'), 0, 1)
        self.selectionGrid.addWidget(QLabel('Signal'), 0, 2)

        self.boxes.clear()

        for i in range(1, int(item.size)+1):
            print('index' + str(i))
            newBoxes = {}
            newBoxes['item'] = item
            newBoxes['boxPlugin'] = QComboBox()
            newBoxes['boxBlock'] = QComboBox()
            newBoxes['boxSignal'] = QComboBox()

            newBoxes['boxPlugin'].currentIndexChanged.connect(lambda index = i,
                                                                     boxIndex = i-1 ,
                                                                     item = item:
                                                               self.selection_changed_plugin(index, boxIndex, item))

            newBoxes['boxBlock'].currentIndexChanged.connect(lambda index = i,
                                                                    boxIndex = i-1 ,
                                                                    item = item:
                                                             self.selection_changed_block(index, boxIndex, item))

            newBoxes['boxSignal'].currentIndexChanged.connect(lambda index = i,
                                                                    boxIndex = i-1 ,
                                                                    item = item:
                                                             self.selection_changed_signal(index, boxIndex, item))


            self.selectionGrid.addWidget(newBoxes['boxPlugin'], i, 0)
            self.selectionGrid.addWidget(newBoxes['boxBlock'], i, 1)
            self.selectionGrid.addWidget(newBoxes['boxSignal'], i, 2)


            dplugin_ids = self.api.get_all_plugins()
            for dplugin_id in dplugin_ids:
                dplugin = dplugin_ids[dplugin_id]

                if len(dplugin.get_dblocks()):
                    newBoxes['boxPlugin'].addItem(dplugin.uname)



                # for dblock_name in dplugin.get_dblocks():
                #     dblock = dplugin.get_dblock_by_name(dblock_name)
                #     newBoxes['boxBlocks'].addItem(dblock.name)

                    # for signal in dblock.get_signals():
                    #     boxSignals.addItem(signal)

            self.boxes.append(newBoxes)

    def selection_changed_plugin(self, index, boxIndex, item):

        if boxIndex >= len(self.boxes) :
            return

        boxPlugin = self.boxes[boxIndex]['boxPlugin']
        boxBlock = self.boxes[boxIndex]['boxBlock']
        boxSignal = self.boxes[boxIndex]['boxSignal']
        # --------------------
        # Remove old items
        # --------------------
        # for index in range(boxBlock.count()):
        #     print('del index' + str(index))
        #     boxBlock.removeItem(index)

        boxBlock.model().clear()
        boxSignal.model().clear()

        dplugin_name = boxPlugin.currentText()

        dplugin = self.api.get_dplugin_by_uname(dplugin_name)

        if dplugin is not None:

            for dblock_name in dplugin.get_dblocks():
                dblock = dplugin.get_dblock_by_name(dblock_name)
                boxBlock.addItem(dblock.name)


    def selection_changed_block(self, index, boxIndex, item):
        boxPlugin = self.boxes[boxIndex]['boxPlugin']
        boxBlock = self.boxes[boxIndex]['boxBlock']
        boxSignal = self.boxes[boxIndex]['boxSignal']

        boxSignal.model().clear()

        dplugin_name = boxPlugin.currentText()
        dblock_name = boxBlock.currentText()

        dplugin = self.api.get_dplugin_by_uname(dplugin_name)

        if dplugin is not None:

            dblock = dplugin.get_dblock_by_name(dblock_name)

            if dblock is not None:

                if len(dblock.get_signals()):
                    for signal in dblock.get_signals():
                        boxSignal.addItem(signal.uname)
                else:
                    item.save[boxIndex] = None
            else:
                item.save[boxIndex] = None
        else:
            item.save[boxIndex] = None

                    #item.save[boxIndex] = 'QUARK'
    def selection_changed_signal(self, index, boxIndex, item):
        boxPlugin = self.boxes[boxIndex]['boxPlugin']
        boxBlock = self.boxes[boxIndex]['boxBlock']
        boxSignal = self.boxes[boxIndex]['boxSignal']


        dplugin_name = boxPlugin.currentText()
        dblock_name = boxBlock.currentText()
        dsignal_name = boxSignal.currentText()


        item.save[boxIndex] = dplugin_name + "::" + dblock_name + "::" + dsignal_name

        print(item.save)

class CRC(vip_base):


    def initiate_layer_0(self, config=None):


        self.widget = CreateRecordingConfig(self.control_api)

        self.set_widget_for_internal_usage( self.widget )


        # ---------------------------
        # Create Parameters
        # ---------------------------
        para_list = []

        # build parameter list to send to Core
        self.send_new_parameter_list(para_list)


        return True

    def show_context_menu(self, pos):
        gloPos = self.widget.mapToGlobal(pos)
        self.cmenu = self.create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def pause(self):
        # will be called, when plugin gets paused
        # can be used to get plugin in a defined state before pause
        # e.a. close communication ports, files etc.
        pass

    def resume(self):
        # will be called when plugin gets resumed
        # can be used to wake up the plugin from defined pause state
        # e.a. reopen communication ports, files etc.
        pass

    def cb_execute(self, Data=None, block_name = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data[CORE_TIME_SIGNAL] = [t1, t2, ...] where CORE_TIME_SIGNAL is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []

        pass

    def set_parameter(self, name, value):
        pass

    def quit(self):
        # do something before plugin will close, e.a. close connections ...
        pass


    def get_plugin_configuration(self):
        #
        # Implement a own part of the config
        # config is a hash of hass object
        # config_parameter_name : {}
        # config[config_parameter_name]['value']  NEEDS TO BE IMPLEMENTED
        # configs can be marked as advanced for create dialog
        # http://utilitymill.com/utility/Regex_For_Range
        config = {}
        return config

    def plugin_meta_updated(self):
        """
        Whenever the meta information is updated this function is called (if implemented).

        :return:
        """
        pass

class CustomField():
    def __init__(self, desc='Data::force::sensor', size='3'):
        self.desc = desc
        self.size = size
        if size is not '':
            self.save = [None] * int(size)

class CustomFieldItem(QStandardItem):
    def __init__(self, custom_field):
        super().__init__()

        self.object = custom_field

    def get_decoration(self):
        return None

    def data(self, role):
        """
        For Qt.Role see 'http://qt-project.org/doc/qt-4.8/qt.html#ItemDataRole-enum'
        :param role:
        :return:
        """

        if role == Qt.ToolTipRole:
            return None

        if role == Qt.DisplayRole:
            return None

        if role == Qt.DecorationRole:
            return self.get_decoration()

        if role == Qt.UserRole:
            return self.object

        if role == Qt.EditRole:
            return None

        return None

class CustomTreeItem(QStandardItem):
    def __init__(self, custom_field):
        super().__init__()

        self.object = custom_field

    def get_decoration(self):
        return None

    def data(self, role):
        """
        For Qt.Role see 'http://qt-project.org/doc/qt-4.8/qt.html#ItemDataRole-enum'
        :param role:
        :return:
        """

        if role == Qt.ToolTipRole:
            return self.tool_tip

        if role == Qt.DisplayRole:
            return self.object.desc

        if role == Qt.DecorationRole:
            return self.get_decoration()

        if role == Qt.UserRole:
            return self.object

        if role == Qt.EditRole:
            return None

        return None

class CustomFieldModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(CustomFieldModel, self).__init__(parent)

    def data(self, index, role):
        """
        For Qt.Role see 'http://qt-project.org/doc/qt-4.8/qt.html#ItemDataRole-enum'
        :param index:
        :param role:
        :return:
        """

        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.ToolTipRole:
            return super(CustomFieldModel, self).data(index, Qt.ToolTipRole)

        if role == Qt.DisplayRole:

            if col == 0:
                field = super(CustomFieldModel, self).data(index, Qt.UserRole)
                return field.desc
            if col == 1:
                index_sibling = index.sibling(row, col-1)
                field = super(CustomFieldModel, self).data(index_sibling, Qt.UserRole)
                return field.size
            if col == 2:
                return None

        if role == Qt.DecorationRole:
            if col == 2:
                return None

        if role == Qt.UserRole:
            pass

        if role == Qt.EditRole:
            if col == 0:
                field = super(CustomFieldModel, self).data(index, Qt.UserRole)
                return field.desc
            if col == 1:
                index_sibling = index.sibling(row, col-1)
                field = super(CustomFieldModel, self).data(index_sibling, Qt.UserRole)
                return field.size
            if col == 2:
                return None

        return None

    def setData(self, index, value, role):
        """
        This function is called when a content in a row is edited by the user.

        :param index: Current selected index.
        :param value: New value from user
        :param role:
        :return:
        """

        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.EditRole:

            if col == 0:

                field = super(CustomFieldModel, self).data(index, Qt.UserRole)
                field.desc = value
                self.dataChanged.emit(index, None)

                return True

            if col == 1:
                index_sibling = index.sibling(row, col-1)
                field = super(CustomFieldModel, self).data(index_sibling, Qt.UserRole)
                field.size = value
                self.dataChanged.emit(index, None)

        return False

    def flags(self, index):


        parent = index.parent()
        flags = parent.flags()

        row = index.row()
        col = index.column()

        if col == 2:
            flags ^= ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable
            return flags
        flags ^=Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return flags

class StructTreeModel(PaPITreeModel):
    """
    This model is used to handle Plugin objects in TreeView created by the yapsy plugin manager.
    """
    def __init__(self, parent=None):
        super(StructTreeModel, self).__init__(parent)

    def data(self, index, role):
        """
        For Qt.Role see 'http://qt-project.org/doc/qt-4.8/qt.html#ItemDataRole-enum'
        :param index:
        :param role:
        :return:
        """

        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.ToolTipRole:
            return super(StructTreeModel, self).data(index, Qt.ToolTipRole)

        if role == Qt.DisplayRole:

            if col == 0:
                return super(StructTreeModel, self).data(index, Qt.DisplayRole)

            if col == 1:
                index_sibling = index.sibling(row, col-1)

                item = super(StructTreeModel, self).data(index_sibling, Qt.UserRole)
                if item is not None:
                    return item.size
            if col == 2:
                return None

        if role == Qt.DecorationRole:
            pass

        if role == Qt.UserRole:
            if col == 0:
                return super(StructTreeModel, self).data(index, Qt.UserRole)
            if col == 1:
                index_sibling = index.sibling(row, col-1)
                return super(StructTreeModel, self).data(index_sibling, Qt.UserRole)
        if role == Qt.EditRole:
            pass

        return None

    def flags(self, index):

        parent = index.parent()
        flags = parent.flags()

        if not index.isValid():
            return flags

        row = index.row()
        col = index.column()
        flags ^= Qt.ItemIsEnabled & ~Qt.ItemIsSelectable

        if col == 0:
            item = super(StructTreeModel, self).data(index, Qt.UserRole)

            if item is not None:
                if item.size != '':
                    flags |= Qt.ItemIsSelectable

        if col == 1:
            index_sibling = index.sibling(row, col-1)
            item = super(StructTreeModel, self).data(index_sibling, Qt.UserRole)
            if item is not None:
                if item.size != '':
                    flags |= Qt.ItemIsSelectable

        if col == 2:
            return flags

        return flags

class StructTreeNode(QStandardItem):
    """
    This model is used to handle Plugin objects in TreeView created by the yapsy plugin manager.
    """
    def __init__(self, field, level, flags=~Qt.ItemIsEnabled, parent=None):

        elements = str.split(field.desc, "::")

        self.nodes = {}
        self.level = level
        self.time_identifier = 'time'
        self.ptime_identifier = 'ptime'
        self.size = ''
        self.field = ''
        self.object = field
        self.flags = flags

        super(StructTreeNode, self).__init__(elements[self.level])

        self.appendRow(field)

    def appendRow(self, field):

        elements = str.split(field.desc, "::")

        # Node is responsible for the first element

        if len(elements) > self.level + 1:

            if self.time_identifier not in self.nodes:

                struct_node = QStandardItem(self.time_identifier)
#                struct_node = StructTreeNode(CustomField(desc=self.time_identifier, size=''), 0)
                struct_node.setColumnCount(2)

                self.nodes[self.time_identifier] = struct_node
                super(StructTreeNode, self).appendRow(struct_node)

            if self.ptime_identifier not in self.nodes:
                struct_node = QStandardItem(self.ptime_identifier)
                #struct_node = StructTreeNode(CustomField(desc=self.ptime_identifier, size=''), 0)
                struct_node.setColumnCount(2)

                self.nodes[self.ptime_identifier] = struct_node
                super(StructTreeNode, self).appendRow(struct_node)

            if elements[self.level + 1] not in self.nodes:
                struct_node = StructTreeNode(field, self.level + 1)
                struct_node.setColumnCount(2)

                self.nodes[elements[self.level + 1]] = struct_node
                super(StructTreeNode, self).appendRow(struct_node)

                self.field = elements[self.level]

            if elements[self.level + 1] in self.nodes:
                self.nodes[elements[self.level + 1]].appendRow(field)

            self.object = None
        else:
            self.field = elements[self.level]

    def data(self, role):
        """
        For Qt.Role see 'http://qt-project.org/doc/qt-4.8/qt.html#ItemDataRole-enum'
        :param role:
        :return:
        """
        if role == Qt.ToolTipRole:
            return None

        if role == Qt.DisplayRole:
            return self.field

        if role == Qt.DecorationRole:
            return None

        if role == Qt.UserRole:
            return self.object

        if role == Qt.EditRole:
            return None

        return None

    def flags(self, index):
        return self.flags

class CustomFieldDelegate (QStyledItemDelegate):
    def paint(self, painter, option, index):

        if index.column() == 2:

            button = QStyleOptionButton()
            r = option.rect # getting the rect of the cell

            x = r.left()
            y = r.top()
            w = r.width()
            h = r.height()
            button.rect = QRect(x, y, w, h)
            button.text = "X"
            button.state = QStyle.State_Enabled;

            QApplication.style().drawControl(QStyle.CE_PushButton, button, painter)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)