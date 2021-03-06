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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Stefan Ruppin
"""



import platform
from os.path import expanduser
import datetime
import os
import papi

now = datetime.datetime.now()

PAPI_DEV_EDITION                = False

# CORE CONSTANTS
CORE_PROCESS_CONSOLE_IDENTIFIER = 'Core Process: '
CORE_CONSOLE_LOG_LEVEL          = 1
DCORE_CONSOLE_LOG_LEVEL         = 2

CORE_PAPI_VERSION               = 'v.1.4' # no spaces allowed
CORE_CORE_VERSION               = CORE_PAPI_VERSION # no spaces allowed
CORE_PAPI_CONSOLE_START_MESSAGE = 'PaPI - Plugin based Process Interaction' + ' Version: ' + CORE_PAPI_VERSION
CORE_CORE_CONSOLE_START_MESSAGE = 'PaPI Core Modul ' + CORE_CORE_VERSION + ' started'
CORE_STOP_CONSOLE_MESSAGE       = 'Core and PaPI finished operation cleanly'


CORE_ALIVE_CHECK_ENABLED        = True
CORE_ALIVE_CHECK_INTERVAL       = 2 # seconds
CORE_ALIVE_MAX_COUNT            = 10

CORE_TIME_SIGNAL                = 'papi_time_signal'

PAPI_LAST_CFG                   =  'last_active_papi.xml'

PAPI_USER_CFG                   = ''
PAPI_USER_FOLDER                = ''

if platform.system() in ['Linux', 'Darwin']:
    PAPI_USER_FOLDER = expanduser("~")

PAPI_USER_CFG =  PAPI_USER_FOLDER + '/.papi/config.xml'

PAPI_DEFAULT_BG_PATH            = 'papi/media/default_bg.png'

PAPI_LAST_CFG_PATH              = PAPI_USER_FOLDER + '/.papi/lastCfg.xml'

# PaPI Information constants

PAPI_COPYRIGHT                  = '&copy; 2014-' + str(now.year)
PAPI_ABOUT_TITLE                = 'About PaPI'
PAPI_ABOUT_TEXT                 = """
<html><body>
<h2>PaPI</h2>
Version """ + CORE_PAPI_VERSION + """
<br/>
<br/>
Copyright """ + PAPI_COPYRIGHT + """ <a href="http://www.control.tu-berlin.de/">Control Systems Group</a>, TU-Berlin.<br/>
Published under <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GPL Version 3</a>. Hosted on <a href="https://github.com/TUB-Control/PaPI">GitHub</a>
<br/><br/>
PaPI is embedding:
<ul>
<li>Yapsy 1.10.423 published under BSD-License, <a href="http://yapsy.sourceforge.net/#license">License</a></li>
<li>pyqtgraph-0.9.10 published under MIT-License, <a href="http://www.opensource.org/licenses/mit-license.php">License</a></li>
<li>JSONlab 1.1 published under BSD-License and GPLv3, <a href="https://github.com/fangq/jsonlab">License</a></li>
</ul>
</body
</html>
"""

PAPI_WIKI_URL                    = 'https://github.com/TUB-Control/PaPI/wiki'
PAPI_DOC_URL                     = 'http://tub-control.github.io/PaPI/'

if PAPI_DEV_EDITION:
    PAPI_DOC_URL += "dev/"

PAPI_DOC_PREFIX_PLUGIN           = 'man.papi.plugin'

# EVENT CONSTANTS
# TODO
# somethink like: EVENT_TYPE_STATUS = 'status_event' and EVENT_OPERATION_CHECK_ALIVE = 'check_alive'


# GUI CONSTANTS
GUI_PROCESS_CONSOLE_IDENTIFIER  = 'Gui  Process: '
GUI_PROCESS_CONSOLE_LOG_LEVEL   = 1
GUI_VERSION                      = CORE_CORE_VERSION
GUI_START_CONSOLE_MESSAGE       = 'PaPI GUI Modul ' + GUI_VERSION + ' started'

GUI_PAPI_WINDOW_TITLE           = 'PaPI - Plugin based Process Interaction'
GUI_WOKRING_INTERVAL            = 16 # in ms
GUI_WAIT_TILL_RELOAD            = 1000 # in ms

GUI_DEFAULT_WIDTH               = 771
GUI_DEFAULT_HEIGHT              = 853

GUI_DEFAULT_TAB                 = 'PaPI-Tab'
GUI_TABWIDGET_IDENTIFIER        = '__tabWidget'

GUI_PLUGIN_CONFIG               = 'info.ini'

# PLUGIN LOCATION CONSTANTS
PLUGIN_ROOT_FOLDER_LIST         = [os.path.dirname(papi.__file__)+'/plugin']
PLUGIN_IOP_FOLDER               = ''
PLUGIN_VIP_FOLDER               = ''
PLUGIN_DPP_FOLDER               = ''
PLUGIN_PCP_FOLDER               = ''

# PLUGIN TYPE IDENTIFIER
PLUGIN_IOP_IDENTIFIER           = 'IOP'
PLUGIN_VIP_IDENTIFIER           = 'ViP'
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
PLUGIN_STATE_DELETE             = 'deleted'

#
PLUGIN_API_CONSOLE_IDENTIFIER  = 'Plugin  API: '
PLUGIN_API_CONSOLE_LOG_LEVEL   = 1

# CONFIG/PROFILE SYSTEM CONSTANTS

CONFIG_DEFAULT_DIRECTORY        = 'cfg_collection/'
CONFIG_DEFAULT_FILE             = 'cfg_collection/testcfg.xml'
CONFIG_ROOT_ELEMENT_NAME        = 'PaPiConfig'   # for xml save
CONFIG_ROOT_ELEMENT_NAME_RELOADED = 'PaPI'
CONFIG_LOADER_SUBSCRIBE_DELAY    = 1000 # ms
CONFIG_SAVE_CFG_BLACKLIST       = ['type', 'regex', 'display_text','tooltip','advanced' ]



# REGEX Collection
REGEX_SINGLE_INT   = '[0-9]+'
REGEX_BOOL_BIN     = '^(1|0)$'
REGEX_SINGLE_UNSIGNED_FLOAT_FORCED = '(\d+\.\d+)'
REGEX_SIGNED_FLOAT = r'([-]{0,1}\d+\.\d+)'
REGEX_SIGNED_FLOAT_OR_INT = r'([-]{0,1}\d+(.\d+)?)'

# CONFIGURATION TYPE Collection

CFG_TYPE_FILE = 'file'
CFG_TYPE_COLOR = 'color'
CFG_TYPE_BOOL = 'bool'

TREE_CSS = """
QTreeView { alternate-background-color: yellow;}
QTreeView::branch:has-siblings:!adjoins-item {
    border-image: url(""" + os.path.dirname(papi.__file__)+ """/gui/default/images/vline.png) 0;
}

QTreeView::branch:has-siblings:adjoins-item {
    border-image: url(""" + os.path.dirname(papi.__file__)+ """/gui/default/images/branch-more.png) 0;
}

QTreeView::branch:!has-children:!has-siblings:adjoins-item {
    border-image: url(""" + os.path.dirname(papi.__file__)+ """/gui/default/images/branch-end.png) 0;
}

QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {
        border-image: none;
        image: url(""" + os.path.dirname(papi.__file__)+ """/gui/default/images/branch-closed.png);
}

QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings  {
        border-image: none;
        image: url(""" + os.path.dirname(papi.__file__)+ """/gui/default/images/branch-open.png);
}
"""
