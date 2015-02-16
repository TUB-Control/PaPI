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

Contributors:
Stefan Ruppin
"""

__author__ = 'stefan'

from papi.plugin.base_classes.base_plugin import base_plugin
import re
from PySide.QtGui import QMdiSubWindow


class base_visual(base_plugin):
    def init_plugin(self, CoreQueue, pluginQueue, id, control_api, dpluginInfo = None,TabManger = None):
        super(base_visual, self).papi_init()
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        self.control_api = control_api
        self.dplugin_info = dpluginInfo
        self.TabManager = TabManger

    def start_init(self, config=None):
        self.config = config
        # --------------------------------

        # get needed data from config
        size_re = re.compile(r'([0-9]+)')
        self.window_size = size_re.findall(self.config['size']['value'])
        self.window_pos = size_re.findall(self.config['position']['value'])

        self.window_name = self.config['name']['value']

        self.set_window_for_internal_usage(QMdiSubWindow())
        return self.initiate_layer_1(self.config)

    def get_current_config(self):
        return self.config

    def initiate_layer_1(self, config):
        raise NotImplementedError("Please Implement this method")


    def get_configuration_base(self):
        config = {
            'size': {
                'value': "(300,300)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
            },
            'position': {
                'value': "(0,0)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine position: (x,y)'
            },
            'name': {
                'value': 'VisualPlugin',
                'tooltip': 'Used for window title'
            },
            'tab': {
                'value': 'Tab',
                'tooltip': 'Used for tabs'
            }}
        return config


    def set_window_for_internal_usage(self, subwindow):
        self._subWindow = subwindow
        self.original_resize_function = self._subWindow.resizeEvent
        self._subWindow.resizeEvent = self.window_resize
        self.original_move_function = self._subWindow.moveEvent
        self._subWindow.moveEvent = self.window_move
        self._subWindow.setWindowTitle(self.window_name)
        self._subWindow.resize(int(self.window_size[0]), int(self.window_size[1]))

    def set_widget_for_internal_usage(self, widget):
        self.widget = widget
        self._subWindow.setWidget(self.widget)


    def window_move(self, event):
        pos = self._subWindow.pos()

        x = pos.x()
        y = pos.y()
        self.config['position']['value'] = '(' + str(x) + ',' + str(y) + ')'
        self.original_move_function(event)


    def window_resize(self, event):
        size = event.size()
        w = size.width()
        h = size.height()
        self.config['size']['value'] = '(' + str(w) + ',' + str(h) + ')'
        self.original_resize_function(event)

    def get_sub_window(self):
        return self._subWindow
