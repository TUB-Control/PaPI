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
from papi.PapiEvent import PapiEvent
from papi.DebugOut import debug_print
from papi.data.DCore import DCore

class Core:

    def __init__(self):
        self.__process_event_by_type__ = {  'status_event': self.__process_status_event__,
                                            'data_event': self.__process_data_event__,
                                            'instr_event': self.__process_instr_event__,
        }
        self.__process_status_event_l__ = { 'start_successfull': self.__process_start_successfull__,
                                            'start_failed': self.__process_start_failed__,
                                            'check_alive_status': self.__process_check_alive__,
                                            'alive': self.__process_alive__,
                                            'join_request': self.__process_join_request__
        }
        self.__process_data_event_l__ = {   'new_data': self.__process_new_data__,
                                            'get_output_size': self.__process_get_output_size__,
                                            'response_output_size': self.__process_response_output_size__
        }

        self.__process_instr_event_l__ = { 'create_plugin': self.__process_create_plugin__,
                                           'stop_plugin': self.__process_stop_plugin__
        }

        self.__debugLevel__ = 1
        self.__debug_var = ''


        self.core_data = DCore()



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






















    # ------- Event processing initial stage ---------

    def __process_event__(self,event: PapiEvent):
         t = event.get_eventtype()
         self.__process_event_by_type__[t](event)


    # ------- Event processing first stage ---------

    def __process_status_event__(self,event):
        debug_print(self.__debugLevel__,'Core: processing status event')
        op = event.get_event_operation()
        return self.__process_status_event_l__[op](event)

    def __process_data_event__(self,event):
        debug_print(self.__debugLevel__,'Core: processing data event')
        op = event.get_event_operation()
        return self.__process_data_event_l__[op](event)

    def __process_instr_event__(self,event):
        debug_print(self.__debugLevel__,'Core: processing instr event')
        op = event.get_event_operation()
        return self.__process_instr_event_l__[op](event)




    # ------- Event processing second stage: status events ---------

    def __process_start_successfull__(self,event):
        self.__debug_var__ = 'start_successfull'
        return True


    def __process_start_failed__(self,event):
        self.__debug_var__ = 'start_failed'
        return True


    def __process_check_alive__(self,event):
        self.__debug_var__ = 'check_alive_status'
        return True


    def __process_alive__(self,event):
        """
         :type event: PapiEvent
        """
        self.__debug_var__ = 'alive'
        return True


    def __process_join_request__(self,event: PapiEvent):
        self.__debug_var__ = 'join_request'
        data_object = self.core_data.get_plugin_by_id(event.get_originID())
        return True


    # ------- Event processing second stage: data events ---------

    def __process_new_data__(self,event):
        self.__debug_var__ = 'new_data'
        return True

    def __process_get_output_size__(self,event):
        self.__debug_var__ = 'get_output_size'
        return True

    def __process_response_output_size__(self,event):
        self.__debug_var__ = 'response_output_size'
        return True


    # ------- Event processing second stage: instr events ---------

    def __process_create_plugin__(self,event):
        self.__debug_var__ = 'create_plugin'
        return True

    def __process_stop_plugin__(self,event):
        self.__debug_var__ = 'stop_plugin'
        return True