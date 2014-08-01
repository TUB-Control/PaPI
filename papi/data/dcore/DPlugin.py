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

#from papi.BufferManager import Buffer
from papi.data.DObject import DObject

class DPlugin(DObject):

    def __init__(self, buffer):
        super(DPlugin,self).__init__()
        self.process = None
        self.pid = None
        self.queue = None
        self.array = None
        self.plugin = None
        self.__subscribers = {}
        self.__subscriptions = {}
        self.state = None

    def add_subscriber(self, dplugin):
        """
        Add `dplugin` as subscriber for this plugin.
        :param dplugin: DPlugin which subscribes this plugin
        :returns: nothing
        """
        if dplugin.id not in self.__subscribers:
            self.__subscribers[dplugin.id] = dplugin
            dplugin.subscribe(self)

    def subscribe(self, dplugin):
        """
        This plugins subscribes `dplugin`
        :param dplugin: DPlugin which should be subscribed
        :return:
        """

        if dplugin.id not in self.__subscriptions:
            self.__subscriptions[dplugin.id] = dplugin
            dplugin.add_subscriber(self)

    def rm_subscriber(self, dplugin):
        """
        Remove `dplugin` as subscripber for this plugin
        :param dplugin: will be unsubscribed
        :returns: Nothing
        """
        if dplugin.id in self.get_subscribers():
            d_pl = self.get_subscribers()[dplugin.id]
            del self.get_subscribers()[dplugin.id]
            d_pl.unsubscribe(self)
            return True
        else:
            return False

    def unsubscribe(self, dplugin):
        """
        This plugin will unsubscribe `dplugin`
        :param dplugin: DPlugin which should be unsubscribed
        :return:
        """
        if dplugin.id in self.get_subcribtions():
            d_pl = self.get_subcribtions()[dplugin.id]
            del self.get_subcribtions()[dplugin.id]
            d_pl.rm_subscriber(self)
            return True
        else:
            return False




    def get_subscribers(self):
        """
        Returns a dictionary of all subscribers
        :return {} of DPlugin :
        :rtype: {}
        """

        return self.__subscribers

    def get_subcribtions(self):
        """
        Returns a dictionary of all subscribtions
        :return {} of DPlugin
        :rtype: {}
        """
        return self.__subscriptions