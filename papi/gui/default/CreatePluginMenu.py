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

from modulefinder import ModuleFinder
import importlib
import re
import os
import configparser

from papi.gui.default.item import PaPIRootItem, PaPITreeModel
from papi.gui.default.item import PluginTreeItem, PaPITreeProxyModel

from papi.ui.gui.default.PluginCreateMenu import Ui_PluginCreateMenu
from papi.gui.default.CreatePluginDialog import CreatePluginDialog

from . import get16Icon

import papi.constants as pc

from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QDesktopServices
from PyQt5.QtWidgets import QListWidgetItem, QMainWindow

class CreatePluginMenu(QMainWindow, Ui_PluginCreateMenu):
    """
    This class creates a menu which displays all avaiable plugins.
    This menu is used to create plugin.

    """

    def __init__(self, gui_api, TabManger, plugin_manager, parent=None):
        """
        Constructor of this class.
        'gui_api' is used to access the GUI data storage 'DGUI' and for creating the plugin.
        'TabManager' access to the tab manager is needed because it provides the information about all used tabs.
        'plugin_manager' provides access to the yapsy manager which is used to parse the plugin information.

        :param gui_api:
        :param TabManger:
        :param plugin_manager:
        :param parent:
        :return:
        """
        super(CreatePluginMenu, self).__init__(parent)
        self.setupUi(self)
        self.dgui = gui_api.gui_data
        self.TabManager = TabManger

        self.gui_api = gui_api

        self.subscriberID = None
        self.targetID = None
        self.blockName = None

        self.plugin_manager = plugin_manager

        self.pluginTree.setDragEnabled(True)
        self.pluginTree.setDropIndicatorShown(True)

        self.setWindowTitle('Available Plugins')

        model = PaPITreeModel()
        model.setHorizontalHeaderLabels(['Name'])

        self.pluginProxyModel = PaPITreeProxyModel(self)
        self.pluginProxyModel.setSourceModel(model)

        regex = QRegExp("*", Qt.CaseInsensitive, QRegExp.Wildcard)
        self.pluginProxyModel.setFilterRegExp(regex)

        self.pluginTree.setModel(self.pluginProxyModel)
        self.pluginTree.setUniformRowHeights(True)
        self.pluginTree.setSortingEnabled(True)
        self.pluginTree.setStyleSheet(pc.TREE_CSS)

        self.plugin_roots = {}

        self.configuration_inputs = {}

        self.pluginTree.clicked.connect(self.plugin_item_changed)

        self.plugin_create_dialog = CreatePluginDialog(self.gui_api, self.TabManager)

        self.createButton.clicked.connect(self.show_create_plugin_dialog)
        self.helpButton.clicked.connect(self.help_button_triggered)
        self.finder = ModuleFinder()

        self.pluginSearchText.textChanged.connect(self.changed_search_plugin_text_field)

        self.pluginSearchText.setFocus(Qt.OtherFocusReason)
        self.helpButton.setText('')
        self.helpButton.setIcon(get16Icon('help.png'))
        self.helpButton.setToolTip('Opens the documentation for the currently selected plugin.')

    def keyPressEvent(self, event):
        """
        Default callback function which is called when an any key was pressed by the user.

        :param event:
        :return:
        """

        if event.key() in [Qt.Key_Right, Qt.Key_Space]:
            index = self.pluginTree.currentIndex()
            self.plugin_item_changed(index)

        if event.key() == Qt.Key_Escape:
            self.close()

        # Use enter/return to bring up the dialog for a selected plugin
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and self.pluginTree.hasFocus():
            self.show_create_plugin_dialog()

        # if search bar has focus and user pressed enter/return,arrow up/down, change focus to the plugin tree
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter or event.key() == Qt.Key_Down \
                    or event.key() == Qt.Key_Up) and self.pluginSearchText.hasFocus():
            self.pluginTree.setFocus(Qt.OtherFocusReason)

    def plugin_item_changed(self, index):
        """
        This function is called when the user selects another plugin in the plugin tree on the left side.
        Every change of plugin updates the displayed plugin information on the right side.

        :param index:
        :return:
        """
        plugin_info = self.pluginTree.model().data(index, Qt.UserRole)

        self.clear()

        self.scrollArea.setDisabled(True)

        if plugin_info is None:
            return

        self.scrollArea.setDisabled(False)

        self.nameEdit.setText(plugin_info.name)
        self.authorEdit.setText(plugin_info.author)
        self.descriptionText.setText(plugin_info.description)
        self.pathEdit.setText(plugin_info.path)

        self.createButton.setEnabled(plugin_info.loadable)

        lines = None
        with open(plugin_info.path + '.py') as f:
            lines = f.readlines()

        found_imports = []

        for line in lines:
            if line.startswith('import'):

                m = re.search('(import)\s+([\w.]*)(\s+as){0,1}', str.strip(line))
                if m is not None:
                    if len(m.groups()) > 2:
                        found_imports.append(m.group(2))

            if line.startswith('from'):
                m = re.search('(from)\s+([\w.]*)(\s+import)', str.strip(line))
                if m is not None:
                    if len(m.groups()) > 2:
                        found_imports.append(m.group(2))
        found_imports.sort()

        for imp in found_imports:
            item = QListWidgetItem(imp)

            spam_loader = importlib.find_loader(imp)
            found = spam_loader is not None
            if not found:
                self.modulesList.addItem(item)
                item.setBackground(QColor(255, 0, 0, 50))

        if not plugin_info.loadable:
            self.modulesList.setEnabled(True)
            self.modulesLabel.setEnabled(True)

    def show_create_plugin_dialog(self):
        """
        This function opens the dialog which is used to create plugin.
        An user opens this dialog by selecting a plugin and clicking on the 'Create Plugin' button.

        :return:
        """

        index = self.pluginTree.currentIndex()
        plugin_info = self.pluginTree.model().data(index, Qt.UserRole)

        if plugin_info is not None:
            if plugin_info.loadable:
                self.plugin_create_dialog.set_plugin(plugin_info)
                self.plugin_create_dialog.show()

    def showEvent(self, *args, **kwargs):
        """
        This function is called when the dialog was displayed.

        :param args:
        :param kwargs:
        :return:
        """

        self.plugin_manager.locatePlugins()
        candidates = self.plugin_manager.getPluginCandidates()
        all_pluginfo = {c[2].path: c[2] for c in candidates}
        loadable_pluginfo = {p.path: p for p in self.plugin_manager.getAllPlugins()}

        for plugin_info in all_pluginfo.values():

            if plugin_info.path in loadable_pluginfo.keys():
                plugin_info = loadable_pluginfo[plugin_info.path]
                plugin_info.loadable = True
            else:
                plugin_info.loadable = False
            plugin_item = PluginTreeItem(plugin_info)

            plugin_root = self.get_plugin_root(plugin_info.path)
            plugin_root.appendRow(plugin_item)

        for root in sorted(self.plugin_roots.keys()):
            self.pluginTree.model().sourceModel().appendRow(self.plugin_roots[root])
            self.plugin_roots[root].sortChildren(0)
        self.pluginTree.expandAll()

    def help_button_triggered(self):
        """
        This function opens the documentation page a plugin in the default web browser.
        An user opens the page by selecting a plugin and clicking on the 'Help' button.

        :return:
        """

        index = self.pluginTree.currentIndex()
        plugin_info = self.pluginTree.model().data(index, Qt.UserRole)

        if plugin_info is not None:
            path = plugin_info.path
            plugin_type = path.split('/')[-3]
            suffix = "." + '.'.join(path.split('/')[-2:])
            target_url = pc.PAPI_DOC_URL + pc.PAPI_DOC_PREFIX_PLUGIN + "." + plugin_type.lower() + suffix + ".html"
            QDesktopServices.openUrl(QUrl(target_url, QUrl.TolerantMode))

    def get_plugin_root(self, path):
        """
        This function returns one of the root-Items of the plugin tree.
        The root-Item is determined by the plugin path.

        :return:
        """

        parts = path.split('/')
        part = parts[-3]
        name = part
        if part not in self.plugin_roots:

            cfg_file = str.join("/", parts[0:-2]) + "/" + pc.GUI_PLUGIN_CONFIG

            if os.path.isfile(cfg_file):
                config = configparser.ConfigParser()
                config.read(cfg_file)
                if 'Config' in config.sections():
                    if 'name' in config.options('Config'):
                        name = config.get('Config', 'name')

            self.plugin_roots[part] = PaPIRootItem(name)

        return self.plugin_roots[part]

    def changed_search_plugin_text_field(self, value):
        """
        This function is triggered by the user. It is called when the text in the search field is changed.
        The plugin-Tree is filtered by `value`

        :param value:
        :return:
        """

        if not len(value):
            value = "*"
            self.pluginTree.collapseAll()
        else:
            value = "*" + value + "*"
            self.pluginTree.expandAll()

        self.pluginProxyModel.sourceModel().mark_visibility_by_name(value)

        # Used to trigger filter action
        regex = QRegExp(value, Qt.CaseInsensitive, QRegExp.Wildcard)
        self.pluginProxyModel.setFilterRegExp(regex)

    def clear(self):
        """
        This function is called to reset all necessary labels and line edits.

        :return:
        """

        self.nameEdit.setText('')
        self.authorEdit.setText('')
        self.descriptionText.setText('')
        self.pathEdit.setText('')
        self.modulesList.clear()
        self.modulesList.setEnabled(False)
        self.modulesLabel.setEnabled(False)

    def closeEvent(self, *args, **kwargs):
        """
        Handles close events for this windows.
        Closing windows will also close the plugin create dialog.

        :param args:
        :param kwargs:
        :return:
        """

        self.plugin_create_dialog.close()
