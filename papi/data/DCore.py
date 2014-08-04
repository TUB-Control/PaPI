#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universitšt Berlin,
Fakultšt IV - Elektrotechnik und Informatik,
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
import copy

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
        self.__newid += 1
        return self.__newid
#        return uuid.uuid4().int >> 64

    def add_plugin(self, process, pid, own_process, queue, array, plugin, id):
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

        d_pl = DPlugin()


        d_pl.process = process
        d_pl.pid = pid
        d_pl.queue = queue
        d_pl.array = array
        d_pl.plugin = plugin
        d_pl.id = id
        d_pl.own_process = own_process


        self.__DPlugins[id] = d_pl

        return d_pl

    #TODO: Map auf dplugin
    def rm_dplugin(self, dplugin):
        """
        Removes DPlugin

        :param dplugin:
        :return:
        :rtype: bool
        """
        if dplugin.id in self.__DPlugins:

            self.rm_all_subscribers(dplugin.id)
            self.unsubscribe_all(dplugin.id)

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

    def get_dplugin_by_uname(self, plugin_uname):
        """
        Returns DPlugin object by uname

        :param plugin_name: uname of an DPlugin object
        :return DPlugin:
        :rtype: DPlugin
        """

        for plugin_id in self.__DPlugins:
            d_pl = self.__DPlugins[plugin_id]

            if d_pl.uname == plugin_uname:
                return d_pl

        return None


    def get_all_plugins(self):
        """

        :return:
        """

        return self.__DPlugins

    def subscribe(self, target_id, source_id):
        """

        :param target_id:
        :param source_id:
        :return:
        """
        #TODO Fehlerbehandlung falls target/source nicht existiert
        target = self.get_dplugin_by_id(target_id)
        source = self.get_dplugin_by_id(source_id)

        return target.subscribe(source)

    def unsubscribe(self, target_id, source_id):
        """

        :param target_id:
        :param source_id:
        :return:
        """

        target = self.get_dplugin_by_id(target_id)
        source = self.get_dplugin_by_id(source_id)

        return target.unsubscribe(source)

    def unsubscribe_all(self, dplugin_id):
        """

        :param dplugin_id:
        :return:
        """

        dplugin = self.get_dplugin_by_id(dplugin_id)

        subscribtions = copy.copy(dplugin.get_subcribtions())

        for sub_id in subscribtions:
            subscribtion = subscribtions[sub_id]
            dplugin.unsubscribe(subscribtion)

        if 0 == len(dplugin.get_subcribtions().keys()):
            return True
        else:
            return False

    def rm_all_subscribers(self, dplugin_id):
        """

        :param dplugin_id:
        :return:
        """

        dplugin = self.get_dplugin_by_id(dplugin_id)

        subscribers = copy.copy(dplugin.get_subscribers())

        for sub_id in subscribers:
            subscriber = subscribers[sub_id]
            dplugin.rm_subscriber(subscriber)

        if len(dplugin.get_subscribers().keys()) == 0:
            return True
        else:
            return False
