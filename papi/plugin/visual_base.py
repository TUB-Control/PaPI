#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universitšt Berlin,
Fakultšt IV - Elektrotechnik und Informatik,
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

import numpy as np
import collections


class visual_base(plugin_base):

    _metaclass__= ABCMeta

    def start_init(self, config=None):

        default_config = self.get_default_config()

        if config is None:

            config = default_config

        if 'sampleintervall' not in config:
            sampleinterval=default_config['sampleinterval']
        else:
            sampleinterval=config['sampleinterval']

        if 'timewindow' not in config:
            timewindow=default_config['timewindow']
        else:
            timewindow=config['timewindow']

        if 'size' not in config:
            size=default_config['size']
        else:
            size=config['size']

        if 'name' not in config:
            name=default_config['name']
        else:
            name=config['name']

        self.name = name
        self._interval = int(sampleinterval*timewindow)
        self._bufsize = int(timewindow/sampleinterval)
        self.tDatabuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        #self.yDatabuffer = collections.deque([0.0]*self._bufsize, self._bufsize)

        self.Databuffer = []

        for i in range(3):
            self.Databuffer.append( collections.deque([0.0]*self._bufsize, self._bufsize) )

        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)

        # create

        self._plotWidget = PlotWidget()

        self._plotWidget.resize(size[0], size[1])
        self._plotWidget.showGrid(x=True, y=True)
        self._plotWidget.setLabel('left', 'amplitude', 'V')
        self._plotWidget.setLabel('bottom', 'time', 's')

        # self.curve = self._plotWidget.plot(self.x, self.y, pen=(255,0,0), symbole='o')
        # self.curve2 = self._plotWidget.plot(self.x, self.y, pen=(128,0,0), symbole='o')

        self._interval = sampleinterval
        self.curves = []
        for i in range(3):
            self.curves.append(self._plotWidget.plot(self.x, self.y, pen=(100,0+i*80,0), symbole='o'))

        #self.curve.setPen((200,200,100))

        self._subWindow = QMdiSubWindow()
        self._subWindow.setWidget(self._plotWidget)
        self._subWindow.setWindowTitle(self.name)

    def get_default_config(self):
        config = {}
        config["sampleinterval"]=1
        config['timewindow']=1000.
        config['size']=(150,150)
        config['name']='ViP_Plugin'
        return config

    def update(self):
        self.x[:] = self.tDatabuffer

        # self.y[:] = self.yDatabuffer
        # self.curve.setData(self.x, self.y)

        for i in range(3):
            curve = self.curves[i]
            y = self.Databuffer[i]

            curve.setData(self.x, y)

        #self._plotWidget.plot(self.x, self.y)

    def add_data(self,t,data:[]):
        for elem in t:
            self.tDatabuffer.append( elem )

        for i in range(len(data)):
            y = data[i]
            for elem in y:
                self.Databuffer[i].append(elem)

    def get_sub_window(self):
        return self._subWindow

    def get_plot_widget(self):
        return self._plotWidget

    def init_plugin(self,CoreQueue,pluginQueue,id):
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        super(visual_base,self).papi_init()
        # TODO mache das mit super init
        #self.__dplugin_ids__ = {}



