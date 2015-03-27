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
from PySide.QtGui import QSlider, QVBoxLayout, QWidget, QLabel, QRadioButton
from PySide import QtCore

from papi.data.DPlugin import DBlock
import papi.constants as pc

class Radiobutton(pcp_base):
    def initiate_layer_0(self, config):

        self.block = DBlock('Choice')

        self.send_new_block_list([self.block])
        self.set_widget_for_internal_usage(self.create_widget())

        return True

    def create_widget(self):
        self.central_widget = QWidget()

        self.option_texts = []
        self.option_values = []
        self.pre_selected_index = None


        if isinstance(self.config['selected_index']['value'], str):
            if self.config['selected_index']['value'] != '':
                self.pre_selected_index = int(self.config['selected_index']['value'])

        if isinstance(self.config['option_values']['value'], str):
            self.option_values = str.split(self.config['option_values']['value'], ',')

            for i in range(len(self.option_values)):
                self.option_values[i] = self.option_values[i].lstrip().rstrip()


        if isinstance(self.config['option_texts']['value'], str):
            self.option_texts = str.split(self.config['option_texts']['value'], ',')

            for i in range(len(self.option_texts)):
                self.option_texts[i] = self.option_texts[i].lstrip().rstrip()


        self.buttons = []

        self.layout = QVBoxLayout(self.central_widget)

        for i in range(len(self.option_texts)):
            button = QRadioButton(self.option_texts[i])

            button.released.connect(self.button_released)

            if i == self.pre_selected_index:
                button.setChecked(True)

            self.buttons.append(button)
            self.layout.addWidget(button)

        self.central_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.central_widget.customContextMenuRequested.connect(self.show_context_menu)

        return self.central_widget

    def show_context_menu(self, pos):
        gloPos = self.central_widget.mapToGlobal(pos)
        self.cmenu = self.create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def button_released(self):
        for i in range(len(self.buttons)):
            if self.buttons[i].isChecked():
                self.config['selected_index']['value'] = str(i)
                if len(self.option_values) == len(self.option_texts):
                    self.send_parameter_change(self.option_values[i], self.block.name)
                else:
                    self.send_parameter_change(self.option_texts[i], self.block.name)

    def plugin_meta_updated(self):
        pass

    def get_plugin_configuration(self):
        config = {
            'option_texts': {
                'display_text' : 'Displayed Option',
                'value': 'Option Text 1, Option Text 2, Option Text 3',
                'tooltip': 'This text is seen by the user. Must be separated by commas.'
            },
            'option_values': {
                'display_text' : 'Value per Option',
                'value': '',
                'tooltip': 'It is possible to set a value for every option. '
                           'The corresponding value is send instead of the displayed text. '
            },
            'selected_index': {
                'display_text' : 'Preselected Option',
                'value' : '',
                'regex' : pc.REGEX_SINGLE_INT,
                'tooltip': 'Preselect an option by its index.',
                'advanced' : '1'
            },
            'name': {
                'display_text' : 'Plugin Name',
                'value': 'RadioButton Label',
                'tooltip': 'Used for window title'
            }}
        return config

    def quit(self):
        pass