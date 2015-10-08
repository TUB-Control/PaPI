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

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
<Stefan Ruppin
"""



from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
from PyQt5.QtGui     import QHBoxLayout

import subprocess
import os
from signal import SIGTERM


from papi.plugin.base_classes.vip_base import vip_base

import papi.constants as pc




class StartExternalScript(vip_base):


    def initiate_layer_0(self, config=None):

        # --------------------------------
        # Create Widget
        # --------------------------------
        # Create Widget needed for this plugin

        self.SESWidget = QWidget()
        self.set_widget_for_internal_usage( self.SESWidget )


        hbox = QHBoxLayout()
        self.SESWidget.setLayout(hbox)


        self.status_label = QLabel()
        self.status_label.setText('offline...')

        hbox.addWidget(self.status_label)

        self.control_button = QPushButton('Start External Script')
        self.control_button.clicked.connect(self.button_click_callback)

        hbox.addWidget(self.control_button)


        # ---------------------------
        # Create Legend
        # ---------------------------
        self.external_state = 'offline'

        self.path = config['path']['value']
        file = os.path.basename(self.path)
        self.dir = self.path[:-len(file)]

        return True

    def button_click_callback(self):
        if self.external_state == 'offline':
            self.external_state = 'online'
            self.control_button.setText('Stop External Script')
            self.status_label.setText('running...')
            self.process = subprocess.Popen(self.path, cwd=self.dir,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False, preexec_fn=os.setsid)
        else:
            self.external_state = 'offline'
            self.control_button.setText('Start External Script')
            self.status_label.setText('offline...')
            os.killpg(self.process.pid, SIGTERM)

    def cb_pause(self):
        # will be called, when plugin gets paused
        # can be used to get plugin in a defined state before pause
        # e.a. close communication ports, files etc.
        pass

    def cb_resume(self):
        # will be called when plugin gets resumed
        # can be used to wake up the plugin from defined pause state
        # e.a. reopen communication ports, files etc.
        pass

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data[CORE_TIME_SIGNAL] = [t1, t2, ...] where CORE_TIME_SIGNAL is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []

        pass

    def cb_set_parameter(self, name, value):
        # attetion: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value
        pass

    def cb_quit(self):
        # do something before plugin will close, e.a. close connections ...
        if self.external_state == 'online':
            os.killpg(self.process.pid, SIGTERM)
            print('External script was running while plugin was closed! Script was killed.')


    def cb_get_plugin_configuration(self):
        #
        # Implement a own part of the config
        # config is a hash of hass object
        # config_parameter_name : {}
        # config[config_parameter_name]['value']  NEEDS TO BE IMPLEMENTED
        # configs can be marked as advanced for create dialog
        # http://utilitymill.com/utility/Regex_For_Range
        config = {
            'size': {
                'value': "(300,75)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
            },
            'path': {
                'value': "~/",
                'advanced': '0',
                'type': pc.CFG_TYPE_FILE,
                'tooltip': 'Path to executable'
            },
        }
        return config

    def cb_plugin_meta_updated(self):
        """
        Whenever the meta information is updated this function is called (if implemented).

        :return:
        """

        #dplugin_info = self.dplugin_info
        pass
