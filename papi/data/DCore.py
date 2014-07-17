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

__author__ = 'control'

from multiprocessing import Process, Queue

from papi.data.DObject import DObject

from papi.data.dcore.DGUIProcess import DGUIProcess
from papi.data.dcore.DPLCollectionProcess import DPLCollectionProcess
from papi.data.dcore.DPluginProcess import DPluginProcess
from papi.data.dcore.DProcess import DProcess
from papi.data.dcore.DPlugin import DPlugin

from papi.plugin_base import plugin_base

import uuid

class DCore():

    def __init__(self):
        self.__PLRunning = {}
        self.__PLAvailable = {}
        self.__EQueues = {}
        self.__Buffers = {}
        self.__PLProcesses = {}
        self.__GProcess = None
        self.__PLCProcess = None


    def __create_id(self):
        return uuid.uuid4()


    def add_pl_process(self, plugin: plugin_base, process: Process, queue: Queue):
        """

        :param plugin:
        :param process:
        :param queue:
        :rtype DPluginProcess
        :return:
        """

        d_pl = DPlugin(plugin)

        d_pl_p = DPluginProcess(plugin, process, queue)

        #d_pl_p.set_id(self.__create_id())

        #assert isinstance(d_pl_p, DPluginProcess)

        #self.__PLProcesses[d_pl_p.id] = d_pl_p

        return d_pl_p

    def set_gui_process(self, gui: Process):
        d_gui_p = DGUIProcess()
        assert isinstance(d_gui_p, DGUIProcess)
        self.__GProcess = d_gui_p

        return True

    def set_plc_process(self, plcp: Process):
        d_plc_p = DPLCollectionProcess()
        assert isinstance(d_plc_p, DPLCollectionProcess)
        self.__PLProcesses = d_plc_p

        return True

    def get_pl_process(self):
        return self.__PLProcesses

    def get_buffers(self):
        return self.__Buffers

    def get_event_queues(self):
        return self.__EQueues

    def get_plugins(self):
        return self.__PLAvailable

    def get_running_plugins(self):
        return self.__PLRunning

    def get_process_by_id(self, pid):
        found_process = None
        if self.__GProcess.id==pid:
            found_process = self.__GProcess
        elif self.__PLCProcess.id==pid:
            found_process = self.__PLCProcess
        else:
            found_process = self.__PLProcesses[pid]

        return found_process

    def get_buffer_by_id(self, bid):
        found_buffer = None
        found_buffer = self.__Buffers[bid]
        return found_buffer

    def get_plugin_by_id(self, pl_id):
        found_plugin = None
        found_plugin = self.__PLAvailable[pl_id]
        return found_plugin

    def get_running_plugin_by_id(self, pl_id):
        found_plugin = None
        found_plugin = self.__PLRunning[pl_id]
        return found_plugin