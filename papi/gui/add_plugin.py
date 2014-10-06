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

from papi.ui.gui.add_plugin import Ui_AddPlugin
from PySide.QtGui import QDialog, QAbstractButton, QDialogButtonBox
from PySide.QtGui import QTreeWidgetItem, QRegExpValidator
from PySide import QtGui
from PySide.QtCore import QRegExp

from yapsy.PluginManager import PluginManager

class AddPlugin(QDialog, Ui_AddPlugin):

    def __init__(self, callback_function, parent=None):
        super(AddPlugin, self).__init__(parent)
        self.setupUi(self)
        self.dgui = None

        self.callback_functions = callback_function

        self.treePlugin.currentItemChanged.connect(self.pluginItemChanged)


        self.buttonBox.clicked.connect(self.button_clicked)

        self.subscriberID = None
        self.targetID = None
        self.blockName = None
        self.setWindowTitle("Add Plugin")

        self.plugin_manager = PluginManager()
        self.plugin_path = "../plugin/"

        self.plugin_manager.setPluginPlaces(
            [
                self.plugin_path + "visual", 'plugin/visual',
                self.plugin_path + "io", 'plugin/io',
                self.plugin_path + "dpp", 'plugin/dpp'
            ]
        )
        self.setWindowTitle('Available Plugins')


        self.visual_root = QTreeWidgetItem(self.treePlugin)
        self.visual_root.setText(0, 'ViP')
        self.io_root = QTreeWidgetItem(self.treePlugin)
        self.io_root.setText(0, 'IOP')
        self.dpp_root = QTreeWidgetItem(self.treePlugin)
        self.dpp_root.setText(0, 'DPP')
        self.pcb_root = QTreeWidgetItem(self.treePlugin)
        self.pcb_root.setText(0, 'PCB')

        self.plugin_uname = None
        self.plugin_name = None

        self.attrs = {}

    def setDGui(self, dgui):
        self.dgui = dgui

    def getDGui(self):
        """

        :return:
        :rtype DGui:
        """
        return self.dgui

    def pluginItemChanged(self, item):
        if hasattr(item, 'pluginfo'):
            pluginfo = item.pluginfo

            self.le_path.setText(pluginfo.path)

            config = pluginfo.plugin_object.get_default_config()

            position = 0;

            attrs = self.attrs.copy()
            for attr in attrs:
                del self.attrs[attr]



            self.clearLayout(self.customFormLayout)

            for attr in config:
                value = self.get_config_value(config, attr)
                label = QtGui.QLabel(self.formLayoutWidget_2)
                label.setText(attr)
                label.setObjectName(attr  + "_label")

                line_edit = QtGui.QLineEdit(self.formLayoutWidget_2)
                line_edit.setText(str(value))
                line_edit.setObjectName(attr + "_line_edit")

                self.customFormLayout.setWidget(position, QtGui.QFormLayout.LabelRole, label)
                self.customFormLayout.setWidget(position, QtGui.QFormLayout.FieldRole, line_edit)

                # -------------------------------
                # Check for regex description
                # -------------------------------
                regex = self.get_config_regex(config, attr)
                if regex is not None:
                    rx = QRegExp(regex)
                    validator = QRegExpValidator(rx, self)
                    line_edit.setValidator(validator)


                self.attrs[attr] = line_edit

                position+=1

    def showEvent(self, *args, **kwargs):
        self.plugin_manager.collectPlugins()
        for pluginfo in self.plugin_manager.getAllPlugins():

            plugin_item = None

            if '/visual/' in pluginfo.path:
                plugin_item = QTreeWidgetItem(self.visual_root)
            if '/io/' in pluginfo.path:
                plugin_item = QTreeWidgetItem(self.io_root)
            if '/dpp/' in pluginfo.path:
                plugin_item = QTreeWidgetItem(self.dpp_root)
            if '/pcp/' in pluginfo.path:
                plugin_item = QTreeWidgetItem(self.pcb_root)

            if plugin_item is not None:
                plugin_item.pluginfo = pluginfo
                plugin_item.setText(0, pluginfo.name)

    def button_clicked(self, button : QAbstractButton):

        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ApplyRole:

            plugin_item = self.treePlugin.currentItem()

            self.plugin_name = plugin_item.pluginfo.name
            self.plugin_uname = self.le_uname.text()

            config = plugin_item.pluginfo.plugin_object.get_default_config()

#            config['uname'] = self.plugin_uname

            for attr in self.attrs:
                config = self.update_config_value(config, attr, self.attrs[attr].text())

            self.callback_functions['do_create_plugin'](self.plugin_name, self.plugin_uname, config=config)

            self.le_uname.setText('')

            button.setFocus()

    def get_config_value(self,config, name):
        if name in config:
            if type(config[name]) is dict:
                return config[name]['value']
            else:
                return config[name]
        else:
            return None

    def get_config_regex(self,config, name):
        if name in config:
            if type(config[name]) is dict:
                if 'regex' in config[name]:
                    return config[name]['regex']
        return None

    def update_config_value(self,config, name, value):
        if name in config:
            if type(config[name]) is dict:
                config[name]['value'] = value
            else:
                config[name] = value
        return config

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())