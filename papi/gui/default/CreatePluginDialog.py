#!/usr/bin/python3
# -*- coding: latin-1 -*-

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

Contributors
Sven Knuth
"""

import operator

from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLineEdit, QCheckBox, QComboBox, QFormLayout, QVBoxLayout, QWidget
from PyQt5.QtCore import *

from papi.ui.gui.default.PluginCreateDialog import Ui_CreatePluginDialog
from papi.gui.default.custom import FileLineEdit, ColorLineEdit

from papi.constants import GUI_DEFAULT_TAB
import papi.constants as pc

import collections


class CreatePluginDialog(QDialog, Ui_CreatePluginDialog):
    """
    This class create a dialog which enable an user to modify the default configuration of a plugin.

    """

    def __init__(self, gui_api, tab_manager, parent=None):
        """
        Constructor of this class.
        'gui_api' is used to access the GUI data storage 'DGUI' and for creating the plugin.
        'TabManager' access to the tab manager is needed because it provides the information about all used tabs.

        :param gui_api: api of the GUI
        :param tab_manager: Object which manages the tabs
        :param parent:
        :return:
        """

        super(CreatePluginDialog, self).__init__(parent)
        self.setupUi(self)
        self.cfg = None
        self.configuration_inputs = {}
        self.gui_api = gui_api
        self.tab_manager = tab_manager
        self.advancedForms = {}

    def set_plugin(self, plugin_info):
        """
        This function must be called before the dialog is shown.

        :param plugin_info: The plugin info object provided by yapsy.
        :return:
        """

        startup_config = plugin_info.plugin_object._get_startup_configuration()
        self.cfg = startup_config
        self.plugin_name = plugin_info.name
        self.plugin_type = plugin_info.plugin_object._get_type()
        self.cfg['uname'] = {}
        self.cfg['uname']['value'] = ''

    def set_dplugin(self, dplugin, startup_config, type):
        """
        Additionally to set_plugin it is also possible to provide a DPlugin object.
        This feature is used by copy a currently running plugin.
        The 'type' of the plugin must be provided.

        :param dplugin: Data object which describes the running plugin.
        :param startup_config: Configuration used at startup. Contains user modification by the user.
        :param type:
        :return:
        """

        self.plugin_name = dplugin.plugin_identifier
        self.plugin_type = type

        plugin_cfg = dplugin.startup_config

        for key in plugin_cfg.keys():
            if key in startup_config:
                startup_config[key]['value'] = plugin_cfg[key]['value']

        self.cfg = startup_config

        self.cfg['uname'] = {}
        self.cfg['uname']['value'] = ''

    def accept(self):
        """
        This function is called when the user accepts the current modification and wants to create the plugin.

        :return:
        """
        config = self.cfg

        for attr in self.configuration_inputs:

            if isinstance(self.configuration_inputs[attr], QCheckBox):

                if self.configuration_inputs[attr].isChecked():
                    config[attr]['value'] = '1'
                else:
                    config[attr]['value'] = '0'

            if isinstance(self.configuration_inputs[attr], QLineEdit):
                config[attr]['value'] = self.configuration_inputs[attr].text()

            if isinstance(self.configuration_inputs[attr], ColorLineEdit):
                config[attr]['value'] = self.configuration_inputs[attr].text()

            if isinstance(self.configuration_inputs[attr], QComboBox):
                config[attr]['value'] = self.configuration_inputs[attr].currentText()

        if not self.gui_api.do_test_name_to_be_unique(config['uname']['value']):
            self.configuration_inputs['uname'].setStyleSheet("QLineEdit  { border : 2px solid red;}")
            self.configuration_inputs['uname'].setFocus()
            return

        self.done(0)

        autostart = True
        if self.plugin_type == pc.PLUGIN_IOP_IDENTIFIER or self.plugin_type == pc.PLUGIN_DPP_IDENTIFIER:
            autostart = self.autostartBox.isChecked()

        self.gui_api.do_create_plugin(self.plugin_name, config['uname']['value'], config=config, autostart=autostart)

    def reject(self):
        """
        This function is called when the user closes the dialog without creating a plugin.

        :return:
        """
        self.done(-1)

    def showEvent(self, *args, **kwargs):
        """
        This function is called before the dialog is displayed.

        :param args:
        :param kwargs:
        :return:
        """
        startup_config = self.cfg

        for form in self.advancedForms:
            self.clear_layout(self.advancedForms[form])

        self.configuration_inputs.clear()

        self.setWindowTitle("Create Plugin " + self.plugin_name)

        position = 0

        if 'uname' in startup_config.keys():
            value = startup_config['uname']['value']

            display_text = 'Unique name'

            if 'display_text' in startup_config['uname'].keys():
                display_text = startup_config['uname']['display_text']

            uname = self.gui_api.do_change_string_to_be_uname(self.plugin_name)
            uname = self.gui_api.change_uname_to_uniqe(uname)

            editable_field = QLineEdit(str(value))
            editable_field.setText(uname)
            editable_field.setObjectName('uname' + "_line_edit")
            editable_field.setToolTip('Name as identifier in PaPI. Must be UNIQUE')

            form_name = 'PaPI -mandatory'
            if form_name not in self.advancedForms:
                self.advancedForms[form_name] = QFormLayout()
                tab_widget = QWidget()

                self.tabWidget.addTab(tab_widget, form_name)
                vlayout = QVBoxLayout(tab_widget)
                vlayout.addLayout(self.advancedForms[form_name])

            self.advancedForms[form_name].addRow(str(display_text), editable_field)

            self.configuration_inputs['uname'] = editable_field

            position += 1

        startup_config_sorted = startup_config.items()
        if not isinstance(startup_config, collections.OrderedDict):
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

                if attr != 'tab':

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

                        if parameter_type == 'color':
                            editable_field = ColorLineEdit()
                            editable_field.set_default_color(startup_config[attr]['value'])
                            #
                            # editable_field.setText(value)

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
                else:
                    editable_field = QComboBox()
                    tabs = list(self.tab_manager.get_tabs_by_uname().keys())
                    if len(tabs) == 0:
                        tabs = [GUI_DEFAULT_TAB]
                    tabs.sort(key=str.lower)
                    editable_field.addItems(tabs)
                    editable_field.setObjectName('Tab' + "_comboBox")
                # -------------------------------
                # Divided in advanced or simple option
                # -------------------------------

                if 'advanced' in startup_config[attr]:

                    form_name = startup_config[attr]['advanced']
                else:
                    form_name = 'PaPI -mandatory'

                if form_name in ['0', 0]:
                    form_name = 'PaPI -mandatory'

                if form_name == '1':
                    form_name = 'Advanced'

                if form_name not in self.advancedForms:
                    self.advancedForms[form_name] = QFormLayout()
                    tab_widget = QWidget()

                    self.tabWidget.addTab(tab_widget, form_name)
                    vlayout = QVBoxLayout(tab_widget)
                    vlayout.addLayout(self.advancedForms[form_name])

                self.advancedForms[form_name].addRow(str(display_text), editable_field)

                if 'tooltip' in startup_config[attr]:
                    editable_field.setToolTip(startup_config[attr]['tooltip'])

                self.configuration_inputs[attr] = editable_field

                position += 1

    def keyPressEvent(self, event):
        """
        Default callback function which is called when an any key was pressed by the user.

        :param event:
        :return:
        """

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.accept()
        if event.key() == Qt.Key_Escape:
            self.close()

    def clear_layout(self, layout):
        """
        This function is called to remove all elements within a tab.
        It is called in showEvent.

        :param layout:
        :return:
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())
