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
from papi.plugin import plugin_base

__author__ = 'control'

from multiprocessing import Process, Queue, Array

from papi.data.dcore.DPlugin import DPlugin
import uuid


class DCore():
    def __init__(self):
        self.__DPlugins = {}



    def create_id(self):
        """

        :return: This function returns a 64bit random integer
        """

        return uuid.uuid4().int >> 64


    def add_plugin(self, process: Process, pid, queue : Queue, array: Array, plugin: plugin_base, plugin_id ):
        """
        :param process: Plugin is running in this process
        :param pid: Process ID of the process in which the plugin is running
        :param queue: Event queue needed for events which should be received by this plugin
        :param array: Used as shared memory by this plugin
        :param plugin: Plugin object
        :param plugin_id: ID of this plugin
        :return: Returns the data object DPlugin
        """

        d_pl = DPlugin(plugin)

        d_pl.process = process
        d_pl.pid = pid
        d_pl.queue = queue
        d_pl.array = array
        d_pl.plugin = plugin
        d_pl.plugin_id = plugin_id
        d_pl.id = self.create_id()

        self.__DPlugins[plugin_id] = d_pl

        return d_pl


    def get_dplugin_by_id(self, plugin_id):
        """

        :param plugin_id: ID of an DPlugin object
        :return: DPlugin
        """

        if plugin_id in self.__DPlugins:
            return self.__DPlugins[plugin_id]
        else:
            return None

