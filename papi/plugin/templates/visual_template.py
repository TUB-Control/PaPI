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

from papi.pyqtgraph.Qt import QtGui, QtCore

#RENAME TO PLUGIN NAME
class TemplateName(vip_base):


    def initiate_layer_0(self, config=None):

#        self.config = config

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

        #self.plotWidget = pq.PlotWidget()

        # This call is important, because the background structure needs to know the used widget!
        # In the background the qmidiwindow will becreated and the widget will be added
        #self.set_widget_for_internal_usage( self.plotWidget )

        # ---------------------------
        # Create Parameters
        # ---------------------------
        # create a parameter object
        #   self.para1 = DParameter('type','ParameterName',InitWert,RangeArray,1)
        #   self.para2 = DParameter('type','ParameterName',InitWert,RangeArray,1)

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

    def execute(self, Data=None, block_name = None):
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
