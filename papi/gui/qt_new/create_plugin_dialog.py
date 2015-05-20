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
from papi.gui.qt_new.item import PaPITreeItem, PaPIRootItem, PaPITreeModel

__author__ = 'knuths'

from papi.ui.gui.qt_new.create_dialog import Ui_CreatePluginDialog
from PySide.QtGui import QDialog, QLabel, QFormLayout, QLineEdit, QRegExpValidator, QCheckBox, QFileDialog
from papi.gui.qt_new.custom import FileLineEdit

from papi.constants import PLUGIN_ROOT_FOLDER_LIST
from PySide.QtCore import *
from PySide import QtGui
import PySide
from yapsy.PluginManager import PluginManager
import operator

class CreatePluginDialog(QDialog, Ui_CreatePluginDialog):

    def __init__(self, gui_api, parent=None):
        super(CreatePluginDialog, self).__init__(parent)
        self.setupUi(self)
        self.cfg = None
        self.configuration_inputs = {}
        self.gui_api = gui_api


    def set_plugin(self, plugin):
        startup_config = plugin.plugin_object.get_startup_configuration()
        self.cfg = startup_config
        self.plugin_name = plugin.name
        self.plugin_type = plugin.plugin_object.get_type()
        self.cfg['uname'] = {}
        self.cfg['uname']['value'] = ''

    def accept(self):

        config = self.cfg

        for attr in self.configuration_inputs:

           if isinstance(self.configuration_inputs[attr], QCheckBox):

                if self.configuration_inputs[attr].isChecked():
                    config[attr]['value'] = '1'
                else:
                    config[attr]['value'] = '0'

           if isinstance(self.configuration_inputs[attr], QLineEdit):
                config[attr]['value'] = self.configuration_inputs[attr].text()

        if not self.gui_api.do_test_name_to_be_unique(config['uname']['value']) :
            self.configuration_inputs['uname'].setStyleSheet("QLineEdit  { border : 2px solid red;}")
            self.configuration_inputs['uname'].setFocus()
            return

        self.done(0)

        autostart = True
        if self.plugin_type == 'IOP' or self.plugin_type == 'DPP':
            autostart = self.autostartBox.isChecked()

        self.gui_api.do_create_plugin(self.plugin_name, config['uname']['value'], config=config, autostart=autostart)

    def reject(self):
        self.done(-1)

    def showEvent(self, *args, **kwargs):
        startup_config = self.cfg

        self.clear_layout(self.formSimple)
        self.clear_layout(self.formAdvance)
        self.configuration_inputs.clear()

        self.setWindowTitle("Create Plugin " + self.plugin_name)

        position = 0

        if 'uname' in startup_config.keys():
            value = startup_config['uname']['value']

            display_text = 'uname'

            if 'display_text' in startup_config['uname'].keys():
                display_text = startup_config['uname']['display_text']

            uname = self.gui_api.change_uname_to_uniqe(self.plugin_name)

            editable_field = QLineEdit(str(value))
            editable_field.setText(uname)
            editable_field.setObjectName('uname' + "_line_edit")

            self.formSimple.addRow(str(display_text) , editable_field)

            self.configuration_inputs['uname'] = editable_field

            #line_edit.selectAll()
            #line_edit.setFocus()

            position += 1

            startup_config_sorted = sorted(startup_config.items(), key=operator.itemgetter(0))

        for attr in startup_config_sorted:
            attr = attr[0]
            if attr != 'uname':
                value = startup_config[attr]['value']

                display_text = attr

                if 'display_text' in startup_config[attr].keys():
                    display_text = startup_config[attr]['display_text']


                # -------------------------------
                # Check for datatype
                # -------------------------------

                editable_field = None

                if 'type' in startup_config[attr]:
                    parameter_type = startup_config[attr]['type']

                    if parameter_type == 'bool':
                        editable_field = QCheckBox()

                        if value == '1':
                            editable_field.setChecked(True)
                        else:
                            editable_field.setChecked(False)

                    if parameter_type == 'file':
                        editable_field = FileLineEdit()
                        editable_field.setReadOnly(True)
                        editable_field.setText(value)

                else:
                    editable_field = QLineEdit()

                    editable_field.setText(str(value))
                    editable_field.setObjectName(attr + "_line_edit")

                    # -------------------------------
                    # Check for regex description
                    # -------------------------------

                    if 'regex' in startup_config[attr]:
                        regex = startup_config[attr]['regex']
                        rx = QRegExp(regex)
                        validator = QRegExpValidator(rx, self)
                        editable_field.setValidator(validator)

                # -------------------------------
                # Divided in advanced or simple option
                # -------------------------------

                if 'advanced' in startup_config[attr]:
                    if startup_config[attr]['advanced'] == '1':
                        self.formAdvance.addRow(str(display_text), editable_field)
                    else:
                        self.formSimple.addRow(str(display_text), editable_field)
                else:
                    self.formSimple.addRow(str(display_text), editable_field)

                if 'tooltip' in startup_config[attr]:
                    editable_field.setToolTip(startup_config[attr]['tooltip'])



                self.configuration_inputs[attr] = editable_field

                position+=1

        # self.configuration_inputs['uname'].setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
           self.accept()
        if event.key() == Qt.Key_Escape:
            self.close()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())