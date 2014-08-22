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

from papi.data import DParameter

__author__ = 'knuths'

from papi.data.DObject import DObject
import copy


class DBlock(DObject):

    def __init__(self, dplugin_id, count, freq,name):
        super(DObject, self).__init__()
        self.signals_count = count
        self.freq = freq
        self.subscribers = {}
        self.dplugin_id = dplugin_id
        self.name = name

    def add_subscribers(self, dplugin):
        """

        :param dplugin:
        :return:
        :rtype boolean:
        """
        if dplugin.id not in self.subscribers:
            self.subscribers[dplugin.id] = dplugin.id
            return True
        else:
            return False

    def rm_subscriber(self, dplugin):
        """

        :param dplugin:
        :return:
        :rtype boolean:
        """
        if dplugin.id in self.subscribers:
            del self.subscribers[dplugin.id]
            return True
        else:
            return False

    def rm_all_subscribers(self):
        """

        :return:
        :rtype boolean:
        """

        pass

    def get_subscribers(self):
        """

        :return:
        :rtype []:
        """
        return self.subscribers.copy().values()


class DPlugin(DObject):

    def __init__(self):
        super(DPlugin, self).__init__()
        self.process = None
        self.pid = None
        self.queue = None
        self.plugin = None

        self.__subscriptions = {}
        self.state = None
        self.own_process = None
        self.uname = None
        self.__parameters = {}
        self.__blocks = {}
        self.type = None

    def subscribe(self, dblock: DBlock):
        """
        This plugins subscribes 'dblock' by remembering the dblog id
        :param dblock: DBlock which should be subscribed
        :return:
        :rtype boolean:
        """

        if dblock.dplugin_id not in self.__subscriptions:
            #dblock.add_subscribers(self)
            #self.__subscriptions.append(dblock.id)
            self.__subscriptions[dblock.dplugin_id] = {}
            self.__subscriptions[dblock.dplugin_id][dblock.name] = 1
            return True
        else:
            if dblock.name not in self.__subscriptions[dblock.dplugin_id]:
                self.__subscriptions[dblock.dplugin_id][dblock.name] = 1
                return True
            else:
                return False
        return False

    def unsubscribe(self, dblock:DBlock):
        """
        This plugins unsubscribes 'dblock' by forgetting the dblog id
        :param dblock: DBlock which should be unsubscribed
        :return:
        :rtype boolean:
        """

        if dblock.dplugin_id not in self.__subscriptions:
            return False
        else:
            if dblock.name in self.__subscriptions[dblock.dplugin_id]:
                del self.__subscriptions[dblock.dplugin_id][dblock.name]

                if len(self.__subscriptions[dblock.dplugin_id]) is 0:
                    del self.__subscriptions[dblock.dplugin_id]
                return True
            else:
                return False
        return False


        # if self.id in dblock.get_subscribers():
        #     dblock.rm_subscribers(self)
        #     del self.__subscriptions[dblock.id]
        #     return True
        # else:
        #     return False

    def get_subscribtions(self):
        """
        Returns a dictionary of all susbcribtions
        :return {}{} of DPlugin ids to DBlock names :
        :rtype: {}{}
        """

        return copy.deepcopy(self.__subscriptions.copy())

    def add_parameter(self, parameter: DParameter):
        """

        :param parameter:
        :return:
        :rtype boolean:
        """
        if parameter.name not in self.__parameters:
            self.__parameters[parameter.name] = parameter
            return True
        else:
            return False

    def rm_parameter(self, parameter : DParameter):
        """

        :param parameter_id:
        :return:
        :rtype boolean:
        """

        if parameter.name in self.__parameters:
            del self.__parameters[parameter.name]
            return True
        else:
            return False

    def get_parameters(self):
        """

        :return:
        :rtype {}:
        """
        return self.__parameters

    def add_dblock(self, dblock: DBlock):
        """

        :param dblock:
        :return:
        :rtype boolean:
        """
        dblock.dplugin_id = self.id

        if dblock.name not in self.__blocks:
            self.__blocks[dblock.name] = dblock
            return True
        else:
            return False

    def rm_dblock(self, dblock:DBlock):
        """

        :param dblock:
        :return:
        :rtype boolean:
        """
        if dblock.name in self.__blocks:
            del self.__blocks[dblock.name]
            return True
        else:
            return False

    def get_dblocks(self):
        """

        :return:
        :rtype {}:
        """
        return self.__blocks

    def get_dblock_by_name(self, dblock_name):
        """

        :return:
        :rtype DBlock:
        """

        if dblock_name in self.__blocks:
            return self.__blocks[dblock_name]
        else:
            return None

    def get_meta(self):
        """

        :return:
        :rtype DPlugin:
        """

        DPlugin_new = DPlugin()
        DPlugin_new.id = self.id
        DPlugin_new.pid = self.pid
        DPlugin_new.state = self.state
        DPlugin_new.own_process = self.own_process
        DPlugin_new.uname = self.uname
        DPlugin_new.type = self.type

        DPlugin_new.__parameters = copy.deepcopy(self.__parameters)
        DPlugin_new.__subscriptions = copy.deepcopy(self.__subscriptions)
        DPlugin_new.__blocks = copy.deepcopy(self.__blocks)

        return DPlugin_new

    def update_meta(self, meta):
        """

        :param meta: of type DPlugin
        :return:
        """

        self.id = meta.id
        self.pid = meta.pid
        self.state = meta.state
        self.own_process = meta.own_process
        self.uname = meta.uname
        self.type = meta.type

        self.__parameters = meta.__parameters
        self.__subscriptions = meta.__subscriptions
        self.__blocks = meta.__blocks