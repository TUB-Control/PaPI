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

Contributors
Sven Knuth
"""




from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui    import QIcon
from PyQt5 import QtGui, QtCore

from papi.data.DPlugin import DEvent
from papi.data.DSignal import DSignal
from papi.plugin.base_classes.vip_base import vip_base
from papi.constants import REGEX_SIGNED_FLOAT

class Button(vip_base):

    def __init__(self):
        super(Button, self).__init__()

        self.name = None
        self.cur_value = None

    def initiate_layer_0(self, config):

        #super(Button, self).start_init(config)

        self.event_click = DEvent('Click')

        self.name = config['name']['value']
        self.cur_value = 0

        self.value_up = self.config['state1']['value']
        self.value_down = self.config['state2']['value']
        self.text_up =  (self.config['state1_text']['value'])
        self.text_down = (self.config['state2_text']['value'])
        self.button_state = 'up'

        self.send_new_event_list([self.event_click])

        self.button = self.create_widget()
        self.set_widget_for_internal_usage(self.button)
        self.button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.button.customContextMenuRequested.connect(self.show_context_menu)

        return True


    def show_context_menu(self, pos):
        gloPos = self.button.mapToGlobal(pos)
        self.cmenu = self.create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def create_widget(self):
        """

        :return:
        :rtype QWidget:
        """
        button = QPushButton(self.name)
        button.clicked.connect(self.clicked)

        button.setText(self.text_up)

        return button

    def clicked(self):
        if self.button_state == 'up':
            # Button is up, goes down now
            self.button_state = 'down'
            self.button.setText(self.text_down)
            val = self.value_down
        else:
            # Button is down, goes up now
            self.button_state = 'up'
            self.button.setText(self.text_up)
            val = self.value_up

        self.emit_event(str(val), self.event_click)


    def cb_get_plugin_configuration(self):
        config = {
            "state1": {
                'value': 0,
                'regex': REGEX_SIGNED_FLOAT,
                'advanced' : '0'
            }, "state2": {
                'value': 1,
                'regex': REGEX_SIGNED_FLOAT,
                'advanced' : '0',
            }, "state1_text": {
                'value': 'Go to state 2',
                'advanced' : '0',
                'display_text': 'Text for state 1'
            }, "state2_text": {
                'value': 'Go to state 1',
                'advanced' : '0',
                'display_text': 'Text for state 2'
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

    def cb_plugin_meta_updated(self):
        pass

    def cb_quit(self):
        pass

    def new_parameter_info(self, dparameter_object):
        pass