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

__author__ = 'knuths'

import sys
import time

from PySide.QtGui import QMainWindow, QApplication




import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=False)

from papi.ui.gui.main import Ui_MainGUI
from papi.gui.manager import Overview
from papi.PapiEvent import PapiEvent
from papi.data.DGui import DGui
from papi.ConsoleLog import ConsoleLog
from papi.data.DOptionalData import DOptionalData
from papi.gui.add_plugin import AddPlugin
from papi.gui.add_subscriber import AddSubscriber
from PySide.QtGui import QIcon
from PySide.QtCore import QSize

from yapsy.PluginManager import PluginManager
import importlib.machinery


from multiprocessing import Queue
import os


class GUI(QMainWindow, Ui_MainGUI):

    def __init__(self, core_queue, gui_queue,gui_id, parent=None):
        super(GUI, self).__init__(parent)
        self.setupUi(self)

        self.create_actions()

        self.callback_functions = {
            'do_create_plugin' : self.do_create_plugin,
            'do_delete_plugin' : self.do_delete_plugin,
            'do_set_parameter' : self.do_set_parameter,
            'do_subscribe'     : self.do_subsribe,
            'do_unsubscribe'   : self.do_unsubscribe,
            'do_set_parameter' : self.do_set_parameter
        }

        self.gui_data = DGui()

        self.manager_overview = Overview(self.callback_functions)
        self.manager_overview.dgui = self.gui_data
        self.setWindowTitle('PaPI')

        self.core_queue = core_queue
        self.gui_queue = gui_queue

        self.gui_id = gui_id

        self.count = 0

        # create a timer and set interval for processing events with working loop
        self.working_interval = 40
        QtCore.QTimer.singleShot(self.working_interval, self.gui_working_v2)

        # switch case for event processing
        self.process_event = {  'new_data': self.process_new_data_event,
                                'close_programm': self.process_close_program_event,
                                'check_alive_status': self.process_check_alive_status,
                                'create_plugin':self.process_create_plugin,
                                'update_meta': self.process_update_meta,
                                'plugin_closed': self.process_plugin_closed,
                                'set_parameter': self.process_set_parameter
        }


        self.log = ConsoleLog(1, 'Gui-Process: ')

        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["plugin","papi/plugin"])

        self.log.printText(1,'Gui: Gui process id: '+str(os.getpid()))

        self.stefans_text_field.setText('1')
        # -------------------------------------
        # Create actions for buttons
        # -------------------------------------

        self.buttonCreatePlugin.clicked.connect(self.create_plugin)
        self.buttonCreateSubscription.clicked.connect(self.create_subscription)
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

        # -------------------------------------
        # Set Tooltipps for buttons
        # -------------------------------------

        self.buttonExit.setToolTip("Exit PaPI")
        self.buttonCreatePlugin.setToolTip("Add New Plugin")
        self.buttonCreateSubscription.setToolTip("Create New Subscription")
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
        AddPlu = AddPlugin(self.callback_functions)
        AddPlu.setDGui(self.gui_data)
        AddPlu.show()
        AddPlu.raise_()
        AddPlu.activateWindow()
        r = AddPlu.exec_()

    def create_subscription(self):
        """
        This function is called to create an QDialog, which is used to create a subscription for a single Plugin
        :return:
        """

        AddSub = AddSubscriber(self.callback_functions)
        AddSub.setDGui(self.gui_data)
        AddSub.show()
        AddSub.raise_()
        AddSub.activateWindow()
        r = AddSub.exec_()

    def menu_license(self):
        pass

    def menu_quit(self):
        self.close()
        pass

    def ap_overview(self):
        self.manager_overview.show()
        pass

    def closeEvent(self, *args, **kwargs):
        opt = DOptionalData()
        opt.reason = 'User clicked close Button'
        event = PapiEvent(self.gui_id, 0, 'instr_event','close_program',opt)
        self.core_queue.put(event)

        self.manager_overview.close()
        self.close()

    def stefan_at_his_best(self):
        #s = self.stefans_text_field.text()
        #val = float(s)

        #self.do_set_parameter('Add1','Count',val)

        #event = PapiEvent(self.gui_id,2,'instr_event','stop_plugin',None)
        #self.core_queue.put(event)
        self.do_subsribe(3,2,'SinMit_f3',[2])
        #pl = self.gui_data.get_dplugin_by_uname('Sinus1')
        #b = pl.get_dblock_by_name('SinMit_f3')
        #print(b.signal_names_internal)

    def stefan(self):
        self.count += 1

        op=2

        if op == 0:
            # 1 test uname subsribe

            self.do_create_plugin('Fourier_Rect','Four')    #id 2
            self.do_create_plugin('Add','Add1')             #id 3
            self.do_create_plugin('Plot','Plot1')           #id 4

            time.sleep(0.1)
            self.do_subsribe(3,2,'Rect1')
            self.do_subsribe(4,3,'AddOut1')

        if op == 1:
            # 1 Sinus IOP und 1 Plot
            opt = DOptionalData()
            opt.plugin_identifier = 'Sinus'
            opt.plugin_uname = 'Sinus1'
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt)  #id 2
            self.core_queue.put(event)

            opt = DOptionalData()
            opt.plugin_identifier = 'Plot'
            opt.plugin_uname = 'Plot'
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt) #id 3
            self.core_queue.put(event)

            time.sleep(2)

            opt =  DOptionalData()
            opt.source_ID = 2
            opt.block_name = 'SinMit_f1'
            event = PapiEvent(3,0,'instr_event','subscribe',opt)
            self.core_queue.put(event)

        if op == 2:
            self.do_create_plugin('Sinus','Sinus1') #id 2
            self.do_create_plugin('Plot','Plot1')   #id 3
            #self.do_create_plugin('Plot','Plot2')   #id 4

            time.sleep(0.1)

            #self.do_subsribe(3,2,'SinMit_f3',2)
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

    def process_plugin_closed(self, event):
        """
        Processes plugin_closed event.
        Gui now knows, that a plugin was closed by core and needs to update its DGui data base
        :param event:
        :type event: PapiEvent
        :return:
        """
        opt = event.get_optional_parameter()
        # remove plugin from DGui data base
        if self.gui_data.rm_dplugin(opt.plugin_id) is True:
            self.log.printText(1,'plugin_closed, Plugin with id: '+str(opt.plugin_id)+'was removed in GUI')
        else:
            self.log.printText(1,'plugin_closed, Plugin with id: '+str(opt.plugin_id)+'was NOT removed in GUI')

    def process_new_data_event(self, event):
        """
        Core sent a new data event to gui. Gui now needs to find the destination plugin and call its execute function
        with the new data.
        :param event: event to process
        :type event: PapiEvent
        :type dplugin: DPlugin
        """
        # debug print
        self.log.printText(2,'new data event')
        # get list of destination IDs
        dID_list = event.get_destinatioID()
        # get optional data of event
        opt = event.get_optional_parameter()
        # iterate over destination list
        for dID in dID_list:
            # get destination plugin from DGUI
            dplugin = self.gui_data.get_dplugin_by_id(dID)
            # check if it exists
            if dplugin != None:
                # it exists, so call its execute function
                dplugin.plugin.execute(dplugin.plugin.demux(opt.data_source_id, opt.block_name, opt.data))
            else:
                # plugin does not exist in DGUI
                self.log.printText(1,'new_data, Plugin with id  '+str(dID)+'  does not exist in DGui')

    def process_create_plugin(self, event):
        """
        Processes the create Plugin event. This event got sent by core to GUI.
        Gui now needs to add a new plugin to DGUI and decide whether it is a plugin running in the GUI process or not.
        :param event: event to process
        :type event: PapiEvent
        :type dplugin: DPlugin
        """
        # get optional data: the plugin id, identifier and uname
        opt = event.get_optional_parameter()
        id = opt.plugin_id
        plugin_identifier = opt.plugin_identifier
        uname = opt.plugin_uname
        # config for passsing additional information to the plugin at the moment of creation
        config = opt.plugin_config

        # debug print
        self.log.printText(2,'create_plugin, Try to create plugin with Name  '+plugin_identifier+ " and UName " + uname )

        # collect plugin in folder for yapsy manager
        self.plugin_manager.collectPlugins()
        # get the plugin object from yapsy manager
        plugin_orginal = self.plugin_manager.getPluginByName(plugin_identifier)

        # check for existance
        if plugin_orginal is None:
            # plugin with given identifier does not exist
            self.log.printText(1, 'create_plugin, Plugin with Name  ' + plugin_identifier + '  does not exist in file system')
            # end function
            return -1

        # plugin seems to exist, so get the path of the plugin file
        imp_path = plugin_orginal.path + ".py"
        # build a loader object for this plugin
        loader = importlib.machinery.SourceFileLoader(plugin_orginal.name.lower(), imp_path)
        # load the plugin source code
        current_modul = loader.load_module()
        # build the plugin class name for usage
        class_name = plugin_orginal.name[:1].upper() + plugin_orginal.name[1:]
        # get the plugin class of the source code loaded and init class as a new object
        plugin = getattr(current_modul, class_name)()
        #
        config['do_set_parameter'] = self.callback_functions['do_set_parameter']
        # check if plugin in ViP (includes pcp) or something which is not running in the gui process
        if plugin.get_type() == "ViP":
            # plugin in running in gui process
            # add a new dplugin object to DGui and set its type and uname
            dplugin =self.gui_data.add_plugin(None,None,False,self.gui_queue,plugin,id)
            dplugin.uname = uname
            dplugin.type = opt.plugin_type

            # call the init function of plugin and set queues and id
            dplugin.plugin.init_plugin(self.core_queue, self.gui_queue, dplugin.id)

            # set name to config object
            config['name'] = dplugin.uname
            # call the plugin developers init function with config
            dplugin.plugin.start_init(config)
            # add a window to gui for new plugin and show it
            self.scopeArea.addSubWindow(dplugin.plugin.get_sub_window())
            dplugin.plugin.get_sub_window().show()

            # debug print
            self.log.printText(1,'create_plugin, Plugin with name  '+str(uname)+'  was started as ViP')

        else:
            # plugin will not be running in gui process, so we just need to add information to DGui
            # so add a new dplugin to DGUI and set name und type
            dplugin =self.gui_data.add_plugin(None,None,True,None,plugin,id)
            dplugin.uname = uname
            dplugin.type = opt.plugin_type
            # debug print
            self.log.printText(1,'create_plugin, Plugin with name  '+str(uname)+'  was added as non ViP')

    def process_close_program_event(self, event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        self.log.printText(1,'event: close_progam was received but there is no action for it')
        pass

    def process_check_alive_status(self, event):
        """
        Gui received check_alive request form core, so gui will respond to it
        :param event: event to process
        :type event: PapiEvent
        :type dplugin: DPlugin
        """
        # send event from GUI to Core
        event = PapiEvent(1,0,'status_event','alive',None)
        self.core_queue.put(event)

    def process_update_meta(self, event):
        """
        Core sent new meta information of an existing plugin. This function will update DGui with these information
        :param event: event to process
        :type event: PapiEvent
        :type dplugin: DPlugin
        """
        # get information of event
        # TODO: pl_id should not be in the origin parameter
        opt = event.get_optional_parameter()
        pl_id = event.get_originID()

        # get plugin of which new meta should be updated
        dplugin = self.gui_data.get_dplugin_by_id(pl_id)
        # check if it exists
        if dplugin is not None:
            # plugin exists, so update its meta information
            dplugin.update_meta(opt.plugin_object)
            # check for block subscriber to update their meta as well
            blocks = dplugin.get_dblocks()
            for bname in blocks:
                block = blocks[bname]
                subscribers = block.get_subscribers()
                for sub in subscribers:
                    sub_plugin = self.gui_data.get_dplugin_by_id(sub)
                    if sub_plugin is not None:
                        sub_plugin.plugin.update_meta(block)

        else:
            # plugin does not exist
            self.log.printText(1,'update_meta, Plugin with id  '+str(pl_id)+'  does not exist')

    def process_set_parameter(self,event):
        """

        :param event:
        :return:
        """
        # debug print
        self.log.printText(2,'set parameter event')

        dID = event.get_destinatioID()
        # get optional data of event
        opt = event.get_optional_parameter()


        # get destination plugin from DGUI
        dplugin = self.gui_data.get_dplugin_by_id(dID)
        # check if it exists
        if dplugin != None:
            # it exists, so call its execute function
            dplugin.plugin.set_parameter_internal(opt.parameter_list)
        else:
            # plugin does not exist in DGUI
            self.log.printText(1,'set_parameter, Plugin with id  '+str(dID)+'  does not exist in DGui')

    def do_create_plugin(self, plugin_identifier, uname, config={}):
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
        # create new optional Data for event
        opt = DOptionalData()
        # set important information
        # plugin to create
        opt.plugin_identifier = plugin_identifier
        # uname to create plugin with
        opt.plugin_uname = uname
        # additional config
        opt.plugin_config = config
        # create event object and sent it to core
        event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt)
        self.core_queue.put(event)

    def do_delete_plugin(self, uname):
        """
        Delete plugin with given uname.
        :param uname: Plugin uname to delete
        :type uname: basestring
        :return:
        """
        #TODO: implement
        self.log.printText(1, " Do delete plugin with uname " + uname + '..NOT IMPLEMENTED YET ')

    def do_subsribe(self, subscriber_id, source_id, block_name, signal_index=None):
        """
        Something like a callback function for gui triggered events.
        In this case, user wants one plugin to subscribe another
        :param subscriber_id: Plugin id of plugin which should get the data
        :type subscriber_id: int
        :param source_id: plugin uname of plugin that should send the data
        :type source_id: int
        :param block_name: name of block to subscribe
        :type block_name: basestring
        :return:
        """
        #TODO: typo in function name
        # build optional data object and add id and block name to it
        opt = DOptionalData()
        opt.source_ID = source_id
        opt.block_name = block_name

        # pre check if subscription already exists
        dplug = self.gui_data.get_dplugin_by_id(source_id)
        if dplug is not None:
            block = dplug.get_dblock_by_name(block_name)
            if block is not None:
                subs_list = block.get_subscribers()
                if subscriber_id not in subs_list:
                    # send event with subscriber id as the origin to CORE
                    event = PapiEvent(subscriber_id, 0, 'instr_event', 'subscribe', opt)
                    self.core_queue.put(event)

        # change parameter of subscriber plugin for signal index
        self.do_set_signal_choice_parameter(subscriber_id, source_id, block_name, signal_index)


    def do_subscribe_uname(self,subscriber_uname,source_uname,block_name, signal_index = None):
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
        # placeholder for ids
        source_id = None
        subscriber_id = None

        # get plugin from DGui with given uname
        # purpose: get its id
        dplug = self.gui_data.get_dplugin_by_uname(subscriber_uname)

        # check for existance
        if dplug is not None:
            # it does exist, so get its id
            subscriber_id = dplug.id
        else:
            # plugin with uname does not exist
            self.log.printText(1, 'do_subscribe, sub uname worng')
            return -1

        # get plugin from DGui with given uname
        # purpose: get its id
        dplug2 = self.gui_data.get_dplugin_by_uname(source_uname)
        # check for existance
        if dplug2 is not None:
             # it does exist, so get its id
            source_id = dplug2.id
        else:
            # plugin with uname does not exist
            self.log.printText(1, 'do_subscribe, target uname  worng')
            return -1

        # call do_subscribe with ids to subscribe
        if source_id is not None and subscriber_id is not None:
            self.do_subsribe(subscriber_id, source_id, block_name, signal_index = None)

    def do_unsubscribe(self, subscriber_id, source_id, block_name):
        """
        Something like a callback function for gui triggered events.
        User wants one plugin to do not get any more data from another plugin
        :param subscriber_id: plugin id which wants to lose a data source
        :type subscriber_id: int
        :param source_id: plugin id of data source
        :type source_id: int
        :param block_name: name of block to unsubscribe
        :type block_name: basestring
        :return:
        """
        # create optional data with source id and block_name
        opt = DOptionalData()
        opt.source_ID = source_id
        opt.block_name = block_name
        # sent event to Core with origin subscriber_id
        event = PapiEvent(subscriber_id, 0, 'instr_event', 'unsubscribe', opt)
        self.core_queue.put(event)

    def do_unsubscribe_uname(self, subscriber_uname, source_uname, block_name):
        """
        Something like a callback function for gui triggered events.
        User wants one plugin to do not get any more data from another plugin
        :param subscriber_uname: plugin uname which wants to lose a data source
        :type subscriber_uname: basestring
        :param source_uname: plugin uname of data source
        :type source_uname: basestring
        :param block_name: name of block to unsubscribe
        :type block_name: basestring
        :return:
        """
        # placeholders for ids
        source_id = None
        subscriber_id = None

        # get plugin from DGui with given uname
        # purpose: get its id
        dplug = self.gui_data.get_dplugin_by_uname(subscriber_uname)
         # check for existance
        if dplug is not None:
            # it does exist, so get its id
            subscriber_id = dplug.id
        else:
            # plugin with uname does not exist
            self.log.printText(1, 'do_subscribe, sub uname worng')
            return -1

        # get plugin from DGui with given uname
        # purpose: get its id
        dplug2 = self.gui_data.get_dplugin_by_uname(source_uname)
        # check for existance
        if dplug2 is not None:
            # it does exist, so get its id
            source_id = dplug2.id
        else:
            # plugin with uname does not exist
            self.log.printText(1, 'do_subscribe, target uname  worng')
            return -1

        # call do_subscripe with ids to subscribe
        if subscriber_id is not None and source_id is not None:
            self.do_unsubscribe(subscriber_id, source_id, block_name)

    def do_set_signal_choice_parameter(self, subscriber_id, source_id, block_name, signal_index):
        """
        :param plugin_uname: name of plugin which owns the parameter
        :type plugin_uname: basestring
        """
        # get plugin from DGUI
        dplug = self.gui_data.get_dplugin_by_id(subscriber_id)
        # check for existance
        if dplug is not None:
            # it exists
            # get its parameter list
            parameters = dplug.get_parameters()
            # check if there are any parameter
            if parameters is not None:
                # there is a parameter list
                # get the parameter with parameter_name
                p = parameters['Signal_choice']
                # check if this specific parameter exists
                if p is not None:
                    # parameter with name parameter_name exists
                    for signal in signal_index:
                        p.value.append([source_id, block_name, signal])
                    # build an event to send this information to Core
                    opt = DOptionalData()
                    opt.parameter_list = [p]
                    opt.plugin_id = dplug.id
                    e = PapiEvent(self.gui_id,dplug.id,'instr_event','set_parameter',opt)
                    self.core_queue.put(e)


    def do_set_parameter(self, plugin_uname, parameter_name, value):
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
        # get plugin from DGUI
        dplug = self.gui_data.get_dplugin_by_uname(plugin_uname)
        # check for existance
        if dplug is not None:
            # it exists
            # get its parameter list
            parameters = dplug.get_parameters()
            # check if there are any parameter
            if parameters is not None:
                # there is a parameter list
                # get the parameter with parameter_name
                p = parameters[parameter_name]
                # check if this specific parameter exists
                if p is not None:
                    # parameter with name parameter_name exists
                    # check new value against type and range
                    # TODO: check against range AND type of parameter
                    if self.check_range_of_value(value,p.range):
                        # new values meets requirements
                        # set new value
                        p.value = value
                        # build an event to send this information to Core
                        opt = DOptionalData()
                        opt.parameter_list = [p]
                        opt.plugin_id = dplug.id
                        e = PapiEvent(self.gui_id,dplug.id,'instr_event','set_parameter',opt)
                        self.core_queue.put(e)
                    else:
                        # value did not pass value check
                        self.log.printText(1,'do_set_parameter, value out of range')

    def check_range_of_value(self, value, ranges):
        min_val = ranges[0]
        max_val = ranges[1]
        if value > max_val:
            return False
        if value < min_val:
            return False
        return True


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
