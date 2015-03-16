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
 
Contributors:
<Stefan Ruppin
"""

__author__ = 'control'

from papi.gui.gui_event_processing import GuiEventProcessing
from papi.gui.gui_api import Gui_api
from papi.data.DGui import DGui
from papi.yapsy.PluginManager import PluginManager
from papi.constants import PLUGIN_ROOT_FOLDER_LIST


class GuiManagement(object):

    def __init__(self, core_queue, gui_queue, gui_id, TabManager, get_gui_config, set_gui_config):
        self.core_queue  = core_queue
        self.gui_queue   = gui_queue
        self.gui_data    = DGui()
        self.gui_id      = gui_id
        self.tab_manager = TabManager

        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(PLUGIN_ROOT_FOLDER_LIST)
        self.plugin_manager.collectPlugins()

        self.gui_api = Gui_api(self.gui_data,
                               self.core_queue,
                               self.gui_id,
                               get_gui_config_function=get_gui_config,
                               set_gui_config_function= set_gui_config )

        self.gui_event_processing = GuiEventProcessing(self.gui_data,
                                                       self.core_queue,
                                                       self.gui_id,
                                                       self.gui_queue,
                                                       self.tab_manager,
                                                       self.plugin_manager )


