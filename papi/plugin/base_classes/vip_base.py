#!/usr/bin/python3
#-*- coding: utf-8 -*-

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
 
Contributors:
Stefan Ruppin
"""

from papi.plugin.base_classes.base_visual import base_visual
from papi.constants import PLUGIN_VIP_IDENTIFIER

class vip_base(base_visual):
    """
    Base class to inherent from when creation a visual plugin for th gui

    """
    def _start_plugin_base(self, config):
        """
        Needs to be implemented by plugin base class

        :param config: cfg to start plugin with (dict)
        :type config: dict
        :return:
        """
        return self.cb_initialize_plugin(config)

    def cb_initialize_plugin(self, config):
        """
        Callback function to be implemented by the plugin developer for the init phase of a plugin
        :param config: cfg to start plugin with (dict)
        :type config: dict
        :return:
        """
        raise NotImplementedError("Please Implement this method")

    def _get_type(self):
        return PLUGIN_VIP_IDENTIFIER


