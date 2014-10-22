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
from PySide.QtGui import QPushButton
from papi.data.DPlugin import DBlock

class Button(pcp_base):

    def start_init(self, config=None):
        super(Button, self).start_init(config)

        block = DBlock(self.__id__, 1, 1, 'Parameter_1', ['Parameter'])
        self.send_new_block_list([block])

        self.cur_value = 0

    def create_widget(self):
        """

        :return:
        :rtype QWidget:
        """
        button = QPushButton('Click ' + self.name)
        button.clicked.connect(self.clicked)

        return button

    def clicked(self):

        if self.cur_value == float(self.config['up']['value']):
            self.cur_value = float(self.config['low']['value'])
        else:
            self.cur_value = float(self.config['up']['value'])

        self.send_parameter_change(self.cur_value, 'Parameter_1', 'TESTALIAS')


    def get_startup_configuration(self):
        config = {
            "low": {
                'value':0.1,
        }, "up": {
                'value': 1,
        },"name": {
            'value' : "PCP_Plugin"
        }}
        return config