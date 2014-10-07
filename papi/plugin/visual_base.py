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

import numpy as np
import collections


class visual_base(plugin_base):

    _metaclass__= ABCMeta

    @abstractmethod
    def start_init(self, config=None):
        pass

    def get_startup_configuration(self):
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

    def set_parameter_internal(self, para_list):

        for parameter in para_list:
            self.set_parameter(parameter)

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





