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

from papi.plugin.visual_base import visual_base
from PySide.QtGui import QMdiSubWindow
import pyqtgraph as pq

import numpy as np

from pyqtgraph.Qt import QtGui, QtCore

class PlotPerformance(visual_base):

    def start_init(self, config=None):

        self._subWindow = QMdiSubWindow()



        self.plot = pq.PlotWidget()
        self.plot.setWindowTitle('PlotPerformanceTitle')

        #self.plot.setRange(QtCore.QRectF(0, -10, 5000, 20))
        #self.plot.setLabel('bottom', 'Index', units='B')
        self.curve = self.plot.plot()

        #self.time_buffer = np.zeros(1000)
        self.data_buffer = np.linspace(1,1000,1000)#np.zeros(1000)

        self._subWindow.setWidget(self.plot)


        return True

    def pause(self):
        print('PlotPerformance paused')

    def resume(self):
        print('PlotPerformance resumed')

    def execute(self, Data=None, block_name = None):

        #self.data_buffer = np.roll(self.data_buffer, len(Data['f3_1']))
        #self.data_buffer[-len(Data['f3_1']):] = Data['f3_1']

        #print(self.data_buffer[Data['f3_1']])
        #self.data_buffer[:len(Data['f3_1'])] = Data['f3_1']
        #self.data_buffer = np.roll(self.data_buffer, len(Data['f3_1']))

        self.data_buffer = np.roll(self.data_buffer, 3)


        self.curve.setData(self.data_buffer)

    def set_parameter(self, parameter):
        pass

    def get_widget(self):
        return Exception

    def get_type(self):
        return "ViP"


    def quit(self):
        print('PlotPerformance: will quit')


    def get_sub_window(self):
        return self._subWindow

    def get_startup_configuration(self):
        config = {
            "sampleinterval": {
                'value': 1,
                'regex': '[0-9]+'
        }, 'timewindow': {
                'value': "1000",
                'regex': '[0-9]+'
        }, 'size': {
                'value': "(300,300)",
                'regex': '\(([0-9]+),([0-9]+)\)'
        }, 'name': {
                'value' : 'Plot_Plugin',
        },
            'label_y': {
                'value': "amplitude, V",
                'regex': '\w+,\s+\w+'
        }, 'label_x': {
                'value': "time, s",
                'regex': '\w+,\s*\w+'
        }}

        return config

    # def hook_update_plugin_meta(self):
    #   pass
    #

