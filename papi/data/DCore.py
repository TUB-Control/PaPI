#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""
from papi.data.DPlugin import DPlugin
from papi.data.DObject import DObject
from papi.ConsoleLog import ConsoleLog
import copy
import papi.error_codes as ERROR

__author__ = 'knuth'


class DCore():
    """
    DCore contains and manages the internal data structure
    """
    def __init__(self):
        """
        Used to initialize this object. An empty dictionary of DPlugin is created

        :return:
        """
        self.__DPlugins = {}

        self.__newid = 0
        self.log = ConsoleLog(2, "DCore: ")

    def create_id(self):
        """
        Creates and returns unique IDs

        :returns: unique ID
        :rtype: int
        """
        #self.__newid += 1
        self.__newid = DObject.get_id()
        return self.__newid
#        return uuid.uuid4().int >> 64

    def add_plugin(self, process, pid, own_process, queue, plugin, id):
        """
        Add plugin with necessary information.

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

        self.__DPlugins[id] = d_pl

        return d_pl

    def rm_dplugin(self, dplugin_id):
        """
        Removes DPlugin with dplugin_id

        :param dplugin_id:
        :return:
        :rtype: bool
        """

        if dplugin_id in self.__DPlugins:
            self.__DPlugins[dplugin_id].state = 'deleted'

            self.rm_all_subscribers(dplugin_id)
            self.unsubscribe_all(dplugin_id)

            del self.__DPlugins[dplugin_id]

            return ERROR.NO_ERROR
        else:
            return ERROR.UNKNOWN_ERROR

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
        Returns a dictionary of all known dplugins

        :return:
        :rtype: {}
        """

        return self.__DPlugins

    def subscribe(self, subscriber_id, target_id, dblock_name):
        """
        Used to create a subscription.

        :param subscriber_id: DPlugin which likes to subscribes dblock
        :param target_id: DPlugin which contains the dblock for subscribtion
        :param dblock_name: DBlock identified by its unique name for subscribtion
        :return:
        """

        #Get Subscriber DPlugin
        subscriber = self.get_dplugin_by_id(subscriber_id)

        if subscriber is None:
            self.log.printText(1, "Found no Subscriber with ID " + subscriber_id)
            return None

        #Get Target DPlugin
        target = self.get_dplugin_by_id(target_id)

        if target is None:
            self.log.printText(1, "Found no Target with ID " + str(target_id))
            return None

        dblock = target.get_dblock_by_name(dblock_name)

        if dblock is None:
            self.log.printText(1, "Target " + target.uname + " has no DBlock " + dblock_name)

            return None

        #Create relation between DPlugin and DBlock

        dsubscription = subscriber.subscribe(dblock)

        if dsubscription is None:
            self.log.printText(1, "Subscriber " + str(subscriber_id) + " has already subscribed " + dblock_name)
            return None

        if dblock.add_subscribers(subscriber) is False:
            self.log.printText(1, "DBlock " + dblock_name + " was already subscribed by Subscriber" + subscriber_id)
            return None

        return dsubscription

    def unsubscribe(self, subscriber_id, target_id, dblock_name):
        """
        Used to remove a subscription.

        :param subscriber_id: DPlugin which likes to unsubscribes dblock
        :param target_id: DPlugin which contains the dblock for subscribtion
        :param dblock_name: DBlock identified by its unique name for unsubscribtion
        :return:
        :rtype boolean:
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
        if subscriber.unsubscribe(dblock) is False:
            self.log.printText(1, "Subscriber " + str(subscriber_id) + " has already unsubscribed " + dblock_name)
            return False

        if dblock.rm_subscriber(subscriber) is False:
            self.log.printText(1, "DBlock " + dblock_name + " was already unsubscribed by Subscriber" + subscriber_id)
            return False

        return True

    def unsubscribe_all(self, dplugin_id):
        """
        This function is used to cancel all subscription of the DPlugin with the dplugin_id.

        :param dplugin_id: dplugin identifed by dplugin_id whose subscription should be canceled.
        :return:
        """

        dplugin = self.get_dplugin_by_id(dplugin_id)

        # copy subscription for iteration and deletion
        subscribtion_ids = copy.deepcopy( dplugin.get_subscribtions() )

        #Iterate over all DPlugins, which own a subscribed DBlock
        for sub_id in subscribtion_ids:
            sub = self.get_dplugin_by_id(sub_id)

            dblock_names = subscribtion_ids[sub_id]

            for dblock_name in dblock_names:

                dblock = sub.get_dblock_by_name(dblock_name)

                dblock.rm_subscriber(dplugin)

                dplugin.unsubscribe(dblock)

        if 0 == len(dplugin.get_subscribtions()):
            return True
        else:
            return False

    def rm_all_subscribers(self, dplugin_id):
        """
        This function is used to remove all subscribers of all DBlocks, which are hold by the DPlugin with the dplugin_id.

        :param dplugin_id: dplugin identifed by dplugin_id whose subscribers should be removed.
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

        # if len(dplugin.get_dblocks()) == 0:
        #     return True
        # else:
        #     return False


    def rm_all_subscribers_of_a_dblock(self, dplugin_id, dblock_name):
        dplugin = self.get_dplugin_by_id(dplugin_id)
        if dplugin is not None:
            dblock = dplugin.get_dblock_by_name(dblock_name)
            if dblock is not None:
                dplugin_ids = dblock.get_subscribers()
                for dplugin_id in dplugin_ids:

                    subscriber = self.get_dplugin_by_id(dplugin_id)

                    subscriber.unsubscribe(dblock)
                    dblock.rm_subscriber(subscriber)


    def subscribe_signals(self, subscriber_id, target_id, dblock_name, signals):
        """
        This function is used to subscribe a bunch of signals.

        :param subscriber_id: DPlugin which likes to subscribes signals of the chosen  dblock
        :param target_id: DPlugin which contains the dblock for subscribtion
        :param dblock_name: DBlock identified by its unique name for subscribtion
        :param signals: List of signals which are needed to be added
        :return:
        """

        #Get Susbcriber DPlugin
        subscriber = self.get_dplugin_by_id(subscriber_id)

        if subscriber is None:
            self.log.printText(1, "Found no Subscriber with ID " + subscriber_id)
            return None

        #Get Target DPlugin
        target = self.get_dplugin_by_id(target_id)

        if target is None:
            self.log.printText(1, "Found no Target with ID " + str(target_id))
            return None

        dblock = target.get_dblock_by_name(dblock_name)

        if dblock is None:
            self.log.printText(1, "Target " + target.uname + " has no DBlock " + dblock_name)

            return None

        return subscriber.subscribe_signals(dblock, signals)


    def unsubscribe_signals(self, subscriber_id, target_id, dblock_name, signals):
        """
        This function is used to unubscribe a bunch of signals.

        :param subscriber_id: DPlugin which likes to unsubscribes signals of the chosen dblock
        :param target_id: DPlugin which contains the dblock for subscribtion
        :param dblock_name: DBlock identified by its unique name for subscribtion
        :param signals: List of signals which are needed to be added
        :return:
        """

        #Get Susbcriber DPlugin
        subscriber = self.get_dplugin_by_id(subscriber_id)

        if subscriber is None:
            self.log.printText(1, "Found no Subscriber with ID " + subscriber_id)
            return False

        #Get Target DPlugin
        target = self.get_dplugin_by_id(target_id)

        if target is None:
            self.log.printText(1, "Found no Target with ID " + str(target_id))
            return False

        dblock = target.get_dblock_by_name(dblock_name)

        if dblock is None:
            self.log.printText(1, " Target " + target.uname + " has no DBlock " + dblock_name)

            return False

        subscription = subscriber.unsubscribe_signals(dblock, signals)

        if subscription is None:
            return False

        if len(subscription.get_signals()) == 0:
            return self.unsubscribe(subscriber_id, target_id, dblock_name)

        return True


