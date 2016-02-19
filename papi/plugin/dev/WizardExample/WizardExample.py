#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
 
Contributors:
<Stefan Ruppin
"""



from papi.plugin.base_classes.vip_base import vip_base
from PyQt5.QtWidgets import QMdiSubWindow, QLabel, QVBoxLayout, QWizardPage, QWizard, QLineEdit
from PyQt5 import QtCore, QtGui


class WizardExample(vip_base):
    def cb_initialize_plugin(self):
        self.wizardwidget = QWizard()
        self.wizardwidget.addPage(self.createIntroPage())
        self.wizardwidget.addPage(sinPage(self.control_api))
        self.wizardwidget.addPage(plotPage(self.control_api))
        self.wizardwidget.addPage(connectPage(self.control_api,'WizardExample'))

        self.pl_set_widget_for_internal_usage( self.wizardwidget )

        self.wizardwidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.wizardwidget.customContextMenuRequested.connect(self.show_context_menu)

        return True

    def show_context_menu(self, pos):
        gloPos = self.wizardwidget.mapToGlobal(pos)
        self.cmenu = self.pl_create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):
        pass

    def cb_set_parameter(self, name, value):
        pass

    def cb_quit(self):
        pass

    def cb_get_plugin_configuration(self):
        config = {}
        return config

    def cb_plugin_meta_updated(self):
        pass

    def createIntroPage(self):
        page = QWizardPage()
        page.setTitle("Introduction")

        label = QLabel("This wizard will show you a simple wizard.")
        label.setWordWrap(True)

        label2 = QLabel("Therefore it will create a Sine plugin, a plot and connect these two.")
        label2.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(label2)

        page.setLayout(layout)
        return page


# CLASS FOR SINUS CREATION PAGE
class sinPage(QWizardPage):
    def __init__(self, controlAPI,parent = None):
        QWizardPage.__init__(self, parent)
        self.setTitle("Create the SINUS")
        self.control_api = controlAPI
        label = QLabel("Now you should enter a uname for the Sinus.")
        label.setWordWrap(True)

        uname_label = QLabel("Uname of Sinus (not used)")
        self.uname_edit = QLineEdit()
        uname_label.setBuddy(self.uname_edit)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(uname_label)
        layout.addWidget(self.uname_edit)

        self.setLayout(layout)

    def validatePage(self):
        print('uname from wizzard',self.uname_edit.text())
        self.control_api.do_create_plugin('Sine','Sin1' , {}, True)
        return True


# CLASS FOR PLOT CREATION PAGE
class plotPage(QWizardPage):
    def __init__(self, controlAPI,parent = None):
        QWizardPage.__init__(self, parent)
        self.setTitle("Create the Plot")
        self.control_api = controlAPI
        label = QLabel("This page will create a plot.")
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def validatePage(self):
        cfg = {
            'size': {
                'value': "(300,300)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
            },
            'position': {
                'value': "(400,100)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine position: (x,y)'
            }}

        self.control_api.do_create_plugin('Plot','Plot1' , cfg, True)
        return True


# CLASS FOR SUB OF BOTH PLUGINS
class connectPage(QWizardPage):
    def __init__(self, controlAPI,name,parent = None):
        QWizardPage.__init__(self, parent)
        self.setTitle("Connect the Plot")
        self.control_api = controlAPI
        self.uname = name
        label = QLabel("This page connect plot and Sine.")
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def validatePage(self):
        self.control_api.do_subscribe_uname('Plot1','Sin1','SinMit_f3', signals=['f3_1', 'f3_2'])
        self.control_api.do_delete_plugin_uname(self.uname)
        return True
