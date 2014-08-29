#!/usr/bin/python3
# -*- coding: latin-1 -*-

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

Contributors
Sven Knuth
"""

__author__ = 'knuths'

from papi.plugin.plugin_base import plugin_base
from PySide.QtGui import QMdiSubWindow
from abc import ABCMeta, abstractmethod
from papi.data.DParameter import DParameter
from papi.data.DOptionalData import DOptionalData
from papi.PapiEvent import PapiEvent


class pcb_base(plugin_base):

    _metaclass__= ABCMeta

    def start_init(self, config=None):

        default_config = self.get_default_config()


        if config is None:
            config = default_config

        if 'name' not in config:
            self.name=default_config['name']
        else:
            self.name=config['name']


        self._dplugin_id = config['dplugin_id']
        self._dparameter = config['dparameter']
        #
        self._callback_set_parameter = config['do_set_parameter']

        self._widget = self.create_widget()

        self._subWindow = QMdiSubWindow()
        self._subWindow.setWidget(self._widget)


    def get_default_config(self):
        config = {}
        config['name']="PCP_Plugin"
        return config

    def set_value(self, new_value):

        self._callback_set_parameter(self._dplugin_uname, self._dparameter.name, new_value)

    @abstractmethod
    def create_widget(self):
        """

        :return:
        :rtype QWidget:
        """
        return None

    def get_sub_window(self):
        """

        :return:
        :rtype QMdiSubWindow:
        """
        return self._subWindow

    def init_plugin(self,CoreQueue,pluginQueue,id):
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id

    def get_output_sizes(self):
        pass


    def pause(self):
        pass

    def resume(self):
        pass

    def execute(self,Data=None):
        pass

    def set_parameter(self,para_list):
        pass

    def quit(self):
        pass

    def get_type(self):
        return 'ViP'


    def send_paramter_change(self, pl_id, parameter_object, value):
        """

        :param pl_id:
        :param parameter_object:
        :param value:
        :type parameter_object: DParameter
        :return:
        """
        if parameter_object is not None:
            if self.check_range_of_value(value,parameter_object.range):
                parameter_object.value = value
                opt = DOptionalData()
                opt.parameter_list = [parameter_object]
                opt.plugin_id = pl_id
                e = PapiEvent(1,pl_id,'instr_event','set_parameter',opt)
                self._Core_event_queue__.put(e)
            else:
                return -1


    def check_range_of_value(self,value,range):
        min = range[0]
        max = range[1]
        if value > max:
            return False
        if value < min:
            return False
        return True


