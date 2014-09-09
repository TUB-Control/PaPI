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
Stefan Ruppin
"""

__author__ = 'control'

import os
from multiprocessing import Process, Queue

from yapsy.PluginManager import PluginManager
from threading import Timer

from papi.PapiEvent import PapiEvent
from papi.data.DCore import DCore
from papi.data.DPlugin import DPlugin
from papi.ConsoleLog import ConsoleLog
from papi.gui.gui_main import startGUI
from papi.data.DOptionalData import DOptionalData




class Core:
    def __init__(self):
        """
        Init funciton of core.
        Will create all data needed to use core and core.run() function
        :return:
        """
        # switch case structure for processing incoming events
        self.__process_event_by_type__ = {  'status_event': self.__process_status_event__,
                                            'data_event': self.__process_data_event__,
                                            'instr_event': self.__process_instr_event__,
        }

        self.__process_status_event_l__ = { 'start_successfull': self.__process_start_successfull__,
                                            'start_failed': self.__process_start_failed__,
                                            'alive': self.__process_alive__,
                                            'join_request': self.__process_join_request__
        }

        self.__process_data_event_l__ = {   'new_data': self.__process_new_data__,
                                            'new_block': self.__process_new_block__,
                                            'new_parameter': self.__process_new_parameter__
        }

        self.__process_instr_event_l__ = { 'create_plugin': self.__process_create_plugin__,
                                           'stop_plugin': self.__process_stop_plugin__,
                                            'close_program':self.__process_close_programm__,
                                            'subscribe': self.__process_subscribe__,
                                            'unsubscribe':self.__process_unsubsribe__,
                                            'set_parameter': self.__process_set_parameter__
        }

        #creating the main core data object DCore and core queue
        self.core_data = DCore()
        self.core_event_queue = Queue()
        self.core_goOn = 1
        self.core_id = 0

        # setting up the yapsy plguin manager for directory structure
        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["plugin","papi/plugin"])

        # define gui information. ID and alive status as well as gui queue for events
        self.gui_event_queue = Queue()
        self.gui_id = self.core_data.create_id()
        self.gui_alive = False

        # set information for console logging part (debug information)
        self.msg_lvl = 1
        self.log = ConsoleLog(self.msg_lvl,'Core-Process: ')

        # define variables for check alive system, e.a. timer and counts
        self.enable_check_alive_status = True
        self.alive_intervall = 2  # in seconds
        self.alive_count_max = 200
        self.alive_timer = Timer(self.alive_intervall,self.check_alive_callback)
        self.alive_count = 0
        self.gui_alive_count = 0

    def run(self):
        """
        Main operation function of core.
        Got Event loop in here.
        :return:
        """
        # some start up information
        self.log.printText(1,'Initialize PaPI - Plugin based Process Interaction')
        self.log.printText(1,'core process id: '+str(os.getpid()))

        # check PlugIn directory for Plugins and collect them
        self.plugin_manager.collectPlugins()

        # start the GUI process to show GUI, set GUI alive status to TRUE
        self.gui_process = Process(target=startGUI, args=(self.core_event_queue,self.gui_event_queue,self.gui_id))
        self.gui_process.start()
        self.gui_alive = True

        # start the check alive timer
        if self.enable_check_alive_status is True:
            self.alive_timer.start()

        # core main operation loop
        while self.core_goOn:
            # get event from queue, blocks until there is a new event
            event = self.core_event_queue.get()

            # debung out
            self.log.printText(2,'Event->'+event.get_eventtype()+'   '+event.get_event_operation())

            # process the next event of queue
            self.__process_event__(event)

            # check if there are still plugins alive or gui is still alive before ending core main loop
            self.core_goOn = self.core_data.get_dplugins_count() != 0 or self.gui_alive

        # core main loop ended, so cancel active alive timer
        self.alive_timer.cancel()

        # core finished operation and did clean shutdown
        self.log.printText(1,'Core finished operation')

    def send_alive_check_events(self):
        """
        function for check_alive_status timer to send check_alive events to all running processes
        :return:
        """
        # get list of all plugins [hash: id->dplug]
        dplugs = self.core_data.get_all_plugins()
        for id in dplugs:
            # get dplug object
            plug = dplugs[id]
            # check if this plugins runs in a separate process
            if plug.own_process is True:
                # send check_alive_status event to plugin process (via queue)
                event = PapiEvent(self.core_id,plug.id,'status_event','check_alive_status',None)
                plug.queue.put(event)

        # send check_alive_status event to gui process (via queue)
        event = PapiEvent(self.core_id,self.gui_id,'status_event','check_alive_status',None)
        self.gui_event_queue.put(event)

    def handle_alive_situation(self):
        """
        Function which handles the check for the alive situation of all plugins in data base
        Will distribute to error_handling methods to handle dead processes
        :return:
        """
        #get all plugins from core data [hash: id->DPlugin]
        dplugs = self.core_data.get_all_plugins()
        for id in dplugs:
            # get DPlugin object
            plug = dplugs[id]
            # check if plugins runs in a separate process
            if plug.own_process is True:
                # check if counts are equal: equal indicates that plugin is alive
                if plug.alive_count is self.alive_count:
                    self.log.printText(2,'Plugin '+plug.uname+' is still alive')
                    # change plugin state in DCore
                    plug.state = 'alive'
                else:
                    # Plugin is not alive anymore, so do error handling
                    self.plugin_process_is_dead_error_handler(plug)

        # check for gui status and do error handling
        if self.gui_alive_count is self.alive_count:
            self.log.printText(2,'GUI  is still ALIVE')
        else:
            self.gui_is_dead_error_handler()

    def gui_is_dead_error_handler(self):
        """
        error handler when gui is dead
        :return:
        """
        self.log.printText(1,'GUI  is  DEAD')
        self.log.printText(1,'core count: '+str(self.alive_count)+' vs. '+ str(self.gui_alive_count)+' :gui count')

    def plugin_process_is_dead_error_handler(self, dplug):
        """
        Error handler for a dead plugin process
        :param dplug: Plugin which is dead
        :type dplug: DPlugin
        :return:
        """
        self.log.printText(1,'Plugin '+dplug.uname+' is DEAD')
        self.log.printText(1,'core count: '+str(self.alive_count)+' vs. '+ str(dplug.alive_count)+' :plugin count')
        dplug.state = 'dead'
        self.update_meta_data_to_gui(dplug.id)

    def check_alive_callback(self):
        """
        callback function for check_alive status timer
        handles sending events to processes and checking their answer
        :return:
        """
        self.log.printText(2,'check alive')

        # check for answer status of all plugins
        self.handle_alive_situation()

        # increase the global check_alive counter
        self.alive_count += 1
        self.alive_count = self.alive_count % self.alive_count_max

        # send new check alive events to plugins
        self.send_alive_check_events()

        # start a new one shot timer with this callback function
        if self.enable_check_alive_status is True:
            self.alive_timer = Timer(self.alive_intervall,self.check_alive_callback)
            self.alive_timer.start()

    def update_meta_data_to_gui(self,pl_id):
        """
        On call this function will send the meta information of pl_id to GUI
        :param pl_id: id of plugin with new meta information
        :return:
        """
        # get DPlugin object with id and check if it exists
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            # DPlugin object exists,so build optinalData for Event
            o = DOptionalData()
            # get meta information of DPlugin
            o.plugin_object = dplugin.get_meta()
            # build event and send it to GUI with meta information
            eventMeta = PapiEvent(pl_id,self.gui_id,'instr_event','update_meta',o)
            self.gui_event_queue.put(eventMeta)
            return 1
        else:
            # Dplugin object with pl_id does not exist in DCore of core
            self.log.printText(1,'update_meta, cannonot update meta information because there is no plugin with id: '+str(pl_id))
            return -1

    # ------- Event processing initial stage ---------
    def __process_event__(self,event):
        """
        Initial stage of event processing, dividing to event type
        :param event: event to process
        :type event: PapiEvent
        """
        t = event.get_eventtype()
        self.__process_event_by_type__[t](event)

    # ------- Event processing first stage ---------
    def __process_status_event__(self,event):
        """
        First stage of event processing, deciding which status_event this is
        :param event: event to process
        :type event: PapiEvent
        """
        op = event.get_event_operation()
        return self.__process_status_event_l__[op](event)

    def __process_data_event__(self,event):
        """
        First stage of event processing, deciding which data_event this is
        :param event: event to process
        :type event: PapiEvent
        """
        op = event.get_event_operation()
        return self.__process_data_event_l__[op](event)

    def __process_instr_event__(self,event):
        """
        First stage of event processing, deciding which instr_event this is
        :param event: event to process
        :type event: PapiEvent
        """
        op = event.get_event_operation()
        return self.__process_instr_event_l__[op](event)

    # ------- Event processing second stage: status events ---------
    def __process_start_successfull__(self,event):
        """
        Process start_successfull event
        :param event: event to process
        :type event: PapiEvent
        """
        # get plugin from DCore with id of event origin and check if it exists
        dplug = self.core_data.get_dplugin_by_id(event.get_originID())
        if (dplug != None):
            # plugin exists and sent successfull event, so change it state
            dplug.state = 'start_successfull'
            return 1
        else:
            # plugin does not exist
            self.log.printText(1,'start_successfull_event, Event with id ' +str(event.get_originID())+ ' but plugin does not exist')
            return -1

    def __process_start_failed__(self,event):
        """
        Process start failed event and do error handling
        :param event: event to process
        :type event: PapiEvent
        """
        # get plugin from DCore with id of event origin and check if it exists
        dplug = self.core_data.get_dplugin_by_id(event.get_originID())
        if (dplug != None):
            # plugin exists but start failed, so change it state
            dplug.state = 'start_failed'
            return 1
        else:
            # plugin does not exist in DCore
            self.log.printText(1,'start_failed_event, Event with id ' +str(event.get_originID())+ ' but plugin does not exist')
            return -1

    def __process_alive__(self,event):
        """
        Processes alive response from processes/plugins and GUI, organising the counter
        :param event: event to process
        :type event: PapiEvent
        """
        # get event origin
        oID = event.get_originID()
        # check if its the gui
        if oID is self.gui_id:
            # increment GUI counter
            self.gui_alive_count += 1
            self.gui_alive_count = self.gui_alive_count % self.alive_count_max
        else:
            # its not the Gui, so search for plugin in DCore
            dplug = self.core_data.get_dplugin_by_id(oID)
            # check if plugin exists. If plugin exists, increment its counter
            if dplug is not None:
                dplug.alive_count += 1
                dplug.alive_count = dplug.alive_count % self.alive_count_max
        return True

    def __process_join_request__(self,event):
        """
        Process join requests of processes
        :param event: event to process
        :type event: PapiEvent
        :type dplugin: DPlugin
        """
        # get event origin id and its corresponding plugin object
        pl_id = event.get_originID()
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        # check for existance
        if dplugin is not None:
            # get process of plugin and join it
            dplugin.process.join()
            # remove plugin from DCore, because process was joined
            if self.core_data.rm_dplugin(dplugin.id) is False:
                # remove failed
                self.log.printText(1,'join request, remove plugin with id '+str(dplugin.id)+'failed')
                return -1
            else:
                # remove from DCore in core successfull
                if self.gui_alive is True:
                    # GUI is still alive, so tell GUI, that this plugin was closed
                    opt = DOptionalData()
                    opt.plugin_id = dplugin.id
                    event = PapiEvent(self.core_id,self.gui_id,'status_event','plugin_closed',opt)
                    self.gui_event_queue.put(event)
                return 1
        else:
            # Plug does not exist
            self.log.printText(1,'join_request, Event with id ' +str(event.get_originID())+ ' but plugin does not exist')
            return -1

    # ------- Event processing second stage: data events ---------
    def __process_new_data__(self,event):
        """
        Process new_data event from plugins.
        Will do the routing: Subscriber/Subscription
        :param event: event to process
        :type event: PapiEvent
        :type tar_plug: DPlugin
        """
        # just proceed with new_data events if GUI is still alive (indicates that program will close)
        if self.gui_alive:
            # get event origin and optional parameter
            oID = event.get_originID()
            opt = event.get_optional_parameter()

            # get origin plugin from DCore
            dplug = self.core_data.get_dplugin_by_id(oID)
            # check for existence
            if dplug is not None:
                # get data block of DPlugin with block_name from event
                block= dplug.get_dblock_by_name(opt.block_name)
                # check for existence of block with block_bame
                if block is not None:
                    # get subscriber list of block
                    subscriber = block.get_subscribers()
                    # id list dummy for event destination id list
                    id_list = []
                    # for all subscriber in subscriber list
                    for sub_id in subscriber:
                        # get plugin with sub_id and check for existence
                        pl = self.core_data.get_dplugin_by_id(sub_id)
                        if pl is not None:
                            # plugin exists, check whether it is a ViP or not
                            if pl.type == 'ViP':
                                # Because its a ViP, we need a list of destination ID for new_data
                                id_list.append(pl.id)
                            else:
                                # Plugin is not running in GUI, so just 1:1 relation for event and destinations
                                new_event = PapiEvent(oID, [pl.id], 'data_event', 'new_data', event.get_optional_parameter())
                                pl.queue.put(new_event)
                        else:
                            # pluign with sub_id does not exist in DCore of core
                            self.log.printText(1, 'new_data, subscriber plugin with id '+str(sub_id)+' does not exists')
                            return -1
                    # check if our list with id is greater than 1, which will indicate that there is at least one ViP
                    # which will need to get this new data event
                    if len(id_list)> 0:
                        # send new_data event to GUI with id_list of destinations
                        new_event = PapiEvent(oID,id_list,'data_event','new_data',event.get_optional_parameter())
                        self.gui_event_queue.put(new_event)
                    # process new_data seemed correct
                    return 1
                else:
                    # block is None
                    self.log.printText(1, 'new_data, block with name '+opt.block_name+' does not exists')
                    return -1
            else:
                # Plugin of event origin does not exist in DCore of core
                self.log.printText(1,'new_data, Plugin with id  '+str(oID)+'  does not exist in DCore')
                return -1

    # ------- Event processing second stage: instr events ---------
    def __process_create_plugin__(self,event):
        """
        Processes create_plugin event.
        So it will create a plugin, start a process if needed, send events to GUI to create a plugin and do the pre configuration
        :param event:
        :param optData: optional Data Object of event
        :type event: PapiEvent
        :type optData: DOptionalData
        :return:
        """
        # get optData to get information about which plugin to start
        optData = event.get_optional_parameter()
        self.log.printText(2,'create_plugin, Try to create plugin with Name  '+optData.plugin_identifier+ " and UName " + optData.plugin_uname )

        # search yapsy plugin object with plugin_idientifier and check if it exists
        plugin = self.plugin_manager.getPluginByName(optData.plugin_identifier)
        if plugin == None:
            self.log.printText(1,'create_plugin, Plugin with Name  '+optData.plugin_identifier+'  does not exist in file system')
            return -1

        #creates a new plugin id because plugin exsits
        plugin_id = self.core_data.create_id()

        # checks if plugin is of not of type ViP or PCP, because these two will run in GUI process
        if plugin.plugin_object.get_type() != 'ViP' and plugin.plugin_object.get_type() != 'PCP':
            # So plugin will not run in GUI
            # it will need an own process and queue to function

            # create Queue for plugin process
            plugin_queue = Queue()

            # decide if plugin will need to get Data from another plugin
            if plugin.plugin_object.get_type()=='DPP':
                # plugin will get data from another, so make its execution triggered by events
                eventTriggered = True
            else:
                # stand alone plugin, so it will do its permanent execute loop
                eventTriggered = False

            # create Process object for new plugin
            # set parameter for work function of plugin, such as queues, id and eventTriggered
            PluginProcess = Process(target=plugin.plugin_object.work_process, args=(self.core_event_queue,plugin_queue,plugin_id,eventTriggered ) )
            PluginProcess.start()

            #Add new Plugin process to DCore
            dplug = self.core_data.add_plugin(PluginProcess, PluginProcess.pid, True, plugin_queue, plugin, plugin_id)
            dplug.uname = optData.plugin_uname
            dplug.type = plugin.plugin_object.get_type()
            dplug.alive_count = self.alive_count

            # change some attributes of optional data before sending it back to GUI for local creation
            optData.plugin_identifier = plugin.name
            optData.plugin_id = plugin_id
            optData.plugin_type = dplug.type

            # send create_plugin event to GUI for local creation, now with new information like id and type
            event = PapiEvent(0,self.gui_id,'instr_event','create_plugin',optData)
            self.gui_event_queue.put(event)
            return 1
        else:
            # Plugin will run in GUI, thats why core does not need to create a new process

            # Adding plugin information to DCore of core for organisation
            dplug = self.core_data.add_plugin(self.gui_process, self.gui_process.pid, False, self.gui_event_queue, plugin, plugin_id)
            dplug.uname = optData.plugin_uname
            dplug.type = plugin.plugin_object.get_type()

            # change some attributes of optional data before sending it back to GUI for local creation
            optData.plugin_identifier = plugin.name
            optData.plugin_id = plugin_id
            optData.plugin_type = dplug.type

            # send create_plugin event to GUI for local creation, now with new information like id and type
            event = PapiEvent(0,self.gui_id,'instr_event','create_plugin',optData)
            self.gui_event_queue.put(event)
            self.log.printText(2,'core sent create event to gui for plugin: '+str(optData.plugin_uname))
            return 1

    def __process_stop_plugin__(self,event):
        """
        Process stop_plugin event.
        Will send an event to destination plugin to close itself. Will lead to a join request of this plugin.
        :param event: event to process
        :type event: PapiEvent
        :type dplugin: DPlugin
        """
        # get destination id
        id = event.get_destinatioID()

        # get DPlugin object and check if plugin exists
        dplugin = self.core_data.get_dplugin_by_id(id)
        if dplugin is not None:
            # dplugin exist, get queue and route event to plugin
            dplugin.queue.put(event)
            return 1
        else:
            # DPlugin does not exist
            self.log.printText(1,'stop_plugin, plugin with id '+str(id)+' not found')
            return -1

    def __process_close_programm__(self,event):
        """
        This functions processes a close_programm event from GUI and
        sends events to all processes to close themselves
        :param event: event to process
        :type event: PapiEvent
        """

        # GUI wants to close, so join process
        self.gui_process.join()

        # Set gui_alive to false for core loop to know that is it closed
        self.gui_alive = False

        # get a list of all running plugIns
        all_plugins = self.core_data.get_all_plugins()

        # iterate through all plugins to send an event to tell them to quit and
        # response with a join_request
        toDelete =[]
        for dplugin_key in all_plugins:
            dplugin = all_plugins[dplugin_key]
            # just send event to plugins running in own process
            if dplugin.own_process:
                event = PapiEvent(0,dplugin.id,'instr_event','stop_plugin',None)
                dplugin.queue.put(event)
            else:
                toDelete.append(dplugin.id)

        for dplugin_ID in toDelete:
            self.core_data.rm_dplugin(dplugin_ID)

    def __process_subscribe__(self,event):
        """
        Process subscribe_event.
        Will set a new route in DCore for this two plugins to route new data events. Update of meta will be send to GUI.
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get event origin id and optional parameters
        opt = event.get_optional_parameter()
        oID = event.get_originID()

        # try subscibe for subsribe request
        if self.core_data.subscribe(oID, opt.source_ID, opt.block_name) is False:
            # subscribtion failed
            self.log.printText(1,'subscribe, something failed in subsription process with subscriber id: '+str(oID)+'..target id:'+str(opt.source_ID)+'..and block '+str(opt.block_name))
        else:
            # subscribtion correct
            self.log.printText(1,'subscribe, subscribtion correct: '+str(oID)+'->('+str(opt.source_ID)+','+str(opt.block_name)+')')
            self.update_meta_data_to_gui(oID)
            self.update_meta_data_to_gui(opt.source_ID)

    def __process_unsubsribe__(self,event):
        """
        Process unsubscribe_event. Will try to remove a subscription from DCore
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get event origin id and optional parameters
        opt = event.get_optional_parameter()
        oID = event.get_originID()
        # try to unsubscribe
        if self.core_data.unsubscribe(oID,opt.source_ID,opt.block_name) is False:
            # unsubscribe failed
            self.log.printText(1,'unsubscribe, something failed in unsubsription process with subscriber id: '+str(oID)+'..target id:'+str(opt.source_ID)+'..and block '+str(opt.block_name))
        else:
            # unsubscribe correct
            self.log.printText(1,'unsubscribe, unsubscribtion correct: '+str(oID)+'->('+str(opt.source_ID)+','+str(opt.block_name)+')')
            self.update_meta_data_to_gui(oID)
            self.update_meta_data_to_gui(opt.source_ID)

    def __process_set_parameter__(self,event):
        """
        Process set_parameter event. Core will just route this event from GUI to destination plugin and update DCore
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get destination id and optional parameter
        opt = event.get_optional_parameter()
        pl_id = event.get_destinatioID()

        # get DPlugin object of destination id from DCore and check for existence
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            # Plugin exists
            # get parameter list of plugin [hash]
            pl_parameter = dplugin.get_parameters()
            # looping through all parameter in events parameter list (parameters that changed)
            for new_para in opt.parameter_list:
                p = pl_parameter[new_para.name]
                # check if parameter exists in Dcore list
                if p is not None:
                    # it exists, so change its values
                    p.value = new_para.value
            # route the event to the destination plugin queue
            dplugin.queue.put(event)
            return 1
        else:
            # destination plugin does not exist
            self.log.printText(1,'set_paramenter, plugin with id '+str(pl_id)+' not found')
            return -1

    def __process_new_block__(self,event):
        """
        Processes new_block event.
        Will try to add a new data block to a DPlugin object
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get event origin id and optional parameter
        opt = event.get_optional_parameter()
        pl_id = event.get_originID()
        # get DPlugin object with origin id of event to add new parameter to THIS DPlugin
        dplugin =  self.core_data.get_dplugin_by_id(pl_id)
        # check for existence
        if dplugin is not None:
            # dplugin exists, so add blocks to DPlugin
            for b in opt.block_list:
                dplugin.add_dblock(b)
            # update meta information of GUI after new blocks were added
            self.update_meta_data_to_gui(pl_id)
            return 1
        else:
            # plugin does not exist
            self.log.printText(1,'new_block, plugin with id '+str(pl_id)+' not found')
            return -1

    def __process_new_parameter__(self,event):
        """
        Processes new parameter event. Adding a new parameter to DPluign in DCore and updating GUI information
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get event origin and optional parameter
        opt = event.get_optional_parameter()
        pl_id = event.get_originID()

        # get DPlugin object of event origin id which is the plugin that wants to add parameter
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            # Plugin exists so loop through parameter list to add all parameter
            for p in opt.parameter_list:
                # add parameter to DPlugin
                dplugin.add_parameter(p)
            # update meta of GUI to introduce new parameter to user
            self.update_meta_data_to_gui(pl_id)
            return 1
        else:
            # plugin does not exist
            self.log.printText(1,'new_parameter, plugin with id '+str(pl_id)+' not found')
            return -1



