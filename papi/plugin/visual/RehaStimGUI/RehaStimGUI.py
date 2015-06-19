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

import traceback
import datetime
import time
import json

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter
from papi.data.DPlugin import DBlock
from papi.data.DSignal import DSignal
from papi.plugin.base_classes.pcp_base import pcp_base

import papi.constants as pc

from PyQt5 import QtGui, QtWidgets, QtCore, Qt
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

import xml.etree.cElementTree as ET

class OptionItem():
    def __init__(self):
        self.attributes = {'1_Min': {
            'value': '0',
            'min': '0.9',
            'max': '1',
            'display_name' : 'Min',
            'regex' : pc.REGEX_SINGLE_UNSIGNED_FLOAT_FORCED
        }, '2_Max': {
            'value': '0',
            'min': '0.5',
            'max': '1',
            'display_name' : 'Max',
            'regex' : pc.REGEX_SINGLE_UNSIGNED_FLOAT_FORCED
        }, '3_Rise': {
            'value': '5',
            'min': '0',
            'max': '100',
            'display_name' : 'Rise',
            'regex' : pc.REGEX_SINGLE_UNSIGNED_FLOAT_FORCED

        }, '4_Type': {
            'value': 'ramp',
            'options': "ramp, trapez",
            'display_name' : 'Type'
        }}


    def set_attr(self, attr, value):
        self.attributes[attr] = value

    def get_attr(self, attr):
        if attr in self.attributes:
            return self.attributes[attr]

    def get_attributes(self):
        return self.attributes

    def clear_attribtues(self):
        self.attributes = {}

#RENAME TO PLUGIN NAME
class RehaStimGUI(pcp_base, object):

    def __init__(self):
        self.__VERSION__ = "0.1"

#        self.row_offset = 1;
#        self.col_offset = 1;

        self.signal_next_state = "next_state"

        pass

    def initiate_layer_0(self, config=None):

        self.widget = self.create_widget()
        self.create_actions()

        self.set_widget_for_internal_usage( self.widget )

        self.current_state = None

        # ---------------------------
        # Create signals
        # ---------------------------

        block = DBlock('Stimulator Configuration')
        signal = DSignal('Array')
        block.add_signal(signal)

        self.send_new_block_list([block])

        # ---------------------------
        # Create Parameters
        # ---------------------------
        para_list = []

        self.set_curent_state = DParameter('SetState', default=0)

        para_list.append(self.set_curent_state)

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
        self.loadConfigButton.clicked.connect(self.load_config_clicked)
        self.saveConfigButton.clicked.connect(self.save_config_clicked)

    def show_context_menu(self, pos):
        gloPos = self.LcdWidget.mapToGlobal(pos)
        self.cmenu = self.create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def load_config_clicked(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(caption="Open File", filter="Config (*xml)")[0]

        if filename == '':
            return

        tree = ET.parse(filename)

        root = tree.getroot()

        for tag_xml in root:
            if tag_xml.tag == "Option":
                for option_tml in tag_xml:
                    if option_tml.tag == "ColumnCount":
                        rowCount = int(option_tml.text)

                        self.tableWidget.setRowCount(rowCount)

                    if option_tml.tag == "RowCount":
                        columnCount = int(option_tml.text)

                        self.tableWidget.setColumnCount(columnCount)

            if tag_xml.tag == "Cells":
                for cell_xml in tag_xml:
                    col = int(cell_xml.get('col'))
                    row = int(cell_xml.get('row'))
                    type = cell_xml.get('type')

                    cellWidget = None
                    if type in ['StateWidget']:
                        cellWidget = StateWidget()

                        cellWidget.trigger_remove_cell.connect(self.remove_cell_widget)
                        cellWidget.trigger_select_state.connect(self.select_state_widget)

                        self.button_group.addButton(cellWidget.get_radio_button())

                    if type in ['ChannelWidget']:
                        cellWidget = ChannelWidget()
                        cellWidget.trigger_remove_cell.connect(self.remove_cell_widget)

                    if type == 'OptionWidget':
                        cellWidget = OptionWidget()

                    cellWidget.readOptionXML(cell_xml)

                    self.tableWidget.setCellWidget(col, row, cellWidget)

        self.adjust()

    def save_config_clicked(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(caption="Open File", filter="Config (*xml)")[0]


        if filename[-4:] != '.xml':
            filename += '.xml'

        try:

            root = ET.Element("RehaStimGUI_Config")
            root.set('Date', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            root.set('PaPI_version', pc.CORE_PAPI_VERSION)
            root.set('plugin_version', self.__VERSION__)

            # -------------------------------
            # Store options
            # -------------------------------

            option = ET.SubElement(root, 'Option')

            columnCount = ET.SubElement(option, 'ColumnCount')
            columnCount.text = str(self.tableWidget.rowCount())
            rowCount = ET.SubElement(option, 'RowCount')
            rowCount.text = str(self.tableWidget.columnCount())

            # -------------------------------
            # Store information about cells
            # -------------------------------

            cell_widgets = ET.SubElement(root, "Cells")

            for c in range(0, self.tableWidget.rowCount()):

                for r in range(0, self.tableWidget.columnCount()):
                    celllWidget  = self.tableWidget.cellWidget(c, r)

                    if (r, c) == (0, 0):
                        continue

                    cell_xml = ET.SubElement(cell_widgets, "Cell")

                    if isinstance(celllWidget, StateWidget):
                        cell_xml.set('type', 'StateWidget')

                    if isinstance(celllWidget, ChannelWidget):
                        cell_xml.set('type', 'ChannelWidget')

                    if isinstance(celllWidget, OptionWidget):
                        cell_xml.set('type', 'OptionWidget')


                    celllWidget.fillOptionXML(cell_xml)

                    cell_xml.set('row', str(r))
                    cell_xml.set('col', str(c))



            self.indent(root)
            tree = ET.ElementTree(root)
            tree.write(filename)

        except Exception as E:
            tb = traceback.format_exc()
            self.error_occured.emit("Error: Config Loader", "Not saveable: " + filename, tb)

    def clear(self):
        for button in self.button_group.buttons():
            self.button_group.removeButton(button)

    def adjust(self):
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def add_state_clicked(self, flag=None, option_item = OptionItem()):
        curCount = self.tableWidget.columnCount()
        self.tableWidget.setColumnCount( curCount + 1 )
        self.tableWidget.resizeColumnsToContents()

        self.add_missing_cell_items()

        for r in range(1, self.tableWidget.rowCount()):
            optionWidget = OptionWidget()
            optionWidget.set_option_item(option_item)
            self.tableWidget.setCellWidget(r, curCount, optionWidget)

        self.adjust()

    def add_ch_clicked(self, flag=None, option_item = OptionItem()):
        rowCount = self.tableWidget.rowCount()
        self.tableWidget.setRowCount( rowCount + 1 )
        self.tableWidget.resizeRowsToContents()

        self.add_missing_cell_items()

        # Add missing option widgets

        for c in range(1, self.tableWidget.columnCount()):
            optionWidget = OptionWidget()
            optionWidget.set_option_item(option_item)
            self.tableWidget.setCellWidget(rowCount, c, optionWidget)

        self.select_state_widget(self.current_state)

        self.adjust()

    def send_config_clicked(self):
        stateWidget = self.current_state


        simulink_cfg = self.create_config_for_simulink_block(current_state=None)


        print(len(simulink_cfg))

        self.send_parameter_change(str(simulink_cfg), "Stimulator Configuration")

        if stateWidget is None:
            return



#        json_config = self.create_json_for_state(stateWidget)

#        print(json_config)


    def add_missing_cell_items(self):

        for c in range(1, self.tableWidget.columnCount()):

            if not isinstance(self.tableWidget.cellWidget(0, c), HeaderWidget):
                cellWidget = StateWidget('State' + str(c))
                cellWidget.trigger_remove_cell.connect(self.remove_cell_widget)
                cellWidget.trigger_select_state.connect(self.select_state_widget)

                self.tableWidget.setCellWidget(0, c, cellWidget)

                self.button_group.addButton(cellWidget.get_radio_button())

        for r in range(1, self.tableWidget.rowCount()):

            if not isinstance(self.tableWidget.cellWidget(r, 0), HeaderWidget):
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

    def create_config_for_simulink_block(self, current_state = None):

        simulink_cfg = []


        for c in range (1, self.tableWidget.columnCount()):
            for r in range(0, self.tableWidget.rowCount()):

                cellWidget = self.tableWidget.cellWidget(r, c)

                cfg = cellWidget.getCfgAsArray()
                if r == 0:
                    state = c


                    next_flag = 0

                    if cellWidget == current_state:
                        next_flag = 1

                    cfg = [ state, next_flag ] + cfg

                simulink_cfg += cfg

        return simulink_cfg

    def create_json_for_state(self, stateWidget):

        json_cfg = {}
        if isinstance(stateWidget, StateWidget):
            for c in range(1, self.tableWidget.columnCount()):
                if stateWidget == self.tableWidget.cellWidget(0, c):
                    self.tableWidget.selectColumn(c)

                    json_cfg['active_state'] = stateWidget.label.text()

                    for r in range(1, self.tableWidget.rowCount()):
                        cellWidget = self.tableWidget.cellWidget(r, c)

                        channelWidget = self.tableWidget.cellWidget(r, 0)

                        json_cfg[channelWidget.label.text()] = cellWidget.getCfgAsDict()


        json_str = json.dumps(json_cfg)

        return json_str

    def select_state_widget(self, stateWidget):
        if stateWidget is None:
            return

        old_stateWidget = self.current_state

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

        simulink_cfg = self.create_config_for_simulink_block(current_state=old_stateWidget)

        print(len(simulink_cfg))

        self.send_parameter_change(str(simulink_cfg), "Stimulator Configuration")

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

        if self. signal_next_state in Data:
            next_state = Data[self.signal_next_state][0]

            print("Set state to: " + str(next_state))

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

    def indent(self, elem, level=0):
        """
        Function which will apply a nice looking indentiation to xml structure before save. Better readability.
        copied from http://effbot.org/zone/element-lib.htm#prettyprint 06.10.2014 15:53

        :param elem:
        :param level:
        :return:
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


class OptionWidget(QtWidgets.QWidget):
    """
    This widget is used as a cell widget for the table widget which contains all attributes
    for a pair of channel and state which can be changed by the user.

    """
    def __init__(self, option_item = OptionItem()):
        super(OptionWidget, self).__init__()

        self.option_item = None

        self.labels = []
        self.lines = []
        self.attrs = []

        self.gLayout = QtWidgets.QGridLayout(self)
        self.gLayout.setContentsMargins(0, 0, 0, 0)

        self.set_option_item(option_item)

    def create_structure(self):
        """
        Adds all labels and fields at the grid layout

        :return:
        """
        for i in range(len(self.lines)):
            self.gLayout.addWidget(self.labels[i], i, 0)
            self.gLayout.addWidget(self.lines[i], i, 1)

        pass

    def set_option_item(self, oItem):
        """
        Used to set a new option item and triggers a rebuild of the grid layout

        :param oItem:
        :return:
        """

        self.option_item = oItem

        self.lines.clear()
        self.labels.clear()
        self.attrs.clear()

        for key in sorted(self.option_item.get_attributes()):
            attr = self.option_item.get_attr(key)

            if 'display_name' in attr:
                self.labels.append(QtWidgets.QLabel(attr['display_name']))
            else:
                self.labels.append(QtWidgets.QLabel(key))

            self.lines.append(RehaStimEditableField(attr))

            self.attrs.append(key)

        self.create_structure()

    def fillOptionXML(self, cell_xml : ET.Element):
        """
        Used for saving the current configuration.

        :param cell_xml:
        :return:
        """
        self.updateOptionItem()

        attrs_xml = ET.SubElement(cell_xml, "Attributes")

        for key in sorted(self.option_item.get_attributes()):

            attr = self.option_item.get_attr(key)

            attr_xml = ET.SubElement(attrs_xml, "Attribute")
            attr_xml.set('name', key)

            for attr_key in attr:

                attr_key_xml = ET.SubElement(attr_xml, attr_key)

                attr_key_xml.text = str(attr[attr_key])

    def updateOptionItem(self):
        """
        Updates the interal option item by the current user input.

        :return:
        """
        for i in range(len(self.labels)):
            self.option_item.attributes[self.attrs[i]]['value'] = str(self.lines[i].get_value())

    def getCfgAsDict(self):

        cfg = {}
        for i in range(len(self.labels)):

            attr_name = self.option_item.attributes[self.attrs[i]]['display_name']

            cfg[attr_name] = str(self.lines[i].get_value())

        return cfg

    def getCfgAsArray(self):
        cfg = []

        for i in range(len(self.labels)):

            value = self.lines[i].get_value()

            attr_name = self.option_item.attributes[self.attrs[i]]['display_name']

            if attr_name == "Type":
                if value == "ramp":
                    cfg.append(1)
                elif value == "trapez":
                    cfg.append(2)
                else:
                    cfg.append(0)

                continue

            cfg.append(float(value))

        return cfg

    def readOptionXML(self, cell_xml : ET.Element):
        """
        Used for loading a new configuration

        :param cell_xml:
        :return:
        """
        attrs_xml = cell_xml.find('Attributes')

        new_oItem = OptionItem()
        new_oItem.clear_attribtues()

        for attr_xml in attrs_xml:
            attr_name = attr_xml.get('name')

            value = {}

            for attr_key_xml in attr_xml:

                value[attr_key_xml.tag] = attr_key_xml.text


            new_oItem.set_attr(attr_name, value)

        self.set_option_item(new_oItem)


class HeaderWidget(QtWidgets.QWidget):
    """
    This cell widget is used as a cell widget in table view and describe
    a single horizontal and vertical header.

    """
    trigger_remove_cell = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, text="Header"):
        super(HeaderWidget, self).__init__()
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

        self.hBLayout = QtWidgets.QHBoxLayout(self.bWidget)
        self.hBLayout.setContentsMargins(0, 0, 0, 0)
        self.hBLayout.setAlignment(QtCore.Qt.AlignRight)
        self.delete_button = QtWidgets.QPushButton('X')
        self.select_button = QtWidgets.QRadioButton()

        self.delete_button.setFixedSize(20, 20)
        self.select_button.setFixedSize(20, 20)

        self.hBLayout.addWidget(self.delete_button)
        self.hBLayout.addWidget(self.select_button)


        self.duration_edit = QtWidgets.QLineEdit("0")
        self.duration_edit.setFixedWidth(40)

        rx = QRegExp(pc.REGEX_SINGLE_UNSIGNED_FLOAT_FORCED)
        validator = QRegExpValidator(rx, self)
        self.duration_edit.setValidator(validator)

        # Add widgets

        self.hLayout.addWidget(self.label)
        self.hLayout.addWidget(self.line_edit)
        self.hLayout.addWidget(self.duration_edit)
        self.hLayout.addWidget(self.bWidget)

        # Actions

        self.delete_button.clicked.connect(self.remove_cell_widget)

    def fillOptionXML(self, cell_xml : ET.Element):
        """
        Used for saving the current configuration.

        :param cell_xml:
        :return:
        """
        name_xml = ET.SubElement(cell_xml, "name")
        name_xml.text = self.label.text()

    def readOptionXML(self, cell_xml : ET.Element):
        """
        Used for loading a new configuration.

        :param cell_xml:
        :return:
        """

        name_xml = cell_xml.find('name')

        self.label.setText(name_xml.text)
        self.line_edit.setText(name_xml.text)

    def label_clicked(self, event):
        """


        :param event:
        :return:
        """
        print('Clicked on ' + self.cell_name)

        self.label.setVisible(False)
        self.line_edit.setVisible(True)


        #self.line_edit.setFocus(Qt.Focu)

    def line_edited(self):
        """


        :return:
        """
        self.cell_name = self.line_edit.text()

        self.label.setText(self.cell_name)

        self.label.setVisible(True)
        self.line_edit.setVisible(False)

    def remove_cell_widget(self):
        """
        Triggers the event that this column OR row should be removed.

        :return:
        """
        self.trigger_remove_cell.emit(self)

    def getCfgAsArray(self):
        cfg = []

        duration = int(float(self.duration_edit.text()))
        cfg.append(duration)

        return cfg
class StateWidget(HeaderWidget):
    """
    More specific version of the HeaderWidget to describe the horizontal header.

    """
    trigger_select_state = QtCore.pyqtSignal(QtWidgets.QWidget)
    def __init__(self, text="State"):
        super(StateWidget, self).__init__(text)
        self.select_button.clicked.connect(self.state_selected)

    def state_selected(self):
        self.trigger_select_state.emit(self)

    def get_radio_button(self):
        return self.select_button


class ChannelWidget(HeaderWidget):

    def __init__(self, text="Channel"):
        super(ChannelWidget, self).__init__(text)
        self.select_button.setVisible(False)
        self.duration_edit.setVisible(False)


class RehaStimEditableField(QtWidgets.QWidget):
    def __init__(self, attr):
        super(RehaStimEditableField, self).__init__()
        self.vLayout = QtWidgets.QVBoxLayout(self)
        self.vLayout.setContentsMargins(1, 1, 1, 1)

        self.editable_field = None

        if 'options' in attr:
            box = QtWidgets.QComboBox()

            options = attr['options'].split(',')
            options = map(str.strip, options)

            box.addItems(options)

            index = box.findText(attr['value'])

            box.setCurrentIndex(index)
            #box.setMaximumWidth(100)
            self.vLayout.addWidget(box)

            self.editable_field = box

        else:
            line = QtWidgets.QLineEdit(attr['value'])
            if 'regex' in attr:
                regex = attr['regex']
                rx = QRegExp(regex)
                validator = QRegExpValidator(rx, self)
                line.setValidator(validator)

            self.editable_field = line
            self.editable_field.setMaximumWidth(70)

            self.vLayout.addWidget(line)

    def get_value(self):

        if isinstance(self.editable_field, QtWidgets.QComboBox):
            return self.editable_field.currentText()

        if isinstance(self.editable_field, QtWidgets.QLineEdit):
            return self.editable_field.text()

        return None