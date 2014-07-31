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

        self.__newid = 0

    def create_id(self):
        """
        Creates and returns random unique 64 bit integer
        :returns: 64bit random integer
        :rtype: int
        """
        self.__newid =+ 1
        return self.__newid
#        return uuid.uuid4().int >> 64

    def add_plugin(self, process, pid, queue, array, plugin, id ):
        """
        Add plugin with necessary information

        :param process: Plugin is running in this process
        :param pid: Process ID of the process in which the plugin is running
        :param queue: Event queue needed for events which should be received by this plugin
        :param array: Used as shared memory by this plugin
        :param plugin: Plugin object
        :param plugin_id: ID of this plugin
        :return: Returns the data object DPlugin
        :rtype: DPlugin
        """

        d_pl = DPlugin(plugin)


        d_pl.process = process
        d_pl.pid = pid
        d_pl.queue = queue
        d_pl.array = array
        d_pl.plugin = plugin
        d_pl.id = id


        self.__DPlugins[id] = d_pl

        return d_pl

    def rm_dplugin(self, dplugin):
        """
        Removes DPlugin

        :param dplugin:
        :return:
        :rtype: bool
        """

        if dplugin.id in self.__DPlugins:
            del self.__DPlugins[dplugin.id]
            return True
        else:
            return False

    def get_dplugins_count(self):
        """
        Returns count of known plugins in this data structure

        :return:
        :rtype: int
        """
        return len(self.__DPlugins.keys())

    def get_dplugin_by_id(self, plugin_id):
        """
        Returns DPlugin object by ID

        :param plugin_id: ID of an DPlugin object
        :return DPlugin:
        :rtype: DPlugin
        """

        if plugin_id in self.__DPlugins:
            return self.__DPlugins[plugin_id]
        else:
            return None

    def get_all_plugins(self):
        return self.__DPlugins