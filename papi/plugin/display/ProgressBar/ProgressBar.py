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



from PyQt5.QtWidgets import QMdiSubWindow, QProgressBar
from PyQt5 import  QtCore

import papi.constants as pc
from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter
import papi.helper as ph
import time


#RENAME TO PLUGIN NAME
class ProgressBar(vip_base):

    def initiate_layer_0(self, config=None):
        # ---------------------------
        # Read configuration
        # ---------------------------
        # Note: this cfg items have to exist!

        self.progress_value = self.config['progress_value']['value']
        self.trigger_value = self.config['trigger_value']['value']
        self.reset_trigger_value = self.config['reset_trigger_value']['value']
        self.show_percent = self.config['show_percent']['value'] == '1'
        self.show_current_max = self.config['show_current_max']['value'] == '1'
        self.round_digit = int(self.config['round_digit']['value'])

        self.min_range = float(self.config['min_rage']['value'])
        self.max_range = float(self.config['max_range']['value'])
        # --------------------------------
        # Create Widget
        # --------------------------------
        # Create Widget needed for this plugin

        self.progressbar = QProgressBar()
        self.progressbar.setRange(0, 100)
        self.progressbar.setTextVisible(True)
        self.progressbar.setValue(0)

        self.progressbar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.progressbar.customContextMenuRequested.connect(self.show_context_menu)
        # This call is important, because the background structure needs to know the used widget!
        # In the background the qmidiwindow will becreated and the widget will be added


        self.set_value(self.min_range)

        self.set_widget_for_internal_usage(self.progressbar)


        # ---------------------------
        # Create Parameters
        # ---------------------------
        para_list = []
        # create a parameter object

        self.para_trigger = DParameter('trigger', default=0)

        self.para_change_progress_value = DParameter('ProgressValue', default=self.progress_value)
        self.para_change_reset_value = DParameter('ResetValue', default=self.reset_trigger_value)
        self.para_change_trigger_value = DParameter('TriggerValue', default=self.trigger_value)

        self.para_change_min_range = DParameter('MinRange', default=self.min_range, Regex=pc.REGEX_SIGNED_FLOAT_OR_INT)
        self.para_change_max_range = DParameter('MaxRange', default=self.max_range, Regex=pc.REGEX_SIGNED_FLOAT_OR_INT)

        self.para_show_percent = DParameter('ShowPercent', default=self.config['show_percent']['value'], Regex=pc.REGEX_BOOL_BIN)
        self.para_show_current_max = DParameter('ShowCurrentMax', default=self.config['show_current_max']['value'], Regex=pc.REGEX_BOOL_BIN)

        para_list.append(self.para_trigger)
        para_list.append(self.para_change_progress_value)
        para_list.append(self.para_change_reset_value)
        para_list.append(self.para_change_trigger_value)
        para_list.append(self.para_change_min_range)
        para_list.append(self.para_change_max_range)
        para_list.append(self.para_show_percent)
        para_list.append(self.para_show_current_max)

        # build parameter list to send to Core
        self.send_new_parameter_list(para_list)

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

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data[CORE_TIME_SIGNAL] = [t1, t2, ...] where CORE_TIME_SIGNAL is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []

        if self.reset_trigger_value in Data:
            self.reset()

        if self.trigger_value in Data:
            self.trigger()

        if self.progress_value in Data:
            new_value = Data[self.progress_value][0]
            self.set_value(new_value)

    def set_parameter(self, name, value):
        # attention: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value

        if name == self.para_trigger.name:
            self.trigger()

        if name == self.para_change_progress_value.name:
            self.progress_value = value

        if name == self.para_change_reset_value.name:
            self.reset_trigger_value = value

        if name == self.para_change_trigger_value.name:
            self.trigger_value = value

        if name == self.para_change_min_range.name:
            self.min_range = float(value)

        if name == self.para_change_max_range.name:
            self.max_range = float(value)

        if name == self.para_show_current_max.name:
            self.show_current_max = value == '1'

        if name == self.para_show_percent.name:
            self.show_percent = value == '1'

    def set_value(self, value, setvalue = True):

        bar_format = ""

        if self.min_range <= value and value <= self.max_range:

            percent = 100 / (abs(self.min_range) + abs(self.max_range)) * ( float(value) + abs(self.min_range))

            if setvalue:
                self.progressbar.setValue(percent)

            if self.show_percent and self.show_current_max:
                bar_format = "%p% [ {0}/{1}]".format(str(round(value, self.round_digit)), str(self.max_range))
            elif self.show_percent:
                bar_format = "%p%"

            elif self.show_current_max:
                bar_format = "%v/%m"

            self.progressbar.setFormat(bar_format)

    def trigger(self):
        percent = self.progressbar.value() + 1
        new_value = (abs(self.min_range) + abs(self.max_range)) / 100 * percent
        self.set_value(new_value, setvalue=False)
        self.progressbar.setValue(percent)

    def reset(self):
        self.set_value(self.min_range, setvalue=False)
        self.progressbar.setValue(0)

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
             "progress_value": {
                 'value': 'percent',
                 'display_text' : 'Progress Value',
                 'tooltip' : 'Name of the signal whose first value is used to set the current value for the progress bar.',
                 'advanced' : '0'
            },
            "show_percent": {
                 'value': '1',
                 'display_text' : 'Show percent',
                 'tooltip' : 'Show progress in percent over the progress bar',
                 'type' : 'bool',
                 'advanced' : '0'
            },
            "show_current_max": {
                 'value': '0',
                 'display_text' : 'Show current/max',
                 'tooltip' : 'A label over the bar shows the current and max value',
                 'type' : 'bool',
                 'advanced' : '0'
            },
            "min_rage": {
                 'value': '0',
                 'display_text' : 'Min Range',
                 'regex': pc.REGEX_SIGNED_FLOAT_OR_INT,
                 'tooltip' : 'Set minimum range for the progress bar.',
                 'advanced' : '1'
            },
            "max_range": {
                 'value': '100',
                 'display_text' : 'Max Range',
                 'regex': pc.REGEX_SIGNED_FLOAT_OR_INT,
                 'tooltip' : 'Set maximum range for the progress bar.',
                 'advanced' : '1'
            },
             "trigger_value": {
                 'value': 'trigger',
                 'display_text' : 'Trigger Value',
                 'tooltip' : 'Name of the signal which triggers the progress bar to increment by one.',
                 'advanced' : '0'
            },
             "reset_trigger_value": {
                 'value': 'reset',
                 'display_text' : 'Reset Value',
                 'tooltip' : 'Name of the signal which triggers the progress bar to reset.',
                 'advanced' : '0'
            },
            'round_digit': {
                'value': '2',
                'regex' : pc.REGEX_SINGLE_INT,
                'display_text' : 'Round to ndigits',
                'tooltip': 'Current value is rounded to ndigits after the decimal point. ',
                'advanced' : '1'
            },
             'name': {
                'value': 'ProgressBar',
                'tooltip': 'Used for window title'
            },
             'size': {
                'value': "(150,50)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
            }
          }
        return config

    def plugin_meta_updated(self):
        """
        Whenever the meta information is updated this function is called (if implemented).

        :return:
        """

        pass
