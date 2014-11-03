#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.visual_base import visual_base
from papi.PapiEvent import PapiEvent
from papi.data.DParameter import DParameter
from pyqtgraph import PlotWidget
from PySide.QtGui import QMdiSubWindow
from PySide.QtCore import QRegExp


import pyqtgraph as pg

import numpy
import re
import collections
import numpy as np

__author__ = 'knuths'


class Plot(visual_base):

    def start_init(self, config=None):
 #       super(Plot,self).start_init(config)

        size_re = re.compile(r'([0-9]+)')

        default_config = self.get_startup_configuration()

        if config is None:
            config = default_config

        self.config = config

        sampleinterval = float(config['sampleinterval']['value'])

        timewindow = int(config['timewindow']['value'])

        name = config['name']['value']

        size = size_re.findall(config['size']['value'])


        self.name = name
        self._interval = int(sampleinterval*timewindow)
        self._bufsize = int(timewindow/sampleinterval)
        self.tDatabuffer = collections.deque([0.0]*self._bufsize, self._bufsize)

        self.Databuffer = []

        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)

        # -----------------------------
        # create plot widget
        # ----------------------------

        self._plotWidget = PlotWidget()

        self._plotWidget.showGrid(x=True, y=True)
        self._plotWidget.setLabel('left', 'amplitude', 'V')
        self._plotWidget.setLabel('bottom', 'time', 's')

        self._interval = sampleinterval
        self.curves = []

        # -----------------------------
        # create QMdiSubWindow
        # ----------------------------

        self.set_window_for_internal_usage(QMdiSubWindow())
        self._subWindow.setWidget(self._plotWidget)
        self._subWindow.setWindowTitle(self.name)
        self._subWindow.resize(int(size[0]), int(size[1]))

        # -----------------------------
        # create array for parameters
        #  ----------------------------
        self.parameters = []

        # -----------------------------
        # Create QTimer
        # -----------------------------

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)


        return True

    def pause(self):
        print('plot paused')

    def resume(self):
        print('plot resumed')

    def execute(self, Data=None, block_name = None):
        #print(Data)


        t = Data['t']

        y = []

        for key in Data:
            if key is 't':
                t = Data['t']
            else:
                y.append(Data[key])

        self.add_data(t, y)

        #self.update()

    def set_parameter(self, parameter):
        a = re.compile("^Color\_[0-9]")

        if a.match(parameter.name):
            print(parameter.name)
        else:
            self.set_parameter(parameter)

        pass

    def get_widget(self):
        return self._plotWidget

    def get_type(self):
        return "ViP"

    def get_output_sizes(self):
        return [0,0]

    def quit(self):
        print('Plot: will quit')

    def update(self):
        self.x[:] = self.tDatabuffer

        for i in range(len(self.Databuffer)):
            curve = self.curves[i]
            y = self.Databuffer[i]

            curve.setData(self.x, y)

    def add_data(self,t,data:[]):
        for elem in t:
            self.tDatabuffer.append( elem )

        for i in range(len(data)):
            y = data[i]
            for elem in y:
                self.Databuffer[i].append(elem)

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
        },
            'label_y': {
                'value': "amplitude, V",
                'regex': '\w+,\s+\w+'
        }, 'label_x': {
                'value': "time, s",
                'regex': '\w+,\s*\w+'
        }}

        return self.merge_configs(self.get_configuration_base(),config)

    def hook_update_plugin_meta(self):

        signal_count = 0;

        subscriptions = self.dplugin_info.get_subscribtions()

        for sub in subscriptions:
            for dblock_name in subscriptions[sub]:
                subscription = subscriptions[sub][dblock_name]

                for signal in subscription.get_signals():
                    signal_count += 1

        diff_count = len(self.Databuffer) - signal_count

        #There are too many buffers
        if diff_count > 0:
            for i in range(abs(diff_count)):
                # print("Remove")
                self.curves.pop()
                self.Databuffer.pop()
                self.parameters.pop()

        #Some Buffers are missing
        if diff_count < 0:
            for i in range(self.signal_count, signal_count):
                # print("Append ")
                new_plot = self._plotWidget.plot(self.x, self.y, pen=(100,0+i*10,0), symbole='o')
                new_plot.setDownsampling(method='peak')
                self.curves.append(new_plot)
                self.Databuffer.append( collections.deque([0.0]*self._bufsize, self._bufsize) )
                self.parameters.append( DParameter(None,'Color_' + str(i),0+i*10,[0,255],1) )

        self.signal_count = signal_count
        #self.send_new_parameter_list(self.parameters)
