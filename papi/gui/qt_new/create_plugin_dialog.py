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
from papi.gui.qt_new.item import PaPITreeItem, RootItem, PaPItreeModel

__author__ = 'knuths'

from papi.ui.gui.qt_new.create_dialog import Ui_CreatePluginDialog
from PySide.QtGui import QMainWindow, QLabel, QFormLayout, QLineEdit, QRegExpValidator

from papi.constants import PLUGIN_ROOT_FOLDER_LIST
from PySide.QtCore import *
from PySide import QtGui
import PySide
from yapsy.PluginManager import PluginManager


class CreatePluginDialog(QMainWindow, Ui_CreatePluginDialog):

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
            config[attr]['value'] = self.configuration_inputs[attr].text()

        self.close()

        autostart = True
        if self.plugin_type == 'IOP' or self.plugin_type == 'DPP':
            autostart = self.autostartBox.isChecked()

        self.gui_api.do_create_plugin(self.plugin_name, config['uname']['value'], config=config, autostart=autostart)


    def reject(self):
        self.close()

    def showEvent(self, *args, **kwargs):
        startup_config = self.cfg

        self.clear_layout(self.formLayout)
        self.configuration_inputs.clear()

        position = 0

        for attr in startup_config:
            value = startup_config[attr]['value']
            label = QLabel(self.formLayoutWidget)
            label.setText(attr)
            label.setObjectName(attr  + "_label")

            line_edit = QLineEdit(self.formLayoutWidget)
            line_edit.setText(str(value))
            line_edit.setObjectName(attr + "_line_edit")

            self.formLayout.setWidget(position, QtGui.QFormLayout.LabelRole, label)
            self.formLayout.setWidget(position, QtGui.QFormLayout.FieldRole, line_edit)

            # -------------------------------
            # Check for regex description
            # -------------------------------

            if 'regex' in startup_config[attr]:
                regex = startup_config[attr]['regex']
                rx = QRegExp(regex)
                validator = QRegExpValidator(rx, self)
                line_edit.setValidator(validator)

            self.configuration_inputs[attr] = line_edit

            position+=1

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())