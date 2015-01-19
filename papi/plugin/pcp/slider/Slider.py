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

Contributors
Sven Knuth
"""

__author__ = 'knuths'

from papi.plugin.base_classes.pcp_base import pcp_base
from PySide.QtGui import QSlider, QHBoxLayout, QWidget, QLineEdit
from PySide import QtCore
from papi.data.DPlugin import DBlock
from papi.data.DSignal import DSignal

class Slider(pcp_base):

    def initiate_layer_0(self, config):

        block = DBlock('SliderBlock')
        signal = DSignal('SliderParameter1')
        block.add_signal(signal)

        self.send_new_block_list([block])
        self.set_widget_for_internal_usage(self.create_widget())

    def create_widget(self):
        self.central_widget = QWidget()

        self.slider = QSlider()
        self.slider.sliderPressed.connect(self.clicked)
        self.slider.valueChanged.connect(self.value_changed)

        self.slider.setMinimum(float(self.config['lower_bound']['value']))
        self.slider.setMaximum(float(self.config['upper_bound']['value']))
        self.slider.setSingleStep(float(self.config['step_size']['value']))

        self.slider.setOrientation(QtCore.Qt.Horizontal)

        self.text_field = QLineEdit()
        self.text_field.setReadOnly(True)
        self.text_field.setFixedWidth(50)

        self.layout = QHBoxLayout(self.central_widget)

        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.text_field)

        return self.central_widget

    def value_changed(self, change):
        self.text_field.setText(str(change))
        self.send_parameter_change(change, 'SliderBlock', 'TESTALIAS')

    def clicked(self):
        pass

    def plugin_meta_updated(self):
        pass

    def get_plugin_configuration(self):
        config = {
            'lower_bound': {
                'value': '0.0'
                },
            'upper_bound': {
                'value': '1.0'
                },
            'step_size': {
                'value': '0.1'
                },
            'size': {
                'value': "(150,75)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
                },
            'name': {
                'value': 'PaPI Slider',
                'tooltip': 'Used for window title'
            } }
        return config

    def quit(self):
        pass