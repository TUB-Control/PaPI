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

from yapsy.IPlugin import IPlugin
from papi.data.DPlugin import DBlock
import papi.event as Event
from papi.exceptions.block_exceptions import Wrong_type, Wrong_length
from papi.data.DOptionalData import DOptionalData



class base_plugin(IPlugin):


    def papi_init(self):
        #self.__dplugin_ids__    = {} Not sure where needed TODO
        self.dplugin_info       = None




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

    def set_parameter_internal(self, name, value):
        self.set_parameter(name, value)


    # some api functions
    # ------------------
    def merge_configs(self, cfg1, cfg2):
        return dict(list(cfg1.items()) + list(cfg2.items()) )

    def evaluate_event_trigger(self,default):
        if self.user_event_triggered == 'default':
            self.EventTriggered = default
        if self.user_event_triggered is True:
            self.EventTriggered = True
        if self.user_event_triggered is False:
            self.EventTriggered = False

    def set_event_trigger_mode(self, mode):
        if mode is True or mode is False or mode == 'default':
            self.user_event_triggered = mode


    def send_parameter_change(self, data, block_name, alias):
        opt = DOptionalData(DATA=data)
        opt.data_source_id = self.__id__
        opt.is_parameter = True
        opt.block_name = block_name
        opt.parameter_alias = alias
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

    def update_plugin_meta(self, dplug):
        self.dplugin_info = dplug

        self.plugin_meta_updated()

    def plugin_meta_updated(self):
        raise NotImplementedError("Please Implement this method")

    def demux(self, source_id, block_name, data):

        subcribtions = self.dplugin_info.get_subscribtions()
        sub_object = subcribtions[source_id][block_name]

        sub_signals = sub_object.signals

        returnData = {}
        returnData['t'] = data['t']
        for key in sub_signals:
            returnData[key] = data[key]

        return returnData

        # returnData = {}
        #
        # subcribtions = self.dplugin_info.get_subscribtions()
        # dblocksub = subcribtions[source_id][block_name]
        # if dblocksub.signals == []:
        #     sig_range = range(0, len(dblocksub.dblock.signal_names_internal))
        # else:
        #     sig_range = dblocksub.signals
        #
        # for ind in sig_range:
        #     returnData[dblocksub.dblock.signal_names_internal[ind]] = data[ind]
        #
        # returnData['t'] = data[0]

        #return returnData