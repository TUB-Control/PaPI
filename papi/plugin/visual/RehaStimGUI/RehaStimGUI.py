#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
<Stefan Ruppin
"""

__author__ = 'Knuth'


from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter
import papi.constants as pc

import time

from PyQt5 import QtGui, QtWidgets, QtCore, Qt

class OptionItem():
    def __init__(self):
        self.attributes = {'1_amplitude' : 0, '2_min' : 0, '3_max': 0, '4_wave_form' : 'Sinus'}

    def set_attr(self, attr, value):
        if attr in self.attributes:
            self.attributes[attr] = value

    def get_value(self, attr):
        if attr in self.attributes:
            return self.attributes[attr]

    def get_attributes(self):
        return self.attributes

#RENAME TO PLUGIN NAME
class RehaStimGUI(vip_base, object):

    def __init__(self):

        pass

    def initiate_layer_0(self, config=None):

        self.widget = self.create_widget()
        self.create_actions()

        self.set_widget_for_internal_usage( self.widget )

        self.current_state = None

        # ---------------------------
        # Create Parameters
        # ---------------------------
        para_list = []
        self.send_new_parameter_list(para_list)


        # ---------------------------
        # Create default structure
        # ---------------------------

        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(1)

        self.tableWidget.setCellWidget(0, 0, QtWidgets.QLabel())

        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.button_group = QtWidgets.QButtonGroup()

        # -----------------------
        # Custom configuration
        # -----------------------

        self.pal_cell_selected = QtGui.QPalette()
        self.pal_cell_selected.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 255))
        #self.pal_cell_selected.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 100))
        #self.pal_cell_selected.setColor(QtGui.QPalette.Base, QtGui.QColor(0, 0, 100))
        #self.pal_cell_selected.setColor(QtGui.QPalette.Button, QtGui.QColor(0, 0, 100))

        # -

        #
        # TESTING
        #

        for i in range(9):
            self.add_ch_clicked()
            self.add_state_clicked()
        return True

    def create_widget(self):

        # -------------------
        # Create structure
        # -------------------

        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setObjectName('centralwidget')
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)

        # -------------------
        # Create and add table
        # -------------------


        #self.tableWidget = QtWidgets.QWidget()
        self.tableWidget = QtWidgets.QTableWidget()
        self.verticalLayout.addWidget(self.tableWidget)
#        self.tableWidget.horizontalHeader().setStretchLastSection(True)
#        self.tableWidget.verticalHeader().setStretchLastSection(True)

#        self.tableWidget.horizontalHeader().setVisible(False)
#        self.tableWidget.verticalHeader().setVisible(False)

        # -------------------
        # Add Buttons: Config
        # -------------------

        self.configButtonsWidget = QtWidgets.QWidget()

        self.configButtonHLayout = QtWidgets.QHBoxLayout(self.configButtonsWidget)

        self.saveConfigButton = QtWidgets.QPushButton("Save")
        self.loadConfigButton = QtWidgets.QPushButton("Load")
        self.sendConfigButton = QtWidgets.QPushButton("Send")

        self.configButtonHLayout.addWidget(self.saveConfigButton)
        self.configButtonHLayout.addWidget(self.loadConfigButton)
        self.configButtonHLayout.addWidget(self.sendConfigButton)

        self.verticalLayout.addWidget(self.configButtonsWidget)

        # -------------------
        # Add Buttons: State/Channels
        # -------------------

        self.tableButtonsWidget = QtWidgets.QWidget()

        self.tableButtonHLayout = QtWidgets.QHBoxLayout(self.tableButtonsWidget)

        self.addStateButton = QtWidgets.QPushButton("Add State")
        self.addChButton = QtWidgets.QPushButton("Add Ch")

        self.tableButtonHLayout.addWidget(self.addStateButton)
        self.tableButtonHLayout.addWidget(self.addChButton)

        self.verticalLayout.addWidget(self.tableButtonsWidget)

        return self.centralwidget

    def create_actions(self):
        self.addChButton.clicked.connect(self.add_ch_clicked)
        self.addStateButton.clicked.connect(self.add_state_clicked)
        self.sendConfigButton.clicked.connect(self.send_config_clicked)

    def show_context_menu(self, pos):
        gloPos = self.LcdWidget.mapToGlobal(pos)
        self.cmenu = self.create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def add_state_clicked(self, flag=None, option_item = OptionItem()):
        curCount = self.tableWidget.columnCount()
        self.tableWidget.setColumnCount( curCount + 1 )
        self.tableWidget.resizeColumnsToContents()

        self.add_missing_cell_items()

        for r in range(1, self.tableWidget.rowCount()):
            optionWidget = OptionWidget('ROW')
            optionWidget.set_option_item(option_item)
            self.tableWidget.setCellWidget(r, curCount, optionWidget)

    def add_ch_clicked(self, flag=None, option_item = OptionItem()):
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.setRowCount( rowCount + 1 )
        self.tableWidget.resizeRowsToContents()

        self.add_missing_cell_items()

        # Add missing option widgets

        for c in range(1, self.tableWidget.columnCount()):
            optionWidget = OptionWidget('COl')
            optionWidget.set_option_item(option_item)
            self.tableWidget.setCellWidget(rowCount, c, optionWidget)

        self.select_state_widget(self.current_state)

    def send_config_clicked(self):
        stateWidget = self.current_state

        if stateWidget is None:
            return

        for c in range(1, self.tableWidget.columnCount()):
            if stateWidget == self.tableWidget.cellWidget(0, c):
                self.tableWidget.selectColumn(c)

                for r in range(1, self.tableWidget.rowCount()):
                    cItem = self.tableWidget.cellWidget(r, c)


    def add_missing_cell_items(self):

        for c in range(1, self.tableWidget.columnCount()):

            if not isinstance(self.tableWidget.cellWidget(0, c), CellWidget):
                cellWidget = StateWidget('State' + str(c))
                cellWidget.trigger_remove_cell.connect(self.remove_cell_widget)
                cellWidget.trigger_select_state.connect(self.select_state_widget)

                self.tableWidget.setCellWidget(0, c, cellWidget)

                self.button_group.addButton(cellWidget.get_radio_button())

        for r in range(1, self.tableWidget.rowCount()):

            if not isinstance(self.tableWidget.cellWidget(r, 0), CellWidget):
                cellWidget = ChannelWidget('Ch' + str(r))
                cellWidget.trigger_remove_cell.connect(self.remove_cell_widget)
                self.tableWidget.setCellWidget(r, 0, cellWidget)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def get_channel_widget(self, text):
        ch_widget = QtWidgets.QLineEdit(text)
        return ch_widget

    def get_state_widget(self, text):
        st_widget = QtWidgets.QLineEdit(text)
        return st_widget

    def remove_cell_widget(self, cellWidget):

        if isinstance(cellWidget, StateWidget):
            for c in range(1, self.tableWidget.columnCount()):
                if cellWidget == self.tableWidget.cellWidget(0, c):
                    self.tableWidget.removeColumn(c)

        if isinstance(cellWidget, ChannelWidget):
            for r in range(1, self.tableWidget.rowCount()):
                if cellWidget == self.tableWidget.cellWidget(r, 0):
                    self.tableWidget.removeRow(r)


    def unselect_state_widget(self, stateWidget):

        if stateWidget is None:
            return

        if isinstance(stateWidget, StateWidget):
            for c in range(1, self.tableWidget.columnCount()):
                if stateWidget == self.tableWidget.cellWidget(0, c):
                    self.tableWidget.selectColumn(c)

                    for r in range(1, self.tableWidget.rowCount()):
                        cItem = self.tableWidget.cellWidget(r, c)
                        cItem.setPalette(QtGui.QPalette())
                        cItem.setBackgroundRole(QtGui.QPalette.NoRole)
                        cItem.setAutoFillBackground(True)




    def select_state_widget(self, stateWidget):
        if stateWidget is None:
            return

        self.unselect_state_widget(self.current_state)

        if isinstance(stateWidget, StateWidget):
            for c in range(1, self.tableWidget.columnCount()):
                if stateWidget == self.tableWidget.cellWidget(0, c):
                    self.tableWidget.selectColumn(c)
                    self.current_state = stateWidget
                    for r in range(1, self.tableWidget.rowCount()):
                        cItem = self.tableWidget.cellWidget(r, c)
                        cItem.setPalette(self.pal_cell_selected)
                        cItem.setBackgroundRole(QtGui.QPalette.Highlight)
                        cItem.setAutoFillBackground(True)


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

    def execute(self, Data=None, block_name = None, plugin_uname = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data['t'] = [t1, t2, ...] where 't' is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []
        pass

    def set_parameter(self, name, value):
        # attetion: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value
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


class OptionWidget(QtWidgets.QWidget):
    def __init__(self, text):
        super(OptionWidget, self).__init__()

        self.option_item = None

        # Create structure

        self.hLayout = QtWidgets.QHBoxLayout(self)
        self.hLayout.setContentsMargins(0, 0, 0, 0)

        # Add label for option

        self.label = QtWidgets.QLabel(text)

        self.label.mouseDoubleClickEvent = self.open_option_dialog

        self.hLayout.addWidget(self.label)

        self.option_dialog = OptionDialog()


    def open_option_dialog(self, event):
        if self.option_dialog is not None:
            self.option_dialog.exec_()
            self.option_dialog.raise_()
            self.option_dialog.activateWindow()

    def set_option_item(self, oItem):
        self.option_item = oItem
        self.option_dialog.set_option_item(oItem)


class OptionDialog(QtWidgets.QDialog):
    def __init__(self):
        super(OptionDialog, self).__init__()

        self.setWindowTitle('Option')

        self.vLayout = QtWidgets.QVBoxLayout(self)

        self.saveButton = QtWidgets.QPushButton('Save')
        self.saveButton.clicked.connect(self.save_button_clicked)
        self.attributes_widget = QtWidgets.QWidget()

        self.gLayout = QtWidgets.QGridLayout(self.attributes_widget)

        self.vLayout.addWidget(self.attributes_widget)
        self.vLayout.addWidget(self.saveButton)


        self.labels = []
        self.edits = []

    def set_option_item(self, oItem):
        self.option_item = oItem
        count = 0
        if not isinstance(self.option_item, OptionItem):
            return

        for attr in sorted(self.option_item.get_attributes()):
            value = self.option_item.get_value(attr)

            label = QtWidgets.QLabel(str(attr))
            edit = QtWidgets.QLineEdit(str(value))
            self.labels.append(label)
            self.edits.append(edit)

            self.gLayout.addWidget(label, count, 0)
            self.gLayout.addWidget(edit, count, 1)
            count += 1

    def save_button_clicked(self):
        print('Save Config !!!')
        self.close()


class CellWidget(QtWidgets.QWidget):

    trigger_remove_cell = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, text):
        super(CellWidget, self).__init__()
        self.cell_name = text

        # Create structure

        self.hLayout = QtWidgets.QHBoxLayout(self)
        self.hLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(self.cell_name)
        self.label.mouseDoubleClickEvent = self.label_clicked

        self.line_edit = QtWidgets.QLineEdit(self.cell_name)
        self.line_edit.setVisible(False)
        self.line_edit.editingFinished.connect(self.line_edited)
        # Widget for the buttons

        self.bWidget = QtWidgets.QWidget()

        self.vLayout = QtWidgets.QVBoxLayout(self.bWidget)
        self.vLayout.setContentsMargins(0, 0, 0, 0)

        self.delete_button = QtWidgets.QPushButton('X')
        self.select_button = QtWidgets.QRadioButton()

        self.delete_button.setFixedSize(20, 20)
        self.select_button.setFixedSize(20, 20)

        self.vLayout.addWidget(self.delete_button)
        self.vLayout.addWidget(self.select_button)

        # Add widgets

        self.hLayout.addWidget(self.label)
        self.hLayout.addWidget(self.line_edit)
        self.hLayout.addWidget(self.bWidget)

        # Actions

        self.delete_button.clicked.connect(self.remove_cell_widget)

    def label_clicked(self, event):
        print('Clicked on ' + self.cell_name)

        self.label.setVisible(False)
        self.line_edit.setVisible(True)


        #self.line_edit.setFocus(Qt.Focu)

    def line_edited(self):

        self.cell_name = self.line_edit.text()

        self.label.setText(self.cell_name)

#        print("NewText: " + self.cell_name)
 #       print(self.label.text())

        self.label.setVisible(True)
        self.line_edit.setVisible(False)

    def remove_cell_widget(self):
        self.trigger_remove_cell.emit(self)

class StateWidget(CellWidget):
    trigger_select_state = QtCore.pyqtSignal(QtWidgets.QWidget)
    def __init__(self, text):
        super(StateWidget, self).__init__(text)
        self.select_button.clicked.connect(self.state_selected)

    def state_selected(self):
        self.trigger_select_state.emit(self)

    def get_radio_button(self):
        return self.select_button


class ChannelWidget(CellWidget):

    def __init__(self, text):
        super(ChannelWidget, self).__init__(text)
        self.select_button.setVisible(False)