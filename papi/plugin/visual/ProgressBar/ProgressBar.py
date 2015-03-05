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

from PySide.QtGui import QMdiSubWindow
import papi.pyqtgraph as pq

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter

import collections
import re
import time

from papi.pyqtgraph.Qt import QtGui, QtCore

#RENAME TO PLUGIN NAME
class ProgressBar(vip_base):


    def initiate_layer_0(self, config=None):

        # ---------------------------
        # Read configuration
        # ---------------------------
        # Note: this cfg items have to exist!
        self.color  = self.config['color']['value']
        self.progress_value = self.config['progress_value']['value']
        self.trigger_value = self.config['trigger_value']['value']
        self.reset_trigger_value = self.config['reset_trigger_value']['value']
        # --------------------------------
        # Create Widget
        # --------------------------------
        # Create Widget needed for this plugin

        self.central_widget = QtGui.QWidget()

        self.horizontal_layoyt = QtGui.QHBoxLayout()

        self.central_widget.setLayout(self.horizontal_layoyt)

        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setRange(0, 100)
        self.progressbar.setTextVisible(True)
        self.progressbar.setValue(0)

        self.progressbar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.progressbar.customContextMenuRequested.connect(self.show_context_menu)
        # This call is important, because the background structure needs to know the used widget!
        # In the background the qmidiwindow will becreated and the widget will be added
        self.set_widget_for_internal_usage( self.progressbar)


        # ---------------------------
        # Create Parameters
        # ---------------------------
        para_list = []
        # create a parameter object
        self.para_color   = DParameter('color',   default=self.color)
        self.para_trigger = DParameter('trigger', default=0)

        para_list.append(self.para_color)
        para_list.append(self.para_trigger)
        # build parameter list to send to Core
        self.send_new_parameter_list(para_list)

        # ---------------------------
        # Create Legend
        # ---------------------------

        self.last_time = int(round(time.time() * 1000))
        return True

    def show_context_menu(self, pos):
        gloPos = self.progressbar.mapToGlobal(pos)
        self.cmenu = self.create_control_context_menu()
        self.cmenu.exec_(gloPos)

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

        if self.reset_trigger_value in Data:
            self.progressbar.reset()

        if self.trigger_value in Data:
            old_value = self.progressbar.value() + 1
            self.progressbar.setValue(old_value)

        if self.progress_value in Data:
            new_value = Data[self.progress_value][0]

            self.progressbar.setValue(new_value)

    def set_parameter(self, name, value):
        # attetion: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value
        if name == self.para_color.name:
            self.color = value
            self.config['color']['value'] = value

        if name == self.para_trigger.name:
            self.para_trigger.value += 1
            self.progressbar.setValue(self.para_trigger.value)

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
             "color": {
                 'value': '(100, 50, 50)',
                 'display_text' : 'Used color for the progress bar',
                 'advanced' : '1'
            },
             "progress_value": {
                 'value': 'percent',
                 'display_text' : 'Progress Value',
                 'tooltip' : 'Name of the scalar which is used for the progress bar.',
                 'advanced' : '0'
            },
             "trigger_value": {
                 'value': 'trigger',
                 'display_text' : 'Trigger Value',
                 'tooltip' : 'Name of the scalar which is used to increment progress bar by one.',
                 'advanced' : '0'
            },
             "reset_trigger_value": {
                 'value': 'reset',
                 'display_text' : 'Reset Value',
                 'tooltip' : 'Name of the scalar which is used to reset the progress bar.',
                 'advanced' : '0'
            },
             'name': {
                'value': 'ProgressBar',
                'tooltip': 'Used for window title'
            },
             'display_text': {
                'value': '1',
                'tooltip': 'Show',
                'advanced' : '1'
            }
          }
        return config

    def plugin_meta_updated(self):
        """
        Whenever the meta information is updated this function is called (if implemented).

        :return:
        """

        pass
