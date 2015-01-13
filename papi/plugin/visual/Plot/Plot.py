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
import numpy as np
import collections
import re
import time

current_milli_time = lambda: int(round(time.time() * 1000))

from papi.pyqtgraph.Qt import QtCore, QtGui


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

        #
        if self.config['xRange-auto']['value']=='1':
            pass
        else:
            self.use_range_for_x(self.config['xRange']['value'])

        if self.config['yRange-auto']['value']== '1':
            pass
        else:
            self.use_range_for_y(self.config['yRange']['value'])

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

        self.__parameters__['xRange-auto'] = DParameter('xRange-auto', '1',  Regex='^(1|0){1}$')
        self.__parameters__['xRange'] = DParameter('xRange', '[0,1]', Regex='(\d+\.\d+)')
        self.__parameters__['yRange-auto'] = DParameter('yRange-auto', '1',  Regex='^(1|0){1}$')
        self.__parameters__['yRange'] = DParameter('yRange', '[0,1]',  Regex='(\d+\.\d+)')

        self.send_new_parameter_list(list(self.__parameters__.values()))

        # ---------------------------
        # Create Legend
        # ---------------------------

        self.__legend__ = pq.LegendItem((100, 40), offset=(40, 1))  # args are (size, offset)
        self.__legend__.setParentItem(self.__plotWidget__.graphicsItem())

        self.__last_time__ = current_milli_time()

        self.__update_intervall__ = 25  # in milliseconds

        self.setup_context_menu()

                #
        if self.config['xRange-auto']['value']=='1':
            pass
        else:
            self.use_range_for_x(self.config['xRange']['value'])

        if self.config['yRange-auto']['value']== '1':
            pass
        else:
            self.use_range_for_y(self.config['yRange']['value'])

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


        if name == 'rolling':
            self.__rolling_plot__ = int(float(value)) == int('1')
            self.config['rolling_plot']['value'] = value
            self.rolling_Checkbox.setChecked(value=='1')
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

        if name == 'xRange-auto':
            self.config['xRange-auto']['value'] = value
            self.xRange_AutoCheckbox.setChecked(value=='1')
            if int(value) == 1:
                self.xRange_minEdit.setDisabled(True)
                self.xRange_maxEdit.setDisabled(True)
                self.__plotWidget__.getPlotItem().getViewBox().menu.xAutoClicked()
            else:
                self.use_range_for_x(self.config['xRange']['value'])
                self.xRange_minEdit.setDisabled(False)
                self.xRange_maxEdit.setDisabled(False)

        if name == 'yRange-auto':
            self.config['yRange-auto']['value'] = value
            self.yRange_AutoCheckbox.setChecked(value=='1')
            if int(value) == 1:
                self.yRange_minEdit.setDisabled(True)
                self.yRange_maxEdit.setDisabled(True)
                self.__plotWidget__.getPlotItem().getViewBox().menu.yAutoClicked()
            else:
                self.yRange_minEdit.setDisabled(False)
                self.yRange_maxEdit.setDisabled(False)
                self.use_range_for_y(self.config['yRange']['value'])

        if name == 'xRange':
            self.config['xRange']['value'] = value
            if self.config['xRange-auto']['value'] == '0':
                self.use_range_for_x(value)

        if name == 'yRange':
            self.config['yRange']['value'] = value
            if self.config['yRange-auto']['value'] == '0':
                self.use_range_for_y(value)

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
                self.__vertical_line__.setValue(tdata[int(self.__append_at__) - 1])
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
            # buffer_new.extend(buffer_old)

            self.signals[signal_name]['buffer'] = buffer_new

        self.__new_added_data__ = 0

    def plugin_meta_updated(self):
        """
        By this function the plot is able to handle more than one input for plotting.

        :return:
        """
        subscriptions = self.dplugin_info.get_subscribtions()

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
                self.add_databuffer(signal, current_signals[signal_name]['index'])

        # Delete old buffers
        for signal_name in self.signals.copy():
            if signal_name not in current_signals:
                signal = self.signals[signal_name]['signal']
                self.remove_databuffer(signal)

        self.update_pens()
        self.update_legend()

    def add_databuffer(self, signal, signal_id):
        """
        Create new buffer for signal_name.

        :param signal_name:
        :param signal_id:
        :return:
        """

        signal_name = signal.uname

        if signal_name not in self.signals:
            self.signals[signal_name] = {}

            start_size = len(self.__tbuffer__)

            buffer = collections.deque([0.0] * start_size, self.__buffer_size__)  # COLLECTION

            curve = self.__plotWidget__.plot([0, 1], [0, 1])

            self.signals[signal_name]['buffer'] = buffer
            self.signals[signal_name]['curve'] = curve
            self.signals[signal_name]['id'] = signal_id
            self.signals[signal_name]['signal'] = signal


    def remove_databuffer(self, signal):
        """
        Remove the databuffer for signal_name.

        :param signal_name:
        :return:
        """

        signal_name = signal.uname

        if signal_name in self.signals:
            curve = self.signals[signal_name]['curve']
            curve.clear()
            # self.__legend__.removeItem(legend_name)
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

    def use_range_for_x(self, value):
        reg = re.compile(r'(\d+\.\d+)')
        range = reg.findall(value)
        if len(range) == 2:
            self.xRange_minEdit.setText(range[0])
            self.xRange_maxEdit.setText(range[1])
            self.__plotWidget__.getPlotItem().getViewBox().setXRange(float(range[0]),float(range[1]))

    def use_range_for_y(self, value):
        reg = re.compile(r'(\d+\.\d+)')
        range = reg.findall(value)
        if len(range) == 2:
            self.__plotWidget__.getPlotItem().getViewBox().setYRange(float(range[0]), float(range[1]))

    def setup_context_menu(self):
        self.custMenu = QtGui.QMenu("Options")
        self.axesMenu = QtGui.QMenu('Axes')
        self.gridMenu = QtGui.QMenu('Grid')


        # ---------------------------------------------------------
        # #### X-Range Actions
        self.xRange_Widget = QtGui.QWidget()
        self.xRange_Layout = QtGui.QVBoxLayout(self.xRange_Widget)
        self.xRange_Layout.setContentsMargins(2, 2, 2, 2)
        self.xRange_Layout.setSpacing(1)

        self.xRange_AutoCheckbox = QtGui.QCheckBox(checked= self.config['xRange-auto']['value'] == '1')
        self.xRange_AutoCheckbox.stateChanged.connect(self.contextMenu_xRange_toogle)
        self.xRange_AutoCheckbox.setText('X-Autorange')
        self.xRange_Layout.addWidget(self.xRange_AutoCheckbox)

        ##### X Line Edits
        # Layout
        self.xRange_EditWidget = QtGui.QWidget()
        self.xRange_EditLayout = QtGui.QHBoxLayout(self.xRange_EditWidget)
        self.xRange_EditLayout.setContentsMargins(2, 2, 2, 2)
        self.xRange_EditLayout.setSpacing(1)

        # get old values;
        reg = re.compile(r'(\d+\.\d+)')
        range = reg.findall(self.config['xRange']['value'])
        if len(range) == 2:
            x_min = range[0]
            x_max = range[1]
        else:
            x_min = '0.0'
            x_max = '1.0'


        # Min
        self.xRange_minEdit = QtGui.QLineEdit()
        self.xRange_minEdit.setFixedWidth(80)
        self.xRange_minEdit.setText(x_min)
        self.xRange_minEdit.editingFinished.connect(self.contextMenu_xRange_toogle)
        # Max
        self.xRange_maxEdit = QtGui.QLineEdit()
        self.xRange_maxEdit.setFixedWidth(80)
        self.xRange_maxEdit.setText(x_max)
        self.xRange_maxEdit.editingFinished.connect(self.contextMenu_xRange_toogle)
        # addTo Layout
        self.xRange_EditLayout.addWidget(self.xRange_minEdit)
        self.xRange_EditLayout.addWidget(QtGui.QLabel('<'))
        self.xRange_EditLayout.addWidget(self.xRange_maxEdit)
        self.xRange_Layout.addWidget(self.xRange_EditWidget)

        # build Action
        self.xRange_Action = QtGui.QWidgetAction(self.__plotWidget__)
        self.xRange_Action.setDefaultWidget(self.xRange_Widget)


        # ---------------------------------------------------------------
        ##### Y-Range Actions
        self.yRange_Widget = QtGui.QWidget()
        self.yRange_Layout = QtGui.QVBoxLayout(self.yRange_Widget)
        self.yRange_Layout.setContentsMargins(2, 2, 2, 2)
        self.yRange_Layout.setSpacing(1)

        self.yRange_AutoCheckbox = QtGui.QCheckBox(checked= self.config['xRange-auto']['value'] == '1')
        self.yRange_AutoCheckbox.stateChanged.connect(self.contextMenu_yRange_toogle)
        self.yRange_AutoCheckbox.setText('Y-Autorange')
        self.yRange_Layout.addWidget(self.yRange_AutoCheckbox)

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

        # Min
        self.yRange_minEdit = QtGui.QLineEdit()
        self.yRange_minEdit.setFixedWidth(80)
        self.yRange_minEdit.setText(y_min)
        self.yRange_minEdit.editingFinished.connect(self.contextMenu_yRange_toogle)

        # Max
        self.yRange_maxEdit = QtGui.QLineEdit()
        self.yRange_maxEdit.setFixedWidth(80)
        self.yRange_maxEdit.setText(y_max)
        self.yRange_maxEdit.editingFinished.connect(self.contextMenu_yRange_toogle)
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
        self.axesMenu.addAction(self.xRange_Action)
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
        self.__plotWidget__.getPlotItem().ctrlMenu = [self.create_control_context_menu(), self.custMenu]


        #self.__plotWidget__.getPlotItem().getViewBox()

    def range_changed(self):
        print('r')

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

    def contextMenu_xRange_toogle(self):
        if self.xRange_AutoCheckbox.isChecked():
            # do autorange
            self.control_api.do_set_parameter(self.__id__, 'xRange-auto', '1')
            self.xRange_minEdit.setDisabled(True)
            self.xRange_maxEdit.setDisabled(True)
        else:
            self.xRange_minEdit.setDisabled(False)
            self.xRange_maxEdit.setDisabled(False)
            mi = self.xRange_minEdit.text()
            ma = self.xRange_maxEdit.text()
            self.control_api.do_set_parameter(self.__id__, 'xRange-auto', '0')
            self.control_api.do_set_parameter(self.__id__, 'xRange', '[' + mi + ' ' + ma + ']')

    def contextMenu_yRange_toogle(self):
        if self.yRange_AutoCheckbox.isChecked():
            # do autorange
            self.control_api.do_set_parameter(self.__id__, 'yRange-auto', '1')
            self.yRange_minEdit.setDisabled(True)
            self.yRange_maxEdit.setDisabled(True)
        else:
            self.yRange_minEdit.setDisabled(False)
            self.yRange_maxEdit.setDisabled(False)
            # do man range
            mi = self.yRange_minEdit.text()
            ma = self.yRange_maxEdit.text()
            self.control_api.do_set_parameter(self.__id__, 'yRange-auto', '0')
            self.control_api.do_set_parameter(self.__id__, 'yRange', '[' + mi + ' ' + ma + ']')

    def update_signals(self):
        subscriptions = self.dplugin_info.get_subscribtions()

        for dpluginsub_id in subscriptions:
            for dblock_name in subscriptions[dpluginsub_id]:

                # get subscription for dblock
                subscription = subscriptions[dpluginsub_id][dblock_name]

                for signal_name in subscription.get_signals():
                    signal = subscription.get_dblock().get_signal_by_uname(signal_name)

                    self.signals[signal_name]['signal'] = signal

    def update_legend(self):
        # self.__plotWidget__.removeItem(self.__legend__)
        self.__legend__.scene().removeItem(self.__legend__)
        del self.__legend__

        self.__legend__ = pq.LegendItem((100, 40), offset=(40, 1))  # args are (size, offset)
        self.__legend__.setParentItem(self.__plotWidget__.graphicsItem())

        self.update_signals()

        for signal_name in sorted(self.signals.keys()):
            curve = self.signals[signal_name]['curve']
            signal = self.signals[signal_name]['signal']
            legend_name = signal.dname

            self.__legend__.addItem(curve, legend_name)

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
            'value': "1000",
            'regex': '^([1-9][0-9]{0,3}|10000)$',
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
        }, 'xRange-auto': {
            'value': '1',
            'regex': '^(1|0)$',
            'type': 'bool',
            'advanced': '1',
            'display_text': 'x: auto range'
        }, 'yRange-auto': {
            'value': '1',
            'regex': '^(1|0)$',
            'type': 'bool',
            'advanced': '1',
            'display_text': 'y: auto range'
        }, 'xRange': {
            'value': '[0.0 1.0]',
            'regex': '(\d+\.\d+)',
            'advanced': '1',
            'display_text': 'x: range'
        }, 'yRange': {
            'value': '[0.0 1.0]',
            'regex': '(\d+\.\d+)',
            'advanced': '1',
            'display_text': 'y: range'
        }
        }
        # http://www.regexr.com/
        return config