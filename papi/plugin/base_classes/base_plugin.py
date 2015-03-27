#!/usr/bin/python3
#-*- coding: utf-8 -*-

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
Stefan Ruppin
"""

from papi.data.DPlugin import DBlock
import papi.event as Event
from papi.exceptions.block_exceptions import Wrong_type, Wrong_length
from papi.data.DOptionalData import DOptionalData
from papi.yapsy.IPlugin import IPlugin


class base_plugin(IPlugin):


    def papi_init(self, ):
        #self.__dplugin_ids__    = {} Not sure where needed TODO
        self.dplugin_info       = None
        self.__subscription_for_demux = None



    def get_type(self):
        raise NotImplementedError("Please Implement this method")

    def execute(self, Data=None, block_name = None):
        raise NotImplementedError("Please Implement this method")

    def get_configuration_base(self):
        raise NotImplementedError("Please Implement this method")

    def get_startup_configuration(self):
        return self.merge_configs(self.get_configuration_base(), self.get_plugin_configuration())

    def get_plugin_configuration(self):
        raise NotImplementedError("Please Implement this method")





    # some control callback functions
    # ----------------------
    def pause(self):
        raise NotImplementedError("Please Implement this method")

    def resume(self):
        raise NotImplementedError("Please Implement this method")

    def quit(self):
        raise NotImplementedError("Please Implement this method")

    def set_parameter(self, parameter_name, parameter_value):
        raise NotImplementedError("Please Implement this method")

    def set_parameter_internal(self, name, value):
        self.set_parameter(name, value)


    # some api functions
    # ------------------
    def merge_configs(self, cfg1, cfg2):
        return dict(list(cfg1.items()) + list(cfg2.items()) )


    def send_parameter_change(self, data, block_name):
        opt = DOptionalData(DATA=data)
        opt.data_source_id = self.__id__
        opt.is_parameter = True
        opt.block_name = block_name
        event = Event.data.NewData(self.__id__, 0, opt)
        self._Core_event_queue__.put(event)

    def create_new_block(self, name, signalNames, types, frequency):
        if isinstance(signalNames, list) is not True:
            raise Wrong_type('signalNames')

        if isinstance(types, list) is not True:
            raise Wrong_type('types')

        if len(signalNames) != len(types):
            raise Wrong_length('signalNames', 'types')

        count = len(signalNames)

        return DBlock(self.__id__, count, frequency, name, signal_names_internal=signalNames, signal_types=types )

    def send_new_data(self, block_name, time_line, data):

        dataHash = data
        dataHash['t'] = time_line
        opt = DOptionalData(DATA = dataHash)
        opt.data_source_id = self.__id__
        opt.block_name = block_name

        event = Event.data.NewData(self.__id__, 0, opt)
        self._Core_event_queue__.put(event)


    def send_new_data_old2(self, time_line, data, block_name):
        # TODO: known limitation, signal count of data+timeline HAVE TO match len of names defined in DBlock of block_name
        vec_data = []
        vec_data.append(time_line)
        for item in data:
            vec_data.append(item)

        opt = DOptionalData(DATA=vec_data)
        opt.data_source_id = self.__id__
        opt.block_name = block_name

        event = Event.data.NewData(self.__id__, 0, opt)
        self._Core_event_queue__.put(event)

    def send_new_data_old1(self, data, block_name):
        opt = DOptionalData(DATA=data)
        opt.data_source_id = self.__id__
        opt.block_name = block_name

        event = Event.data.NewData(self.__id__, 0, opt)
        self._Core_event_queue__.put(event)

    def send_new_block_list(self, blocks):
        opt = DOptionalData()
        opt.block_list = blocks
        event = Event.data.NewBlock(self.__id__, 0, opt)
        self._Core_event_queue__.put(event)

    def send_new_parameter_list(self, parameters):
        opt = DOptionalData()
        opt.parameter_list = parameters

        event = Event.data.NewParameter(self.__id__, 0, opt)
        self._Core_event_queue__.put(event)

    def send_delete_block(self, blockname):
        event = Event.data.DeleteBlock(self.__id__, 0, blockname)
        self._Core_event_queue__.put(event)

    def send_delete_parameter(self, parameterName):
        event = Event.data.DeleteParameter(self.__id__, 0, parameterName)
        self._Core_event_queue__.put(event)

    def update_plugin_meta(self, dplug):
        self.dplugin_info = dplug
        self.__subscription_for_demux = self.dplugin_info.get_subscribtions()
        self.plugin_meta_updated()

    def plugin_meta_updated(self):
        raise NotImplementedError("Please Implement this method")

    def demux(self, source_id, block_name, data):
        if self.__subscription_for_demux is None:
           self.__subscription_for_demux = self.dplugin_info.get_subscribtions()

        sub_object = self.__subscription_for_demux[source_id][block_name]
        sub_signals = sub_object.signals
        if 't' not in sub_signals:
            sub_signals.append('t')

        return dict([(i, data[i]) for i in sub_signals if i in data])
