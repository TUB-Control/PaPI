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
<Stefan Ruppin
"""

__author__ = 'Stefan'

from PySide.QtGui import QMdiSubWindow
import pyqtgraph as pq

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter
import numpy as np

import collections
import re

from pyqtgraph.Qt import QtGui, QtCore

class PlotPerformance(vip_base):

    def __init__(self):
        super(PlotPerformance, self).__init__()

        self.signal_count = 0

    def initiate_layer_0(self, config=None):

        # get needed data from config
        self.show_grid_x = int(self.config['show_grid']['value']) == 1
        self.show_grid_y = int(self.config['show_grid']['value']) == 1
        # --------------------------------

        # set pq graph plot widget options
        self.plotWidget = pq.PlotWidget()
        self.plotWidget.setWindowTitle('PlotPerformanceTitle')
#        self.plot = pq.plot(title='PlotPerformanceTitle')

        self.plotWidget.showGrid(x=self.show_grid_x, y=self.show_grid_y)
        # --------------------------------

        self.curve = self.plotWidget.plot()

        self.data_buffer = np.linspace(1,1000,1000)

        self.set_widget_for_internal_usage( self.plotWidget )

        self.parameters = {}
        self.parameters['x-grid'] = DParameter(None, 'X-Grid', 0, [0,1],1, Regex='^(1|0){1}$')
        self.parameters['y-grid'] = DParameter(None, 'y-Grid', 0, [0,1],1, Regex='^(1|0){1}$')

        self.send_new_parameter_list(list(self.parameters.values()))

        return True

    def pause(self):
        print('PlotPerformance paused')

    def resume(self):
        print('PlotPerformance resumed')

    def execute(self, Data=None, block_name = None):
        self.data_buffer = np.roll(self.data_buffer, 1)

        t = Data['t']

        y = []

        for key in Data:
            if key != 't':
                y = Data[key]

        #self.curve.addData(t, y)
        self.curve.setData(t, y)
        #self.plotWidget.plot(t, y)

#       self.plotWidget.plot(Data[0], Data[0])
        #self.curve.setData(self.data_buffer)
        #self.plot.pl

    def set_parameter(self, name, value):
        print('set_parameter')
        print(name)
        print(value)

    def quit(self):
        print('PlotPerformance: will quit')

    def get_plugin_configuration(self):
        config = {
            'label_y': {
                'value': "amplitude, V",
                'regex': '\w+,\s+\w+'
        }, 'label_x': {
                'value': "time, s",
                'regex': '\w+,\s*\w+'
        }, 'show_grid': {
                'value': "0",
                'regex': '^(1|0)$'
        }}
        # http://www.regexr.com/
        return config

    def plugin_meta_updated(self):

        signal_count = 0;

        subscriptions = self.dplugin_info.get_subscribtions()

        for sub in subscriptions:
            for dblock_name in subscriptions[sub]:
                subscription = subscriptions[sub][dblock_name]

                for signal in subscription.get_signals():
                    signal_count += 1

#        diff_count = len(self.Databuffer) - signal_count

        #print(self.signal_count)

        # #There are too many buffers
        # if diff_count > 0:
        #     for i in range(abs(diff_count)):
        #         # print("Remove")
        #         self.curves.pop()
        #         self.Databuffer.pop()
        #         self.parameters.pop()
        #
        # #Some Buffers are missing
        # if diff_count < 0:
        #     for i in range(self.signal_count, signal_count):
        #         # print("Append ")
        #         new_plot = self._plotWidget.plot(self.x, self.y, pen=(100,0+i*10,0), symbole='o')
        #         new_plot.setDownsampling(method='peak')
        #         self.curves.append(new_plot)
        #         self.Databuffer.append( collections.deque([0.0]*self._bufsize, self._bufsize) )
        #         self.parameters.append( DParameter(None,'Color_' + str(i),0+i*10,[0,255],1) )
        #
        self.signal_count = signal_count



