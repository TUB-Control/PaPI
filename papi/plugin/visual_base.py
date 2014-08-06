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

from abc import ABCMeta, abstractmethod

import numpy as np
import collections

class visual_base(plugin_base):

    _metaclass__= ABCMeta

    def setConfig(self, name='Plot', sampleinterval=1, timewindow=1000., size=(300,300)):

        self.name = name
        #PlotWidget.__init__(self)

        # Set internal variables

        self._interval = int(sampleinterval*timewindow)
        self._bufsize = int(timewindow/sampleinterval)
        self.tDatabuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.yDatabuffer = collections.deque([0.0]*self._bufsize, self._bufsize)

        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)

        # create

        self._plotWidget = PlotWidget()
        self._plotWidget.resize(*size)
        self._plotWidget.showGrid(x=True, y=True)
        self._plotWidget.setLabel('left', 'amplitude', 'V')
        self._plotWidget.setLabel('bottom', 'time', 's')
        self.curve = self._plotWidget.plot(self.x, self.y, pen=(255,0,0))
        self._interval = sampleinterval
        self.curve.setPen((200,200,100))

        self._subWindow = QMdiSubWindow()
        self._subWindow.setWidget(self._plotWidget)

    def update(self):
        self.x[:] = self.tDatabuffer
        self.y[:] = self.yDatabuffer
        self.curve.setData(self.x, self.y)

    def add_data(self,t,y):
        for elem in t:
            self.tDatabuffer.append( elem )

        for elem in y:
            self.yDatabuffer.append( elem )

    def get_sub_window(self):
        return self._subWindow

    def get_plot_widget(self):
        return self._plotWidget

    def init_plugin(self,CoreQueue,pluginQueue,sharedMemory,buffer,id):
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__shared_memory__ = sharedMemory
        self.__buffer__ = buffer
        self.__id__ = id
        print('Plot init')