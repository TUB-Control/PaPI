#!/usr/bin/python3
#-*- coding: utf-8 -*-

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
Stefan Ruppin
"""

from papi.plugin.base_classes.base_visual import base_visual

from papi.constants import PLUGIN_VIP_IDENTIFIER

from papi.pyqtgraph.Qt import QtGui

class vip_base(base_visual):

    def initiate_layer_1(self, config):
        return self.initiate_layer_0(config)

    def initiate_layer_0(self, config):
        raise NotImplementedError("Please Implement this method")

    def get_type(self):
        return PLUGIN_VIP_IDENTIFIER

    def create_control_context_menu(self):
        ctrlMenu = QtGui.QMenu("Control")

        del_action = QtGui.QAction('Exit plugin',self.widget)
        del_action.triggered.connect(self.ctlrMenu_exit)

        pause_action = QtGui.QAction('Pause plugin',self.widget)
        pause_action.triggered.connect(self.ctlrMenu_pause)

        resume_action = QtGui.QAction('Resume plugin',self.widget)
        resume_action.triggered.connect(self.ctlrMenu_resume)

        subMenu_action = QtGui.QAction('Open Signal Manager',self.widget)
        #subMenu_action.triggered.connect(self.ctlrMenu_resume)


        tabMenu = QtGui.QMenu('Move to')
        tabs = list(self.TabManager.get_tabs_by_uname().keys())
        tab_entrys = []
        for t in tabs:
            if t != self.config['tab']['value']:
                entry = QtGui.QAction(t, self.widget)
                entry.triggered.connect(lambda p=t: self.tabMenu_triggered(p))
                tab_entrys.append(entry)
                tabMenu.addAction(entry)


        ctrlMenu.addMenu(tabMenu)
        ctrlMenu.addAction(subMenu_action)
        ctrlMenu.addAction(resume_action)
        ctrlMenu.addAction(pause_action)
        ctrlMenu.addAction(del_action)
        return ctrlMenu

    def tabMenu_triggered(self, item):
        pos = self._subWindow.pos()
        posX = pos.x()
        posY = pos.y()
        if self.TabManager.moveFromTo(self.config['tab']['value'], item, self._subWindow, posX=posX, posY=posY):
            self.config['tab']['value'] = item


    def ctlrMenu_exit(self):
        self.control_api.do_delete_plugin_uname(self.dplugin_info.uname)

    def ctlrMenu_pause(self):
        self.control_api.do_pause_plugin_by_uname(self.dplugin_info.uname)

    def ctlrMenu_resume(self):
        self.control_api.do_resume_plugin_by_uname(self.dplugin_info.uname)