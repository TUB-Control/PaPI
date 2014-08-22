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
from papi.data.DPlugin import DPlugin, DBlock

__author__ = 'control'

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

    def add_plugin(self, process, pid, own_process, queue, plugin, id):
        """
        Add plugin with necessary information

        :param process: Plugin is running in this process
        :param pid: Process ID of the process in which the plugin is running
        :param queue: Event queue needed for events which should be received by this plugin
        :param plugin: Plugin object
        :param plugin_id: ID of this plugin
        :param id: ID for the new DPlugin
        :return: Returns the data object DPlugin
        :rtype: DPlugin
        """

        d_pl = DPlugin()


        d_pl.process = process
        d_pl.pid = pid
        d_pl.queue = queue
        d_pl.plugin = plugin
        d_pl.id = id
        d_pl.own_process = own_process

        #print(plugin)

        self.__DPlugins[id] = d_pl

        return d_pl

    #TODO: Map auf dplugin
    def rm_dplugin(self, dplugin_id):
        """
        Removes DPlugin with dplugin_id

        :param dplugin_id:
        :return:
        :rtype: bool
        """

        if dplugin_id in self.__DPlugins:


            self.rm_all_subscribers(dplugin_id)
            self.unsubscribe_all(dplugin_id)

            del self.__DPlugins[dplugin_id]

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

    def subscribe(self, subscriber_id, target_id, dblock_name):
        """

        :param subscriber_id: DPlugin which likes to subscribes dblock
        :param target_id: DPlugin which contains the dblock for subscribtion
        :param dblock_name: DBlock for subscribtion
        :return:
        """

        #Get Susbcriber DPlugin
        subscriber = self.get_dplugin_by_id(subscriber_id)

        if subscriber is None:
            return False

        #Get Target DPlugin
        target = self.get_dplugin_by_id(target_id)

        if target is None:
            return False

        dblock = target.get_dblock_by_name(dblock_name)

        if dblock is None:
            return False

        #Create relation between DPlugin and DBlock
        subscriber.subscribe(dblock)
        dblock.add_subscribers(subscriber)

        return True

    def unsubscribe(self, subscriber_id, target_id, dblock_name):
        """

        :param subscriber_id: DPlugin which likes to unsubscribes dblock
        :param target_id: DPlugin which contains the dblock for subscribtion
        :param dblock_name: DBlock for unsubscribtion
        :return:
        """

        #Get Susbcriber DPlugin
        subscriber = self.get_dplugin_by_id(subscriber_id)

        if subscriber is None:
            return False

        #Get Target DPlugin
        target = self.get_dplugin_by_id(target_id)

        if target is None:
            return False

        dblock = target.get_dblock_by_name(dblock_name)

        if dblock is None:
            return False

        #Destroy relation between DPlugin and DBlock
        subscriber.unsubscribe(dblock)
        dblock.rm_subscriber(subscriber)

    def unsubscribe_all(self, dplugin_id):
        """
        This function is used to cancel all subscribtion of the DPlugin with the dplugin_id
        :param dplugin_id:
        :return:
        """

        dplugin = self.get_dplugin_by_id(dplugin_id)


        subscribtion_ids = dplugin.get_subscribtions().copy()


        #Iterate over all DPlugins, which own a subscribed DBlock
        for sub_id in subscribtion_ids:
            sub = self.get_dplugin_by_id(sub_id)

            dblock_names = subscribtion_ids[sub_id]

            for dblock_name in dblock_names:

                dblock = sub.get_dblock_by_name(dblock_name)

                dblock.rm_subscriber(dplugin)
#                print(dblock_names)
                dplugin.unsubscribe(dblock)

        if 0 == len(dplugin.get_subscribtions()):
            return True
        else:
            return False

    def rm_all_subscribers(self, dplugin_id):
        """
        This function is used to remove all subscribers of all DBlocks, which are hold by the DPlugin with the dplugin_id
        :param dplugin_id:
        :return:
        """

        dplugin = self.get_dplugin_by_id(dplugin_id)

        dblock_names = dplugin.get_dblocks()

        for dblock_name in dblock_names:

            dblock = dplugin.get_dblock_by_name(dblock_name)

            dplugin_ids = dblock.get_subscribers()
            for dplugin_id in dplugin_ids:

                subscriber = self.get_dplugin_by_id(dplugin_id)

                subscriber.unsubscribe(dblock)
                dblock.rm_subscriber(subscriber)

        if len(dplugin.get_dblocks()) == 0:
            return True
        else:
            return False
