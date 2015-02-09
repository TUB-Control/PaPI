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


class PapiTabManger(QObject):

    def __init__(self, tabWigdet = None, parent=None):
        super(PapiTabManger, self).__init__(parent)

        self.tabWidget = tabWigdet

        self.tabWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.cmenu = self.create_context_menu()

        # make tabs movable
        self.tabWidget.setMovable(True)

        # create dict for saving tabs
        self.tab_dict_id = {}
        self.tab_dict_uname = {}

        self.add_tab()
        self.add_tab()
        self.add_tab(name='Tab')

    def get_tabs_by_id(self):
        return self.tab_dict_id

    def get_tabs_by_uname(self):
        return self.tab_dict_uname

    def add_tab(self, name = None):
        # check tab name for existance
        if name is None:
            tab_name = 'Tab'
        else:
            tab_name = name

        # check if unique
        while tab_name in self.tab_dict_uname:
            tab_name = tab_name + 'X'


        area = QtGui.QMdiArea()
        id = self.tabWidget.addTab(area,tab_name)
        newTab = TabObject(id, area, tab_name)

        if id not in self.tab_dict_id:
            self.tab_dict_id[id] = newTab
        else:
            print('tab id already in list')

        if newTab.name not in self.tab_dict_uname:
            self.tab_dict_uname[newTab.name] = newTab
        else:
            print('tab uname already in list')

    def rename_tab(self, id, new_name ):
        self.name = new_name
        if id in self.tab_dict:
            tab = self.tab_dict[id]
            tab.name = new_name
            self.tabWidget.setTabText(id,tab.name)

    def show_context_menu(self, pos):
        gloPos = self.tabWidget.mapToGlobal(pos)
        self.cmenu.exec_(gloPos)

    def create_context_menu(self):
        ctrlMenu = QtGui.QMenu("Control")
        new_tab_action = QtGui.QAction('New Tab',self.tabWidget)
        new_tab_action.triggered.connect(self.cmenu_new_tab)
        close_tab_action = QtGui.QAction('Close Tab',self.tabWidget)
        ctrlMenu.addAction(new_tab_action)
        ctrlMenu.addAction(close_tab_action)
        return ctrlMenu

    def cmenu_new_tab(self):
        print('TODO: new tab')


    def cmenu_close_tab(self):
        print('TODO: close tab')

class TabObject(QObject):
    def __init__(self, id, widgetArea, name, parent=None):
        super(TabObject, self).__init__(parent)
        self.id = id
        self.widgetArea = widgetArea
        self.name = name
        self.background = None


