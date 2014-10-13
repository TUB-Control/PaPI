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

from abc import ABCMeta, abstractmethod
import os

from yapsy.IPlugin import IPlugin

from papi.PapiEvent import PapiEvent
from papi.data.DOptionalData import DOptionalData
from papi.data.DParameter import DParameter
from papi.data.DPlugin import DPlugin,DBlock



class plugin_base(IPlugin):

    __metaclass__= ABCMeta

    def __init_(self, CoreQueue, pluginQueue, id):
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        #self.__dplugin_ids__ = {}

    def papi_init(self):
        self.__dplugin_ids__ = {}
        self.dplugin_info = None

    def work_process(self, CoreQueue, pluginQueue, id, defaultEventTriggered=False, config=None):
        print("Plugin work_process called")
        # set queues and id
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        self.EventTriggered = defaultEventTriggered
        self.user_event_triggered = 'default'
        self.paused = False

        self.papi_init()

        # working should go at least one time
        self.goOn = 1

        # call start_init function to use developers init
        if self.start_init(config):
            # report start successfull event
            event = PapiEvent(self.__id__,0,'status_event','start_successfull',None)
            self._Core_event_queue__.put(event)
        else:
            # init failed, so report it to core
            event = PapiEvent(self.__id__,0,'status_event','start_failed',None)
            self._Core_event_queue__.put(event)
            # end plugin
            self.goOn = 0
            # sent join request to core
            event = PapiEvent(self.__id__,0,'status_event','join_request',None)
            self._Core_event_queue__.put(event)

        # main working loop
        while self.goOn:
            self.evaluate_event_trigger(defaultEventTriggered)
            try:
                event = self.__plugin_queue__.get( self.paused or self.EventTriggered)
                #process event
                op = event.get_event_operation()
                if (op=='stop_plugin'):
                    self.quit()
                    self.goOn = 0
                    event = PapiEvent(self.__id__,0,'status_event','join_request',None)
                    self._Core_event_queue__.put(event)
                if op=='pause_plugin':
                    self.paused = True
                    self.pause()
                if op=='resume_plugin':
                    self.paused = False
                    self.resume()
                if op=='check_alive_status':
                    alive_event = PapiEvent(self.__id__,0,'status_event','alive',None)
                    self._Core_event_queue__.put(alive_event)
                if op=='new_data' and self.paused is not True:
                    opt = event.get_optional_parameter()
                    if opt.is_parameter is False:
                        data = self.demux(opt.data_source_id, opt.block_name, opt.data)
                        self.execute(data)
                    if opt.is_parameter is True:
                        self.set_parameter_internal(opt.parameter_alias, opt.data)
                if op == 'set_parameter':
                    opt = event.get_optional_parameter()
                    self.set_parameter_internal(opt.parameter_alias, opt.data)

                if op == 'update_meta':
                    opt = event.get_optional_parameter()
                    self.update_plugin_meta(opt.plugin_object)
            except:
                self.execute()

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

    def send_new_data(self, data, block_name):
        opt = DOptionalData(DATA=data)
        opt.data_source_id = self.__id__
        opt.block_name = block_name
        event = PapiEvent(self.__id__, 0, 'data_event', 'new_data', opt)
        self._Core_event_queue__.put(event)

    def send_parameter_change(self, data, block_name, alias):
        opt = DOptionalData(DATA=data)
        opt.data_source_id = self.__id__
        opt.is_parameter = True
        opt.block_name = block_name
        opt.parameter_alias = alias
        event = PapiEvent(self.__id__, 0, 'data_event', 'new_data', opt)
        self._Core_event_queue__.put(event)

    def send_new_block_list(self, blocks):
        opt = DOptionalData()
        opt.block_list = blocks
        event = PapiEvent(self.__id__,0,'data_event','new_block',opt)
        self._Core_event_queue__.put(event)

    def send_new_parameter_list(self, parameters):
        opt = DOptionalData()
        opt.parameter_list = parameters

        event = PapiEvent(self.__id__,0,'data_event','new_parameter',opt)
        self._Core_event_queue__.put(event)

    def update_plugin_meta(self, dplug):
        self.dplugin_info = dplug

        if hasattr(self, 'hook_update_plugin_meta'):
            self.hook_update_plugin_meta()

    def demux(self, source_id, block_name, data):

        returnData = {}

        subcribtions = self.dplugin_info.get_subscribtions()
        dblocksub = subcribtions[source_id][block_name]
        if dblocksub.signals == []:
            sig_range = range(0, len(dblocksub.dblock.signal_names_internal))
        else:
            sig_range = dblocksub.signals

        for ind in sig_range:
            returnData[dblocksub.dblock.signal_names_internal[ind]] = data[ind]

        returnData['t'] = data[0]

        return returnData

    def set_parameter_internal(self, name, value):
        self.set_parameter(name, value)

    @abstractmethod
    def start_init(self, config=None):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def pause(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def resume(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def execute(self, Data=None):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def set_parameter(self, parameter):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def quit(self):
        raise NotImplementedError("Please Implement this method")

    def get_startup_configuration(self):
        """
        OnlineRegexTester: http://regexpal.com/
        :return:
        """
        config = {}
        return config

    @abstractmethod
    def get_type(self):
        raise NotImplementedError("Please Implement this method")