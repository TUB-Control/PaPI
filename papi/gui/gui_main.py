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
Sven Knuth, Stefan Ruppin
"""

__author__ = 'knuths'

import sys
import time

from PySide.QtGui               import QMainWindow, QApplication
from PySide.QtGui               import QIcon
from PySide.QtCore              import QSize


from papi.ui.gui.main           import Ui_MainGUI
from papi.gui.manager           import Overview
from papi.PapiEvent             import PapiEvent
from papi.data.DGui             import DGui
from papi.ConsoleLog            import ConsoleLog
from papi.data.DOptionalData    import DOptionalData
from papi.gui.add_plugin        import AddPlugin
from papi.gui.add_subscriber    import AddSubscriber
from papi.gui.add_pcp_subscriber import AddPCPSubscriber

from papi.constants import GUI_PAPI_WINDOW_TITLE, GUI_WOKRING_INTERVAL, GUI_PROCESS_CONSOLE_IDENTIFIER, \
    GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_START_CONSOLE_MESSAGE

from papi.constants import CONFIG_DEFAULT_FILE

from papi.gui.gui_api import Gui_api
from papi.gui.gui_event_processing import GuiEventProcessing

from papi.constants import CORE_PAPI_VERSION

from multiprocessing import Queue

import os

import datetime

import xml.etree.cElementTree as ET

from yapsy.PluginManager import PluginManager

import importlib.machinery

import pyqtgraph as pg

from pyqtgraph import QtGui, QtCore


# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=False)

class GUI(QMainWindow, Ui_MainGUI):

    def __init__(self, core_queue, gui_queue,gui_id, parent=None):
        super(GUI, self).__init__(parent)
        self.setupUi(self)

        self.create_actions()

        self.gui_data = DGui()

        # TODO:
        # callback functions for create plugin (intead scopeArea parameter) and for delete Plugin in ..GuiEventProcessing
        self.gui_api = Gui_api(self.gui_data, core_queue, gui_id)
        self.gui_event_processing = GuiEventProcessing(self.gui_data, core_queue, gui_id, gui_queue, self.scopeArea)


        self.callback_functions = {
            'do_create_plugin' : self.gui_api.do_create_plugin,
            'do_delete_plugin' : self.gui_api.do_delete_plugin,
            'do_set_parameter' : self.gui_api.do_set_parameter,
            'do_subscribe'     : self.gui_api.do_subscribe,
            'do_unsubscribe'   : self.gui_api.do_unsubscribe,
            'do_set_parameter' : self.gui_api.do_set_parameter_uname
        }

        self.manager_overview = Overview(self.callback_functions)
        self.manager_overview.dgui = self.gui_data
        self.setWindowTitle(GUI_PAPI_WINDOW_TITLE)

        self.core_queue = core_queue
        self.gui_queue = gui_queue

        self.gui_id = gui_id

        self.count = 0

        # create a timer and set interval for processing events with working loop
        self.working_interval = GUI_WOKRING_INTERVAL
        QtCore.QTimer.singleShot(self.working_interval, self.gui_working_v2)

        # switch case for event processing
        self.process_event = {  'new_data':             self.gui_event_processing.process_new_data_event,
                                'close_programm':       self.gui_event_processing.process_close_program_event,
                                'check_alive_status':   self.gui_event_processing.process_check_alive_status,
                                'create_plugin':        self.gui_event_processing.process_create_plugin,
                                'update_meta':          self.gui_event_processing.process_update_meta,
                                'plugin_closed':        self.gui_event_processing.process_plugin_closed,
                                'set_parameter':        self.gui_event_processing.process_set_parameter,
                                'pause_plugin':         self.gui_event_processing.process_pause_plugin,
                                'resume_plugin':        self.gui_event_processing.process_resume_plugin
        }


        self.log = ConsoleLog(GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER)

        self.AddSub = None
        self.AddPlu = None

        self.log.printText(1,GUI_START_CONSOLE_MESSAGE + ' .. Process id: '+str(os.getpid()))

        self.stefans_text_field.setText('1')
        # -------------------------------------
        # Create actions for buttons
        # -------------------------------------

        self.buttonCreatePlugin.clicked.connect(self.create_plugin)
        self.buttonCreateSubscription.clicked.connect(self.create_subscription)
        self.buttonCreatePCPSubscription.clicked.connect(self.create_pcp_subscription)
        self.buttonShowOverview.clicked.connect(self.ap_overview)
        self.buttonExit.clicked.connect(self.close)

        # -------------------------------------
        # Create Icons for buttons
        # -------------------------------------

        addplugin_icon = QIcon.fromTheme("list-add")
        close_icon = QIcon.fromTheme("application-exit")
        overview_icon = QIcon.fromTheme("view-fullscreen")
        addsubscription_icon = QIcon.fromTheme("list-add")

        # -------------------------------------
        # Set Icons for buttons
        # -------------------------------------

        self.buttonCreatePlugin.setIcon(addplugin_icon)
        self.buttonCreatePlugin.setIconSize(QSize(30, 30))

        self.buttonExit.setIcon(close_icon)
        self.buttonExit.setIconSize(QSize(30, 30))

        self.buttonShowOverview.setIcon(overview_icon)
        self.buttonShowOverview.setIconSize(QSize(30, 30))

        self.buttonCreateSubscription.setIcon(addsubscription_icon)
        self.buttonCreateSubscription.setIconSize(QSize(30, 30))

        self.buttonCreatePCPSubscription.setIcon(addsubscription_icon)
        self.buttonCreatePCPSubscription.setIconSize(QSize(30, 30))

        # -------------------------------------
        # Set Tooltipps for buttons
        # -------------------------------------

        self.buttonExit.setToolTip("Exit PaPI")
        self.buttonCreatePlugin.setToolTip("Add New Plugin")
        self.buttonCreateSubscription.setToolTip("Create New Subscription")
        self.buttonCreatePCPSubscription.setToolTip("Create New PCP Subscription")

        self.buttonShowOverview.setToolTip("Show Overview")

        # -------------------------------------
        # Set TextName to ''
        # -------------------------------------

        self.buttonExit.setText('')
        self.buttonCreatePlugin.setText('')
        self.buttonCreateSubscription.setText('')
        self.buttonShowLicence.setText('')
        self.buttonShowOverview.setText('')

    def set_dgui_data(self, dgui):
        self.gui_data = dgui
        self.manager_overview.dgui =dgui

    def dbg(self):
        print("Action")

    def create_actions(self):
        self.actionM_License.triggered.connect(self.menu_license)
        self.actionM_Quit.triggered.connect(self.menu_quit)

        self.actionP_Overview.triggered.connect(self.ap_overview)


        self.stefans_button.clicked.connect(self.stefan)
        self.stefans_button_2.clicked.connect(self.stefan_at_his_best)

    def create_plugin(self):
        """
        This function is called to create an QDialog, which is used to create Plugins
        :return:
        """
        self.AddPlu = AddPlugin(self.callback_functions)
        self.AddPlu.setDGui(self.gui_data)
        self.AddPlu.show()
        self.AddPlu.raise_()
        self.AddPlu.activateWindow()
        r = self.AddPlu.exec_()

        del self.AddPlu
        self.AddPlu = None

    def create_subscription(self):
        """
        This function is called to create an QDialog, which is used to create a subscription for a single Plugin
        :return:
        """

        self.AddSub = AddSubscriber(self.callback_functions)

        self.AddSub.setDGui(self.gui_data)
        self.AddSub.show()
        self.AddSub.raise_()
        self.AddSub.activateWindow()
        r = self.AddSub.exec_()

        del self.AddSub
        self.AddSub = None

    def create_pcp_subscription(self):
        """
        This function is called to create an QDialog, which is used to create a subscription for a single Plugin
        :return:
        """

        self.AddPCPSub = AddPCPSubscriber(self.callback_functions)

        self.AddPCPSub.setDGui(self.gui_data)
        self.AddPCPSub.show()
        self.AddPCPSub.raise_()
        self.AddPCPSub.activateWindow()
        r = self.AddPCPSub.exec_()

        del self.AddPCPSub
        self.AddPCPSub = None


    def menu_license(self):
        pass

    def menu_quit(self):
        self.close()
        pass

    def ap_overview(self):
        self.manager_overview.show()
        pass

    def closeEvent(self, *args, **kwargs):
        self.gui_api.do_close_program()

        self.manager_overview.close()

        if self.AddPlu is not None:
            self.AddPlu.close()

        if self.AddSub is not None:
            self.AddSub.close()

        self.close()




    def stefan_at_his_best(self):

        self.gui_api.do_load_xml(CONFIG_DEFAULT_FILE)

    def stefan(self):
        self.count += 1

        op= 0

        if op == 0:
            self.gui_api.do_save_xml_config(CONFIG_DEFAULT_FILE)

        if op == 1:
            allplugs = self.gui_data.get_all_plugins()

            for plug_id in allplugs:
                plugin = allplugs[plug_id]
                allpara = plugin.get_parameters()
                for para_id in allpara:
                    para = allpara[para_id]
                    print(plugin.uname, para.name, para.value)

        if op == 2:
            self.do_create_plugin('Sinus','Sinus1') #id 2
            self.do_create_plugin('Plot','Plot1')   #id 3
            #self.do_create_plugin('Plot','Plot2')   #id 4

            time.sleep(0.1)

            #self.do_subscribe(3,2,'SinMit_f3',2)
            #self.do_subsribe(4,2,'SinMit_f3')


    def gui_working_v2(self):
        """
         Event processing loop of gui. Build to get called every 40ms after a run through.
         Will process all events of the queue at the time of call.
         Procedure was built this way, so that the processing of an event is not covered by the try/except structure.
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        # event flag, true for first loop iteration to enter loop
        isEvent = True
        # event object, if there is an event
        event = None
        while(isEvent):
            # look at queue and try to get a new element
            try:
                event = self.gui_queue.get_nowait()
                # if there is a new element, event flag remains true
                isEvent = True
            except:
                # there was no new element, so event flag is set to false
                isEvent = False

            # check if there was a new element to process it
            if(isEvent):
                # get the event operation
                op = event.get_event_operation()
                # debug out
                self.log.printText(2,'Event: ' + op)
                # process this event
                self.process_event[op](event)

        # after the loop ended, which means that there are no more new events, a new timer will be created to start
        # this method again in a specific time
        QtCore.QTimer.singleShot(self.working_interval, self.gui_working_v2)







def startGUI(CoreQueue, GUIQueue,gui_id):
    """
    Function to call to start gui operation
    :param CoreQueue: link to queue of core
    :type CoreQueue: Queue
    :param GUIQueue: queue where gui receives messages
    :type GUIQueue: Queue
    :param gui_id: id of gui for events
    :type gui_id: int
    :return:
    """
    app = QApplication(sys.argv)
    gui = GUI(CoreQueue, GUIQueue,gui_id)
    gui.show()
    app.exec_()

if __name__ == '__main__':
    # main of GUI, just for stand alone gui testing
    app = QApplication(sys.argv)
    frame = GUI(None,None,None)
    frame.show()
    app.exec_()
