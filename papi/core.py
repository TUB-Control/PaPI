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

version = '0.1'

from yapsy.PluginManager import PluginManager
from multiprocessing import Process, Array, Lock, Queue
import time
import os
from papi.Event import PapiEvent
from papi.DebugOut import debug_print

class Core:



    def __init__(self):
        self.__process_event_by_type__ = {   'status_event': self.__process_status_event__,
                                        'data_event': self.__process_data_event__,
                                        'instr_event': self.__process_instr_event__,
        }
        self.__debugLevel__ = 1


    def run(self):
        debug_print(self.__debugLevel__,'Core: initialize PaPI - Plugin based Process Interaction')
        debug_print(self.__debugLevel__, ['Core: core process id: ',os.getpid()] )
        coreEventQueue = Queue()

        guiEventQueue = Queue()

        # sollte weg, wenn Datenstruktur da
        process_alive_cout = 0


        # GUIAlive
        guiAlive = 0



        coreGoOn = 0

        debug_print(self.__debugLevel__,'Core:  entering event loop')
        while coreGoOn:
            event = coreEventQueue.get()
            self.__process_event__(event)
            coreGoOn = process_alive_cout == 0 & guiAlive






    def __process_event__(self,event: PapiEvent):
         t = event.get_eventtype()
         self.__process_event_by_type__[t](event)

    def __process_status_event__(self,event):
        debug_print(self.__debugLevel__,'Core: processing status event')

    def __process_data_event__(self):
        debug_print(self.__debugLevel__,'Core: processing data event')

    def __process_instr_event__(self):
        debug_print(self.__debugLevel__,'Core: processing instr event')

