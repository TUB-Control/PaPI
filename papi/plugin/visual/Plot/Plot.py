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

import pyqtgraph as pq

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter
import numpy as np
import collections
import re
import time

current_milli_time = lambda: int(round(time.time() * 1000))

from pyqtgraph.Qt import QtCore


class Plot(vip_base):
    """
    style_codes:
            0 : QtCore.Qt.SolidLine,
            1 : QtCore.Qt.DashDotDotLine,
            2 : QtCore.Qt.DashDotLine,
            3 : QtCore.Qt.DashLine,
            4 : QtCore.Qt.DotLine

    color_codes:
            0 : (255, 255, 255),
            1 : (255, 0  , 0  ),
            2 : (0  , 255, 0  ),
            3 : (0  , 0  , 255),
            4 : (100, 100, 100)
    """

    def __init__(self):
        super(Plot, self).__init__()
        """
        Function init

        :param config:
        :return:
        """

        self.signals = {}

        self.__buffer_size__ = None
        self.__downsampling_rate__ = 1
        self.__tbuffer__ = []
        self.__tdata_old__ = [0]
        self.__signals_have_same_length = True
        self.__roll_shift__ = None
        self.__append_at__ = 1
        self.__new_added_data__ = 0
        self.__input_size__ = 0
        self.__rolling_plot__ = False
        self.__colors_selected__ = []
        self.__styles_selected__ = []
        self.__show_grid_x__ = None
        self.__show_grid_y__ = None
        self.__parameters__ = {}
        self.__update_intervall__ = None
        self.__last_time__ = None
        self.__plotWidget__ = None
        self.__legend__ = None
        self.__text_item__ = None
        self.__vertical_line__ = None
        self.__offset_line__ = None

        self.styles = {
            0: QtCore.Qt.SolidLine,
            1: QtCore.Qt.DashDotDotLine,
            2: QtCore.Qt.DashDotLine,
            3: QtCore.Qt.DashLine,
            4: QtCore.Qt.DotLine
        }

        self.colors = {
            0: (255, 255, 255),
            1: (255, 0, 0  ),
            2: (0, 255, 0  ),
            3: (0, 0, 255),
            4: (100, 100, 100)
        }

    def initiate_layer_0(self, config=None):
        """
        Function initiate layer 0

        :param config:
        :return:
        """

        # ---------------------------
        # Read configuration
        # ---------------------------
        int_re = re.compile(r'(\d+)')

        self.__show_grid_x__ = self.config['x-grid']['value'] == '1'
        self.__show_grid_y__ = self.config['y-grid']['value'] == '1'
        self.__rolling_plot__ = self.config['rolling_plot']['value'] == '1'

        self.__colors_selected__ = int_re.findall(self.config['color']['value'])
        self.__styles_selected__ = int_re.findall(self.config['style']['value'])

        self.__buffer_size__ = int(int_re.findall(self.config['buffersize']['value'])[0])

        self.__downsampling_rate__ = int(int_re.findall(self.config['downsampling_rate']['value'])[0])

        # ----------------------------
        # Create internal variables
        # ----------------------------

        self.__tbuffer__ = collections.deque([0.0] * 0, self.__buffer_size__)

        # --------------------------------
        # Create PlotWidget
        # --------------------------------

        self.__text_item__ = pq.TextItem(text='', color=(200, 200, 200), anchor=(0, 0))
        self.__vertical_line__ = pq.InfiniteLine()

        self.__plotWidget__ = pq.PlotWidget()
        self.__plotWidget__.addItem(self.__text_item__)

        if self.__rolling_plot__:
            self.__plotWidget__.addItem(self.__vertical_line__)

        self.__text_item__.setPos(0, 0)
        self.__plotWidget__.setWindowTitle('PlotPerformanceTitle')

        self.__plotWidget__.showGrid(x=self.__show_grid_x__, y=self.__show_grid_y__)

        self.set_widget_for_internal_usage(self.__plotWidget__)

        # ---------------------------
        # Create Parameters
        # ---------------------------

        self.__parameters__['x-grid'] = DParameter(None, 'x-grid', 0, [0, 1], 1, Regex='^(1|0){1}$')
        self.__parameters__['y-grid'] = DParameter(None, 'y-grid', 0, [0, 1], 1, Regex='^(1|0){1}$')

        self.__parameters__['color'] = DParameter(None, 'color', '[0 1 2 3 4]', [0, 1], 1, Regex='^\[(\s*\d\s*)+\]')
        self.__parameters__['style'] = DParameter(None, 'style', '[0 0 0 0 0]', [0, 1], 1, Regex='^\[(\s*\d\s*)+\]')
        self.__parameters__['rolling'] = DParameter(None, 'rolling', '0', [0, 1], 1, Regex='^(1|0){1}')

        self.__parameters__['downsampling_rate'] = DParameter(None, 'downsampling_rate', self.__downsampling_rate__,
                                                              [1, 100],
                                                              1, Regex='^([1-9][0-9]?|100)$')
        self.__parameters__['buffersize'] = DParameter(None, 'buffersize', self.__buffer_size__, [1, 100],
                                                       1, Regex='^([1-9][0-9]{0,3}|10000)$')
        self.send_new_parameter_list(list(self.__parameters__.values()))

        # ---------------------------
        # Create Legend
        # ---------------------------

        self.__legend__ = pq.LegendItem((100, 40), offset=(40, 1))  # args are (size, offset)
        self.__legend__.setParentItem(self.__plotWidget__.graphicsItem())

        self.__last_time__ = current_milli_time()

        self.__update_intervall__ = 25  # in milliseconds

        return True

    def pause(self):
        """
        Function pause

        :return:
        """
        print('PlotPerformance paused')

    def resume(self):
        """
        Function resume

        :return:
        """
        print('PlotPerformance resumed')

    def execute(self, Data=None, block_name=None):
        """
        Function execute

        :param Data:
        :param block_name:
        :return:
        """
        t = Data['t']

        self.__input_size__ = len(t)
        self.__tbuffer__.extend(t)
        self.__new_added_data__ += len(t)
        self.__signals_have_same_length = True

        for key in Data:
            if key != 't':
                y = Data[key]
                if key in self.signals:
                    buffer = self.signals[key]['buffer']
                    buffer.extend(y)
                    self.__signals_have_same_length &= (len(t) == len(y))

        if self.__input_size__ > 1 or self.__signals_have_same_length:
            if current_milli_time() - self.__last_time__ > self.__update_intervall__:
                self.__last_time__ = current_milli_time()
                self.update_plot()
                self.__last_time__ = current_milli_time()
                self.__new_added_data__ = 0
        else:
            self.update_plot_single_timestamp(Data)

    def set_parameter(self, name, value):
        """
        Function set parameters

        :param name:
        :param value:
        :return:
        """
        if name == 'x-grid':
            self.config['x-grid']['value'] = value
            self.__plotWidget__.showGrid(x=value == '1')

        if name == 'y-grid':

            self.config['y-grid']['value'] = value
            self.__plotWidget__.showGrid(y=value == '1')

        if name == 'downsampling_rate':
            self.config['downsampling_rate']['value'] = value
            self.__downsampling_rate__ = int(value)
            self.__new_added_data__ = 0

        if name == 'rolling':
            self.__rolling_plot__ = int(float(value)) == int('1')
            self.config['rolling_plot']['value'] = value

            if self.__rolling_plot__:
               # if self.__vertical_line__ not in self.__plotWidget__.listDataItems():

                self.__plotWidget__.addItem(self.__vertical_line__)

        if name == 'color':
            self.config['color']['value'] = value
            int_re = re.compile(r'(\d+)')
            self.__colors_selected__ = int_re.findall(self.config['color']['value'])
            self.update_pens()

        if name == 'style':
            self.config['style']['value'] = value
            int_re = re.compile(r'(\d+)')
            self.__styles_selected__ = int_re.findall(self.config['style']['value'])
            self.update_pens()

        if name == 'buffersize':
            self.config['buffersize']['value'] = value
            self.set_buffer_size(value)

    def update_pens(self):
        """
        Function update pens

        :return:
        """

        for signal_name in self.signals.keys():
            signal_id = self.signals[signal_name]['id']

            new_pen = self.get_pen(signal_id)

            self.signals[signal_name]['curve'].setPen(new_pen)

    def update_plot(self):
        """
        Function update_plot

        :return:
        """
        shift_data = 0


        for last_tvalue in self.__tdata_old__:
            if last_tvalue in self.__tbuffer__:
                shift_data = list(self.__tbuffer__).index(last_tvalue)
                break

        tdata = list(self.__tbuffer__)[shift_data::self.__downsampling_rate__]

        if self.__rolling_plot__:
            self.__append_at__ += self.__new_added_data__ / self.__downsampling_rate__
            self.__append_at__ %= len(tdata)

        # --------------------------
        # iterate over all buffers
        # --------------------------
        for signal_name in self.signals:
            data = list(self.signals[signal_name]['buffer'])[shift_data::self.__downsampling_rate__]

            if self.__rolling_plot__:
                data = np.roll(data, int(self.__append_at__))
                self.__vertical_line__.setValue(tdata[int(self.__append_at__)-1])
            else:
                self.__vertical_line__.setValue(tdata[0])

            curve = self.signals[signal_name]['curve']
            curve.setData(tdata, data, _callSync='off')

        self.__tdata_old__ = tdata

    def update_plot_single_timestamp(self, data):
        """
        Function update_plot_single_timestamp

        :return:
        """

        self.__text_item__.setText("Time " + str(data['t'][0]), color=(200, 200, 200))

        for signal_name in data:
            if signal_name != 't':
                signal_data = data[signal_name]
                if signal_name in self.signals:
                    tdata = np.linspace(1, len(signal_data), len(signal_data))

                    curve = self.signals[signal_name]['curve']
                    curve.setData(tdata, signal_data, _callSync='off')

        pass

    def quit(self):
        """
        Function quit plugin

        :return:
        """
        print('PlotPerformance: will quit')

    def get_plugin_configuration(self):
        """
        Function get plugin configuration

        :return {}:
        """
        config = {
            'label_y': {
                'value': "amplitude, V",
                'regex': '\w+,\s+\w+',
                'display_text': 'Label-Y'
            }, 'label_x': {
            'value': "time, s",
            'regex': '\w+,\s*\w+',
            'display_text': 'Label-X'
        }, 'x-grid': {
            'value': "0",
            'regex': '^(1|0)$',
            'type': 'bool',
            'display_text': 'Grid-X'
        }, 'y-grid': {
            'value': "0",
            'regex': '^(1|0)$',
            'type': 'bool',
            'display_text': 'Grid-Y'
        }, 'color': {
            'value': "[0 1 2 3 4]",
            'regex': '^\[(\s*\d\s*)+\]',
            'advanced': '1',
            'display_text': 'Color'
        }, 'style': {
            'value': "[0 0 0 0 0]",
            'regex': '^\[(\s*\d\s*)+\]',
            'advanced': '1',
            'display_text': 'Style'
        }, 'buffersize': {
            'value': "3000",
            'regex': '^([1-9][0-9]{0,3}|10000)$',
            'advanced': '1',
            'display_text': 'Buffersize'
        }, 'downsampling_rate': {
            'value': "10",
            'regex': '(\d+)'
        }, 'rolling_plot': {
            'value': '0',
            'regex': '^(1|0)$',
            'type': 'bool',
            'display_text': 'Rolling Plot'
        }
        }
        # http://www.regexr.com/
        return config

    def set_buffer_size(self, new_size):
        """
        Function set buffer size

        :param new_size:
        :return:
        """

        self.__buffer_size__ = int(new_size)

        # -------------------------------
        # Change Time Buffer
        # -------------------------------

        self.__tbuffer__ = collections.deque([0.0] * 0, self.__buffer_size__)

        # -------------------------------
        # Change Buffer of current
        # plotted signals
        # -------------------------------

        start_size = len(self.__tbuffer__)

        for signal_name in self.signals:
            buffer_new = collections.deque([0.0] * start_size, self.__buffer_size__)  # COLLECTION

            buffer_old = self.signals[signal_name]['buffer']
            #buffer_new.extend(buffer_old)

            self.signals[signal_name]['buffer'] = buffer_new

        self.__new_added_data__ = 0

    def plugin_meta_updated(self):
        """
        By this function the plot is able to handle more than one input for plotting.

        :return:
        """

        subscriptions = self.dplugin_info.get_subscribtions()

        current_signals = []

        for dpluginsub_id in subscriptions:
            for dblock_name in subscriptions[dpluginsub_id]:

                # get subscription for dblock
                subscription = subscriptions[dpluginsub_id][dblock_name]

                for signal in subscription.get_signals():
#                    signal_name = dblocksub.dblock.get_signal_name(signal)
                    current_signals.append(signal)

        # Add missing buffers
        for signal_name in current_signals:
            if signal_name not in self.signals:
                self.add_databuffer(signal_name, current_signals.index(signal_name))

        # Delete old buffers
        for signal_name in self.signals.copy():
            if signal_name not in current_signals:
                self.remove_databuffer(signal_name)

    def add_databuffer(self, signal_name, signal_id):
        """
        Create new buffer for signal_name.

        :param signal_name:
        :param signal_id:
        :return:
        """

        if signal_name not in self.signals:
            self.signals[signal_name] = {}

            start_size = len(self.__tbuffer__)

            buffer = collections.deque([0.0] * start_size, self.__buffer_size__)  # COLLECTION

            legend_name = str(signal_id) + "# " + signal_name
            curve = self.__plotWidget__.plot([0, 1], [0, 1], name=legend_name, clipToView=True)

            self.signals[signal_name]['buffer'] = buffer
            self.signals[signal_name]['curve'] = curve
            self.signals[signal_name]['id'] = signal_id

            self.__legend__.addItem(curve, legend_name)

        self.update_pens()

    def remove_databuffer(self, signal_name):
        """
        Remove the databuffer for signal_name.

        :param signal_name:
        :return:
        """

        if signal_name in self.signals:
            curve = self.signals[signal_name]['curve']
            curve.clear()
            self.__legend__.removeItem(signal_name)
            del self.signals[signal_name]

    def get_pen(self, index):
        """
        Function get pen

        :param index:
        :return:
        """
        index = int(index)

        style_index = index % len(self.__styles_selected__)
        style_code = int(self.__styles_selected__[style_index])

        color_index = index % len(self.__colors_selected__)
        color_code = int(self.__colors_selected__[color_index])

        if style_code in self.styles:
            style = self.styles[style_code]
        else:
            style = self.styles[1]

        if color_code in self.colors:
            color = self.colors[color_code]
        else:
            color = self.colors[1]

        return pq.mkPen(color=color, style=style)
