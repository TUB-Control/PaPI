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

__author__ = 'control'

from PySide.QtGui import QDialog, QLineEdit, QRegExpValidator, QCheckBox , QTabWidget
from PySide.QtCore import *
from papi.pyqtgraph import QtCore, QtGui

from papi.constants import PLUGIN_PCP_IDENTIFIER, PLUGIN_IOP_IDENTIFIER, PLUGIN_VIP_IDENTIFIER, PLUGIN_DPP_IDENTIFIER


class PapiTabManger(QObject):

    def __init__(self, tabWigdet = None, dgui = None, parent=None):
        super(PapiTabManger, self).__init__(parent)

        self.tabWidget = tabWigdet

        self.tabWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.cmenu = self.create_context_menu()

        self.tabWidget.tabCloseRequested.connect(self.closeTab)

        self.dGui = dgui
        # make tabs movable
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)

        # create dict for saving tabs
        self.tab_dict_uname = {}

        self.add_tab(name='Tab')

    def get_tabs_by_uname(self):
        return self.tab_dict_uname

    def add_tab(self, name):
        if name in self.tab_dict_uname:
            print('Tab with name already exists')
        else:
            newTab = TabObject( name)
            newTab.index = self.tabWidget.addTab(newTab,newTab.name)

            self.tab_dict_uname[newTab.name] = newTab

            return newTab

    def remove_tab(self,tabObject):
        self.tab_dict_uname.pop(tabObject.name)
        ind = self.tabWidget.indexOf(tabObject)
        self.tabWidget.removeTab(ind)
        tabObject.destroy()


    def rename_tab(self, tabObject, new_name):
        if new_name not in self.tab_dict_uname:
            # rename it
            self.tab_dict_uname.pop(tabObject.name)
            tabObject.name = new_name
            self.tab_dict_uname[tabObject.name] = tabObject
            ind = self.tabWidget.indexOf(tabObject)
            self.tabWidget.setTabText(ind,tabObject.name)


    def get_first_tab(self):
        return self.tabWidget.widget(0)

    def moveFromTo(self, start, dest, subWindow, posX=0, posY=0):
        if start in self.tab_dict_uname and dest in self.tab_dict_uname:
            startTab = self.tab_dict_uname[start]
            destTab = self.tab_dict_uname[dest]
            startTab.removeSubWindow(subWindow)
            destTab.addSubWindow(subWindow)
            subWindow.move(posX, posY)
            subWindow.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowTitleHint )
            return True

    def show_context_menu(self, pos):
        gloPos = self.tabWidget.mapToGlobal(pos)
        self.cmenu.exec_(gloPos)

    def create_context_menu(self):
        ctrlMenu = QtGui.QMenu("Control")

        new_tab_action = QtGui.QAction('New Tab',self.tabWidget)
        new_tab_action.triggered.connect(self.cmenu_new_tab)

        close_tab_action = QtGui.QAction('Close Tab',self.tabWidget)
        close_tab_action.triggered.connect(self.cmenu_close_tab)

        rename_tab_action = QtGui.QAction('Rename Tab',self.tabWidget)
        rename_tab_action.triggered.connect(self.cmenu_rename_tab)

        ctrlMenu.addAction(new_tab_action)
        ctrlMenu.addAction(close_tab_action)
        ctrlMenu.addAction(rename_tab_action)

        return ctrlMenu

    def cmenu_new_tab(self):
        name = 'Tab'
        while name in self.tab_dict_uname:
            name = name + 'X'
        self.add_tab(name)


    def cmenu_close_tab(self):
        ind = self.tabWidget.currentIndex()
        self.closeTab(ind)

    def closeTab(self, ind):
        tabOb = self.tabWidget.widget(ind)
        tab_name = tabOb.name

        plugins = self.dGui.get_all_plugins()
        for pl_id in plugins:
            plugin = plugins[pl_id]
            if plugin.type == PLUGIN_VIP_IDENTIFIER or plugin.type == PLUGIN_PCP_IDENTIFIER:
                if plugin.startup_config['tab']['value'] == tab_name:
                    self.moveFromTo(tab_name,self.get_first_tab().name, plugin.plugin.get_sub_window())
                    plugin.startup_config['tab']['value'] = self.get_first_tab()

        self.remove_tab(tabOb)

    def cmenu_rename_tab(self):
        tabOb = self.tabWidget.currentWidget()
        self.rename_tab(tabOb,'NEW NAME')






class TabObject(QtGui.QMdiArea):
    def __init__(self, name, parent=None):
        super(TabObject, self).__init__(parent)
        self.index = None
        self.name = name
        self.background = None


