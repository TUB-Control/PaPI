#!/usr/bin/python3
# -*- coding: latin-1 -*-

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

from papi.plugin.plugin_base import plugin_base
from PySide.QtGui import QMdiSubWindow
from pyqtgraph import PlotWidget
from pyqtgraph import QtCore
from abc import ABCMeta, abstractmethod
from papi.data.DParameter import DParameter

import re

import numpy as np
import collections


class visual_base(plugin_base):

    _metaclass__= ABCMeta

    def start_init(self, config=None):
        print('visual base init')
        self.config = config
        # --------------------------------

        # get needed data from config
        size_re = re.compile(r'([0-9]+)')
        self.window_size = size_re.findall(self.config['size']['value'])
        self.window_pos = size_re.findall(self.config['position']['value'])


        self.window_name = self.config['name']['value']


    def get_startup_configuration(self): # TODO SVEN
        config = {}
        config["sampleinterval"]=1
        config['timewindow']=1000.
        config['size']=(150,150)
        config['name']='ViP_Plugin'
        return config

    @abstractmethod
    def get_sub_window(self):
        return self._subWindow

    @abstractmethod
    def get_widget(self):
        pass

    @abstractmethod
    def set_parameter(self, parameter):
        pass

    @abstractmethod
    def update(self):
        pass

    def init_plugin(self,CoreQueue,pluginQueue,id):
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        super(visual_base,self).papi_init()
        # TODO mache das mit super init
        #self.__dplugin_ids__ = {}


    def get_current_config(self):
        return self.config


    def get_configuration_base(self):
        config = {
        'size': {
                'value': "(300,300)",
                'regex': '\(([0-9]+),([0-9]+)\)'
        }, 'position': {
                'value': "(0,0)",
                'regex': '\(([0-9]+),([0-9]+)\)'
        },'name': {
                'value' : 'Plot_Plugin',
        }}
        return config

    def merge_configs(self, cfg1, cfg2):
        return dict(list(cfg1.items()) + list(cfg2.items()) )


    def window_move(self, event):
        pos = self._subWindow.pos()

        x = pos.x()
        y = pos.y()
        self.config['position']['value'] = '('+str(x)+','+str(y)+')'
        self.original_move_function(event)


    def window_resize(self, event):
        size = event.size()
        w = size.width()
        h = size.height()
        self.config['size']['value'] = '('+str(w)+','+str(h)+')'
        self.original_resize_function(event)


    def get_sub_window(self):
        return self._subWindow

    def set_window_for_internal_usage(self, subwindow):
        self._subWindow = subwindow
        self.original_resize_function = self._subWindow.resizeEvent
        self._subWindow.resizeEvent = self.window_resize
        self.original_move_function = self._subWindow.moveEvent
        self._subWindow.moveEvent = self.window_move