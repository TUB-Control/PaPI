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

from papi.Buffer import Buffer
from papi.data.DObject import DObject

class DPlugin(DObject):

    def __init__(self, buffer):
        super(DPlugin,self).__init__()
        self.process = None
        self.pid = None
        self.queue = None
        self.array = None
        self.plugin = None
        self.plugin_id = None
        self.__subscribers = {}
        self.state = None

    def add_subscriber(self, dplugin):
        """
        An other DPlugin should subscribe this plugin.
        :param dplugin: DPlugin which should subscribes this plugin
        :returns: nothing
        """
        self.__subscribers[dplugin.id] = dplugin

    def rm_subscriber(self, dplugin):
        """
        Cancel the subscribtion of DPlugin for this plugin
        :param dplugin: DPlugin will unsubscribe
        :returns: Nothing
        """
        if dplugin.id in self.__subscribers:
            del self.__subscribers[dplugin.id]
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