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

import numpy as np

import re

from pyqtgraph.Qt import QtGui, QtCore

class PlotPerformanceNEWBASE(vip_base):

    def initiate_layer_0(self, config=None):

        # get needed data from config
        self.show_grid_x = int(self.config['show_grid']['value']) == 1
        self.show_grid_y = int(self.config['show_grid']['value']) == 1
        # --------------------------------

        # set pq graph plot widget options
        self.plot = pq.PlotWidget()
        self.plot.setWindowTitle('PlotPerformanceTitle')
        self.plot.showGrid(x=self.show_grid_x, y=self.show_grid_y)
        # --------------------------------

        self.curve = self.plot.plot()
        self.data_buffer = np.linspace(1,1000,1000)

        self.set_widget_for_internal_usage( self.plot )
        return True


    def pause(self):
        print('PlotPerformance paused')

    def resume(self):
        print('PlotPerformance resumed')

    def execute(self, Data=None, block_name = None):
        self.data_buffer = np.roll(self.data_buffer, 3)
        self.curve.setData(self.data_buffer)


    def set_parameter(self, name, value):
        raise Exception

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
        pass



