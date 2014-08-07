#!/usr/bin/python3
#-*- coding: latin-1 -*-

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
from yapsy.IPlugin import IPlugin
from papi.PapiEvent import PapiEvent
import os

class plugin_base(IPlugin):

    __metaclass__= ABCMeta


    def __init_(self,CoreQueue,pluginQueue,id):
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id


    def work_process(self,CoreQueue,pluginQueue,id,EventTriggered=False):
        print("Plugin work_process called")
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id

        self.goOn = 1

        if self.start_init():
            event = PapiEvent(self.__id__,0,'status_event','start_successfull','')
            self._Core_event_queue__.put(event)
        else:
            event = PapiEvent(self.__id__,0,'status_event','start_failed','')
            self._Core_event_queue__.put(event)
            self.goOn = 0
            event = PapiEvent(self.__id__,0,'status_event','join_request','')
            self._Core_event_queue__.put(event)

        while self.goOn:
            try:
                event = self.__plugin_queue__.get(EventTriggered)
                #process event
                op = event.get_event_operation()
                if (op=='stop_plugin'):
                    self.quit()
                    self.goOn = 0
                    event = PapiEvent(self.__id__,0,'status_event','join_request','')
                    self._Core_event_queue__.put(event)
                if op=='pause_plugin':
                    self.pause()
                if op=='resume_plugin':
                    self.resume()
                if op=='check_alive_status':
                    alive_event = PapiEvent(self.__id__,0,'status_event','alive','')
                    self._Core_event_queue__.put(alive_event)
                if op=='new_data':
                    self.execute(event.get_optional_parameter())
            except:
                self.execute()


    @abstractmethod
    def get_output_sizes(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def start_init(self):
        raise Exception("Unable to create an instance of abstract class")


    @abstractmethod
    def pause(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def resume(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def execute(self,Data=None):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def set_parameter(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def quit(self):
        raise Exception("Unable to create an instance of abstract class")

    def get_type(self):
        raise Exception("Unable to create an instance of abstract class")