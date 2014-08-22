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
import time
from multiprocessing import Process, Queue, Manager

from yapsy.PluginManager import PluginManager


from papi.PapiEvent import PapiEvent
from papi.DebugOut import debug_print
from papi.data.DCore import DCore
from papi.data.DPlugin import DPlugin
from papi.ConsoleLog import ConsoleLog
from papi.gui.gui_main import startGUI
from papi.data.DOptionalData import DOptionalData




class Core:

    def __init__(self):
        self.__process_event_by_type__ = {  'status_event': self.__process_status_event__,
                                            'data_event': self.__process_data_event__,
                                            'instr_event': self.__process_instr_event__,
        }
        self.__process_status_event_l__ = { 'start_successfull': self.__process_start_successfull__,
                                            'start_failed': self.__process_start_failed__,
                                            'check_alive_status': self.__process_check_alive__,
                                            'alive': self.__process_alive__,
                                            'join_request': self.__process_join_request__
        }
        self.__process_data_event_l__ = {   'new_data': self.__process_new_data__,
                                            'get_output_size': self.__process_get_output_size__,
                                            'response_output_size': self.__process_response_output_size__,
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

        self.msg_lvl = 1
        self.__debugLevel__ = 1
        self.__debug_var = ''

        self.core_data = DCore()

        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["plugin","papi/plugin"])

        self.core_event_queue = Queue()

        self.gui_event_queue = Queue()
        self.gui_id = self.core_data.create_id()

        self.gui_alive = 0

        self.core_goOn = 1

        self.log = ConsoleLog(self.msg_lvl,'Core-Process: ')

        self.core_id = 0


    def run(self):
        debug_print(self.__debugLevel__,'Core: initialize PaPI - Plugin based Process Interaction')
        debug_print(self.__debugLevel__, ['Core: core process id: ',os.getpid()] )

        # check PlugIn directory for Plugins and collect them
        self.plugin_manager.collectPlugins()

        self.gui_process = Process(target=startGUI, args=(self.core_event_queue,self.gui_event_queue,self.gui_id))
        self.gui_process.start()
        self.gui_alive = True

        debug_print(self.__debugLevel__,'Core:  entering event loop')
        while self.core_goOn:

            event = self.core_event_queue.get()

            self.log.printText(2,'Event->'+event.get_eventtype()+'   '+event.get_event_operation())

            self.__process_event__(event)

            self.core_goOn = self.core_data.get_dplugins_count() != 0


        self.log.printText(1,'Core finished operation')







    # ------- Event processing initial stage ---------
    def __process_event__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        t = event.get_eventtype()
        self.__process_event_by_type__[t](event)

    # ------- Event processing first stage ---------
    def __process_status_event__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        op = event.get_event_operation()
        return self.__process_status_event_l__[op](event)

    def __process_data_event__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        op = event.get_event_operation()
        return self.__process_data_event_l__[op](event)

    def __process_instr_event__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        op = event.get_event_operation()
        return self.__process_instr_event_l__[op](event)







    # ------- Event processing second stage: status events ---------

    def __process_start_successfull__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        self.__debug_var__ = 'start_successfull'
        dplug = self.core_data.get_dplugin_by_id(event.get_originID())
        if (dplug != None):
            dplug.state = 'start_successfull'
            return 1
        else:
            self.log.printText(1,'start_successfull_event, Event with id ' +str(event.get_originID())+ ' but plugin does not exist')
            return -1


    def __process_start_failed__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        self.__debug_var__ = 'start_failed'

        dplug = self.core_data.get_dplugin_by_id(event.get_originID())
        if (dplug != None):
            dplug.state = 'start_failed'
            return 1
        else:
            self.log.printText(1,'start_failed_event, Event with id ' +str(event.get_originID())+ ' but plugin does not exist')
            return -1


    def __process_check_alive__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        self.__debug_var__ = 'check_alive_status'
        return True


    def __process_alive__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        self.__debug_var__ = 'alive'
        return True


    def __process_join_request__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        self.__debug_var__ = 'join_request'

        pl_id = event.get_originID()
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if (dplugin != None):
            dplugin.process.join()
            return self.core_data.rm_dplugin(dplugin.id)
        else:
            self.log.printText(1,'join_request, Event with id ' +str(event.get_originID())+ ' but plugin does not exist')
            return -1







    # ------- Event processing second stage: data events ---------

    def __process_new_data__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type tar_plug: DPlugin
        """
        self.__debug_var__ = 'new_data'

        if self.gui_alive:
            oID = event.get_originID()
            opt = event.get_optional_parameter()

            dplug = self.core_data.get_dplugin_by_id(oID)
            if dplug != None:
                block= dplug.get_dblock_by_name(opt.block_name)
                subscriber = block.get_subscribers()
                #print(subscriber)
                for sub_id in subscriber:
                    pl = self.core_data.get_dplugin_by_id(sub_id)
                    #TODO: just 1 Event for multiple VIP...
                    new_event = PapiEvent(oID,pl.id,'data_event','new_data',event.get_optional_parameter())
                    pl.queue.put(new_event)
                return 1
            else:
                self.log.printText(1,'new_data, Plugin with id  '+str(oID)+'  does not exist in DCore')
                return -1
        return 1


    def __process_get_output_size__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        self.__debug_var__ = 'get_output_size'
        return True


    def __process_response_output_size__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
        """
        self.__debug_var__ = 'response_output_size'
        return True








    # ------- Event processing second stage: instr events ---------

    def __process_create_plugin__(self,event):
        """
         :param event: event to process
         :param optData: optional Data Object of event
         :type event: PapiEvent
         :type optData: DOptionalData
        """
        self.__debug_var__ = 'create_plugin'


        #decide which Plugin to start
        optData = event.get_optional_parameter()

        plugin = self.plugin_manager.getPluginByName(optData.plugin_identifier)

        if plugin == None:
            self.log.printText(1,'create_plugin, Plugin with Name  '+optData.plugin_identifier+'  does not exist in file system')
            return -1

        #creates a new plugin id
        plugin_id = self.core_data.create_id()


        if plugin.plugin_object.get_type() != 'ViP':
            plugin_queue = Queue()

            if plugin.plugin_object.get_type()=='DPP':
                eventTriggered = True
            else:
                eventTriggered = False

            # create Process object for new plugin
            PluginProcess = Process(target=plugin.plugin_object.work_process, args=(self.core_event_queue,plugin_queue,plugin_id,eventTriggered ) )
            PluginProcess.start()

            #Add new Plugin process to DCore
            dplug = self.core_data.add_plugin(PluginProcess, PluginProcess.pid, True, plugin_queue, plugin, plugin_id)
            dplug.uname = optData.plugin_uname


            # set plugin info for gui
            opt = DOptionalData()
            opt.plugin_identifier = plugin.name
            opt.plugin_id = plugin_id
            opt.plugin_uname = dplug.uname
            event = PapiEvent(0,plugin_id,'instr_event','create_plugin',opt)
            self.gui_event_queue.put(event)


        else:
            dplug = self.core_data.add_plugin(self.gui_process, self.gui_process.pid, False, self.gui_event_queue, plugin, plugin_id)
            dplug.uname = optData.plugin_uname

            #event = PapiEvent(0,plugin_id,'instr_event','create_plugin',[plugin.name,plugin_id,dplug.uname])
            opt = DOptionalData()
            opt.plugin_identifier = plugin.name
            opt.plugin_id = plugin_id
            opt.plugin_uname = dplug.uname
            event = PapiEvent(0,plugin_id,'instr_event','create_plugin',opt)
            self.gui_event_queue.put(event)
            self.log.printText(1,'core sent create event to gui for plugin: '+str(opt.plugin_uname))

        return True


    def __process_stop_plugin__(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        self.__debug_var__ = 'stop_plugin'

        id = event.get_destinatioID()

        dplugin =  self.core_data.get_dplugin_by_id(id)
        if dplugin != None:
            dplugin.queue.put(event)
            return 1
        else:
            self.log.printText(1,'stop_plugin, plugin with id '+str(id)+' not found')
            return -1


    def __process_close_programm__(self,event):
        """
         This functions processes a close_programm event from GUI and
         sends events to all processes to close themselves

         :param event: event to process
         :type event: PapiEvent
        """
        self.__debug_var__ = 'close_program'

        # GUI wants to close, so join process
        self.gui_process.join()

        # Set gui_alive to false for core loop to know that is it closed
        self.gui_alive = 0

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
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """

        opt = event.get_optional_parameter()
        oID = event.get_originID()



        if self.core_data.subscribe(oID, opt.source_ID, opt.block_name) == False:
            self.log.printText(1,'subscribe, something failed in subsription process with subscriber id: '+str(oID)+'..target id:'+str(opt.source_ID)+'..and block '+str(opt.block_name))
        else:
            self.log.printText(1,'subscribe, subscribtion correct: '+str(oID)+'->('+str(opt.source_ID)+','+str(opt.block_name)+')')

        self.update_meta_data_to_gui(oID)
        self.update_meta_data_to_gui(opt.source_ID)

        pass


    def __process_unsubsribe__(self,event):
        """
        Case A:
        Plugin wants to unsubscribe from another plugin
        PapiEvent(oID,CoreID,'instr_event','unsubscribe',SourceID)
        Case B:
         Plugin wants to close all his subscribtions
        PapiEvent(oID,CoreID,'instr_event','unsubscribe','all'
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        pass


    def __process_set_parameter__(self,event):
        """
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        opt = event.get_optional_parameter()
        pl_id = opt.plugin_id

        dplugin =  self.core_data.get_dplugin_by_id(pl_id)
        if dplugin != None:
            dplugin.queue.put(event)
            return 1
        else:
            self.log.printText(1,'set_paramenter, plugin with id '+str(pl_id)+' not found')
            return -1


    def __process_new_block__(self,event):
        """
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        opt = event.get_optional_parameter()
        pl_id = event.get_originID()
        dplugin =  self.core_data.get_dplugin_by_id(pl_id)

        if dplugin != None:
            for b in opt.block_list:
                dplugin.add_dblock(b)

            self.update_meta_data_to_gui(pl_id)
        else:
            self.log.printText(1,'new_block, plugin with id '+str(pl_id)+' not found')
        return -1


    def __process_new_parameter__(self,event):
        """
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        opt = event.get_optional_parameter()
        pl_id = event.get_originID()

        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin != None:
            for p in opt.parameter_list:
                dplugin.add_parameter(p)
            self.update_meta_data_to_gui(pl_id)
            return 1
        else:
            self.log.printText(1,'new_parameter, plugin with id '+str(pl_id)+' not found')
            return -1



    def update_meta_data_to_gui(self,pl_id):
        """
        :param event: event to process
        :type event: PapiEvent
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin != None:
            o = DOptionalData()
            o.plugin_object = dplugin.get_meta()
            eventMeta = PapiEvent(pl_id,self.gui_id,'instr_event','update_meta',o)
            self.gui_event_queue.put(eventMeta)