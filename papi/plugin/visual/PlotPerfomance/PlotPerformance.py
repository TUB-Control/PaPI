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
        self.signals = {}
        self._bufsize = 1000
        self.timewindow = 1000

        self._tbuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-self.timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)

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

        # ---------------------------
        # Create Legend
        # ---------------------------

        self.legend = pq.LegendItem((100, 40), offset=(40, 1))  # args are (size, offset)
        self.legend.setParentItem(self.plotWidget.graphicsItem())

#        legend = pq.LegendItem((100,100), 0)


        #self.plotWidget.addLegend()

        return True

    def pause(self):
        print('PlotPerformance paused')

    def resume(self):
        print('PlotPerformance resumed')

    def execute(self, Data=None, block_name = None):
        self.data_buffer = np.roll(self.data_buffer, 10)

        t = Data['t']
        for elem in t:
            self._tbuffer.append( elem )

        self.x[:] = self._tbuffer

        for key in Data:
            if key != 't':
                y = Data[key]
                if key in self.signals:
                    for elem in y:
                        self.signals[key]['buffer'].append(elem)

        # --------------------------
        # iterate over all buffers
        # --------------------------
        #print(self._tbuffer)
        for signal_name in self.signals:
           # print(self.buffers[signal_name])

            #self.curve.setData(self.x, self.buffers[signal_name]['buffer'])

            self.signals[signal_name]['curve'].setData(self.x, self.signals[signal_name]['buffer'])

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
        """
        By this function the plot is able to handle more than one input for plotting.
        :return:
        """
        subscriptions = self.dplugin_info.get_subscribtions()

        current_signals = []

        for dpluginsub_id in subscriptions:
            for dblock_name in subscriptions[dpluginsub_id]:
                dblocksub = subscriptions[dpluginsub_id][dblock_name]

                for signal in dblocksub.get_signals():
                    signal_name = dblocksub.dblock.get_signal_name(signal)
                    current_signals.append(signal_name)

        for signal_name in current_signals:
            if signal_name not in self.signals:
                self.add_databuffer(signal_name)

        # Delete old buffers
        for signal_name in self.signals.copy():
            if signal_name not in current_signals:
                self.remove_databuffer(signal_name)

    def add_databuffer(self, signal_name):
        """
        Create new buffer for signal_name.
        :param signal_name:
        :return:
        """
        print('Add buffer for ' + signal_name)
        if signal_name not in self.signals:
            self.signals[signal_name] = {}
            buffer = collections.deque([0.0]*self._bufsize, self._bufsize)
            curve = self.plotWidget.plot(self.x, self.y, pen=(255,255,255), symbole='o', name=signal_name, clear=False)

            self.signals[signal_name]['buffer'] = buffer
            self.signals[signal_name]['curve'] = curve
            self.legend.addItem(curve, signal_name)


    def remove_databuffer(self, signal_name):
        """
        Remove the databuffer for signal_name.
        :param signal_name:
        :return:
        """
        print('Delete buffer for ' + signal_name)
        if signal_name in self.signals:
            curve = self.signals[signal_name]['curve']
            curve.clear()
            self.legend.removeItem(signal_name)
            del self.signals[signal_name]
