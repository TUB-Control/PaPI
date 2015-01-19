#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
Stefan Ruppin
"""
__author__ = 'stefan'


import papi.event as Event

from papi.data.DOptionalData import DOptionalData
from papi.ConsoleLog import ConsoleLog
from papi.constants import PLUGIN_API_CONSOLE_IDENTIFIER, PLUGIN_API_CONSOLE_LOG_LEVEL, CONFIG_LOADER_SUBSCRIBE_DELAY, \
    CONFIG_ROOT_ELEMENT_NAME, CORE_PAPI_VERSION, PLUGIN_PCP_IDENTIFIER, PLUGIN_VIP_IDENTIFIER

from papi.pyqtgraph import QtCore
from papi.gui.gui_api import Gui_api

import papi.error_codes as ERROR

import datetime
import time

import xml.etree.cElementTree as ET

class Plugin_api(QtCore.QObject):

    resize_gui = QtCore.Signal(int, int)

    def __init__(self, gui_data, core_queue, gui_id, PLUGIN_API_IDENTIFIER):
        super(Plugin_api, self).__init__()
        self.__default_api = Gui_api(gui_data, core_queue, gui_id, PLUGIN_API_IDENTIFIER)

    def do_create_plugin(self, plugin_identifier, uname, config={}, autostart = True):
        """
        Something like a callback function for gui triggered events e.a. when a user wants to create a new plugin.

        :param plugin_identifier: plugin to create
        :type plugin_identifier: basestring
        :param uname: uniqe name to set for new plugin
        :type uname: basestring
        :param config: additional configuration for creation
        :type config:
        :return:
        """
        self.__default_api.do_create_plugin(plugin_identifier,uname,config,autostart)

    def do_subscribe_uname(self,subscriber_uname,source_uname,block_name, signals=None, sub_alias = None):
        """
        Something like a callback function for gui triggered events.
        In this case, user wants one plugin to subscribe another

        :param subscriber_uname:  Plugin uname of plugin which should get the data
        :type subscriber_uname: basestring
        :param source_uname: plugin uname of plugin that should send the data
        :type source_uname: basestring
        :param block_name: name of block to subscribe
        :type block_name: basestring
        :return:
        """
        self.__default_api.do_subscribe_uname(subscriber_uname, source_uname, block_name, signals, sub_alias)


    def do_set_parameter_uname(self, plugin_uname, parameter_name, value):
        """
        Something like a callback function for gui triggered events.
        User wants to change a parameter of a plugin

        :param plugin_uname: name of plugin which owns the parameter
        :type plugin_uname: basestring
        :param parameter_name: name of parameter to change
        :type parameter_name: basestring
        :param value: new parameter value to set
        :type value:
        """
        self.__default_api.do_set_parameter_uname(plugin_uname, parameter_name, value)

    def do_load_xml(self, path):
        self.__default_api.do_load_xml(path)


    def do_delete_plugin_uname(self, uname):
        """
        Delete plugin with given uname.

        :param uname: Plugin uname to delete
        :type uname: basestring
        :return:
        """
        self.__default_api.do_delete_plugin_uname(uname)

    def do_set_parameter(self, plugin_id, parameter_name, value):
        """
        Something like a callback function for gui triggered events.
        User wants to change a parameter of a plugin

        :param plugin_id: id of plugin which owns the parameter
        :type plugin_id: int
        :param parameter_name: name of parameter to change
        :type parameter_name: basestring
        :param value: new parameter value to set
        :type value:
        """
        self.__default_api.do_set_parameter(plugin_id,parameter_name,value)


    def do_resume_plugin_by_uname(self, plugin_uname):
        """
        Something like a callback function for gui triggered events.
        User wants to resume a plugin, so this method will send an event to core.

        :param plugin_uname: uname of plugin to resume
        :type plugin_uname: basestring
        """
        self.__default_api.do_resume_plugin_by_uname(plugin_uname)


    def do_pause_plugin_by_uname(self, plugin_uname):
        """
        Something like a callback function for gui triggered events.
        User wants to pause a plugin, so this method will send an event to core.

        :param plugin_uname: uname of plugin to pause
        :type plugin_uname: basestring
        """
        self.__default_api.do_pause_plugin_by_uname(plugin_uname)