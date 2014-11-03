#!/usr/bin/python3
#-*- coding: utf-8 -*-

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

Contributors:
Stefan Ruppin
"""

__author__ = 'stefan'

from papi.plugin.base_classes.base_plugin import base_plugin
import re

class base_visual(base_plugin):

    def init_plugin(self,CoreQueue,pluginQueue,id):
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        super(base_plugin, self).papi_init()



    def start_init(self, config=None):

        self.config = config
        # --------------------------------

        # get needed data from config
        size_re = re.compile(r'([0-9]+)')
        self.window_size = size_re.findall(self.config['size']['value'])
        self.window_pos = size_re.findall(self.config['position']['value'])


        self.window_name = self.config['name']['value']

        self.initiate_layer_1(self.config)



    def initiate_layer_1(self, config):
        raise NotImplementedError("Please Implement this method")


