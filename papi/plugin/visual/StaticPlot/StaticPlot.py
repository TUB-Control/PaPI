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

import papi.pyqtgraph as pq

import numpy as np
import collections
import re
import copy
import time
import json

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter
from papi.data.DSignal import DSignal
import papi.pyqtgraph as pg
import papi.constants as pc


current_milli_time = lambda: int(round(time.time() * 1000))

from papi.pyqtgraph.Qt import QtCore, QtGui
from PySide.QtGui import QRegExpValidator
from PySide.QtCore import *

class StaticPlot(vip_base):
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

    def __init__(self, debug=False):
        super(StaticPlot, self).__init__()
        """
        Function init

        :param config:
        :return:
        """

        self.signals = {}

        self.__papi_debug__ = debug
        self.__buffer_size__ = None
        self.__downsampling_rate__ = 1
        self.__tbuffer__ = []

        self.__signals_have_same_length = True

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
        self.__last_plot_time__ = None
        self.__plotWidget__ = None
        self.__legend__ = None

        self.__stp_min_x = None
        self.__stp_max_x = None

        self.__stp_min_y = None
        self.__stp_max_y = None
        self.__stp_active__ = None

        self.__downsampling_rate_start__ = None;
        self.__downsampling_rate__ = None

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

        self.__colors_selected__ = int_re.findall(self.config['color']['value'])
        self.__styles_selected__ = int_re.findall(self.config['style']['value'])

        # ----------------------------
        # Set internal variables used for single timestamp plotting (stp)
        # ----------------------------

        self.__plotWidget__ = pg.PlotWidget()

        self.__plotWidget__.setWindowTitle('StaticPlot')

        self.__plotWidget__.showGrid(x=self.__show_grid_x__, y=self.__show_grid_y__)
        self.__plotWidget__.getPlotItem().getViewBox().disableAutoRange()
        self.__plotWidget__.getPlotItem().getViewBox().setYRange(0,6)

        self.set_widget_for_internal_usage(self.__plotWidget__)

        # ---------------------------
        # Create Parameters
        # ---------------------------

        self.__parameters__['x-grid'] = \
            DParameter('x-grid', self.config['x-grid']['value'], Regex='^(1|0){1}$')
        self.__parameters__['y-grid'] = \
            DParameter('y-grid', self.config['y-grid']['value'], Regex='^(1|0){1}$')

        self.__parameters__['color'] = \
            DParameter('color', self.config['color']['value'], Regex='^\[(\s*\d\s*)+\]')
        self.__parameters__['style'] = \
            DParameter('style', self.config['style']['value'], Regex='^\[(\s*\d\s*)+\]')

        self.__parameters__['yRange'] = \
            DParameter('yRange', '[0,1]',  Regex='^\[(\d+\.\d+)\s+(\d+\.\d+)\]$')

        self.send_new_parameter_list(list(self.__parameters__.values()))

        # ---------------------------
        # Create Legend
        # ---------------------------

        self.__legend__ = pq.LegendItem((100, 40), offset=(40, 1))  # args are (size, offset)
        self.__legend__.setParentItem(self.__plotWidget__.graphicsItem())

        self.setup_context_menu()
        self.__plotWidget__.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.__plotWidget__.customContextMenuRequested.connect(self.showContextMenu)

        self.use_range_for_y(self.config['yRange']['value'])

        self.read_json_data()

        return True

    def pause(self):
        """
        Function pause

        :return:
        """
        pass

    def resume(self):
        """
        Function resume

        :return:
        """
        pass

    def execute(self, Data=None, block_name=None):
        """
        Function execute

        :param Data:
        :param block_name:
        :return:
        """
        pass

    def set_parameter(self, name, value):
        """
        Function set parameters

        :param name:
        :param value:
        :return:
        """
        print(value)
        if name == 'x-grid':
            self.config['x-grid']['value'] = value
            self.__plotWidget__.showGrid(x=value == '1')
            self.xGrid_Checkbox.setChecked(value=='1')

        if name == 'y-grid':
            self.config['y-grid']['value'] = value
            self.__plotWidget__.showGrid(y=value == '1')
            self.yGrid_Checkbox.setChecked(value=='1')

        if name == 'color':
            self.clear()
            self.config['color']['value'] = value
            int_re = re.compile(r'(\d+)')
            self.__colors_selected__ = int_re.findall(self.config['color']['value'])

        if name == 'style':
            self.clear()
            self.config['style']['value'] = value
            int_re = re.compile(r'(\d+)')
            self.__styles_selected__ = int_re.findall(self.config['style']['value'])

        if name == 'yRange':
            self.config['yRange']['value'] = value
            self.use_range_for_y(value)


    def read_json_data(self):

        json_str = self.config['json_data']['value']
        axis_id  = self.config['axis_identifier']['value']
        data = json.loads(json_str)


        self.plot_data(data, axis_id)

    def plot_data(self, data, axis_id):
        """
        Function update_plot_single_timestamp

        :return:
        """

        self.__plotWidget__.clear()


        tdata = data[axis_id]

        x_min = min(tdata)
        x_max = max(tdata)

        y_min = None
        y_max = None

        for signal_name in data:
            if signal_name != axis_id:
                signal_data = data[signal_name]
                print(signal_data)

                if y_max is not None:
                    y_max = max(max(signal_data), y_max)
                else:
                    y_max = max(signal_data)

                if y_min is not None:
                    y_min = min(min(signal_data), y_min)
                else:
                    y_min = min(signal_data)

                graphic = GraphicItem(np.array(tdata), np.array(signal_data), 0)

                self.__plotWidget__.addItem(graphic)


        self.use_range_for_x("[{:2.2f} {:2.2f}]".format(x_min, x_max))
        self.use_range_for_y("[{:2.2f} {:2.2f}]".format(y_min, y_max))

#        self.__plotWidget__.getPlotItem().getViewBox().setXRange(x_min, x_max)


    def plugin_meta_updated(self):
        """
        This function is called whenever meta information are changed.
        This enables the plot to handle more than one input for plotting.

        :return:
        """

        pass

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
            style = self.styles[0]

        if color_code in self.colors:
            color = self.colors[color_code]
        else:
            color = self.colors[0]

        return pq.mkPen(color=color, style=style)

    def use_range_for_x(self, value):
        """

        :param value:
        :return:
        """
        reg = re.compile(r'(\d+\.\d+)')
        range = reg.findall(value)

        if len(range) == 2:
            self.__plotWidget__.getPlotItem().getViewBox().setXRange(float(range[0]),float(range[1]))

    def use_range_for_y(self, value):
        """

        :param value:
        :return:
        """
        reg = re.compile(r'([-]{0,1}\d+\.\d+)')
        range = reg.findall(value)

        if len(range) == 2:
            self.__plotWidget__.getPlotItem().getViewBox().setYRange(float(range[0]), float(range[1]))

    def setup_context_menu(self):
        """

        :return:
        """

        self.custMenu = QtGui.QMenu("Options")
        self.gridMenu = QtGui.QMenu('Grid')


        # get old values;
        reg = re.compile(r'(\d+\.\d+)')
        range = reg.findall(self.config['yRange']['value'])
        if len(range) == 2:
            y_min = range[0]
            y_max = range[1]
        else:
            y_min = '0.0'
            y_max = '1.0'

        rx = QRegExp(r'([-]{0,1}\d+\.\d+)')
        validator = QRegExpValidator(rx, self.__plotWidget__)




        # Grid Menu:
        # -----------------------------------------------------------
        # Y-Grid checkbox
        self.xGrid_Checkbox = QtGui.QCheckBox()
        self.xGrid_Checkbox.stateChanged.connect(self.contextMenu_xGrid_toogle)
        self.xGrid_Checkbox.setText('X-Grid')
        self.xGrid_Action = QtGui.QWidgetAction(self.__plotWidget__)
        self.xGrid_Action.setDefaultWidget(self.xGrid_Checkbox)
        self.gridMenu.addAction(self.xGrid_Action)
        # Check config for startup  state
        if self.__show_grid_x__:
            self.xGrid_Checkbox.setChecked(True)

        # X-Grid checkbox
        self.yGrid_Checkbox = QtGui.QCheckBox()
        self.yGrid_Checkbox.stateChanged.connect(self.contextMenu_yGrid_toogle)
        self.yGrid_Checkbox.setText('Y-Grid')
        self.yGrid_Action = QtGui.QWidgetAction(self.__plotWidget__)
        self.yGrid_Action.setDefaultWidget(self.yGrid_Checkbox)
        self.gridMenu.addAction(self.yGrid_Action)
        # Check config for startup  state
        if self.__show_grid_y__:
            self.yGrid_Checkbox.setChecked(True)

        # add Menus

        self.custMenu.addMenu(self.gridMenu)
        self.custMenu.addSeparator().setText("Rolling Plot")

        self.__plotWidget__.getPlotItem().getViewBox().menu.clear()

        if not self.__papi_debug__:
            self.__plotWidget__.getPlotItem().ctrlMenu = [self.create_control_context_menu(), self.custMenu]

    def showContextMenu(self):
        self.setup_context_menu()


    def contextMenu_yAutoRangeButton_clicked(self):
        mi = None
        ma = None

        if self.__stp_active__:
            mi = self.__stp_min_y
            ma = self.__stp_max_y
        else:
            for sig in self.signals:
                graphics = self.signals[sig].graphics
                buf = []
                for graphic in graphics:
                    buf.extend(graphic.y)

                ma_buf = max(buf)
                mi_buf = min(buf)
                if ma is not None:
                    if ma_buf > ma:
                        ma = ma_buf
                else:
                    ma = ma_buf

                if mi is not None:
                    if mi_buf < mi:
                        mi = mi_buf
                else:
                    mi = mi_buf

        self.yRange_maxEdit.setText(ma)
        self.yRange_minEdit.setText(mi)
        self.control_api.do_set_parameter(self.__id__, 'yRange', '[' + str(float(mi)) + ' ' + str(float(ma)) + ']')

    def contextMenu_xGrid_toogle(self):
        if self.xGrid_Checkbox.isChecked():
            self.control_api.do_set_parameter(self.__id__, 'x-grid', '1')
        else:
            self.control_api.do_set_parameter(self.__id__, 'x-grid', '0')

    def contextMenu_yGrid_toogle(self):
        if self.yGrid_Checkbox.isChecked():
            self.control_api.do_set_parameter(self.__id__, 'y-grid', '1')
        else:
            self.control_api.do_set_parameter(self.__id__, 'y-grid', '0')

    def contextMenu_yRange_toogle(self):
        mi = self.yRange_minEdit.text()
        ma = self.yRange_maxEdit.text()
        if float(mi) < float(ma):
            self.control_api.do_set_parameter(self.__id__, 'yRange', '[' + float(mi) + ' ' + float(ma) + ']')


    def quit(self):
        """
        Function quit plugin

        :return:
        """
        print('StaticPlot: will quit')

    def get_plugin_configuration(self):
        """
        Function get plugin configuration

        :return {}:
        """
        config = {
            'json_data' : {
                'value' : '{"v1": [5, 6, 7, 8, 9 ], "v2": [ 0, 1, 2, 3, 4 ], '
                          '"v3": [ -5, -6, -7, -8, -9 ], "v4": [ 0, -1, -2, -3, -4 ], '
                          '"t": [ 0, 1, 2, 3, 4 ]}',
                'tooltip' : 'Used as data source. Format: { "time" : [...], "y1" : [...], "y2" : [...]}'
            },
            'axis_identifier' : {
                'value' :  't',
                'tooltip' : 'Used to specify the identifier for the X-Axis e.g. time in json_data'
            },
            'x-grid': {
                'value': "0",
                'regex': pc.REGEX_BOOL_BIN,
                'type': 'bool',
                'display_text': 'Grid-X'
            }, 'y-grid': {
                'value': "0",
                'regex': pc.REGEX_BOOL_BIN,
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
            }, 'yRange': {
                'value': '[0.0 1.0]',
                'regex': '(\d+\.\d+)',
                'advanced': '1',
                'display_text': 'y: range'
            }
        }
        # http://www.regexr.com/
        return config

    def clear(self):
        """

        :return:
        """
        self.__plotWidget__.clear()

class GraphicItem(pg.QtGui.QGraphicsPathItem):
    """
    Represents a single object which is drawn by a plot.
    """
    def __init__(self, x, y, counter, pen=pg.mkPen('r')):
        """

        :param x:
        :param y:
        :param pen:
        :return:
        """

        x = np.array(x[:])[np.newaxis, :]

        connect = np.ones(x.shape, dtype=bool)
        connect[:,-1] = 0 # don't draw the segment between each trace
        self.path = pg.arrayToQPath(x.flatten(), y.flatten(), connect.flatten())
        pg.QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.setCacheMode(pg.QtGui.QGraphicsItem.NoCache)
        self.setPen(pen)
        self.not_drawn = True
        self.counter = counter
        self.y = y
        self.last_x = x[0][-1]
        self.last_y = y[-1]

    def shape(self): # override because QGraphicsPathItem.shape is too expensive.
        return pg.QtGui.QGraphicsItem.shape(self)

    def length(self):
        return self.counter

    def boundingRect(self):
        return self.path.boundingRect()


