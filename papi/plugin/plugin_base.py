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
        # add signal_choice_parameter:
        self.signal_choice = DParameter(None,'Signal_choice',[],None,1)
        self.send_new_parameter_list([self.signal_choice])

    def work_process(self, CoreQueue, pluginQueue, id, EventTriggered=False):
        print("Plugin work_process called")
        # set queues and id
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id

        self.papi_init()

        # working should go at least one time
        self.goOn = 1

        # call start_init function to use developers init
        if self.start_init():
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
            try:
                event = self.__plugin_queue__.get(EventTriggered)
                #process event
                op = event.get_event_operation()
                if (op=='stop_plugin'):
                    self.quit()
                    self.goOn = 0
                    event = PapiEvent(self.__id__,0,'status_event','join_request',None)
                    self._Core_event_queue__.put(event)
                if op=='pause_plugin':
                    self.pause()
                if op=='resume_plugin':
                    self.resume()
                if op=='check_alive_status':
                    alive_event = PapiEvent(self.__id__,0,'status_event','alive',None)
                    self._Core_event_queue__.put(alive_event)
                if op=='new_data':
                    opt = event.get_optional_parameter()
                    data = self.demux(opt.data_source_id, opt.block_name, opt.data)
                    self.execute(data)
                if op == 'update_meta':
                    opt = event.get_optional_parameter()
                    self.update_meta(opt.dblock_object)
                if op=='set_parameter':
                    opt = event.get_optional_parameter()
                    self.set_parameter(opt.parameter_list)
            except:
                self.execute()

    def send_new_data(self, data, block_name):
        opt = DOptionalData(DATA=data)
        opt.data_source_id = self.__id__
        opt.block_name = block_name
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

    def update_meta(self, dblock: DBlock):
        """
        A DBlock should be updated (or added unless it exists)
        :param dblock:
        :return:
        """
        dplugin_id = dblock.dplugin_id

        # Add hash for dplugin_id which is used to store DBlock names
        if dplugin_id not in self.__dplugin_ids__:
            self.__dplugin_ids__[dplugin_id] = {}

        # Update or add if necessary
        self.__dplugin_ids__[dplugin_id][dblock.name] = dblock

    def remove_meta(self, dblock: DBlock):
        """
        This function is used to remove the meta information for a specific DBlock.
        :param dblock:
        :return:
        :return Bool:
        """
        dplugin_id = dblock.dplugin_id

        # Found no dplugin with the dplugin_id mentioned in dblock
        if dplugin_id not in self.__dplugin_ids__:
            return False

        # Found no dblock for the dplugin_id
        if dblock.name not in self.__dplugin_ids__[dplugin_id]:
            return False

        del self.__dplugin_ids__[dplugin_id][dblock.name]

        # Check if all dblock,names were deleted
        if len(self.__dplugin_ids__[dplugin_id].keys()) == 0:
            del self.__dplugin_ids__[dplugin_id]

        return True

    def demux(self, source_id, block_name, data):
        block = self.__dplugin_ids__[source_id][block_name]
        names = block.signal_names_internal
        tmp_par = [[2,'SinMit_f3',1]]
        if names is not None:
            returnData = {}
            returnData['t'] = data[0]
            for ele in tmp_par:
                if ele[0] == source_id:
                    if ele[1] == block_name:
                        returnData[names[ele[2]]] = data[ele[2]]
            return returnData

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
    def set_parameter(self, para_list):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def quit(self):
        raise NotImplementedError("Please Implement this method")

    def get_type(self):
        raise NotImplementedError("Please Implement this method")