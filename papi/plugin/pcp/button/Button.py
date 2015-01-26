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
from PySide.QtGui import QPushButton, QIcon
from papi.data.DPlugin import DBlock
from papi.data.DSignal import DSignal

class Button(pcp_base):

    def __init__(self):
        super(Button, self).__init__()

        self.name = None
        self.cur_value = None

    def initiate_layer_0(self, config):

        #super(Button, self).start_init(config)

        block = DBlock('Click_Event')
        signal = DSignal('Parameter')
        block.add_signal(signal)

        self.name = config['name']['value']
        self.cur_value = 0

        self.send_new_block_list([block])

        self.button = self.create_widget()
        self.set_widget_for_internal_usage(self.button)


    def create_widget(self):
        """

        :return:
        :rtype QWidget:
        """
        button = QPushButton(self.name)
        button.clicked.connect(self.clicked)

        return button

    def clicked(self):


        if self.cur_value == float(self.config['up']['value']):
            self.cur_value = float(self.config['low']['value'])
        else:
            self.cur_value = float(self.config['up']['value'])

        self.send_parameter_change(str(self.cur_value), 'Click_Event')


    def get_plugin_configuration(self):
        config = {
            "low": {
                'value': 0,
                'advanced' : '0'
            }, "up": {
                'value': 1,
                'advanced' : '0'
            },"name": {
                'value': "PaPI Button",
                'advanced': '0'
            },'size': {
                'value': "(150,50)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
            } }
        return config

    def plugin_meta_updated(self):
        pass

    def quit(self):
        pass