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

class plugin_base(IPlugin):

    __metaclass__= ABCMeta


    def __init_(self,CoreQueue,pluginQueue,sharedMemory,buffer,id):
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__shared_memory__ = sharedMemory
        self.__buffer__ = buffer
        self.__id__ = id


    def work(self):
        print("Plugin work called")

    def work_process(self,CoreQueue,pluginQueue,sharedMemory,buffer,id):
        print("Plugin work_process called")
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__shared_memory__ = sharedMemory
        self.__buffer__ = buffer
        self.__id__ = id

    def get_output_sizes(self):
        return [1,1]

    @abstractmethod
    def start_init(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def start(self):
        raise Exception("Unable to create an instance of abstract class")


    @abstractmethod
    def pause_init(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def pause(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def resume_init(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def resume(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def execute(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def set_parameter(self):
        raise Exception("Unable to create an instance of abstract class")

    @abstractmethod
    def quit(self):
        raise Exception("Unable to create an instance of abstract class")