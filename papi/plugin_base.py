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

class plugin_base(object):

    __metaclass__= ABCMeta


    def __init_(self,CoreQueue,sharedMemory,buffer):
        self._CoreEventQueue = CoreQueue
        self._sharedMemory = sharedMemory
        self._buffer_ = buffer


    def work(self):
        print("Plugin work called")

    def work_process(self):
        print("Plugin work_process called")

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