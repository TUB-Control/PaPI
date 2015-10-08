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



from papi.plugin.base_classes.vip_base import vip_base
from PyQt5.QtGui        import QRegExpValidator
from PyQt5.QtWidgets import QLineEdit
from PyQt5 import QtCore
from papi.data.DPlugin import DEvent
from papi.data.DParameter import DParameter


class Textfield(vip_base):

    def initiate_layer_0(self, config):

        self.event_change = DEvent('Change')

        self.send_new_event_list([self.event_change])
        self.set_widget_for_internal_usage(self.create_widget())

        return True

    def create_widget(self):

        self.lineedit = QLineEdit()
        self.lineedit.returnPressed.connect(self.value_changed)

        self.init_value = self.config['value_init']['value']

        self.lineedit.setText(self.init_value)

        self.lineedit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lineedit.customContextMenuRequested.connect(self.show_context_menu)

        return self.lineedit

    def show_context_menu(self, pos):
        gloPos = self.lineedit.mapToGlobal(pos)
        self.cmenu = self.create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def value_changed(self, change):
        self.emit_event(str(change), self.event_change)

    def clicked(self):
        pass

    def cb_plugin_meta_updated(self):
        pass

    def cb_get_plugin_configuration(self):
        config = {
            'size': {
                'value': "(150,60)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
                },
            'value_init': {
                    'value': '',
                    'tooltip': 'Used as initial value for the Textfield'
            },
            'name': {
                'value': 'PaPI Textfield',
                'tooltip': 'Used for window title'
            }}
        return config

    def cb_quit(self):
        pass

    def value_changed(self):
        change = self.lineedit.text()
        self.emit_event(str(change), self.event_change)

    def new_parameter_info(self, dparameter_object):
        if isinstance(dparameter_object, DParameter):
            value = dparameter_object.default

            regex = dparameter_object.regex
            if regex is not None:
                rx = QtCore.QRegExp(regex)
                validator = QRegExpValidator(rx, self.lineedit)
                self.lineedit.setValidator(validator)

            self.lineedit.returnPressed.disconnect()
            self.lineedit.setText(str(value))
            self.lineedit.returnPressed.connect(self.value_changed)
