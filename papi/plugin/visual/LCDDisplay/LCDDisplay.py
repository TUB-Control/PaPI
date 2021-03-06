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
from papi.data.DParameter import DParameter
import papi.constants as pc
from papi.constants import CORE_TIME_SIGNAL

import time
import collections

from PyQt5 import QtGui, QtWidgets, QtCore

from papi.data import DConfiguration

class LCDDisplay(vip_base):

    def cb_initialize_plugin(self):
        # ---------------------------
        # Read configuration
        # ---------------------------
        # Note: this cfg items have to exist!
        self.time_treshold  = int  (self.pl_get_config_element('update_interval'))
        self.value_scale    = float(self.pl_get_config_element('value_scale')    )
        self.value_offset   = float(self.pl_get_config_element('value_offset')   )
        self.digit_count    = int  (self.pl_get_config_element('digit_count')    )

        # if self.config['value_init']['value'] is not None:
        self.init_value     = self.pl_get_config_element('value_init', castHandler=float)

        if self.init_value is None:
            self.init_value = 0

        # --------------------------------
        # Create Widget
        # --------------------------------
        # Create Widget needed for this plugin
        self.LcdWidget = QtWidgets.QLCDNumber()
        self.LcdWidget.setSmallDecimalPoint(True)
        self.LcdWidget.display(self.init_value)

        self.LcdWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.LcdWidget.customContextMenuRequested.connect(self.show_context_menu)
        # This call is important, because the background structure needs to know the used widget!
        # In the background the qmidiwindow will becreated and the widget will be added
        self.pl_set_widget_for_internal_usage( self.LcdWidget )


        # ---------------------------
        # Create Parameters
        # ---------------------------
        para_list = []
        # create a parameter object
        self.para_treshold      = DParameter('update_interval',default=self.time_treshold, Regex='[0-9]+')
        self.para_value_scale   = DParameter('value_scale',default= self.value_scale, Regex='-?[1-9]+[0-9]*(\.?[0-9]+)?')
        self.para_value_offset  = DParameter('value_offset',default= self.value_offset, Regex='-?\d+(\.?\d+)?')
        self.para_digit_count   = DParameter('digit_count',default= self.digit_count, Regex=pc.REGEX_SINGLE_INT)

        para_list.append(self.para_treshold)
        para_list.append(self.para_value_scale)
        para_list.append(self.para_value_offset)
        para_list.append(self.para_digit_count)


        # build parameter list to send to Core
        self.pl_send_new_parameter_list(para_list)

        # ---------------------------
        # Create Legend
        # ---------------------------

        self.last_time = int(round(time.time() * 1000))
        return True

    def show_context_menu(self, pos):
        gloPos = self.LcdWidget.mapToGlobal(pos)
        self.cmenu = self.pl_create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def cb_pause(self):
        # will be called, when plugin gets paused
        # can be used to get plugin in a defined state before pause
        # e.a. close communication ports, files etc.
        self.LcdWidget.display('PAUSE')

    def cb_resume(self):
        # will be called when plugin gets resumed
        # can be used to wake up the plugin from defined pause state
        # e.a. reopen communication ports, files etc.
        self.LcdWidget.display('...')

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data[CORE_TIME_SIGNAL] = [t1, t2, ...] where CORE_TIME_SIGNAL is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []

        cur_time = int(round(time.time() * 1000))
        if cur_time - self.last_time > self.time_treshold:
            self.last_time = cur_time
            t = Data[CORE_TIME_SIGNAL]
            keys = list(Data.keys())
            keys.sort()
            y = 0
            if keys[0] != CORE_TIME_SIGNAL:
                y = Data[keys[0]][-1]
            else:
                if len(keys) > 1:
                    y = Data[keys[1]][-1]

            y = y*self.value_scale + self.value_offset
            self.LcdWidget.display(round(y,self.digit_count))



    def cb_set_parameter(self, name, value):
        # attetion: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value
        if name == self.para_treshold.name:
            self.time_treshold = int(value)
            #self.config['updateFrequency']['value'] = value
            self.pl_set_config_element(self.para_treshold.name,value)

        if name == self.para_value_scale.name:
            self.pl_set_config_element(self.para_value_scale.name, value)
            self.value_scale = float(value)

        if name == self.para_value_offset.name:
            self.pl_set_config_element(self.para_value_offset.name, value)
            self.value_offset = float(value)

        if name == self.para_digit_count.name:
                self.pl_set_config_element(self.para_digit_count.name, value)
                self.digit_count = int(value)
                #self.LcdWidget.setDigitCount(self.digit_count)




    def cb_quit(self):
        # do something before plugin will close, e.a. close connections ...
        pass


    def cb_get_plugin_configuration(self):
        #
        # Implement a own part of the config
        # config is a hash of hass object
        # config_parameter_name : {}
        # config[config_parameter_name]['value']  NEEDS TO BE IMPLEMENTED
        # configs can be marked as advanced for create dialog
        # http://utilitymill.com/utility/Regex_For_Range

        config = collections.OrderedDict()
        config['update_interval'] = {
                     'value': '1000',
                     'regex': '[0-9]+',
                     'display_text' : 'Minimal time between updates (in ms)',
                     'advanced' : 'LCD Display'
        }

        config['size'] = {
                    'value': "(150,75)",
                    'regex': '\(([0-9]+),([0-9]+)\)',
                    'advanced': 'Appearance',
                    'tooltip': 'Determine size: (height,width)'
        }

        config['name'] = {
                    'value': 'LCD',
                    'tooltip': 'Used for window title',
                    'advanced': 'Appearance'
        }

        config['value_init'] = {
                    'value': '0',
                    'regex' : pc.REGEX_SIGNED_FLOAT_OR_INT,
                    'tooltip': 'Used as initial value for the LCD-Display',
                    'advanced': 'LCD Display'
        }

        config['value_scale'] = {
                    'value': '1',
                    'tooltip': 'Used to scale displayed value',
                    'regex': '-?[1-9]+[0-9]*(\.?[0-9]+)?',
                    'advanced': 'LCD Display'
        }

        config['value_offset'] = {
                    'value': '0',
                    'tooltip': 'Used to offset displayed value',
                    'regex': pc.REGEX_SIGNED_FLOAT_OR_INT,
                    'advanced': 'LCD Display'
        }

        config['digit_count'] = {
                    'value': '3',
                    'tooltip': 'Number of digits',
                    'regex': pc.REGEX_SINGLE_INT,
                    'advanced': 'LCD Display'
        }
        return config

    def cb_plugin_meta_updated(self):
        pass
