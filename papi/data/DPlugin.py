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


class DBlock(DObject):

    def __init__(self, dplugin, count, freq):
        super(DObject, self).__init__()
        self.signals_count = count
        self.freq = freq
        self.subscribers = {}
        self.dplugin = dplugin

    def add_subscribers(self, dplugin):
        """

        :param dplugin:
        :return:
        :rtype boolean:
        """
        if dplugin.id not in self.subscribers:
            self.subscribers[dplugin.id] = dplugin
            return True
        else:
            return False

    def rm_subscribers(self, dplugin):
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
        :rtype {}:
        """
        return self.subscribers


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

    def subscribe(self, dblock: DBlock):
        """
        This plugins subscribes 'dblock'
        :param dblock: DBlock which should be subscribed
        :return:
        :rtype boolean:
        """

        if self.id not in dblock.get_subscribers():
            dblock.add_subscribers(self)
            self.__subscriptions[dblock.id] = dblock
            return True
        else:
            return False

    def unsubscribe(self, dblock:DBlock):
        """
        This plugins unsubscribes 'dblock'
        :param dblock: DBlock which should be unsubscribed
        :return:
        :rtype boolean:
        """

        if self.id in dblock.get_subscribers():
            dblock.rm_subscribers(self)
            del self.__subscriptions[dblock.id]
            return True
        else:
            return False

    def get_subscribtions(self):
        """
        Returns a dictionary of all susbcribtions
        :return {} of DBlock :
        :rtype: {}
        """

        return self.__subscriptions

    def add_parameter(self, parameter: DParameter):
        """

        :param parameter:
        :return:
        :rtype boolean:
        """
        if parameter.id not in self.__parameters:
            self.__parameters[parameter.id] = parameter
            return True
        else:
            return False

    def rm_parameter(self, parameter : DParameter):
        """

        :param parameter_id:
        :return:
        :rtype boolean:
        """

        if parameter.id in self.__parameters:
            del self.__parameters[parameter.id]
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
        if dblock.id not in self.__blocks:
            self.__blocks[dblock.id] = dblock
            return True
        else:
            return False

    def rm_dblock(self, dblock:DBlock):
        """

        :param dblock:
        :return:
        :rtype boolean:
        """
        if dblock.id in self.__blocks:
            del self.__blocks[dblock.id]
            return True
        else:
            return False

    def get_dblocks(self):
        """

        :return:
        :rtype boolean:
        """
        return self.__blocks

    def get_dblock_by_id(self, dblock_id):
        """

        :return:
        :rtype DBlock:
        """

        if dblock_id in self.__blocks:
            return self.__blocks[dblock_id]
        else:
            return None