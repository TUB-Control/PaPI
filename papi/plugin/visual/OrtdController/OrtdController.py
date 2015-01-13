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

__author__ = 'Stefan'

from papi.plugin.base_classes.vip_base import vip_base

from PySide import QtGui, QtCore
from PySide.QtGui import QRegExpValidator

import threading, time


class OrtdController(vip_base):

    def initiate_layer_0(self, config=None):

        # ---------------------------
        # Read configuration
        # ---------------------------
        self.ortd_uname = config['ORTD_Plugin_uname']['value']
        self.alreadyConfigured = False
        # --------------------------------
        # Create Widget
        # --------------------------------
        # Create Widget needed for this plugin
        self.ControllerWidget = QtGui.QWizard()
        self.ControllerWidget.setOption(QtGui.QWizard.NoCancelButton)
        self.ControllerWidget.setOption(QtGui.QWizard.NoBackButtonOnLastPage)
        self.ControllerWidget.setOption(QtGui.QWizard.NoBackButtonOnStartPage)
        self.ControllerWidget.setOption(QtGui.QWizard.DisabledBackButtonOnLastPage)
        self.set_widget_for_internal_usage( self.ControllerWidget )
        self.ControllerWidget.addPage(ControllerIntroPage())
        self.ControllerWidget.addPage(ControllerOrtdStart(api=self.control_api, uname=self.dplugin_info.uname,ortd_uname=self.ortd_uname))
        self.ControllerWidget.addPage(ControllerWorking(api=self.control_api, uname=self.dplugin_info.uname))

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

    def execute(self, Data=None, block_name = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data['t'] = [t1, t2, ...] where 't' is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []
        if self.alreadyConfigured is False:
            self.thread1 = threading.Thread(target=self.execute_cfg, args=[Data])
            self.alreadyConfigured = True
            self.thread1.start()

    def execute_cfg(self,Data):
        ############################
        #       Create Plugins     #
        ############################
        if 'ControlSignalCreate' in Data:
            cfg = Data['ControlSignalCreate']
            for pl_uname in cfg:
                pl_cfg = cfg[pl_uname]
                self.control_api.do_create_plugin(pl_cfg['identifier']['value'],pl_uname, pl_cfg['config'])
        time.sleep(0.5)

        ############################
        #       Create Subs        #
        ############################
        if 'ControlSignalSub' in Data:
            cfg = Data['ControlSignalSub']
            for pl_uname in cfg:
                pl_cfg = cfg[pl_uname]
                sig = []
                if 'signals' in pl_cfg:
                    sig = pl_cfg['signals']
                self.control_api.do_subscribe_uname(pl_uname,self.ortd_uname, pl_cfg['block'], signals=sig, sub_alias= None)

        ############################
        #    Set parameter links   #
        ############################
        if 'ControllerSignalParameter' in Data:
            cfg = Data['ControllerSignalParameter']
            for pl_uname in cfg:
                pl_cfg = cfg[pl_uname]
                para = None
                if 'parameter' in pl_cfg:
                    para = pl_cfg['parameter']
                self.control_api.do_subscribe_uname(self.ortd_uname,pl_uname, pl_cfg['block'], signals=[], sub_alias= para)

        ############################
        #    Close plugin          #
        ############################
        if 'ControllerSignalClose' in Data:
            cfg = Data['ControllerSignalClose']
            for pl_uname in cfg:
                self.control_api.do_delete_plugin_uname(pl_uname)


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
        config = {
            "ORTD_Plugin_uname": {
                'value': 'ORTDPlugin1',
                'display_text': 'Uname to use for ortd plugin instance',
                'advanced': "0"
            },
            'name': {
                'value': 'ORTDController'
            }
        }
        return config

    def plugin_meta_updated(self):
        """
        Whenever the meta information is updated this function is called (if implemented).

        :return:
        """

        #dplugin_info = self.dplugin_info
        pass



class ControllerIntroPage(QtGui.QWizardPage):
    def __init__(self,parent = None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setTitle("ORTD Controller")
        label = QtGui.QLabel("This is the ORTD Controller plugin.")
        label.setWordWrap(True)

        label2 = QtGui.QLabel("Click next to start the configuration")

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(label2)

        self.setLayout(layout)

    def validatePage(self):
        print('intro: next clicked')
        return True


class ControllerOrtdStart(QtGui.QWizardPage):
    def __init__(self,api = None, uname= None, parent = None, ortd_uname = None):
        QtGui.QWizardPage.__init__(self, parent)
        self.uname = uname
        self.api = api
        self.ortd_uname = ortd_uname
        self.setTitle("ORTD Controller")
        label = QtGui.QLabel("Please configure the ORTD plugin.")
        label.setWordWrap(True)

        # ----------- #
        # IP line edit#
        # ----------- #
        self.ip_line_edit = QtGui.QLineEdit()
        ip_label = QtGui.QLabel('IP-Address:')
        ip_label.setBuddy(self.ip_line_edit)
        regex = '\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}'
        rx = QtCore.QRegExp(regex)
        validator = QRegExpValidator(rx, self)
        self.ip_line_edit.setValidator(validator)
        self.ip_line_edit.setText('127.0.0.1')

        # ----------- #
        # Port line edit#
        # ----------- #
        self.port_line_edit = QtGui.QLineEdit()
        port_label = QtGui.QLabel('Port:')
        port_label.setBuddy(self.port_line_edit)
        regex = '\d{1,5}'
        rx = QtCore.QRegExp(regex)
        validator = QRegExpValidator(rx, self)
        self.port_line_edit.setValidator(validator)
        self.port_line_edit.setText('20000')


        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(ip_label)
        layout.addWidget(self.ip_line_edit)
        layout.addWidget(port_label)
        layout.addWidget(self.port_line_edit)

        self.setLayout(layout)

    def validatePage(self):
        print('Start: next clicked')
        IP = self.ip_line_edit.text()
        port = self.port_line_edit.text()
        cfg ={
            'address': {
                'value': IP,
                'advanced': '1'
            },
            'source_port': {
                'value': port,
                'advanced': '1'
            },
            'out_port': {
                'value': '20001',
                'advanced': '1'
            }
        }
        self.api.do_create_plugin('ORTD_UDP', self.ortd_uname, cfg, True)

        self.thread = threading.Thread(target=self.subscribe_control_signal)
        self.thread.start()

        return True

    def subscribe_control_signal(self):
        time.sleep(0.5)
        self.api.do_subscribe_uname(self.uname,self.ortd_uname, 'ControllerSignals', signals=['ControlSignalCreate',
                                                                                              'ControlSignalSub',
                                                                                              'ControllerSignalParameter',
                                                                                              'ControllerSignalClose'])
        self.api.do_set_parameter_uname(self.ortd_uname, 'triggerConfiguration', 0)


class ControllerWorking(QtGui.QWizardPage):
    def __init__(self,api = None, uname= None, parent = None):
        QtGui.QWizardPage.__init__(self, parent)
        self. api = api

        self.setTitle("ORTD Controller")
        label = QtGui.QLabel("Controller plugin is working")
        label.setWordWrap(True)

        label2 = QtGui.QLabel("")

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(label2)

        self.setLayout(layout)

    def validatePage(self):
        return False
