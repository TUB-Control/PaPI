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

__author__ = 'ruppin'


# CORE CONSTANTS
CORE_PROCESS_CONSOLE_IDENTIFIER = 'Core Process: '
CORE_CONSOLE_LOG_LEVEL          = 1


CORE_PAPI_VERSION               = 'v_0.1' # no spaces allowed
CORE_CORE_VERSION               = 'v_0.3' # no spaces allowed
CORE_PAPI_CONSOLE_START_MESSAGE = 'PaPI - Plugin based Process Interaction' + ' Version: ' + CORE_PAPI_VERSION
CORE_CORE_CONSOLE_START_MESSAGE = 'PaPI Core Modul ' + CORE_CORE_VERSION + ' started'
CORE_STOP_CONSOLE_MESSAGE       = 'Core and PaPI finished operation cleanly'


CORE_ALIVE_CHECK_ENABLED        = True
CORE_ALIVE_CHECK_INTERVAL       = 2 # seconds
CORE_ALIVE_MAX_COUNT            = 2

# EVENT CONSTANTS
# TODO
# somethink like: EVENT_TYPE_STATUS = 'status_event' and EVENT_OPERATION_CHECK_ALIVE = 'check_alive'


# GUI CONSTANTS
GUI_PROCESS_CONSOLE_IDENTIFIER  = 'Gui  Process: '
GUI_PROCESS_CONSOLE_LOG_LEVEL   = 1
GUI_VESION                      = 'v_0.1_dev'
GUI_START_CONSOLE_MESSAGE       = 'PaPI GUI Modul ' + GUI_VESION + ' started'

GUI_PAPI_WINDOW_TITLE           = 'PaPI - Plugin based Process Interaction'
GUI_WOKRING_INTERVAL            = 5 # in ms

# PLUGIN LOCATION CONSTANTS
PLUGIN_ROOT_FOLDER_LIST         = ['plugin','papi/plugin', '../plugin']
PLUGIN_IOP_FOLDER               = ''
PLUGIN_VIP_FOLDER               = ''
PLUGIN_DPP_FOLDER               = ''
PLUGIN_PCP_FOLDER               = ''

# PLUGIN TYPE IDENTIFIER
PLUGIN_IOP_IDENTIFIER           = 'IOP'
PLUGIN_VIP_IDENTIFIER           = 'ViP'
PLUGIN_PCP_IDENTIFIER           = 'PCP'
PLUGIN_DPP_IDENTIFIER           = 'DPP'

# PLUGIN STATE IDENTIFIER
PLUGIN_STATE_PAUSE              = 'paused'
PLUGIN_STATE_RESUMED            = 'resumed'
PLUGIN_STATE_START_SUCCESFUL    = 'start_successfull'
PLUGIN_STATE_START_FAILED       = 'start_failed'
PLUGIN_STATE_ALIVE              = 'alive'
PLUGIN_STATE_DEAD               = 'dead'
PLUGIN_STATE_ADDED              = 'added'
PLUGIN_STATE_STOPPED            = 'stopped'

# CONFIG/PROFILE SYSTEM CONSTANTS
CONFIG_DEFAULT_FILE             = 'testcfg.xml'
CONFIG_ROOT_ELEMENT_NAME        = 'PaPiConfig'
CONFIG_LOADER_SUBCRIBE_DELAY    = 1000 # ms