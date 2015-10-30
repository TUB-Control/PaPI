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

Contributors
Sven Knuth, Stefan Ruppin
"""

from PyQt5.QtWidgets import QSlider, QHBoxLayout, QWidget, QLabel
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DPlugin import DEvent
from papi.data.DParameter import DParameter
import papi.constants as pc

class Slider(vip_base):
    def cb_initialize_plugin(self):
        # Creates Slider Change Event to connect to Parameters and send it
        self.event_change = DEvent('Change')
        self.pl_send_new_event_list([self.event_change])

        # get items of cfg for fist start of the Slider and cast to float
        self.value_max  = self.pl_get_config_element('upper_bound',castHandler=float)
        self.value_min  = self.pl_get_config_element('lower_bound',castHandler=float)
        self.tick_count = self.pl_get_config_element('step_count',castHandler=float)
        self.init_value = self.pl_get_config_element('value_init',castHandler=float)

        # Create Parameter list for change slider parameter live and send it
        self.para_value_max     = DParameter('MaxValue', default= self.value_max, Regex=pc.REGEX_SIGNED_FLOAT_OR_INT)
        self.para_value_min     = DParameter('MinValue', default=self.value_min, Regex=pc.REGEX_SIGNED_FLOAT_OR_INT)
        self.para_tick_count    = DParameter('StepCount',default=self.tick_count,  Regex=pc.REGEX_SINGLE_INT)
        self.pl_send_new_parameter_list([self.para_tick_count, self.para_value_max, self.para_value_min])
        # Set Slider widget for use in PaPI
        self.pl_set_widget_for_internal_usage(self.create_widget())
        # return successful initialization
        return True

    def create_widget(self):
        self.central_widget = QWidget()

        self.slider = QSlider()
        self.slider.sliderPressed.connect(self.clicked)
        self.slider.valueChanged.connect(self.value_changed)

        self.tick_width = self.get_tick_width(self.value_max, self.value_min,self.tick_count)

        self.slider.setMinimum(self.value_min)
        self.slider.setMaximum(self.tick_count-1)

        self.slider.setOrientation(QtCore.Qt.Horizontal)

        self.text_field = QLabel()
        self.text_field.setMinimumWidth(25)
        self.text_field.setText(str(self.init_value))

        init_value = (self.init_value - self.value_min)/self.tick_width
        init_value = round(init_value,0)
        self.slider.setValue(init_value)
        self.layout = QHBoxLayout(self.central_widget)

        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.text_field)

        self.slider.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.slider.customContextMenuRequested.connect(self.show_context_menu)

        self.central_widget.keyPressEvent = self.key_event

        return self.central_widget

    def show_context_menu(self, pos):
        gloPos = self.slider.mapToGlobal(pos)
        self.cmenu = self.pl_create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def value_changed(self, change):
        val = change * self.tick_width + self.value_min
        val = round(val, 8)
        self.text_field.setText(str(val))
        self.pl_emit_event(str(val), self.event_change)

    def clicked(self):
        pass

    def get_tick_width(self, max, min, count):
        return (max-min)/(count-1)


    def cb_set_parameter(self, parameter_name, parameter_value):
        if parameter_name == self.para_value_max.name:
            self.value_max = float(parameter_value)
            self.tick_width = self.get_tick_width(self.value_max, self.value_min,self.tick_count)
            self.pl_set_config_element('upper_bound', parameter_value)

        if parameter_name == self.para_value_min.name:
            self.value_min = float(parameter_value)
            self.tick_width = self.get_tick_width(self.value_max, self.value_min,self.tick_count)
            self.pl_set_config_element('lower_bound', parameter_value)
            if float(self.pl_get_config_element('value_init')) < self.value_min:
                self.pl_set_config_element('value_init', self.value_min)

        if parameter_name == self.para_tick_count.name:
            self.tick_count = float(parameter_value)
            self.tick_width = self.get_tick_width(self.value_max, self.value_min,self.tick_count)
            self.slider.setMinimum(self.value_min)
            self.slider.setMaximum(self.tick_count-1)
            self.pl_set_config_element('step_count', parameter_value)


    def cb_get_plugin_configuration(self):
        config = {
            'lower_bound': {
                'value': '0.0'
                },
            'upper_bound': {
                'value': '1.0'
                },
            'step_count': {
                'value': '11',
                'regex': pc.REGEX_SINGLE_INT,
                },
            'size': {
                'value': "(150,75)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
                },
            'value_init': {
                    'value': '0',
                    'regex' : pc.REGEX_SIGNED_FLOAT_OR_INT,
                    'tooltip': 'Used as initial value for the Slider'
            },
            'name': {
                'value': 'PaPI Slider',
                'tooltip': 'Used for window title'
            }}
        return config

    def key_event(self, event):
        if event.key() == Qt.Key_Plus:
            self.slider.setValue(self.slider.value() + 1)

        if event.key() == Qt.Key_Minus:
            self.slider.setValue(self.slider.value() - 1)

    def cb_quit(self):
        pass

    def cb_new_parameter_info(self, dparameter_object):
        if isinstance(dparameter_object, DParameter):
            value = float(dparameter_object.default)
            self.text_field.setText(str(value))
            init_value = (value - self.value_min)/self.tick_width
            init_value = round(init_value,0)

            self.slider.valueChanged.disconnect()
            self.slider.sliderPressed.disconnect()
            self.slider.setValue(init_value)
            self.slider.valueChanged.connect(self.value_changed)
            self.slider.sliderPressed.connect(self.clicked)