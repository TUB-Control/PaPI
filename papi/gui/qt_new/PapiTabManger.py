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

from PyQt4.QtGui import QDialog, QLineEdit, QRegExpValidator, QCheckBox , QTabWidget
from PyQt4.QtCore import *
from papi.pyqtgraph import QtCore, QtGui
from papi.gui.qt_new.custom import FileLineEdit
from papi.constants import PLUGIN_PCP_IDENTIFIER, PLUGIN_IOP_IDENTIFIER, PLUGIN_VIP_IDENTIFIER, PLUGIN_DPP_IDENTIFIER


class PapiTabManger(QObject):

    def __init__(self, tabWigdet = None, dgui = None,gui_api = None, parent=None):
        super(PapiTabManger, self).__init__(parent)

        self.tabWidget = tabWigdet
        self.gui_api = gui_api
        self.tabWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.cmenu = self.create_context_menu()

        self.tabWidget.tabCloseRequested.connect(self.closeTab_by_ind)

        self.tabWidget.setTabShape(QtGui.QTabWidget.Triangular)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)

        self.dGui = dgui
        # make tabs movable
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)

        # create dict for saving tabs
        self.tab_dict_uname = {}

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
            old_name = tabObject.name
            self.tab_dict_uname.pop(tabObject.name)

            tabObject.name = new_name
            self.tab_dict_uname[tabObject.name] = tabObject

            ind = self.tabWidget.indexOf(tabObject)
            self.tabWidget.setTabText(ind,tabObject.name)

            allPlugins = self.dGui.get_all_plugins()
            for pluign_ind in allPlugins:
                dplugin = allPlugins[pluign_ind]
                if dplugin.plugin.get_type() == PLUGIN_VIP_IDENTIFIER or dplugin.plugin.get_type() == PLUGIN_PCP_IDENTIFIER:
                    tabOfPlugin = dplugin.plugin.config['tab']['value']
                    if tabOfPlugin == old_name:
                        dplugin.plugin.config['tab']['value'] = new_name

    def get_default_tab(self, NotThisIndex):
        if NotThisIndex == 0:
           if self.tabWidget.count() > 1:
                return self.tabWidget.widget(1)
           else:
                raise Exception('no tab open')
        else:
            return self.tabWidget.widget(0)

    def get_currently_active_tab(self):
        return self.tabWidget.currentIndex()

    def set_tab_active_by_index(self, index):
        self.tabWidget.setCurrentIndex(index)

    def set_tab_active_by_name(self, tabName):
        if tabName in self.tab_dict_uname:
            tabObj = self.tab_dict_uname[tabName]
            ind = self.tabWidget.indexOf(tabObj)
            self.set_tab_active_by_index(ind)

    def moveFromTo(self, start, dest, subWindow, posX=0, posY=0):
        if start in self.tab_dict_uname and dest in self.tab_dict_uname:
            startTab = self.tab_dict_uname[start]
            destTab = self.tab_dict_uname[dest]
            startTab.removeSubWindow(subWindow)
            destTab.addSubWindow(subWindow)
            subWindow.show()
            subWindow.move(posX, posY)
            subWindow.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowTitleHint )
            return True
        else:
            return False

    def set_background_for_tab_with_name(self, name, bg):
        if bg is not None:
            if name in self.tab_dict_uname:
                pixmap  = QtGui.QPixmap(bg)
                widgetArea = self.tab_dict_uname[name]

                qbrush_bg = QtGui.QBrush(QtGui.QColor() ,pixmap)

                widgetArea.setBackground(qbrush_bg)
                widgetArea.background = bg

    def set_all_tabs_to_close_when_empty(self, state):
        for tabName in self.tab_dict_uname:
            tabO = self.tab_dict_uname[tabName]
            tabO.closeIfempty = state

    def closeTab_by_ind(self, ind):
        tabOb = self.tabWidget.widget(ind)
        tab_name = tabOb.name
        if self.tabWidget.count() > 1 or len(tabOb.subWindowList()) == 0: #tab_name != 'Default':
            # not the default tab, just close and move plugins to default tab
            plugins = self.dGui.get_all_plugins()
            for pl_id in plugins:
                plugin = plugins[pl_id]
                if plugin.type == PLUGIN_VIP_IDENTIFIER or plugin.type == PLUGIN_PCP_IDENTIFIER:
                    if plugin.plugin.config['tab']['value'] == tab_name:
                        self.moveFromTo(tab_name,self.get_default_tab(ind).name, plugin.plugin.get_sub_window())
                        plugin.plugin.config['tab']['value'] = self.get_default_tab(ind).name

            self.remove_tab(tabOb)
        else:
            # default tab: ask if really want to close
            diag = DefaultCloseBox()#QtGui.QDialog()
            ret = diag.exec_()
            if ret == QtGui.QMessageBox.Ok:
                allPlugins = self.dGui.get_all_plugins()
                for pl_id in allPlugins:
                    dplugin = allPlugins[pl_id]
                    if dplugin.own_process is False:
                        self.gui_api.do_delete_plugin(dplugin.id)
                self.remove_tab(tabOb)

    def closeTab_by_name(self,name):
        if name in self.tab_dict_uname:
            tabO = self.tab_dict_uname[name]
            ind = self.tabWidget.indexOf(tabO)
            self.closeTab_by_ind(ind)

    def close_all_empty_tabs(self):
        tabs = self.tab_dict_uname
        tabs_to_close = []
        for tab in tabs:
            tabO = tabs[tab]
            if tabO.isEmpty():
                tabs_to_close.append(tab)

        for tab in tabs_to_close:
            self.closeTab_by_name(tab)

    def getTabPosition_by_name(self, tabName):
        if tabName in self.tab_dict_uname:
            tabObj = self.tab_dict_uname[tabName]
            ind = self.tabWidget.indexOf(tabObj)
            return ind

    def setTabs_movable_closable(self, move, close):
        if isinstance(move, bool):
            self.tabWidget.setMovable(move)

        if isinstance(close,bool):
            self.tabWidget.setTabsClosable(close)


    def show_context_menu(self, pos):
        self.cmenu = self.create_context_menu()
        gloPos = self.tabWidget.mapToGlobal(pos)
        self.cmenu.exec_(gloPos)

    def create_context_menu(self):
        ctrlMenu = QtGui.QMenu("")


        title_action = QtGui.QAction('Tab menu', self.tabWidget)
        title_action.setDisabled(True)

        sep_action = QtGui.QAction('',self.tabWidget)
        sep_action.setSeparator(True)

        new_tab_action = QtGui.QAction('New Tab',self.tabWidget)
        new_tab_action.triggered.connect(self.cmenu_new_tab)

        new_tab_action_cust_name = QtGui.QAction('New Tab with name',self.tabWidget)
        new_tab_action_cust_name.triggered.connect(self.cmenu_new_tab_custom_name)

        close_tab_action = QtGui.QAction('Close Tab',self.tabWidget)
        close_tab_action.triggered.connect(self.cmenu_close_tab)

        rename_tab_action = QtGui.QAction('Rename Tab',self.tabWidget)
        rename_tab_action.triggered.connect(self.cmenu_rename_tab)

        bg_action = QtGui.QAction('Set background',self.tabWidget)
        bg_action.triggered.connect(self.cmenu_set_bg)

        ctrlMenu.addAction(title_action)
        ctrlMenu.addAction(sep_action)
        ctrlMenu.addAction(sep_action)
        ctrlMenu.addAction(new_tab_action)
        ctrlMenu.addAction(new_tab_action_cust_name)
        if self.tabWidget.count() > 0:
            ctrlMenu.addAction(close_tab_action)
            ctrlMenu.addAction(rename_tab_action)
            ctrlMenu.addAction(bg_action)

        return ctrlMenu

    def cmenu_new_tab(self):
        name = 'Tab'
        while name in self.tab_dict_uname:
            name = name + 'X'
        self.add_tab(name)

    def cmenu_new_tab_custom_name(self):
        name = 'Tab'
        while name in self.tab_dict_uname:
            name = name + 'X'
        text, ok = QtGui.QInputDialog.getText(self.tabWidget, 'Tab name',' Name of new tab', QtGui.QLineEdit.Normal,name)

        if ok:
            if text in self.tab_dict_uname:
                print('Tab name already exists')
            else:
                self.add_tab(text)

    def cmenu_set_bg(self):
        fileNames = ''

        dialog = QtGui.QFileDialog(self.tabWidget)
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)

        if dialog.exec_():
            fileNames = dialog.selectedFiles()

        if len(fileNames):
            if fileNames[0] != '':
                path = fileNames[0]
                self.set_background_for_tab_with_name(self.tabWidget.currentWidget().name, path)

    def cmenu_close_tab(self):
        ind = self.tabWidget.currentIndex()
        self.closeTab_by_ind(ind)

    def cmenu_rename_tab(self):
        tabOb = self.tabWidget.currentWidget()

        text, ok = QtGui.QInputDialog.getText(self.tabWidget, 'Rename a tab','New name for tab: '+ tabOb.name,
                                              QtGui.QLineEdit.Normal,tabOb.name)

        if ok:
            if text in self.tab_dict_uname:
                #print('Tab name already exists')
                pass
            else:
                self.rename_tab(tabOb,text)



class TabObject(QtGui.QMdiArea):
    def __init__(self, name, parent=None):
        super(TabObject, self).__init__(parent)
        self.index = None
        self.name = name
        self.background = 'default'
        self.closeIfempty = False

    def isEmpty(self):
        return len(self.subWindowList()) == 0


class DefaultCloseBox(QtGui.QMessageBox):

    def __init__(self, parent=None):
        super(DefaultCloseBox, self).__init__(parent)
        self.setWindowTitle('Close last tab?')
        self.setText('All plugins in this tab will be closed. Are you sure?')
        self.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)


