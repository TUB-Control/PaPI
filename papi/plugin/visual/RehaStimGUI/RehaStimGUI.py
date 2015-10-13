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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
<Stefan Ruppin
"""



import traceback
import datetime
import time
import json
import os.path

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter
from papi.data.DPlugin import DBlock, DEvent
from papi.data.DSignal import DSignal


import papi.constants as pc

from papi.gui.default import get32Icon

from PyQt5 import QtGui, QtWidgets, QtCore, Qt
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

import xml.etree.cElementTree as ET

class OptionItem():
    def __init__(self):
        self.attributes = {'1_Start': {
            'value': '0',
            'min': '0.9',
            'max': '1',
            'display_name' : 'Start',
            'type' : 'slider',
            'regex' : pc.REGEX_SINGLE_UNSIGNED_FLOAT_FORCED
        }, '2_End': {
            'value': '0',
            'min': '0.5',
            'max': '1',
            'type' : 'slider',
            'display_name' : 'End',
            'regex' : pc.REGEX_SINGLE_UNSIGNED_FLOAT_FORCED
        }, '3_Rise': {
            'value': '5',
            'min': '0',
            'max': '100',
            'type' : 'slider',
            'display_name' : 'Rise',
            'regex' : pc.REGEX_SINGLE_UNSIGNED_FLOAT_FORCED
        }, '4_Type': {
            'value': 'ramp',
            'options': "ramp, trapez",
            'display_name' : 'Type'
        }}


    def set_attr(self, attr, key, value):
        if attr in self.attributes:
            if key in self.attributes[attr]:
                self.attributes[attr][key] = value

    def get_attr(self, attr):
        if attr in self.attributes:
            return self.attributes[attr]

    def get_attributes(self):
        return self.attributes

    def clear_attribtues(self):
        self.attributes = {}

class RehaStimGUI(vip_base, object):

    def __init__(self):
        super(RehaStimGUI, self).__init__()

        self.__VERSION__ = "0.8"

        self.signal_next_state = "next_state"



        pass

    def cb_initialize_plugin(self):


        # ---------------------------
        # Read configuration
        # ---------------------------
        self.config = self.pl_get_current_config_ref()
        self.signal_next_state = self.config['signal_next_state']['value']
        self.readOnly = self.config['readonly']['value'] == '1'

        # ---------------------------
        # Create Widget
        # ---------------------------

        self.widget = self.create_widget()
        self.create_actions()
        self.pl_set_widget_for_internal_usage( self.widget )
        self.current_state = None


        # ---------------------------
        # Create events
        # ---------------------------

        self.event_new_config        = DEvent('StimulatorConfiguration')
        self.event_heartbeat     = DEvent('Heartbeat')
        self.event_maxima_slider = DEvent('MaximaSlider')
        self.event_control_stim  = DEvent('ControlStim')
        self.event_start         = DEvent('Start')

        self.pl_send_new_event_list([self.event_new_config, self.event_heartbeat,
                                  self.event_maxima_slider, self.event_control_stim, self.event_start])

        # ---------------------------
        # Create Parameters
        # ---------------------------

        # ---------------------------
        # Create default structure
        # ---------------------------

        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(1)

        self.tableWidget.setCellWidget(0, 0, QtWidgets.QLabel())

        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().hide()

        self.gridLayout = QtWidgets.QGridLayout()

        self.gridWidget.setLayout(self.gridLayout)

        self.tableRowCount = 0
        self.tableColCount = 0


        self.button_group = QtWidgets.QButtonGroup()


        # -----------------------
        # Custom configuration
        # -----------------------

        self.pal_cell_selected = QtGui.QPalette()
        self.pal_cell_selected.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 255))
        #self.pal_cell_selected.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 100))
        #self.pal_cell_selected.setColor(QtGui.QPalette.Base, QtGui.QColor(0, 0, 100))
        #self.pal_cell_selected.setColor(QtGui.QPalette.Button, QtGui.QColor(0, 0, 100))

        # -----------------------
        # Load configuration
        # -----------------------

        filename = self.config['config']['value'];

        if os.path.isfile(filename):
            self.load_config(filename)

        # --------------------
        # Create timer for heartbeat
        # --------------------

        self.timer = QtCore.QTimer()

        self.timer.timeout.connect(self.timeout_send_heartbeat)
        self.timer.start(1000)

        self.heartbeat = 0

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

        self.gridWidget = QtWidgets.QWidget()

        self.verticalLayout.addWidget(self.gridWidget)

        self.verticalLayout.addWidget(self.tableWidget)
#        self.tableWidget.horizontalHeader().setStretchLastSection(True)
#        self.tableWidget.verticalHeader().setStretchLastSection(True)

#        self.tableWidget.horizontalHeader().setVisible(False)
#        self.tableWidget.verticalHeader().setVisible(False)

        self.horizonLayoutButtons = QtWidgets.QHBoxLayout()
        self.allButons = QtWidgets.QWidget()
        self.allButons.setLayout(self.horizonLayoutButtons)

        self.verticalLayout.addWidget(self.allButons)

        # -------------------
        # Add Buttons: LoadSave
        # -------------------

        self.loadsaveButtonsWidget = QtWidgets.QWidget()

        self.loadsaveButtonVLayout = QtWidgets.QVBoxLayout(self.loadsaveButtonsWidget)

        self.saveConfigButton = QtWidgets.QPushButton("Speichern")
        self.saveConfigButton.setToolTip("Aktuelle Konfiguration speichern.")
        self.loadConfigButton = QtWidgets.QPushButton("Laden")
        self.loadConfigButton.setToolTip("Neue Konfiguration laden.")

        load_icon = get32Icon('folder')
        save_icon = get32Icon('file_save_as')

        self.saveConfigButton.setIcon(save_icon)
        self.loadConfigButton.setIcon(load_icon)

        self.loadsaveButtonVLayout.addWidget(self.saveConfigButton)
        self.loadsaveButtonVLayout.addWidget(self.loadConfigButton)

        self.horizonLayoutButtons.addWidget(self.loadsaveButtonsWidget)

        # -------------------
        # Add Buttons: Start/Stop configButtonsWidget
        # -------------------

        self.configButtonsWidget = QtWidgets.QWidget()
        self.configButtonVLayout = QtWidgets.QVBoxLayout(self.configButtonsWidget)

        self.sendConfigButton = QtWidgets.QPushButton()
        self.stopButton = QtWidgets.QPushButton()
        self.finishedCalibrationButton = QtWidgets.QPushButton("Beende Kalibrierung")
        self.reCalibrationButton = QtWidgets.QPushButton("Erneut Kalibrierung")
        self.reCalibrationButton.hide()

        self.stopButton.hide()
        stop_icon = get32Icon('delete')
        start_icon = get32Icon('control_play_blue')

        self.stopButton.setIcon(stop_icon)
        self.sendConfigButton.setIcon(start_icon)
        self.configButtonVLayout.addWidget(self.finishedCalibrationButton)
        self.configButtonVLayout.addWidget(self.reCalibrationButton)
        self.configButtonVLayout.addWidget(self.sendConfigButton)
        self.configButtonVLayout.addWidget(self.stopButton)


        self.horizonLayoutButtons.addWidget(self.configButtonsWidget)

        # -------------------
        # Add Buttons: State/Channels
        # -------------------

        self.tableButtonsWidget = QtWidgets.QWidget()

        self.tableButtonVLayout = QtWidgets.QVBoxLayout(self.tableButtonsWidget)

        self.addStateButton = QtWidgets.QPushButton("Neuen Zustand erzeugen")
        self.addChButton = QtWidgets.QPushButton("Neuen Kanal anlegen")

        if not self.readOnly:

            self.tableButtonVLayout.addWidget(self.addStateButton)
            self.tableButtonVLayout.addWidget(self.addChButton)

            self.horizonLayoutButtons.addWidget(self.tableButtonsWidget)

        return self.centralwidget

    def create_actions(self):
        self.addChButton.clicked.connect(self.add_ch_clicked)
        self.addStateButton.clicked.connect(self.add_state_clicked)

#        self.sendConfigButton.clicked.connect(self.clicked_send_config)

        self.loadConfigButton.clicked.connect(self.clicked_load_config)
        self.saveConfigButton.clicked.connect(self.clicked_save_config)

        self.stopButton.clicked.connect(self.clicked_stop_button)
        self.sendConfigButton.clicked.connect(self.clicked_start_button)

        self.finishedCalibrationButton.clicked.connect(self.clicked_finished_button)
        self.reCalibrationButton.clicked.connect(self.clicked_re_calibrate_button)

    def show_context_menu(self, pos):
        gloPos = self.LcdWidget.mapToGlobal(pos)
        self.cmenu = self.pl_create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def clicked_load_config(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(caption="Open File", filter="Config (*xml)")[0]

        if filename == '':
            return

        self.load_config(filename)

    def load_config(self, filename):

        tree = ET.parse(filename)

        root = tree.getroot()

        for tag_xml in root:
            if tag_xml.tag == "Option":
                for option_tml in tag_xml:
                    if option_tml.tag == "ColumnCount":
                        rowCount = int(option_tml.text)

                        self.tableRowCount = rowCount
                        self.tableWidget.setRowCount(rowCount)

                    if option_tml.tag == "RowCount":
                        columnCount = int(option_tml.text)
                        self.tableColCount = columnCount

                        self.tableWidget.setColumnCount(columnCount)

            if tag_xml.tag == "Cells":
                for cell_xml in tag_xml:
                    col = int(cell_xml.get('col'))
                    row = int(cell_xml.get('row'))
                    type = cell_xml.get('type')

                    cellWidget = None
                    if type in ['StateWidget']:
                        cellWidget = StateWidget(readOnly=self.readOnly)

                        cellWidget.trigger_remove_cell.connect(self.remove_cell_widget)
                        cellWidget.trigger_select_state.connect(self.select_state_widget)

                        self.button_group.addButton(cellWidget.get_radio_button())

                    if type in ['ChannelWidget']:
                        cellWidget = ChannelWidget(readOnly=self.readOnly)
                        cellWidget.changed_slider.connect(self.changed_max_sliders)
                        cellWidget.trigger_remove_cell.connect(self.remove_cell_widget)

                    if type == 'OptionWidget':
                        cellWidget = OptionWidget()

                    cellWidget.readOptionXML(cell_xml)

                    #self.gridLayout.addWidget(cellWidget, row, col)
                    # cellWidget = QtWidgets.QSlider()
                    # cellWidget.setOrientation(QtCore.Qt.Horizontal)

                    self.tableWidget.setCellWidget(col, row, cellWidget)

        self.adjust()

    def clicked_save_config(self):
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

    def clicked_send_config(self):
        pass
        # stateWidget = self.current_state
        #
        #
        # simulink_cfg = self.create_config_for_simulink_block(current_state=None)
        #
        #
        # print("Length of config " + str(len(simulink_cfg)))
        #
        # self.pl_emit_event(str(simulink_cfg), self.block_config.name)
        #
        # if stateWidget is None:
        #     return

    def clicked_start_button(self):
        self.pl_emit_event('1', self.event_start)
        self.sendConfigButton.hide()
        self.stopButton.show()


    def clicked_stop_button(self):

        self.pl_emit_event('0', self.event_start)
        self.sendConfigButton.show()
        self.stopButton.hide()

    def clicked_finished_button(self):
        self.finishedCalibrationButton.hide()
        self.reCalibrationButton.show()
        self.pl_emit_event('2', self.event_control_stim)

        if self.current_state is None:
            first_state = self.tableWidget.cellWidget(0, 1)
            if isinstance(first_state, StateWidget):
                self.current_state = self.tableWidget.cellWidget(1,0)
                self.select_state_widget(first_state, True)
        else:
            self.select_state_widget(self.current_state, True)


    def clicked_re_calibrate_button(self):
        self.finishedCalibrationButton.show()
        self.reCalibrationButton.hide()
        self.pl_emit_event('3', self.event_control_stim)

#        json_config = self.create_json_for_state(stateWidget)

#        print(json_config)

    def changed_max_sliders(self):

        all_values = []

        for r in range(1, self.tableWidget.rowCount()):
            channelWidget = self.tableWidget.cellWidget(r, 0)
            if channelWidget is not None:

                slider_value = channelWidget.slider.value()
                all_values.append(float(slider_value)/100)

                if channelWidget.check_slider.isChecked():
                    all_values.append(1)
                else:
                    all_values.append(0)


        self.pl_emit_event(str(all_values), self.event_maxima_slider)

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

    # def get_channel_widget(self, text):
    #     ch_widget = QtWidgets.QLineEdit(text)
    #     return ch_widget
    #
    # def get_state_widget(self, text):
    #     st_widget = QtWidgets.QLineEdit(text)
    #     return st_widget

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

    def select_state_widget(self, stateWidget, send_config=True):
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

        if send_config:
            self.pl_emit_event(str(simulink_cfg), self.event_new_config.name)

    def cb_pause(self):
        # will be called, when plugin gets paused
        # can be used to get plugin in a defined state before pause
        # e.a. close communication ports, files etc.
        pass

    def cb_resume(self):
        # will be called when plugin gets resumed
        # can be used to wake up the plugin from defined pause state
        # e.a. reopen communication ports, files etc.
        pass

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):

        if self.signal_next_state in Data:
            next_state_nr = int(Data[self.signal_next_state][0])

            if self.current_state is not None:
                for c in range(1, self.tableWidget.columnCount()):
                    if self.current_state == self.tableWidget.cellWidget(0, c):

                        if c+1 == next_state_nr:
                            # The next state must exists
                            if next_state_nr < self.tableWidget.columnCount():
                                next_state = self.tableWidget.cellWidget(0,next_state_nr)
                                self.select_state_widget(next_state, send_config=False)

                        if c == self.tableWidget.columnCount()-1 and next_state_nr == 1:
                            next_state = self.tableWidget.cellWidget(0, next_state_nr)
                            self.select_state_widget(next_state, send_config=False)

    def timeout_send_heartbeat(self):

        self.heartbeat = self.heartbeat % 2

        self.heartbeat += 1

        self.pl_emit_event(str(self.heartbeat), self.event_heartbeat.name)


    def cb_set_parameter(self, name, value):
        # attetion: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value
        pass

    def cb_quit(self):
        # do something before plugin will close, e.a. close connections ...
        pass


    def cb_get_plugin_configuration(self):
        #
        # Implement a own part of the config
        # config is a hash of hass object
        # config_parameter_name : {}
        # config[config_parameter_name]['value']  NEEDS TO BE IMPLEMENTED
        # configs can be marked as advanced for create dialog
        # http://utilitymill.com/utility/Regex_For_Range
        config = {
            'config' : {
                'value' : 'config.xml'
            },'maximized' : {
                'value' : '1',
                'type' : 'bool',
                'advanced' : '1',
                'tooltip' : 'Set true to start plugin maximized',
                'display_text' : 'Start maximized'
            },'signal_next_state' : {
                'value' : 'next_state',
                'tooltip' : 'Signal which contains the next state which should be chosen in the gui.',
                'display_text' : 'Signal: NextState'
            }, 'readonly' : {
                'value' : '0',
                'tooltip' : 'Removes the ability to add/remove channels/states when enabled.',
                'display_text' : 'Read-Only',
                'type' : 'bool'
            }
        }
        return config

    def cb_plugin_meta_updated(self):
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

    def cb_new_parameter_info(self, dparameter_object):
        pass

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
        self.gLayout.setContentsMargins(1, 1, 1, 1)

        self.set_option_item(option_item)

    def create_structure(self):
        """
        Adds all labels and fields at the grid layout

        :return:
        """
        for i in range(len(self.lines)):
            self.gLayout.addWidget(self.labels[i], i, 0)
            self.gLayout.addWidget(self.lines[i], i, 1)
            #Due to gui bug: Slider/Label aren't correctly updated

        pass

    def set_option_item(self, oItem):
        """
        Used to set a new option item and triggers a rebuild of the grid layout

        :param oItem:
        :return:
        """

        self.option_item = oItem

        for i in range(len(self.lines)):
            self.gLayout.removeWidget(self.lines[i])
            self.gLayout.removeWidget(self.labels[i])

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

                if attr_key not in ["value"]:
                    continue
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
            if attr_name in ["Start", "End"]:

                cfg.append(float(value)/100)
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

#        new_oItem = OptionItem()
#        new_oItem.clear_attribtues()

        for attr_xml in attrs_xml:
            attr_name = attr_xml.get('name')

            value = {}

            for attr_key_xml in attr_xml:

                self.option_item.set_attr(attr_name, attr_key_xml.tag, attr_key_xml.text)


        self.set_option_item(self.option_item)

class HeaderWidget(QtWidgets.QWidget):
    """
    This cell widget is used as a cell widget in table view and describe
    a single horizontal and vertical header.

    """
    trigger_remove_cell = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, text="Header", readOnly=False):
        super(HeaderWidget, self).__init__()
        self.cell_name = text
        self.readOnly = readOnly
        self.vLayout = QtWidgets.QVBoxLayout(self)
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.setAlignment(QtCore.Qt.AlignTop)

        self.topWidget = QtWidgets.QWidget()
        self.topPart = QtWidgets.QHBoxLayout(self.topWidget)
        #self.topPart.setContentsMargins(0, 0, 0, 0)

        self.bottomWidget = QtWidgets.QWidget()
        self.bottomPart = QtWidgets.QHBoxLayout(self.bottomWidget)
        #self.bottomPart.setContentsMargins(0, 0, 0, 0)

        self.vLayout.addWidget(self.topWidget)
        self.vLayout.addWidget(self.bottomWidget)

        # Create structure


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

        if not self.readOnly:
            self.hBLayout.addWidget(self.delete_button)

        self.hBLayout.addWidget(self.select_button)


        self.duration_edit = QtWidgets.QLineEdit("0")
        self.duration_edit.setFixedWidth(40)

        rx = QRegExp(pc.REGEX_SINGLE_UNSIGNED_FLOAT_FORCED)
        validator = QRegExpValidator(rx, self)
        self.duration_edit.setValidator(validator)

        # Slider: Used for channel

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_value = QtWidgets.QLabel()
        self.slider_value.setText('0')
        self.slider_value.setFixedWidth(40)

        self.slider.setMaximum(100)

        self.check_slider= QtWidgets.QCheckBox()


        # Add widgets

        self.bottomPart.addWidget(self.slider)
        self.bottomPart.addWidget(self.slider_value)
        self.bottomPart.addWidget(self.check_slider)

        self.topPart.addWidget(self.label)
        self.topPart.addWidget(self.line_edit)
        self.topPart.addWidget(self.duration_edit)
        self.topPart.addWidget(self.bWidget)

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

        if isinstance(self, ChannelWidget):
            slider_value = str(self.slider.value())
            slider_active = str(self.check_slider.isChecked())
            name_xml.set('slider', slider_value)
            name_xml.set('sliderActive', slider_active)

        if isinstance(self, StateWidget):
            duration =str(self.duration_edit.text())
            name_xml.set('duration', duration)

    def readOptionXML(self, cell_xml : ET.Element):
        """
        Used for loading a new configuration.

        :param cell_xml:
        :return:
        """

        name_xml = cell_xml.find('name')

        self.label.setText(name_xml.text)
        self.line_edit.setText(name_xml.text)


        if isinstance(self, ChannelWidget):
            if 'slider' in name_xml.keys():
                slider_value = name_xml.get('slider')
                slider_active = name_xml.get('sliderActive')

                self.slider.setValue(int(slider_value))
                self.slider_value.setText(slider_value + "%")

                self.check_slider.setChecked(slider_active == "True")

        if isinstance(self, StateWidget):
            if 'duration' in name_xml.keys():
                duration = name_xml.get('duration')
                self.duration_edit.setText(duration)

    def label_clicked(self, event):
        """


        :param event:
        :return:
        """
        print('Clicked on ' + self.cell_name)

        self.label.setVisible(False)
        self.line_edit.setVisible(True)
        self.line_edit.setFocus()

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

    def __init__(self, text="State", readOnly=False):
        super(StateWidget, self).__init__(text, readOnly)
        self.select_button.clicked.connect(self.state_selected)

        self.slider.hide()
        self.slider_value.hide()
        self.check_slider.hide()

    def state_selected(self):
        self.trigger_select_state.emit(self)

    def get_radio_button(self):
        return self.select_button

class ChannelWidget(HeaderWidget):

    changed_slider = QtCore.pyqtSignal(QtWidgets.QWidget)


    def __init__(self, text="Channel", readOnly=False):
        super(ChannelWidget, self).__init__(text, readOnly)
        self.select_button.setVisible(False)
        self.duration_edit.setVisible(False)
        self.slider.valueChanged.connect(self.value_changed)

        self.check_slider.stateChanged.connect(self.checkbox_checked)

        self.slider.wheelEvent = self.sliderMousePressEvent
        self.slider.setOrientation(QtCore.Qt.Vertical)

    def value_changed(self, change):
        self.slider_value.setText(str(change) + "%")
        self.changed_slider.emit(self)

    def checkbox_checked(self, state):
        self.changed_slider.emit(self)

    def sliderMousePressEvent(self, event):
        return

class RehaStimEditableField(QtWidgets.QWidget):
    def __init__(self, attr):
        super(RehaStimEditableField, self).__init__()
        self.vLayout = QtWidgets.QGridLayout(self)
        #self.vLayout.setContentsMargins(1, 1, 1, 1)

        self.editable_field = None
        self.start_value = attr['value'];
        self.slider = None

        if 'options' in attr:
            # box = QtWidgets.QComboBox()
            # options = attr['options'].split(',')
            # options = map(str.strip, options)
            # box.addItems(options)
            # index = box.findText(attr['value'])
            # box.setCurrentIndex(index)
            # #box.setMaximumWidth(100)
            # self.vLayout.addWidget(box, 0, 0)
            # self.editable_field = box

            non_stripped_options = attr['options'].split(',')

            options = list(map(str.strip, non_stripped_options))
            self.button_group = QtWidgets.QButtonGroup()

            check_box1 = QtWidgets.QRadioButton()
            check_box1.setText(options[0])


            check_box2 = QtWidgets.QRadioButton()
            check_box2.setText(options[1])

            if attr['value'] == options[0]:
                check_box1.setChecked(True)
            elif attr['value'] == options[1]:
                check_box2.setChecked(True)

            self.button_group.addButton(check_box1)
            self.button_group.addButton(check_box2)

            check_widget = QtWidgets.QWidget()
            check_h_layout = QtWidgets.QHBoxLayout()
            check_widget.setLayout(check_h_layout)
            check_h_layout.addWidget(check_box1)
            check_h_layout.addWidget(check_box2)

            self.editable_field = check_widget

            self.vLayout.addWidget(check_widget, 0, 0)


        elif 'type' in attr:

            if 'slider' == attr['type']:

                self.slider = QtWidgets.QSlider();
                self.editable_field = self.slider

                self.vLayout.addWidget(self.slider, 0, 0)

                self.slider.setOrientation(QtCore.Qt.Horizontal)
                self.slider.setTickInterval(101)
                self.slider.setMaximum(100)
                self.slider.setMinimum(0)

                self.slider.setValue(int(attr['value']))
                self.text_field = QtWidgets.QLabel()
                self.text_field.setMinimumWidth(50)
                self.text_field.setText(attr['value']  + "%")

                self.slider.setFixedWidth(70)

                self.vLayout.addWidget(self.text_field, 0, 1)

                self.slider.valueChanged.connect(self.value_changed)

        else:
            line = QtWidgets.QLineEdit(attr['value'])
            if 'regex' in attr:
                regex = attr['regex']
                rx = QRegExp(regex)
                validator = QRegExpValidator(rx, self)
                line.setValidator(validator)

            self.editable_field = line
            self.editable_field.setMaximumWidth(70)

            self.vLayout.addWidget(line, 0, 0)

    def get_value(self):

        if isinstance(self.editable_field, QtWidgets.QComboBox):
            return self.editable_field.currentText()

        if isinstance(self.editable_field, QtWidgets.QLineEdit):
            return self.editable_field.text()

        if isinstance(self.editable_field, QtWidgets.QSlider):
            return self.editable_field.value()

        if isinstance(self.editable_field, QtWidgets.QWidget):
            cb = self.button_group.checkedButton()
            if  cb is not None:
                return cb.text()
            else:
                return ''

        return None

    def value_changed(self, change):
        self.text_field.setText(str(change) + "%")
