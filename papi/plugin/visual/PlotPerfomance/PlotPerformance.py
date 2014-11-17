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

        self._tbuffer = collections.deque([0.0]*0, self._bufsize)
        self.x = np.linspace(-self.timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)

        self.styles = {
            0 : QtCore.Qt.SolidLine,
            1 : QtCore.Qt.DashDotDotLine,
            2 : QtCore.Qt.DashDotLine,
            3 : QtCore.Qt.DashLine,
            4 : QtCore.Qt.DotLine
        }

        self.colors = {
            0 : (255, 255, 255),
            1 : (255, 0  , 0  ),
            2 : (0  , 255, 0  ),
            3 : (0  , 0  , 255),
            4 : (100, 100, 100)

        }

    def initiate_layer_0(self, config=None):

#        self.config = config

        # ---------------------------
        # Read configuration
        # ---------------------------

        self.show_grid_x = int(self.config['x-grid']['value']) == '1'
        self.show_grid_y = int(self.config['y-grid']['value']) == '1'

        int_re = re.compile(r'(\d+)')

        self.colors_selected = int_re.findall(self.config['color']['value']);
        self.types_selected = int_re.findall(self.config['style']['value']);

        print(self.colors_selected)
        print(self.types_selected)
        # --------------------------------
        # Create PlotWidget
        # --------------------------------

        self.plotWidget = pq.PlotWidget()
        self.plotWidget.setWindowTitle('PlotPerformanceTitle')

        self.plotWidget.showGrid(x=self.show_grid_x, y=self.show_grid_y)

        self.curve = self.plotWidget.plot()

        self.set_widget_for_internal_usage( self.plotWidget )

        # ---------------------------
        # Create Parameters
        # ---------------------------

        self.parameters = {}
        self.parameters['x-grid'] = DParameter(None, 'x-grid', 0, [0,1],1, Regex='^(1|0){1}$')
        self.parameters['y-grid'] = DParameter(None, 'y-grid', 0, [0,1],1, Regex='^(1|0){1}$')

        self.send_new_parameter_list(list(self.parameters.values()))

        # ---------------------------
        # Create Legend
        # ---------------------------

        self.legend = pq.LegendItem((100, 40), offset=(40, 1))  # args are (size, offset)
        self.legend.setParentItem(self.plotWidget.graphicsItem())

        return True

    def pause(self):
        print('PlotPerformance paused')

    def resume(self):
        print('PlotPerformance resumed')

    def execute(self, Data=None, block_name = None):

        t = Data['t']
        #for elem in t:

        self._tbuffer.extend( t )

        for key in Data:
            if key != 't':
                y = Data[key]
                if key in self.signals:

                    self.signals[key]['buffer'].extend(y)

        # --------------------------
        # iterate over all buffers
        # --------------------------
        #print(self._tbuffer)
        for signal_name in self.signals:
           # print(self.buffers[signal_name])

            #self.curve.setData(self.x, self.buffers[signal_name]['buffer'])

            self.signals[signal_name]['curve'].setData(self._tbuffer, self.signals[signal_name]['buffer'])

    def set_parameter(self, name, value):
        print('set_parameter')
        print(name)
        print(value)

        if name == 'x-grid':
            self.config['x-grid']['value'] = value
            self.plotWidget.showGrid(x=value=='1')
        if name == 'y-grid':
            self.config['y-grid']['value'] = value
            self.plotWidget.showGrid(y=value=='1')

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
        }, 'x-grid': {
                'value': "0",
                'regex': '^(1|0)$'
        }, 'y-grid': {
                'value': "0",
                'regex': '^(1|0)$'
        }, 'color': {
                'value': "[0 1 2 3 4]",
                'regex': '^\[(\s*\d\s*)+\]'
        }, 'style': {
                'value': "[0 0 0 0 0]",
                'regex': '^\[(\s*\d\s*)+\]'
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

        # Add missing buffers
        for signal_name in current_signals:
            if signal_name not in self.signals:
                self.add_databuffer(signal_name, current_signals.index(signal_name))

        # Delete old buffers
        for signal_name in self.signals.copy():
            if signal_name not in current_signals:
                self.remove_databuffer(signal_name)

    def add_databuffer(self, signal_name, id):
        """
        Create new buffer for signal_name.
        :param signal_name:
        :return:
        """
        print('Add buffer for ' + signal_name)
        if signal_name not in self.signals:
            self.signals[signal_name] = {}

            start_size = len(self._tbuffer)

            buffer = collections.deque([0.0]*start_size, self._bufsize)

            pen = self.get_pen(id)

            curve = self.plotWidget.plot(self.x, self.y, pen=pen, name=signal_name)

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

    def get_pen(self, index):

        index = int(index)

        style_code = int(self.types_selected[index])
        color_code = int(self.colors_selected[index])

        if style_code in self.styles:
            style = self.styles[style_code]
        else:
            print('default style')
            style = self.styles[1]

        if color_code in self.colors:
            color = self.colors[color_code]
        else:
            print('default color')
            color = self.colors[1]

        return pq.mkPen(color=color, style=style)
