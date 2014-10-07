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

from papi.plugin.pcp_base import pcp_base
from PySide.QtGui import QSlider, QHBoxLayout, QWidget, QLineEdit
from PySide import QtCore
from papi.data.DPlugin import DBlock

class Slider(pcp_base):

    def start_init(self, config=None):
        super(Slider, self).start_init(config)

    def create_widget(self):
        self.central_widget = QWidget()

        self.slider = QSlider()
        self.slider.sliderPressed.connect(self.clicked)
        self.slider.valueChanged.connect(self.value_changed)

        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)

        self.slider.setOrientation(QtCore.Qt.Horizontal)

        self.text_field = QLineEdit()
        self.text_field.setReadOnly(True)
        self.layout = QHBoxLayout(self.central_widget)

        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.text_field)

        block = DBlock(self.__id__, 1, 1, 'Parameter_1', ['Parameter'])
        self.send_new_block_list([block])



        return self.central_widget

    def value_changed(self, change):
        cur_value = change/100
        #self.set_value(cur_value)
        self.text_field.setText(str(cur_value))
        self.send_parameter_change(cur_value, 'Parameter_1', 'TESTALIAS')

    def clicked(self):
        pass
