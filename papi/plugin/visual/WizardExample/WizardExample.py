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

from papi.plugin.base_classes.vip_base import vip_base
from PyQt5.QtWidgets import QMdiSubWindow, QLabel, QVBoxLayout, QWizardPage, QWizard, QLineEdit
from PyQt5 import QtCore, QtGui


class WizardExample(vip_base):

    def createIntroPage(self):
        page = QWizardPage()
        page.setTitle("Introduction")

        label = QLabel("This wizard will show you a simple wizard.")
        label.setWordWrap(True)

        label2 = QLabel("Therefore it will create a sinus plugin, a plot and connect these two.")
        label2.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(label2)


        page.setLayout(layout)
        return page




    def initiate_layer_0(self, config=None):

        #self.config = config

        # ---------------------------
        # Read configuration
        # ---------------------------
        # Note: this cfg items have to exist!
        # self.show_grid_x = int(self.config['x-grid']['value']) == '1'
        # self.show_grid_y = int(self.config['y-grid']['value']) == '1'
        #
        # int_re = re.compile(r'(\d+)')
        #
        # self.colors_selected = int_re.findall(self.config['color']['value']);
        # self.types_selected = int_re.findall(self.config['style']['value']);


        # --------------------------------
        # Create Widget
        # --------------------------------
        # Create Widget needed for this plugin

        self.wizardwidget = QWizard()
        self.wizardwidget.addPage(self.createIntroPage())
        self.wizardwidget.addPage(sinPage(self.control_api))
        self.wizardwidget.addPage(plotPage(self.control_api))
        self.wizardwidget.addPage(connectPage(self.control_api,'WizardExample'))



        # This call is important, because the background structure needs to know the used widget!
        # In the background the qmidiwindow will becreated and the widget will be added
        self.set_widget_for_internal_usage( self.wizardwidget )

        # ---------------------------
        # Create Parameters
        # ---------------------------
        # create a parameter object
        #   self.para1 = DParameter('ParameterName',InitWert,1)
        #   self.para2 = DParameter('ParameterName',InitWert,1)

        # build parameter list to send to Core
        #   para_list = [self.para1 self.para2]
        #   self.send_new_parameter_list(para_list)

        # ---------------------------
        # Create Legend
        # ---------------------------


        return True

    def pause(self):
        # will be called, when plugin gets paused
        # can be used to get plugin in a defined state before pause
        # e.a. close communication ports, files etc.
        pass

    def resume(self):
        # will be called when plugin gets resumed
        # can be used to wake up the plugin from defined pause state
        # e.a. reopen communication ports, files etc.
        pass

    def execute(self, Data=None, block_name = None, plugin_uname = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data['t'] = [t1, t2, ...] where 't' is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []

        pass

    def set_parameter(self, name, value):
        # attetion: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value
        pass

    def quit(self):
        # do something before plugin will close, e.a. close connections ...
        pass


    def get_plugin_configuration(self):
        #
        # Implement a own part of the config
        # config is a hash of hass object
        # config_parameter_name : {}
        # config[config_parameter_name]['value']  NEEDS TO BE IMPLEMENTED
        # configs can be marked as advanced for create dialog
        # http://utilitymill.com/utility/Regex_For_Range

        # config = {
        #     "amax": {
        #         'value': 3,
        #         'regex': '[0-9]+',
        #         'display_text' : 'This AMax',
        #         'advanced' : '1'
        # }, 'f': {
        #         'value': "1",
        #         'regex': '\d+.{0,1}\d*'
        # }}
        config = {}
        return config

    def plugin_meta_updated(self):
        """
        Whenever the meta information is updated this function is called (if implemented).

        :return:
        """

        #dplugin_info = self.dplugin_info
        pass





# CLASS FOR SINUS CREATION PAGE
class sinPage(QWizardPage):
    def __init__(self, controlAPI,parent = None):
        QWizardPage.__init__(self, parent)
        self.setTitle("Create the SINUS")
        self.control_api = controlAPI
        label = QLabel("Now you should enter a uname for the Sinus.")
        label.setWordWrap(True)

        uname_label = QLabel("Uname of Sinus (wird aber nicht benutzt)")
        self.uname_edit = QLineEdit()
        uname_label.setBuddy(self.uname_edit)

        #QtGui.QWizardPage.registerField("uname",uname_edit)


        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(uname_label)
        layout.addWidget(self.uname_edit)

        self.setLayout(layout)

    def validatePage(self):
        print('uname from wizzard',self.uname_edit.text())
        self.control_api.do_create_plugin('Sinus','Sin1' , {}, True)
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
        label = QLabel("This page connect plot and sinus.")
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)


        self.setLayout(layout)

    def validatePage(self):
        self.control_api.do_subscribe_uname('Plot1','Sin1','SinMit_f3', signals=['f3_1', 'f3_2'])
        self.control_api.do_delete_plugin_uname(self.uname)
        return True
