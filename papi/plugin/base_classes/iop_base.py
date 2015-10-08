#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
<Stefan Ruppin
"""



from papi.plugin.base_classes.ownProcess_base import ownProcess_base
from papi.constants import PLUGIN_IOP_IDENTIFIER

class iop_base(ownProcess_base):
    """
    This plugin is used to create an interface to different data sources.
    """
    def _start_plugin_base(self):
        """
        Needs to be implemented by plugin base class

        :return:
        """
        return self.cb_initialize_plugin()

    def cb_initialize_plugin(self):
        """
        Callback function to be implemented by the plugin developer for the init phase of a plugin

        :return:
        """
        raise NotImplementedError("Please Implement this method")

    def _get_configuration_base(self):
        config = {}
        return config


    def _get_type(self):
        return PLUGIN_IOP_IDENTIFIER