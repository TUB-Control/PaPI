#!/usr/bin/python3
#-*- coding: latin-1 -*-

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

__author__ = 'ruppins'


class DOptionalData(object):

    def __init__(self,DATA=None,pluginID=None):
        self.data = DATA
        self.data_source_id = None
        self.plugin_identifier = None
        self.plugin_uname = None
        self.plugin_id = pluginID
        self.source_ID = None
        self.unsubscribe_all = None
        self.reason = None
        self.parameter_list = None
        self.block_name = None
        self.block_list = None
        self.plugin_object = None
        self.plugin_type = None
        self.plugin_config = {}


