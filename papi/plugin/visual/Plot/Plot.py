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

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter
from papi.data.DSignal import DSignal
import numpy as np
import collections
import re
import copy
import time
import papi.pyqtgraph as pg

current_milli_time = lambda: int(round(time.time() * 1000))

from papi.pyqtgraph.Qt import QtCore, QtGui
from PySide.QtGui import QRegExpValidator
from PySide.QtCore import *

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

    def __init__(self, debug=False):
        super(Plot, self).__init__()
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
        self.__last_plot_time__ = None
        self.__plotWidget__ = None
        self.__legend__ = None
        self.__text_item__ = None
        self.__vertical_line__ = None
        self.__offset_line__ = None
        self.__y_axis__ = None
        self.__x_axis__ = None
        self.__amount_of_slices__ = None
        self.downsampling_rate_start = None;
        self.downsampling_rate = None

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
        self.downsampling_rate_start = 0
        self.downsampling_rate = self.__downsampling_rate__

        # ----------------------------
        # Create internal variables
        # ----------------------------

        self.__tbuffer__ = collections.deque([0.0] * 0, self.__buffer_size__)
        self.__amount_of_slices__ = 10

        # --------------------------------
        # Create PlotWidget
        # --------------------------------
        self.__text_item__ = pq.TextItem(text='', color=(200, 200, 200), anchor=(0, 0))

        self.__vertical_line__ = pq.InfiniteLine()

#        self.__plotWidget__ = pq.PlotWidget()

        self.__plotWidget__ = PlotWidget()

        self.__plotWidget__.addItem(self.__text_item__)

        if self.__rolling_plot__:
            self.__plotWidget__.addItem(self.__vertical_line__)

        self.__text_item__.setPos(0, 0)
        self.__plotWidget__.setWindowTitle('PlotPerformanceTitle')

        self.__plotWidget__.showGrid(x=self.__show_grid_x__, y=self.__show_grid_y__)
        self.__plotWidget__.getPlotItem().getViewBox().disableAutoRange()
        self.__plotWidget__.getPlotItem().getViewBox().setYRange(0,6)

        self.__plotWidget__.getPlotItem().setDownsampling(auto=True)
        if not self.__papi_debug__:
            self.set_widget_for_internal_usage(self.__plotWidget__)
        self.__plotWidget__.getPlotItem().getViewBox().enableAutoRange(axis=pq.ViewBox.YAxis, enable=False)
        self.__plotWidget__.getPlotItem().getViewBox().enableAutoRange(axis=pq.ViewBox.XAxis, enable=False)

        #self.__plotWidget__.getPlotItem().getViewBox().setMouseEnabled(x=False, y=True)

        # ---------------------------
        # Create Parameters
        # ---------------------------

        self.__parameters__['x-grid'] = DParameter('x-grid', 0, Regex='^(1|0){1}$')
        self.__parameters__['y-grid'] = DParameter('y-grid', 0, Regex='^(1|0){1}$')

        self.__parameters__['color'] = DParameter('color', '[0 1 2 3 4]', Regex='^\[(\s*\d\s*)+\]')
        self.__parameters__['style'] = DParameter('style', '[0 0 0 0 0]', Regex='^\[(\s*\d\s*)+\]')
        self.__parameters__['rolling'] = DParameter('rolling', '0', Regex='^(1|0){1}')

        self.__parameters__['downsampling_rate'] = DParameter('downsampling_rate', self.__downsampling_rate__, Regex='^([1-9][0-9]?|100)$')
        self.__parameters__['buffersize'] = DParameter('buffersize', self.__buffer_size__, Regex='^([1-9][0-9]{0,3}|10000)$')

        #self.__parameters__['xRange'] = DParameter('xRange', '[0,1]', Regex='(\d+\.\d+)')
        self.__parameters__['yRange'] = DParameter('yRange', '[0,1]',  Regex='(\d+\.\d+)')

        if not self.__papi_debug__:
            self.send_new_parameter_list(list(self.__parameters__.values()))

        # ---------------------------
        # Create Legend
        # ---------------------------

        self.__legend__ = pq.LegendItem((100, 40), offset=(40, 1))  # args are (size, offset)
        self.__legend__.setParentItem(self.__plotWidget__.graphicsItem())

        self.__last_time__ = current_milli_time()

        self.__update_intervall__ = 20  # in milliseconds
        self.__last_plot_time__   = 0

        self.setup_context_menu()

        #self.use_range_for_x(self.config['xRange']['value'])
        self.use_range_for_y(self.config['yRange']['value'])

        return True

    def pause(self):
        """
        Function pause

        :return:
        """
        self.__plotWidget__.getPlotItem().getViewBox().setMouseEnabled(x=True, y=True)
        print('PlotPerformance paused')

    def resume(self):
        """
        Function resume

        :return:
        """
        self.__plotWidget__.getPlotItem().getViewBox().setMouseEnabled(x=False, y=True)
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

        #print('Execute')

        self.__signals_have_same_length = True

        now = pg.ptime.time()

        for key in Data:
            if key != 't':
                y = Data[key]
                if key in self.signals:
                    if self.downsampling_rate_start < len(y):
                        ds_y = y[self.downsampling_rate_start::self.downsampling_rate]
                        #print(ds_y)
                        self.signals[key].add_data(ds_y)

                        self.__signals_have_same_length &= ( len(y) == len(t) )

        if self.downsampling_rate_start >= len(t):
            self.downsampling_rate_start -= len(t)
        else:
            ds_t = t[self.downsampling_rate_start::self.downsampling_rate]
            #print(ds_t)
            self.downsampling_rate_start += self.downsampling_rate - len(ds_t)
            self.__tbuffer__.extend(ds_t)


        self.__new_added_data__ += len(t)

        if self.__input_size__ > 1 or self.__signals_have_same_length:

            if current_milli_time() - self.__last_time__ > self.__update_intervall__ - self.__last_plot_time__:
                self.__last_time__ = current_milli_time()
                self.update_plot()
                self.__last_time__ = current_milli_time()
                self.__new_added_data__ = 0
        else:
            self.update_plot_single_timestamp(Data)

#        print("Plot time: %0.5f sec" % (self.__last_plot_time__) )

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
            self.xGrid_Checkbox.setChecked(value=='1')

        if name == 'y-grid':
            self.config['y-grid']['value'] = value
            self.__plotWidget__.showGrid(y=value == '1')
            self.yGrid_Checkbox.setChecked(value=='1')

        if name == 'downsampling_rate':
            self.config['downsampling_rate']['value'] = value
            self.__downsampling_rate__ = int(value)
            #self.__plotWidget__.getPlotItem().setDownsampling(ds=int(value),auto=False,mode='mean')
            self.__new_added_data__ = 0
            self.update_downsampling_rate()

        if name == 'rolling':
            self.clear()
            self.config['rolling_plot']['value'] = value
            self.update_rolling_plot()

        if name == 'color':
            self.clear()
            self.config['color']['value'] = value
            int_re = re.compile(r'(\d+)')
            self.__colors_selected__ = int_re.findall(self.config['color']['value'])
            self.update_pens()
            self.update_legend()

        if name == 'style':
            self.clear()
            self.config['style']['value'] = value
            int_re = re.compile(r'(\d+)')
            self.__styles_selected__ = int_re.findall(self.config['style']['value'])
            self.update_pens()
            self.update_legend()

        if name == 'buffersize':
            self.config['buffersize']['value'] = value
            self.update_buffer_size(value)

        # if name == 'xRange':
        #     self.config['xRange']['value'] = value
        #     self.use_range_for_x(value)

        if name == 'yRange':
            self.config['yRange']['value'] = value
            self.use_range_for_y(value)

    def update_pens(self):
        """
        Function update pens

        :return:
        """

        for signal_name in self.signals.keys():
            signal_id = self.signals[signal_name].id

            new_pen = self.get_pen(signal_id)

            self.signals[signal_name].pen = new_pen

    def update_plot(self):
        """
        Function update_plot

        :return:
        """


        if len(self.__tbuffer__) == 0:
            return

        if not self.__rolling_plot__:
            tdata = list(self.__tbuffer__)

        if self.__rolling_plot__:
            tdata = list(range(0, len(self.__tbuffer__)))
            self.__append_at__ += self.signals[list(self.signals.keys())[0]].get_new_added_since_last_drawing()
            self.__append_at__ %= len(tdata)
            tdata = np.roll(tdata, -int(self.__append_at__))

        now = pg.ptime.time()

        for signal_name in self.signals:

            # get all no more needed graphic items
            graphics = self.signals[signal_name].get_old_graphics()
            for graphic in graphics:
                self.__plotWidget__.removeItem(graphic)

            # Create new new graphic items
            self.signals[signal_name].create_graphics(tdata)

            # Get new created graphic item and paint them
            graphics = self.signals[signal_name].get_graphics()
            for graphic in graphics:
                self.__plotWidget__.addItem(graphic)

                # Set positon for vertical line
                if self.__rolling_plot__:
                    self.__vertical_line__.setValue(graphic.last_x)

        self.__last_plot_time__ = pg.ptime.time()-now

        if self.__rolling_plot__:
            self.__plotWidget__.getPlotItem().getViewBox().setXRange(0, len(tdata)-1)
        else:
            self.__plotWidget__.getPlotItem().getViewBox().setXRange(tdata[0], tdata[-1])

        # if self.__papi_debug__:
        #     print("Plot time: %0.5f sec" % (self.__last_plot_time__) )

    def update_plot_single_timestamp(self, data):
        """
        Function update_plot_single_timestamp

        :return:
        """

        self.__text_item__.setText("Time " + str(data['t'][0]), color=(200, 200, 200))
        self.__plotWidget__.clear()
        for signal_name in data:
            if signal_name != 't':
                signal_data = data[signal_name]
                if signal_name in self.signals:
                    pass
                    tdata = np.linspace(1, len(signal_data), len(signal_data))

                    plot_item = self.signals[signal_name]

                    graphic = GraphicItem(np.array(tdata), np.array(signal_data), 0, pen=plot_item.pen)

                    self.__plotWidget__.addItem(graphic)
                    #curve = self.signals[signal_name]['curve']
                    #curve.setData(tdata, signal_data, _callSync='off')

        pass

    def update_buffer_size(self, new_size):
        """
        Function set buffer size

        :param new_size:
        :return:
        """

        self.__buffer_size__ = int(new_size)

        # -------------------------------
        # Change Time Buffer
        # -------------------------------

#        self.__tbuffer__ = collections.deque([0.0] * 0, self.__buffer_size__)

        # -------------------------------
        # Change Buffer of current
        # plotted signals
        # -------------------------------

        start_size = len(self.__tbuffer__)

        for signal_name in self.signals:
            self.__tbuffer__ = collections.deque([0.0] * start_size, self.__buffer_size__)  # COLLECTION

            plot_item = self.signals[signal_name]
            plot_item.max_elements = self.__buffer_size__
            plot_item.clear()
            self.__plotWidget__.clear()

        self.update_rolling_plot()

        self.__new_added_data__ = 0

    def plugin_meta_updated(self):
        """
        By this function the plot is able to handle more than one input for plotting.

        :return:
        """

        subscriptions = self.dplugin_info.get_subscribtions()
        changes = False
        current_signals = {}
        index = 0

        for dpluginsub_id in subscriptions:
            for dblock_name in subscriptions[dpluginsub_id]:

                # get subscription for dblock
                subscription = subscriptions[dpluginsub_id][dblock_name]

                for signal_name in subscription.get_signals():

                    signal = subscription.get_dblock().get_signal_by_uname(signal_name)
                    index += 1
                    current_signals[signal_name] = {}
                    current_signals[signal_name]['signal'] = signal
                    current_signals[signal_name]['index'] = index

                # current_signals = sorted(current_signals)

        # Add missing buffers
        for signal_name in sorted(current_signals.keys()):
            if signal_name not in self.signals:
                signal = current_signals[signal_name]['signal']
                self.add_plot_item(signal, current_signals[signal_name]['index'])
                changes = True

        # Delete old buffers
        for signal_name in self.signals.copy():
            if signal_name not in current_signals:
                self.remove_plot_item(signal_name)
                changes = True

        if changes:
            self.update_pens()
            self.update_legend()
            self.update_rolling_plot()
            self.update_downsampling_rate()

    def add_plot_item(self, signal, signal_id):
        """
        Create a new plot item object for a given signal and internal id

        :param signal: DSignal object
        :param signal_id: plot internal signal id
        :return:
        """

        signal_name = signal.uname

        if signal_name not in self.signals:
            self.signals[signal_name] = {}

            plot_item = PlotItem(signal, signal_id, self.__buffer_size__)
            plot_item.set_downsampling_rate(self.__downsampling_rate__)

            self.signals[signal_name] = plot_item


    def remove_plot_item(self, signal_name):
        """
        Remove the plot item object for a given signal_name.

        :param signal_name:
        :return:
        """

        if signal_name in self.signals:
            plot_item = self.signals[signal_name]

            # Remove all graphic objects

            for graphic in plot_item.graphics:
                self.__plotWidget__.removeItem(graphic)

            # Remove from Legend
            self.__legend__.removeItem(plot_item.signal_name)
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

    def update_rolling_plot(self):

        value = self.config['rolling_plot']['value']

        self.__rolling_plot__ = int(float(self.config['rolling_plot']['value'])) == int('1')

        self.rolling_Checkbox.setChecked(value == '1')

        self.clear()

        for signal_name in self.signals:
            self.signals[signal_name].rolling_plot = self.__rolling_plot__

        if self.__rolling_plot__:
            # if self.__vertical_line__ not in self.__plotWidget__.listDataItems():

            self.__plotWidget__.addItem(self.__vertical_line__)


    def use_range_for_x(self, value):
        """

        :param value:
        :return:
        """
        reg = re.compile(r'(\d+\.\d+)')
        range = reg.findall(value)
        if len(range) == 2:
            #self.xRange_minEdit.setText(range[0])
            #self.xRange_maxEdit.setText(range[1])
            self.__plotWidget__.getPlotItem().getViewBox().setXRange(float(range[0]),float(range[1]))

    def use_range_for_y(self, value):
        """

        :param value:
        :return:
        """
        reg = re.compile(r'([-]{0,1}\d+\.\d+)')
        range = reg.findall(value)
        if len(range) == 2:
            self.yRange_minEdit.setText(range[0])
            self.yRange_maxEdit.setText(range[1])
            self.__plotWidget__.getPlotItem().getViewBox().setYRange(float(range[0]), float(range[1]))


    def setup_context_menu(self):
        """

        :return:
        """
        self.custMenu = QtGui.QMenu("Options")
        self.axesMenu = QtGui.QMenu('Y-Axis')
        self.gridMenu = QtGui.QMenu('Grid')


        # ---------------------------------------------------------
        # #### X-Range Actions
        #self.xRange_Widget = QtGui.QWidget()
        #self.xRange_Layout = QtGui.QVBoxLayout(self.xRange_Widget)
        #self.xRange_Layout.setContentsMargins(2, 2, 2, 2)
        #self.xRange_Layout.setSpacing(1)


        ##### X Line Edits
        # Layout
        #self.xRange_EditWidget = QtGui.QWidget()
        #self.xRange_EditLayout = QtGui.QHBoxLayout(self.xRange_EditWidget)
        #self.xRange_EditLayout.setContentsMargins(2, 2, 2, 2)
        #self.xRange_EditLayout.setSpacing(1)

        # get old values;
        #reg = re.compile(r'(\d+\.\d+)')
        #range = reg.findall(self.config['xRange']['value'])
        #if len(range) == 2:
        #    x_min = range[0]
        #    x_max = range[1]
        #else:
        #    x_min = '0.0'
        #    x_max = '1.0'


        # Min
        # self.xRange_minEdit = QtGui.QLineEdit()
        # self.xRange_minEdit.setFixedWidth(80)
        # self.xRange_minEdit.setText(x_min)
        # self.xRange_minEdit.editingFinished.connect(self.contextMenu_xRange_toogle)
        # # Max
        # self.xRange_maxEdit = QtGui.QLineEdit()
        # self.xRange_maxEdit.setFixedWidth(80)
        # self.xRange_maxEdit.setText(x_max)
        # self.xRange_maxEdit.editingFinished.connect(self.contextMenu_xRange_toogle)
        # # addTo Layout
        # self.xRange_EditLayout.addWidget(self.xRange_minEdit)
        # self.xRange_EditLayout.addWidget(QtGui.QLabel('<'))
        # self.xRange_EditLayout.addWidget(self.xRange_maxEdit)
        # self.xRange_Layout.addWidget(self.xRange_EditWidget)
        #
        # # build Action
        # self.xRange_Action = QtGui.QWidgetAction(self.__plotWidget__)
        # self.xRange_Action.setDefaultWidget(self.xRange_Widget)


        # ---------------------------------------------------------------
        ##### Y-Range Actions
        self.yRange_Widget = QtGui.QWidget()
        self.yRange_Layout = QtGui.QVBoxLayout(self.yRange_Widget)
        self.yRange_Layout.setContentsMargins(2, 2, 2, 2)
        self.yRange_Layout.setSpacing(1)

        self.yAutoRangeButton = QtGui.QPushButton()
        self.yAutoRangeButton.clicked.connect(self.contextMenu_yAutoRangeButton_clicked)
        self.yAutoRangeButton.setText('Set y range')
        self.yRange_Layout.addWidget(self.yAutoRangeButton)

        ##### Y Line Edits
        # Layout
        self.yRange_EditWidget = QtGui.QWidget()
        self.yRange_EditLayout = QtGui.QHBoxLayout(self.yRange_EditWidget)
        self.yRange_EditLayout.setContentsMargins(2, 2, 2, 2)
        self.yRange_EditLayout.setSpacing(1)

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

        # Min
        self.yRange_minEdit = QtGui.QLineEdit()
        self.yRange_minEdit.setFixedWidth(80)
        self.yRange_minEdit.setText(y_min)
        self.yRange_minEdit.editingFinished.connect(self.contextMenu_yRange_toogle)
        self.yRange_minEdit.setValidator(validator)
        # Max
        self.yRange_maxEdit = QtGui.QLineEdit()
        self.yRange_maxEdit.setFixedWidth(80)
        self.yRange_maxEdit.setText(y_max)
        self.yRange_maxEdit.editingFinished.connect(self.contextMenu_yRange_toogle)
        self.yRange_maxEdit.setValidator(validator)
        # addTo Layout
        self.yRange_EditLayout.addWidget(self.yRange_minEdit)
        self.yRange_EditLayout.addWidget(QtGui.QLabel('<'))
        self.yRange_EditLayout.addWidget(self.yRange_maxEdit)
        self.yRange_Layout.addWidget(self.yRange_EditWidget)

        # build Action
        self.yRange_Action = QtGui.QWidgetAction(self.__plotWidget__)
        self.yRange_Action.setDefaultWidget(self.yRange_Widget)

        ##### Rolling Plot
        self.rolling_Checkbox = QtGui.QCheckBox()
        self.rolling_Checkbox.setText('Rolling plot')
        self.rolling_Checkbox.setChecked(self.config['rolling_plot']['value'] == '1')
        self.rolling_Checkbox.stateChanged.connect(self.contextMenu_rolling_toogled)
        self.rolling_Checkbox_Action = QtGui.QWidgetAction(self.__plotWidget__)
        self.rolling_Checkbox_Action.setDefaultWidget(self.rolling_Checkbox)



        ##### Build axes menu
        #self.axesMenu.addAction(self.xRange_Action)
        self.axesMenu.addSeparator().setText("Y-Range")
        self.axesMenu.addAction(self.yRange_Action)

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
        self.custMenu.addMenu(self.axesMenu)
        self.custMenu.addMenu(self.gridMenu)
        self.custMenu.addSeparator().setText("Rolling Plot")
        self.custMenu.addAction(self.rolling_Checkbox_Action)
        self.__plotWidget__.getPlotItem().getViewBox().menu.clear()

        if not self.__papi_debug__:
            self.__plotWidget__.getPlotItem().ctrlMenu = [self.create_control_context_menu(), self.custMenu]

    def contextMenu_yAutoRangeButton_clicked(self):
        mi = None
        ma = None
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

        ma = str(ma)
        mi = str(mi)
        self.yRange_maxEdit.setText(ma)
        self.yRange_minEdit.setText(mi)
        self.control_api.do_set_parameter(self.__id__, 'yRange', '[' + mi + ' ' + ma + ']')

    def contextMenu_rolling_toogled(self):
        if self.rolling_Checkbox.isChecked():
            self.control_api.do_set_parameter(self.__id__, 'rolling', '1')
        else:
            self.control_api.do_set_parameter(self.__id__, 'rolling', '0')

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
            self.control_api.do_set_parameter(self.__id__, 'yRange', '[' + mi + ' ' + ma + ']')

    def update_signals(self):
        subscriptions = self.dplugin_info.get_subscribtions()

        for dpluginsub_id in subscriptions:
            for dblock_name in subscriptions[dpluginsub_id]:

                # get subscription for dblock
                subscription = subscriptions[dpluginsub_id][dblock_name]

                for signal_name in subscription.get_signals():
                    signal = subscription.get_dblock().get_signal_by_uname(signal_name)

                    self.signals[signal_name].update_signal(signal)

    def update_legend(self):
        # self.__plotWidget__.removeItem(self.__legend__)
        self.__legend__.scene().removeItem(self.__legend__)
        del self.__legend__

        self.__legend__ = pq.LegendItem((100, 40), offset=(40, 1))  # args are (size, offset)
        self.__legend__.setParentItem(self.__plotWidget__.graphicsItem())

        if not self.__papi_debug__:
            self.update_signals()

        for signal_name in sorted(self.signals.keys()):

            graphic = self.signals[signal_name].get_legend_item()

            if graphic is not None:
                signal = self.signals[signal_name].signal
                legend_name = signal.dname

                self.__legend__.addItem(graphic, legend_name)

    def update_downsampling_rate(self):
        rate = self.__downsampling_rate__

        self.downsampling_rate_start = 0
        self.downsampling_rate = rate

        for signal_name in self.signals:
            self.signals[signal_name].set_downsampling_rate(rate)

    def quit(self):
        """
        Function quit plugin

        :return:
        """
        print('PlotPerformance: will quit')

    def debug_papi(self):
        config = self.get_plugin_configuration()

        config['yRange'] =  {
            'value': '[0.0 50.0]',
            'regex': '(\d+\.\d+)',
            'advanced': '1',
            'display_text': 'y: range'
        }
        config['buffersize'] =  {
            'value': '1000',
            'regex': '(\d+\.\d+)',
            'advanced': '1',
            'display_text': 'y: range'
        }
        config['downsampling_rate'] =  {
            'value': '10',
            'regex': '(\d+\.\d+)',
            'advanced': '1',
            'display_text': 'y: range'
        }

        self.config = config
        self.__id__ = 0
        self.initiate_layer_0(config)

        signal_1 = DSignal('signal_1')
        signal_2 = DSignal('signal_2')
        signal_3 = DSignal('signal_3')
        signal_4 = DSignal('signal_4')
        signal_5 = DSignal('signal_5')

        self.add_plot_item(signal_1, 1)
        self.add_plot_item(signal_2, 2)
        self.add_plot_item(signal_3, 3)
        self.add_plot_item(signal_4, 4)
        self.add_plot_item(signal_5, 5)

        self.update_pens()
        self.update_legend()

        pass

    def get_plugin_configuration(self):
        """
        Function get plugin configuration

        :return {}:
        """
        config = {
        #     'label_y': {
        #         'value': "amplitude, V",
        #         'regex': '\w+,\s+\w+',
        #         'display_text': 'Label-Y'
        #     }, 'label_x': {
        #     'value': "time, s",
        #     'regex': '\w+,\s*\w+',
        #     'display_text': 'Label-X'
        # },
        'x-grid': {
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
            'value': "100",
            'regex': '^(\d+)$',
            'advanced': '1',
            'display_text': 'Buffersize'
        }, 'downsampling_rate': {
            'value': "1",
            'regex': '(\d+)'
        }, 'rolling_plot': {
            'value': '0',
            'regex': '^(1|0)$',
            'type': 'bool',
            'display_text': 'Rolling Plot'
        # }, 'xRange': {
        #     'value': '[0.0 1.0]',
        #     'regex': '(\d+\.\d+)',
        #     'advanced': '1',
        #     'display_text': 'x: range'
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
        self.__tbuffer__.clear()

        for signal_name in self.signals:
            self.signals[signal_name].clear()

class GraphicItem(pg.QtGui.QGraphicsPathItem):
    """

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


class PlotItem(object):
    """
    This object is used to manage the graphic items for a single signal object.
    """

    def __init__(self, signal, signal_id, max_elements):
        """
        Initialized by setting a corresponding DSignal object and an internal signal_id

        :param signal: DSignal object
        :param signal_id: Plot internal ID
        :return:
        """
        super(PlotItem,self).__init__()
        self.signal_name = signal.dname

        #self.buffer = [] # buffer

        self.buffer = collections.deque([0.0] * 0, max_elements)

        self.id = signal_id
        self.signal = signal

        self.amount_elements = 0

        self.downsampling_rate_start = None;
        self.downsampling_rate = None

        self.max_elements = max_elements

        self.pen = None
        self.graphics = []
        self.rolling_plot = None
        self.last_x = None
        self.last_y = None
        self.new_added_element = 0

    def get_legend_item(self):
        """
        Returns an item for a legend with the correct pen style

        :return:
        """

        data_item = pg.PlotDataItem()
        data_item.setPen(self.pen)
        return data_item

    def add_data(self, elements):
        """

        :param elements:
        :param tdata:
        :return:
        """

        buffer = self.buffer

        # TODO: Downsampling before extending the internal buffer


        # if self.downsampling_rate_start >= len(elements):
        #     self.downsampling_rate_start -= len(elements)
        # else:
        #
        #     # print('AddData')
        #     # print('Start ' + str(self.downsampling_rate_start))
        #     # print('Rate ' + str(self.downsampling_rate))
        #     # print('Len ' + str(len(elements)))
        #
        #     ds_elements = elements[self.downsampling_rate_start::self.downsampling_rate]
        #     self.downsampling_rate_start += self.downsampling_rate - len(ds_elements)
        #     # print(elements)
        #     # print(ds_elements)
        #     buffer.extend(ds_elements)

        self.new_added_element += len(elements)

        # if self.downsampling_rate_start < len(elements):
        #     ds_elements = elements[self.downsampling_rate_start:self.downsampling_rate:]
        #
        #     if self.downsampling_rate > len(elements):
        #         self.downsampling_rate_start = self.downsampling_rate - len(elements)
        # else:
        #     self.downsampling_rate_start -= len(elements)

        buffer.extend(elements)

    def update_signal(self, new_signal):
        """

        :param new_signal:
        :return:
        """

        self.signal = new_signal
        self.signal_name = new_signal.dname

    def set_downsampling_rate(self, rate):
        """

        :param rate:
        :return:
        """
        self.downsampling_rate = rate

        self.downsampling_rate_start = 0

    def create_graphics(self, xdata):
        """

        :param xdata:
        :return:
        """

        self.new_added_element = 0

        # get amount of elements in our buffer
        counter = len(self.buffer)

        if not counter > 0:
            return

        self.amount_elements += counter

        # shift_data = 0
        # if self.last_x is not None:
        #     if self.last_x in xdata:
        #         shift_data = list(xdata).index(self.last_x)
        #
        #     print(shift_data)



        #xdata = xdata[::self.downsampling_rate]
        amount_elements = len(xdata)

        self.last_x = xdata[0]
        # print( "Len Buffer " + str(len(self.buffer)))
        # print( "TData" + str(len(tdata)))

        x_axis = np.array(xdata)
        y_axis = np.array(list(self.buffer))

        # print( "Len Buffer " + str(len(x_axis)))
        # print( "TData" + str(len(y_axis)))
        #

        # # Old Solution
        # if False:
        #
        #     if self.rolling_plot:
        #         #print('I keep it rolling')
        #
        #         i_max = np.argmax(x_axis)
        #         i_min = np.argmin(x_axis)
        #
        #         # Create two graphic objects due plot border
        #         if i_min > i_max:
        #             x_axis_1 = np.array(x_axis[:i_max+1])
        #             x_axis_2 = np.array(x_axis[i_min:])
        #
        #             y_axis_1 = y_axis[:i_max+1]
        #             y_axis_2 = y_axis[i_min:]
        #
        #             if len(self.graphics):
        #                 prev_graphic = self.graphics[-1]
        #                 prev_last_x = prev_graphic.last_x;
        #                 prev_last_y = prev_graphic.last_y;
        #
        #                 x_axis_1 = np.insert(x_axis_1, 0, prev_last_x)
        #                 y_axis_1 = np.insert(y_axis_1, 0, prev_last_y)
        #
        #             graphic_1 = GraphicItem(x_axis_1, y_axis_1, len(y_axis_1) - 1, self.pen)
        #             graphic_2 = GraphicItem(x_axis_2, y_axis_2, len(y_axis_2), self.pen)
        #
        #             self.graphics.append(graphic_1)
        #             self.graphics.append(graphic_2)
        #
        #             del self.buffer
        #             self.buffer = []
        #
        #             return
        #     # Connect with previous graphic if a previous graphic exists
        #
        #     if len(self.graphics):
        #         prev_graphic = self.graphics[-1]
        #         prev_last_x = prev_graphic.last_x;
        #         prev_last_y = prev_graphic.last_y;
        #
        #         if prev_last_x < x_axis[0]:
        #             x_axis = np.insert(x_axis, 0, prev_last_x)
        #             y_axis = np.insert(y_axis, 0, prev_last_y)
        #
        #     graphic = GraphicItem(x_axis, y_axis, counter, pen=self.pen)
        #
        #     del self.buffer
        #     self.buffer = []
        #
        #     self.graphics.append(graphic)

        if self.rolling_plot:
            #print('First X_Value' + str(xdata))

            i_max = np.argmax(x_axis)
            i_min = np.argmin(x_axis)

            x_axis_1 = np.array(x_axis[:i_max+1])
            x_axis_2 = np.array(x_axis[i_min:])

            y_axis_1 = y_axis[:i_max+1]
            y_axis_2 = y_axis[i_min:]

            graphic_1 = GraphicItem(x_axis_1, y_axis_1, len(y_axis_1) - 1, self.pen)
            graphic_2 = GraphicItem(x_axis_2, y_axis_2, len(y_axis_2), self.pen)

            self.graphics.append(graphic_1)
            self.graphics.append(graphic_2)

            return

        graphic = GraphicItem(x_axis, y_axis, counter, pen=self.pen)
        self.graphics.append(graphic)

    def get_graphics(self):
        """

        :return:
        """
        res_graphics = []

        for graphic in self.graphics:

            if graphic.not_drawn:
                res_graphics.append(graphic)
                graphic.not_drawn = False

        return res_graphics

    def get_old_graphics(self):
        """

        :return:
        """



        res_graphic = []


        # if len(self.graphics):
        #     res_graphic.append(self.graphics.pop(0))

        for i in range(len(self.graphics)):
            graphic = self.graphics[0]

            if graphic.not_drawn:
                break

            graphic = self.graphics.pop(0)

            res_graphic.append(graphic)

        return res_graphic

        # # print(self.amount_elements)
        # # print(len(self.graphics))
        #
        # while self.amount_elements >= self.max_elements:
        #
        #     graphic = self.graphics[0]
        #
        #     if graphic.not_drawn:
        #         break
        #
        #     graphic = self.graphics.pop(0)
        #     self.amount_elements -= graphic.length()
        #
        #     res_graphic.append(graphic)
        #
        # return res_graphic

    def clear(self):
        """

        :return:
        """
        self.graphics = []
        self.downsampling_rate_start = 0
        self.buffer = collections.deque([0.0] * 0, self.max_elements)
        self.amount_elements = 0

    def get_new_added_since_last_drawing(self):
        return self.new_added_element

    def get_buffersize(self):
        """

        :return:
        """

        if len(self.buffer) < self.max_elements:
            return len(self.buffer)
        else:
            return self.max_elements

class PlotWidget(pg.PlotWidget):

    def __init__(self):
        super(PlotWidget, self).__init__()
        self.paint = True

    def enablePainting(self):
        self.paint = True

    def disablePainting(self):
        self.paint = False

    # def refreshPlot(self):
    #     self.enablePainting()
    #     super(PlotWidget, self).repaint()
    #     self.disablePainting()

    def paintEvent(self, ev):
        if self.paint:
            self.scene().prepareForPaint()
        return QtGui.QGraphicsView.paintEvent(self, ev)
#        if self.paint:
#        print('REPAINT !!')
 #       super(PlotWidget, self).paintEvent(ev)

