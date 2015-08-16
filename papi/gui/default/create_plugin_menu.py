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

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""

from modulefinder import ModuleFinder
import importlib
import re

from papi.gui.default.item import PaPIRootItem, PaPITreeModel
from papi.gui.default.item import PluginTreeItem
from papi.yapsy.PluginManager import PluginManager

__author__ = 'knuths'

from papi.ui.gui.default.PluginCreateMenu import Ui_PluginCreateMenu

from papi.gui.default.create_plugin_dialog import CreatePluginDialog
import papi.constants as pc

from PyQt5.QtCore       import *
from PyQt5.QtGui        import QColor, QDesktopServices
from PyQt5.QtWidgets    import QListWidgetItem, QMainWindow

class CreatePluginMenu(QMainWindow, Ui_PluginCreateMenu):

    def __init__(self, gui_api, TabManger, plugin_manager, parent=None):
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

        # self.plugin_manager.setPluginPlaces(
        #     PLUGIN_ROOT_FOLDER_LIST
        # )
        self.setWindowTitle('Available Plugins')

        model = PaPITreeModel()
        model.setHorizontalHeaderLabels(['Name'])

        self.pluginTree.setModel(model)
        self.pluginTree.setUniformRowHeights(True)
        self.pluginTree.setSortingEnabled(True)

        self.visual_root = PaPIRootItem('ViP')
        self.io_root = PaPIRootItem('IOP')
        self.dpp_root = PaPIRootItem('DPP')
        self.pcp_root = PaPIRootItem('PCP')

        model.appendRow(self.visual_root)
        model.appendRow(self.io_root)
        model.appendRow(self.dpp_root)
        model.appendRow(self.pcp_root)

        self.configuration_inputs = {}

        self.pluginTree.clicked.connect(self.pluginItemChanged)

        self.plugin_create_dialog = CreatePluginDialog(self.gui_api, self.TabManager)

        self.createButton.clicked.connect(self.show_create_plugin_dialog)
        self.helpButton.clicked.connect(self.help_button_triggered)
        self.finder = ModuleFinder()



    def keyPressEvent(self, event):

        if event.key() in [Qt.Key_Right, Qt.Key_Space]:
            index = self.pluginTree.currentIndex()
            self.pluginItemChanged(index)

        if event.key() == Qt.Key_Escape:
            self.close()

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
           self.show_create_plugin_dialog()


    def pluginItemChanged(self, index):
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

                m = re.search('(import)\s+([\w.]*)(\s+as){0,1}',str.strip(line))
                if m is not None:
                    if len(m.groups()) > 2:
                        found_imports.append(m.group(2))

            if line.startswith('from'):
                m = re.search('(from)\s+([\w.]*)(\s+import)',str.strip(line))
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
                item.setBackground(QColor(255,0,0,50))

        if not plugin_info.loadable:

            self.modulesList.setEnabled(True)
            self.modulesLabel.setEnabled(True)



    def show_create_plugin_dialog(self):
        index = self.pluginTree.currentIndex()
        plugin_info = self.pluginTree.model().data(index, Qt.UserRole)

        if plugin_info is not None:
            if plugin_info.loadable:
                self.plugin_create_dialog.set_plugin(plugin_info)
                self.plugin_create_dialog.show()

    def showEvent(self, *args, **kwargs):


        self.plugin_manager.locatePlugins()
        candidates = self.plugin_manager.getPluginCandidates()
        all_pluginfo = {c[2].path:c[2] for c in candidates}
        loadable_pluginfo = {p.path:p for p in self.plugin_manager.getAllPlugins()}

        for pluginfo in all_pluginfo.values():

            if pluginfo.path in loadable_pluginfo.keys():
                pluginfo = loadable_pluginfo[pluginfo.path]
                pluginfo.loadable = True
            else:
                pluginfo.loadable = False
            plugin_item = PluginTreeItem(pluginfo)

            if '/visual/' in pluginfo.path:
                self.visual_root.appendRow(plugin_item)
            if '/io/' in pluginfo.path:
                self.io_root.appendRow(plugin_item)
            if '/dpp/' in pluginfo.path:
                self.dpp_root.appendRow(plugin_item)
            if '/pcp/' in pluginfo.path:
                self.pcp_root.appendRow(plugin_item)

        self.visual_root.sortChildren(0)
        self.io_root.sortChildren(0)
        self.dpp_root.sortChildren(0)
        self.pcp_root.sortChildren(0)

    def help_button_triggered(self):
        index = self.pluginTree.currentIndex()
        plugin_info = self.pluginTree.model().data(index, Qt.UserRole)

        if plugin_info is not None:
            plugin_type = plugin_info.plugin_object.get_type();

            if plugin_type.lower() == 'iop':
                plugin_type = 'io'

            if plugin_type.lower() == 'vip':
                plugin_type = 'visual'


            path = plugin_info.path
            suffix = "." + '.'.join(path.split('/')[-2:])
            target_url = pc.PAPI_DOC_URL + pc.PAPI_DOC_PREFIX_PLUGIN + "." + plugin_type.lower() + suffix + ".html"
            QDesktopServices.openUrl(QUrl(target_url, QUrl.TolerantMode))

    def clear(self):
        self.nameEdit.setText('')
        self.authorEdit.setText('')
        self.descriptionText.setText('')
        self.pathEdit.setText('')
        self.modulesList.clear()
        self.modulesList.setEnabled(False)
        self.modulesLabel.setEnabled(False)

    def closeEvent(self, *args, **kwargs):
        self.plugin_create_dialog.close()