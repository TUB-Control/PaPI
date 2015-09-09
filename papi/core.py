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

Contributors
Stefan Ruppin
"""

__author__ = 'ruppin'

import os
from multiprocessing import Process, Queue
from threading import Timer
import copy
from papi.yapsy.PluginManager import PluginManager
from papi.data.DCore import DCore
from papi.data.DPlugin import DPlugin, DBlock
from papi.data.DSignal import DSignal
from papi.ConsoleLog import ConsoleLog
from papi.data.DOptionalData import DOptionalData

import papi.constants as pc

from papi.constants import CORE_PROCESS_CONSOLE_IDENTIFIER, CORE_CONSOLE_LOG_LEVEL, CORE_PAPI_CONSOLE_START_MESSAGE, \
    CORE_CORE_CONSOLE_START_MESSAGE, CORE_ALIVE_CHECK_ENABLED, \
    CORE_STOP_CONSOLE_MESSAGE, CORE_ALIVE_CHECK_INTERVAL, CORE_ALIVE_MAX_COUNT

from papi.constants import PLUGIN_ROOT_FOLDER_LIST, PLUGIN_VIP_IDENTIFIER, \
    PLUGIN_DPP_IDENTIFIER, PLUGIN_STATE_PAUSE, PLUGIN_STATE_RESUMED, \
    PLUGIN_STATE_START_SUCCESFUL, PLUGIN_STATE_START_FAILED, PLUGIN_STATE_ALIVE, PLUGIN_STATE_STOPPED, \
    PLUGIN_STATE_DEAD

import papi.error_codes as ERROR

from papi.event.event_base import PapiEventBase
import papi.event as Event

import signal

def run_core_in_own_process(gui_queue, core_queue, gui_id):
    core = Core(None,False,False)
    core.gui_id = gui_id
    core.core_event_queue = core_queue
    core.gui_event_queue = gui_queue

    core.run()

class Process_dummy(object):
    def __init__(self):
        self.pid= 0


class Core:
    def __init__(self, gui_start_function = None, use_gui=True, is_parent = True, gui_process_pid = None, args=None):
        """
        Init funciton of core.
        Will create all data needed to use core and core.run() function

        .. document private functions
        .. automethod:: __*
        """
        self.is_parent = is_parent

        # switch case structure for processing incoming events
        self.__process_event_by_type__ = {'status_event': self.__process_status_event__,
                                          'data_event': self.__process_data_event__,
                                          'instr_event': self.__process_instr_event__,
        }

        self.__process_status_event_l__ = {'start_successfull': self.__process_start_successfull__,
                                           'start_failed': self.__process_start_failed__,
                                           'alive': self.__process_alive__,
                                           'join_request': self.__process_join_request__,
                                           'plugin_stopped': self.__process_plugin_stopped__
        }

        self.__process_data_event_l__ = {'new_data':                self.__process_new_data__,
                                         'new_block':               self.__process_new_block__,
                                         'new_parameter':           self.__process_new_parameter__,
                                         'edit_dplugin':            self.__process_edit_dplugin,
                                         'edit_dplugin_by_uname':   self.__process_edit_dplugin_by_uname__,
                                         'delete_block':            self.__process_delete_block__,
                                         'delete_parameter':        self.__delete_parameter__
        }

        self.__process_instr_event_l__ = {'create_plugin':          self.__process_create_plugin__,
                                          'stop_plugin':            self.__process_stop_plugin__,
                                          'stop_plugin_by_uname':   self.__process_stop_plugin_by_uname__,
                                          'close_program':          self.__process_close_programm__,
                                          'subscribe':              self.__process_subscribe__,
                                          'subscribe_by_uname':     self.__process_subscribe_by_uname__,
                                          'unsubscribe':            self.__process_unsubsribe__,
                                          'set_parameter':          self.__process_set_parameter__,
                                          'pause_plugin':           self.__process_pause_plugin__,
                                          'resume_plugin':          self.__process_resume_plugin__,
                                          'start_plugin':           self.__process_start_plugin__
        }

        self.args = args

        # creating the main core data object DCore and core queue
        self.core_data = DCore()
        self.core_goOn = 1
        self.core_id = 0

        # setting up the yapsy plguin manager for directory structure
        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(PLUGIN_ROOT_FOLDER_LIST)

        # define gui information. ID and alive status as well as gui queue for events
        self.gui_id = self.core_data.create_id()
        self.gui_alive = False
        self.use_gui = use_gui

        # set information for console logging part (debug information)

        self.log = ConsoleLog(CORE_CONSOLE_LOG_LEVEL, CORE_PROCESS_CONSOLE_IDENTIFIER)
        self.log.lvl = pc.CORE_CONSOLE_LOG_LEVEL

        try:
            if args:
                if args.debug_level:
                    self.log.lvl = int(args.debug_level)
        except:
            pass

        # define variables for check alive system, e.a. timer and counts
        self.alive_intervall = CORE_ALIVE_CHECK_INTERVAL
        self.alive_count_max = CORE_ALIVE_MAX_COUNT
        self.alive_timer = Timer(self.alive_intervall, self.check_alive_callback)
        self.alive_count = 0
        self.gui_alive_count = 0

        self.core_event_queue = None
        self.gui_event_queue = None
        self.gui_process = Process_dummy()
        self.gui_process.pid = gui_process_pid
        self.gui_alive = True

        if is_parent:
            if gui_start_function is None:
                raise Exception('Core started with wrong arguments')
            if use_gui is True and is_parent is False:
                 raise Exception('Core started with wrong arguments')
            if is_parent is False and gui_process_pid is None:
                 raise Exception('Core started with wrong arguments')

            self.gui_start_function = gui_start_function
            self.core_event_queue = Queue()
            self.gui_event_queue = Queue()


        self.core_delayed_operation_queue = []

        signal.signal(signal.SIGINT, lambda a,b,c=self: self.signal_handler(a,b,c))

    def run(self):
        """
        Main operation function of core.
        Event loop is in here.

        :return:
        """
        # some start up information
        self.log.printText(1, CORE_PAPI_CONSOLE_START_MESSAGE)
        self.log.printText(1, CORE_CORE_CONSOLE_START_MESSAGE + ' .. Process id: ' + str(os.getpid()))

        # start the GUI process to show GUI, set GUI alive status to TRUE

        if self.use_gui and self.is_parent:
            self.gui_process = Process(target=self.gui_start_function,
                                       args=(self.core_event_queue, self.gui_event_queue, self.gui_id, self.args))
            self.gui_process.start()

        # start the check alive timer
        if CORE_ALIVE_CHECK_ENABLED is True:
            self.log.printText(1, 'Alive check of processes is enabled')
            self.alive_timer.start()

        # core main operation loop
        while self.core_goOn:
            # get event from queue, blocks until there is a new event
            event = self.core_event_queue.get()

            # debung out
            self.log.printText(2, 'Event->' + event.get_eventtype() + '   ' + event.get_event_operation())

            # process the next event of queue
            self.__process_event__(event)

            # check if there are still plugins alive or gui is still alive before ending core main loop
            self.core_goOn = self.core_data.get_dplugins_count() != 0 or self.gui_alive

        # core main loop ended, so cancel active alive timer
        self.alive_timer.cancel()

        # core finished operation and did clean shutdown
        self.log.printText(1, CORE_STOP_CONSOLE_MESSAGE)

    def signal_handler(self,signal, frame,core):
        """
        This is an empty
        :return:
        """
        pass

    def send_alive_check_events(self):
        """
        Function for check_alive_status timer to send check_alive events to all running processes
        This will trigger all correctly running processes to send an answer to core

        :return:
        """

        # get list of all plugins [hash: id->dplug], type DPlugin
        dplugs = self.core_data.get_all_plugins()
        for id in dplugs:
            # get dplugin object
            plug = dplugs[id]
            # check if this plugin runs in a separate process
            if plug.own_process is True:
                # send check_alive_status event to plugin process (via queue)
                event = Event.status.CheckAliveStatus(self.core_id, plug.id, None)
                plug.queue.put(event)

        # send check_alive_status event to gui process (via queue)
        event = Event.status.CheckAliveStatus(self.core_id, self.gui_id, None)
        self.gui_event_queue.put(event)

    def handle_alive_situation(self):
        """
        Function which handles the check for the alive situation of all plugins in data base
        Will distribute to error_handling methods to handle dead processes

        :return:
        """
        # get all plugins from core data [hash: id->DPlugin]
        dplugs = self.core_data.get_all_plugins()
        if dplugs is not None:
            for id in dplugs:
                # get DPlugin object
                plug = dplugs[id]
                # check if plugins runs in a separate process
                if plug.own_process is True:
                    # check if counts are equal: equal indicates that plugin is alive
                    if plug.alive_count is self.alive_count:
                        self.log.printText(2, 'Plugin ' + plug.uname + ' is still alive')
                        # change plugin state in DCore
                        plug.alive_state = PLUGIN_STATE_ALIVE
                    else:
                        # Plugin is not alive anymore, so do error handling
                        self.plugin_process_is_dead_error_handler(plug)

            # check for gui status and do error handling
            if self.gui_alive_count is self.alive_count:
                self.log.printText(2, 'GUI  is still ALIVE')
            else:
                self.gui_is_dead_error_handler()

    def gui_is_dead_error_handler(self):
        """
        error handler when gui is dead

        :return:
        """
        self.log.printText(1, 'GUI  is  DEAD')
        self.log.printText(1,
                           'core count: ' + str(self.alive_count) + ' vs. ' + str(self.gui_alive_count) + ' :gui count')

    def plugin_process_is_dead_error_handler(self, dplug):
        """
        Error handler for a dead plugin process

        :param dplug: Plugin which is dead
        :type dplug: DPlugin
        :return:
        """
        self.log.printText(1, 'Plugin ' + dplug.uname + ' is DEAD')
        self.log.printText(1,
                           'core count: ' + str(self.alive_count) + ' vs. ' + str(dplug.alive_count) + ' :plugin count')
        dplug.alive_state = PLUGIN_STATE_DEAD
        self.update_meta_data_to_gui(dplug.id)

    def check_alive_callback(self):
        """
        callback function for check_alive status timer
        handles sending events to processes and checking their answer

        :return:
        """
        self.log.printText(2, 'check alive')

        # check for answer status of all plugins
        self.handle_alive_situation()

        # increase the global check_alive counter
        self.alive_count += 1
        self.alive_count = self.alive_count % self.alive_count_max

        # send new check alive events to plugins
        self.send_alive_check_events()

        # start a new one shot timer with this callback function
        if CORE_ALIVE_CHECK_ENABLED is True:
            self.alive_timer = Timer(self.alive_intervall, self.check_alive_callback)
            self.alive_timer.start()

    def update_meta_data_to_gui(self, pl_id, inform_subscriber=False):
        """
        On call this function will send the meta information of pl_id to GUI

        :param pl_id: id of plugin with new meta information
        :param inform_subscriber: flag used to determine if a meta_update for all subscriber should be initiated
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
            #eventMeta = PapiEvent(pl_id, self.gui_id, 'instr_event', 'update_meta', o)
            eventMeta = Event.instruction.UpdateMeta(pl_id,self.gui_id,o)
            self.gui_event_queue.put(eventMeta)

            # check if plugin got some subscribers which run in own process
            if dplugin.own_process is True:
                dplugin.queue.put(eventMeta)

            # ---------------------------------------------
            # Inform all subscriber if needed and wished
            # ---------------------------------------------
            if inform_subscriber:
                dblocks = dplugin.get_dblocks()
                for dblock_name in dblocks:
                    dblock = dblocks[dblock_name]
                    for subscriber_id in dblock.get_subscribers():
                        dplugin_sub = self.core_data.get_dplugin_by_id(subscriber_id)
                        if dplugin_sub.own_process is False:
                            self.update_meta_data_to_gui(dplugin_sub.id, False)

            return 1
        else:
            # Dplugin object with pl_id does not exist in DCore of core
            self.log.printText(1,
                               'update_meta, cannot update meta information because there is no plugin with id: ' + str(
                                   pl_id))
            return -1

    def update_meta_data_to_gui_for_all(self):
        plugins = self.core_data.get_all_plugins()
        for id in plugins:
            self.update_meta_data_to_gui(id)

    def handle_parameter_change(self, plugin, parameter_name, value):
        """
        This function should be called, when there is a new_data event for changing a parameter value
        This function will change the value in DCore and update this information to GUI via meta update

        :param plugin: Plugin which owns the parameter
        :type plugin: DPlugin
        :param parameter_name: Name of the parameter which value should be changed
        :type parameter_name: basestring
        :param value: new value for the parameter
        :type value: all possible, depends on plugin
        :return: -1 for error(parameter with parameter_name does not exist in plugin), 1 for o.k., done
        """
        allparas = plugin.get_parameters()
        if parameter_name in allparas:
            para = allparas[parameter_name]
            para.value = value
            self.update_meta_data_to_gui(plugin.id)
            return 1
        else:
            return -1

    def new_subscription(self, subscriber_id, source_id, block_name, signals, sub_alias, orginal_event=None):
        """
        Gets information of a new and wanted subscription.
        This methond will try to create the wanted subscription.

        :param subscriber_id: Id of the plugin that want to get data
        :param source_id:  Id of the plugin that will be the data source
        :param block_name:  name of source block of source plugin
        :param signals:  signals to subscribe
        :param sub_alias:  optional alias for parameter
        :return:
        """
        already_sub = False
        # test if already subscribed
        source_pl = self.core_data.get_dplugin_by_id(source_id)
        if source_pl is not None:

            if source_pl.state != PLUGIN_STATE_START_SUCCESFUL:
                self.core_delayed_operation_queue.append(orginal_event)
                self.log.printText(2, 'subscribe, event was placed in delayed queue because plugin with id: '
                                   + str(source_id) + ' is still starting.')
                return 0

            blocks = source_pl.get_dblocks()
            if block_name in blocks:
                b = blocks[block_name]
                subs = b.get_subscribers()
                if subscriber_id in subs:
                    already_sub = True

        if already_sub is False:
            dsubscription = self.core_data.subscribe(subscriber_id, source_id, block_name)
            if dsubscription is None:
                # subscription failed
                self.log.printText(1, 'subscribe, something failed in subscription process with subscriber id: ' + str(
                    subscriber_id) + '..target id:' + str(source_id) + '..and block ' + str(block_name))
                return -1
            else:
                # subscription correct
                # set alias for parameter control (can be none if no parameter)
                dsubscription.alias = sub_alias
                # send event to plugin which will control this parameter with information of parameter
                if sub_alias is not None:
                    sub_pl = self.core_data.get_dplugin_by_id(subscriber_id)
                    if sub_pl is not None:
                        parameters = sub_pl.get_parameters()
                        if sub_alias in parameters:
                            parameter = parameters[sub_alias]
                            para_event = Event.status.ParameterInfo(self.core_id, source_id, copy.deepcopy(parameter) )
                            source_pl.queue.put(para_event)

        if signals != []:
            if self.core_data.subscribe_signals(subscriber_id, source_id, block_name, signals) is None:
                # subscription failed
                self.log.printText(1, 'subscribe, something failed in subsription process with subscriber id: ' + str(
                    subscriber_id) + '..target id:' + str(source_id) + '..and block ' + str(block_name)
                                   + '. A Problem with signals')
                return -1
            else:
                pass

        self.log.printText(1, 'subscribe, subscribtion correct: ' + str(subscriber_id) + '->(' + str(source_id) + ',' + str(
            block_name) + ')')
        self.update_meta_data_to_gui(subscriber_id)
        self.update_meta_data_to_gui(source_id)
        return ERROR.NO_ERROR



    # ------- Event processing initial stage ---------
    def __process_event__(self, event):
        """
        Initial stage of event processing, dividing to event type

        :param event: event to process
        :type event: PapiEventBase
        """
        t = event.get_eventtype()
        self.__process_event_by_type__[t](event)

    # ------- Event processing first stage ---------
    def __process_status_event__(self, event):
        """
        First stage of event processing, deciding which status_event this is

        :param event: event to process
        :type event: PapiEventBase
        """
        op = event.get_event_operation()
        return self.__process_status_event_l__[op](event)

    def __process_data_event__(self, event):
        """
        First stage of event processing, deciding which data_event this is

        :param event: event to process
        :type event: PapiEventBase
        """
        op = event.get_event_operation()
        return self.__process_data_event_l__[op](event)

    def __process_instr_event__(self, event):
        """
        First stage of event processing, deciding which instr_event this is

        :param event: event to process
        :type event: PapiEventBase
        """
        op = event.get_event_operation()
        return self.__process_instr_event_l__[op](event)

    # ------- Event processing second stage: status events ---------
    def __process_start_successfull__(self, event):
        """
        Process start_successfull event

        :param event: event to process
        :type event: PapiEventBase
        """
        # get plugin from DCore with id of event origin and check if it exists
        dplug = self.core_data.get_dplugin_by_id(event.get_originID())
        if (dplug != None):
            # plugin exists and sent successfull event, so change it state
            dplug.state = PLUGIN_STATE_START_SUCCESFUL
            self.update_meta_data_to_gui(dplug.id)

            # process delayed_operation_queue
            while len(self.core_delayed_operation_queue) != 0:
                self.core_event_queue.put(self.core_delayed_operation_queue.pop(0))
            return 1
        else:
            # plugin does not exist
            self.log.printText(1, 'start_successfull_event, Event with id ' + str(
                event.get_originID()) + ' but plugin does not exist')
            return -1

    def __process_start_failed__(self, event):
        """
        Process start failed event and do error handling

        :param event: event to process
        :type event: PapiEventBase
        """
        # get plugin from DCore with id of event origin and check if it exists
        dplug = self.core_data.get_dplugin_by_id(event.get_originID())
        if (dplug != None):
            # plugin exists but start failed, so change it state
            dplug.state = PLUGIN_STATE_START_FAILED
            return 1
        else:
            # plugin does not exist in DCore
            self.log.printText(1, 'start_failed_event, Event with id ' + str(
                event.get_originID()) + ' but plugin does not exist')
            return -1

    def __process_alive__(self, event):
        """
        Processes alive response from processes/plugins and GUI, organising the counter

        :param event: event to process
        :type event: PapiEventBase
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

    def __process_join_request__(self, event):
        """
        Process join requests of processes

        :param event: event to process
        :type event: PapiEventBase
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
                self.log.printText(1, 'join request, remove plugin with id ' + str(dplugin.id) + 'failed')
                return -1
            else:
                # remove from DCore in core successfull
                if self.gui_alive is True:
                    # GUI is still alive, so tell GUI, that this plugin was closed
                    opt = DOptionalData()
                    opt.plugin_id = dplugin.id
                    event = Event.status.PluginClosed(self.core_id, self.gui_id, opt)
                    self.gui_event_queue.put(event)

                self.log.printText(1, 'join_request, plugin with id ' + str(
                    dplugin.id) + ' was joined (uname: ' + dplugin.uname + ' )')
            return ERROR.NO_ERROR
        else:
            # Plug does not exist
            self.log.printText(1, 'join_request, Event with id ' + str(
                event.get_originID()) + ' but plugin does not exist')
            return -1

    # ------- Event processing second stage: data events ---------
    def __process_new_data__(self, event):
        """
        Process new_data event from plugins.
        Will do the routing: Subscriber/Subscription

        :param event: event to process
        :type event: PapiEventBase
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
                block = dplug.get_dblock_by_name(opt.block_name)
                # check for existence of block with block_name
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
                            if pl.state != PLUGIN_STATE_PAUSE or pl.state != PLUGIN_STATE_STOPPED:
                                # plugin exists, check whether it is a ViP
                                if pl.type == PLUGIN_VIP_IDENTIFIER:
                                    # Because its a ViP, we need a list of destination ID for new_data
                                    id_list.append(pl.id)
                                else:
                                    # Plugin is not running in GUI, so just 1:1 relation for event and destinations
                                    opt.parameter_alias = pl.get_subscribtions()[oID][opt.block_name].alias
                                    new_event = Event.data.NewData(oID, [pl.id], opt, source_plugin_uname= dplug.uname)
                                    pl.queue.put(new_event)

                                    # this event will be a new parameter value for a plugin
                                    #if opt.is_parameter is True:
                                    #    self.handle_parameter_change(pl, opt.parameter_alias, opt.data)
                            else:
                                # plugin is paused
                                pass
                        else:
                            # pluign with sub_id does not exist in DCore of core
                            self.log.printText(1, 'new_data, subscriber plugin with id ' + str(
                                sub_id) + ' does not exists')
                            return -1
                    # check if our list with id is greater than 1, which will indicate that there is at least one ViP
                    # which will need to get this new data event
                    if len(id_list) > 0:
                        # send new_data event to GUI with id_list of destinations
                        opt = event.get_optional_parameter()
                        opt.parameter_alias = pl.get_subscribtions()[oID][opt.block_name].alias
                        new_event = Event.data.NewData(oID, id_list, opt, source_plugin_uname= dplug.uname)
                        self.gui_event_queue.put(new_event)

                    # this event will be a new parameter value for a plugin, so update dcore data
                    if opt.is_parameter is True:
                        try:
                            self.handle_parameter_change(pl, opt.parameter_alias, opt.data)
                        except:
                            self.log.printText(2, 'pl not assigned (Use of pcp parameter which isn\'t used)')
                    # process new_data seemed correct
                    return 1
                else:
                    # block is None
                    self.log.printText(1, 'new_data, block with name ' + opt.block_name + ' does not exists')
                    return -1
            else:
                # Plugin of event origin does not exist in DCore of core
                self.log.printText(1, 'new_data, Plugin with id  ' + str(oID) + '  does not exist in DCore')
                return -1

    def BACKUP__process_new_data__(self, event):
        """
        Process new_data event from plugins.
        Will do the routing: Subscriber/Subscription

        :param event: event to process
        :type event: PapiEventBase
        :type tar_plug: DPlugin
        """
        # just proceed with new_data events if GUI is still alive (indicates that program will close)
        if self.gui_alive:
            # get event origin and optional parameter
            oID = event.get_originID()
            opt = event.get_optional_parameter()
            Data = opt.data

            # get origin plugin from DCore
            dplug = self.core_data.get_dplugin_by_id(oID)
            # check for existence
            if dplug is not None:
                # get data block of DPlugin with block_name from event
                block = dplug.get_dblock_by_name(opt.block_name)
                # check for existence of block with block_name
                if block is not None:
                    # get subscriber list of block
                    subscriber = block.get_subscribers()
                    # for all subscriber in subscriber list
                    for sub_id in subscriber:
                        # get plugin with sub_id and check for existence
                        pl = self.core_data.get_dplugin_by_id(sub_id)
                        if pl is not None:
                            # demux signals


                            subcribtions = pl.get_subscribtions()
                            sub_object = subcribtions[oID][opt.block_name]
                            sub_signals = sub_object.signals
                            sub_signals.append('t')
                            opt.data = dict([(i, Data[i]) for i in sub_signals if i in Data])

                            # plugin exists, check whether it is a ViP
                            if pl.type == PLUGIN_VIP_IDENTIFIER:
                                # Plugin runs in GUI
                                opt = event.get_optional_parameter()
                                opt.parameter_alias = pl.get_subscribtions()[oID][opt.block_name].alias
                                new_event = Event.data.NewData(oID, [pl.id], opt)
                                self.gui_event_queue.put(new_event)
                            else:
                                # Plugin is not running in GUI
                                opt.parameter_alias = pl.get_subscribtions()[oID][opt.block_name].alias
                                new_event = Event.data.NewData(oID, [pl.id], opt)
                                pl.queue.put(new_event)

                                # this event will be a new parameter value for a plugin
                                if opt.is_parameter is True:
                                    self.handle_parameter_change(pl, opt.parameter_alias, opt.data)
                        else:
                            # pluign with sub_id does not exist in DCore of core
                            self.log.printText(1, 'new_data, subscriber plugin with id ' + str(
                                sub_id) + ' does not exists')
                            return -1

                    # process new_data seemed correct
                    return 1
                else:
                    # block is None
                    self.log.printText(1, 'new_data, block with name ' + opt.block_name + ' does not exists')
                    return -1
            else:
                # Plugin of event origin does not exist in DCore of core
                self.log.printText(1, 'new_data, Plugin with id  ' + str(oID) + '  does not exist in DCore')
                return -1

    def __process_edit_dplugin(self, event):
        """
        Process edit_dplugin event from gui.

        :param event: event to process
        :type event: PapiEventBaseBase
        :type tar_plug: DPlugin
        """
        eObject = event.editedObject
        cRequest = event.changeRequest

        dID = event.get_destinatioID()

        pl = self.core_data.get_dplugin_by_id(dID)

        if pl is not None:
            if pl.state != PLUGIN_STATE_START_SUCCESFUL:
                self.core_delayed_operation_queue.append(event)
                self.log.printText(2, 'edit_dplugin, event was placed in delayed queue because plugin with name: ' +
                                   pl.uname + ' is still starting')

                return 0

            # DBlock of DPlugin should be edited
            if isinstance(eObject, DBlock):

                dblock = pl.get_dblock_by_name(eObject.name)

                if "edit" in cRequest:
                    cObject = cRequest["edit"]

                    # Signal should be modified in DBlock
                    if isinstance(cObject, DSignal):
                        dsignal = dblock.get_signal_by_uname(cObject.uname)

                        dsignal.dname = cObject.dname

                        self.log.printText(3,
                                           'edit_dplugin, Edited Dblock ' + dblock.name + ' of DPlugin ' + pl.uname +
                                           " : DSignal " + dsignal.uname + " to dname -> " + dsignal.dname)

            self.update_meta_data_to_gui(pl.id, True)

    def __process_edit_dplugin_by_uname__(self, event):

        dplugin = self.core_data.get_dplugin_by_uname(event.plugin_uname)
        if dplugin is not None:
            pl_id = dplugin.id

            idEvent = Event.data.EditDPlugin(self.gui_id, pl_id, event.editedObject, event.changeRequest)

            self.__process_edit_dplugin(idEvent)
        else:
            self.log.printText(1, " Do edit plugin with uname " + event.plugin_uname + ' failed')

    # ------- Event processing second stage: instr events ---------
    def __process_create_plugin__(self, event):
        """
        Processes create_plugin event.
        So it will create a plugin, start a process if needed, send events to GUI to create a plugin and do the pre configuration

        :param event:
        :param optData: optional Data Object of event
        :type event: PapiEventBase
        :type optData: DOptionalData
        :return: -1: Error
        """
        # get optData to get information about which plugin to start
        optData = event.get_optional_parameter()
        self.log.printText(2,
                           'create_plugin, Try to create plugin with Name  ' + optData.plugin_identifier
                           + " and UName " + optData.plugin_uname)

        # search yapsy plugin object with plugin_idientifier and check if it exists
        plugin = self.plugin_manager.getPluginByName(optData.plugin_identifier)
        if plugin is None:
            # Plugin does not exist in yapsy manger, maybe it is new
            # collect plugin information from file system again and recheck
            self.plugin_manager.collectPlugins()
            plugin = self.plugin_manager.getPluginByName(optData.plugin_identifier)
            if plugin is None:
                self.log.printText(1,
                                   'create_plugin, Plugin with Name  ' + optData.plugin_identifier
                                   + ' does not exist in file system')
                return -1

        # creates a new plugin id because plugin exsits
        plugin_id = self.core_data.create_id()

        # checks if plugin is of not of type ViP, because these two will run in GUI process
        if plugin.plugin_object.get_type() != PLUGIN_VIP_IDENTIFIER:
            # So plugin will not run in GUI
            # it will need an own process and queue to function

            # create Queue for plugin process
            plugin_queue = Queue()

            # decide if plugin will need to get Data from another plugin
            if plugin.plugin_object.get_type() == PLUGIN_DPP_IDENTIFIER:
                # plugin will get data from another, so make its execution triggered by events
                eventTriggered = True
            else:
                # stand alone plugin, so it will do its permanent execute loop
                eventTriggered = False

            plugin_config = optData.plugin_config

            if plugin_config is None or plugin_config == {}:
                plugin_config = plugin.plugin_object.get_startup_configuration()
            else:
                plugin_config = dict(list(plugin.plugin_object.get_startup_configuration().items())+list(plugin_config.items()))


            # create Process object for new plugin
            # set parameter for work function of plugin, such as queues, id and eventTriggered
            PluginProcess = Process(target=plugin.plugin_object.work_process, \
                                    args=(self.core_event_queue, plugin_queue, plugin_id, eventTriggered, \
                                          plugin_config, optData.autostart))
            PluginProcess.start()

            #Add new Plugin process to DCore
            dplug = self.core_data.add_plugin(PluginProcess, PluginProcess.pid, True, plugin_queue, plugin, plugin_id)
            dplug.plugin_identifier = plugin.name
            dplug.uname = optData.plugin_uname
            dplug.type = plugin.plugin_object.get_type()
            dplug.alive_count = self.alive_count
            dplug.startup_config = plugin_config
            dplug.path = plugin.path

            # change some attributes of optional data before sending it back to GUI for local creation
            optData.plugin_identifier = plugin.name
            optData.plugin_id = plugin_id
            optData.plugin_type = dplug.type

            # send create_plugin event to GUI for local creation, now with new information like id and type
            event = Event.instruction.CreatePlugin(0, self.gui_id, optData)
            self.gui_event_queue.put(event)
            return 1
        else:
            # Plugin will run in GUI, thats why core does not need to create a new process

            # Adding plugin information to DCore of core for organisation
            dplug = self.core_data.add_plugin(self.gui_process, self.gui_process.pid, False, self.gui_event_queue,
                                              plugin, plugin_id)
            dplug.uname = optData.plugin_uname
            dplug.type = plugin.plugin_object.get_type()
            dplug.plugin_identifier = plugin.name
            dplug.startup_config = optData.plugin_config
            dplug.path = plugin.path

            # change some attributes of optional data before sending it back to GUI for local creation
            optData.plugin_identifier = plugin.name
            optData.plugin_id = plugin_id
            optData.plugin_type = dplug.type

            # send create_plugin event to GUI for local creation, now with new information like id and type
            event = Event.instruction.CreatePlugin(0, self.gui_id, optData)
            self.gui_event_queue.put(event)
            self.log.printText(2, 'core sent create event to gui for plugin: ' + str(optData.plugin_uname))
            return 1

    def __process_stop_plugin__(self, event):
        """
        Process stop_plugin event.
        Will send an event to destination plugin to close itself. Will lead to a join request of this plugin.

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin: DPlugin
        """
        # get destination id
        id = event.get_destinatioID()

        # get DPlugin object and check if plugin exists
        dplugin = self.core_data.get_dplugin_by_id(id)
        if dplugin is not None:
            # dplugin exist, get queue and route event to plugin
            if dplugin.own_process is True:
                # dplugin is not running in gui
                # tell plugin to quit
                dplugin.queue.put(event)
                dplugin.state = PLUGIN_STATE_STOPPED
                self.core_data.unsubscribe_all(dplugin.id)
                self.core_data.rm_all_subscribers(dplugin.id)
                self.update_meta_data_to_gui_for_all()

            else:
                if event.delete is True:
                    # plugin is running in GUI
                    # tell gui to close plugin
                    opt = DOptionalData()
                    opt.plugin_id = id
                    dplugin.queue.put(Event.status.PluginClosed(self.core_id, self.gui_id, opt))

                    # remove plugin from DCore
                    if self.core_data.rm_dplugin(id) != ERROR.NO_ERROR:
                        self.log.printText(1, 'stop plugin, unable to remove plugin von core_data')
                        return ERROR.UNKNOWN_ERROR

                else:
                    dplugin.queue.put(Event.instruction.StopPlugin(self.core_id, id, None, delete=False))
                    dplugin.state = PLUGIN_STATE_STOPPED
                    self.core_data.unsubscribe_all(dplugin.id)
                    self.core_data.rm_all_subscribers(dplugin.id)
                    self.update_meta_data_to_gui_for_all()

            return ERROR.NO_ERROR
        else:
            # DPlugin does not exist
            self.log.printText(1, 'stop_plugin, plugin with id ' + str(id) + ' not found')
            return ERROR.UNKNOWN_ERROR

    def __process_stop_plugin_by_uname__(self, event):
        """

        :param event:
        :return:
        """
        dplugin = self.core_data.get_dplugin_by_uname(event.plugin_uname)

        if dplugin is not None:
            id = dplugin.id

            idEvent = Event.instruction.StopPlugin(self.gui_id, id, None)
            self.__process_stop_plugin__(idEvent)


    def __process_start_plugin__(self, event):
        # get destination id
        id = event.get_destinatioID()

        # get DPlugin object and check if plugin exists
        dplugin = self.core_data.get_dplugin_by_id(id)
        if dplugin is not None:
            # dplugin exist, get queue and route event to plugin
            if dplugin.own_process is True:
                # dplugin is not running in gui
                # tell plugin to quit
                dplugin.queue.put(event)
            else:
                dplugin.state = PLUGIN_STATE_START_SUCCESFUL
                self.gui_event_queue.put(event)
                self.update_meta_data_to_gui(id)

    def __process_plugin_stopped__(self, event):
        """
        Process plugin_stopped event.
        Will change plugins state and delete its parameters and blocks.
        Will update meta to gui

        :param event:
        :return:
        """
        pl_id = event.get_originID()
        plugin = self.core_data.get_dplugin_by_id(pl_id)
        if plugin is not None:
            plugin.state = PLUGIN_STATE_STOPPED

            self.core_data.rm_all_subscribers(pl_id)

            # delete all blocks of plugin
            blocks = plugin.get_dblocks()
            block_to_delete = []
            for block_key in blocks:
                block = blocks[block_key]
                block_to_delete.append(block)

            for b in block_to_delete:
                plugin.rm_dblock(b)

            # delete all parameters of plugin
            paras = plugin.get_parameters()
            paras_to_delete = []
            for key in paras:
                para = paras[key]
                paras_to_delete.append(para)

            for p in paras_to_delete:
                plugin.rm_parameter(p)

            # update to gui
            self.update_meta_data_to_gui(pl_id)

    def __process_close_programm__(self, event):
        """
        This functions processes a close_programm event from GUI and
        sends events to all processes to close themselves

        :param event: event to process
        :type event: PapiEventBase
        """

        # GUI wants to close, so join process
        if self.gui_alive is True and self.is_parent is True:
            self.gui_process.join()

        # Set gui_alive to false for core loop to know that is it closed
        self.gui_alive = False

        # get a list of all running plugIns
        all_plugins = self.core_data.get_all_plugins()

        # iterate through all plugins to send an event to tell them to quit and
        # response with a join_request
        toDelete = []
        for dplugin_key in all_plugins:
            dplugin = all_plugins[dplugin_key]
            # just send event to plugins running in own process
            if dplugin.own_process:
                event = Event.instruction.StopPlugin(0, dplugin.id, None)
                dplugin.queue.put(event)
            else:
                toDelete.append(dplugin.id)

        for dplugin_ID in toDelete:
            self.core_data.rm_dplugin(dplugin_ID)

    def __process_subscribe__(self, event):
        """
        Process subscribe_event.
        Will set a new route in DCore for this two plugins to route new data events. Update of meta will be send to GUI.

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get event origin id and optional parameters
        opt = event.get_optional_parameter()
        self.new_subscription(event.get_originID(), opt.source_ID, opt.block_name, opt.signals, opt.subscription_alias,
                              orginal_event=event)

        # already_sub = False
        # # test if already subscribed
        # source_pl = self.core_data.get_dplugin_by_id(opt.source_ID)
        # if source_pl is not None:
        #     blocks = source_pl.get_dblocks()
        #     if opt.block_name in blocks:
        #         b = blocks[opt.block_name]
        #         subs = b.get_subscribers()
        #         if oID in subs:
        #             already_sub = True
        #
        # if already_sub is False:
        #     dsubscription = self.core_data.subscribe(oID, opt.source_ID, opt.block_name)
        #     if dsubscription is None:
        #         # subscribtion failed
        #         self.log.printText(1, 'subscribe, something failed in subsription process with subscriber id: ' + str(
        #             oID) + '..target id:' + str(opt.source_ID) + '..and block ' + str(opt.block_name))
        #         return -1
        #     else:
        #         # subscribtion correct
        #         dsubscription.alias = opt.subscription_alias
        #
        # if opt.signals != []:
        #     if self.core_data.subscribe_signals(oID, opt.source_ID, opt.block_name, opt.signals) is None:
        #         # subscribtion failed
        #         self.log.printText(1, 'subscribe, something failed in subsription process with subscriber id: ' + str(
        #             oID) + '..target id:' + str(opt.source_ID) + '..and block ' + str(opt.block_name))
        #         return -1
        #     else:
        #         pass
        #
        # self.log.printText(1, 'subscribe, subscribtion correct: ' + str(oID) + '->(' + str(opt.source_ID) + ',' + str(
        #     opt.block_name) + ')')
        # self.update_meta_data_to_gui(oID)
        # self.update_meta_data_to_gui(opt.source_ID)

    def __process_subscribe_by_uname__(self, event):
        """
        Process subscribe_event.
        Will set a new route in DCore for this two plugins to route new data events. Update of meta will be send to GUI.

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        pl = self.core_data.get_dplugin_by_uname(event.subscriber_uname)
        if pl is not None:
            subscriber_id = pl.id
        else:
            # plugin with uname does not exist
            self.log.printText(1, 'do_subscribe, sub uname worng')
            return -1

        pl = self.core_data.get_dplugin_by_uname(event.source_uname)
        if pl is not None:
            source_id = pl.id
        else:
            # plugin with uname does not exist
            self.log.printText(1, 'do_subscribe, target uname wrong')
            return -1

        self.new_subscription(subscriber_id, source_id, event.block_name, event.signals, event.sub_alias,
                              orginal_event=event)

    def __process_unsubsribe__(self, event):
        """
        Process unsubscribe_event. Will try to remove a subscription from DCore

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get event origin id and optional parameters
        opt = event.get_optional_parameter()
        oID = event.get_originID()

        if opt.signals == []:
            # try to unsubscribe
            if self.core_data.unsubscribe(oID, opt.source_ID, opt.block_name) is False:
                # unsubscribe failed
                self.log.printText(1,
                                   'unsubscribe, something failed in unsubsription process with subscriber id: ' + str(
                                       oID) + '..target id:' + str(opt.source_ID) + '..and block ' + str(
                                       opt.block_name))
                return -1
        else:
            if self.core_data.unsubscribe_signals(oID, opt.source_ID, opt.block_name, opt.signals) is False:
                return -1

        # unsubscribe correct
        self.log.printText(1,
                           'unsubscribe, unsubscribtion correct: ' + str(oID) + '->(' + str(opt.source_ID) + ',' + str(
                               opt.block_name) + ')')
        self.update_meta_data_to_gui(oID)
        self.update_meta_data_to_gui(opt.source_ID)

    def __process_set_parameter__(self, event):
        """
        Process set_parameter event. Core will just route this event from GUI to destination plugin and update DCore

        :param event: event to process
        :type event: PapiEventBase
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
            parameters = dplugin.get_parameters()

            if opt.parameter_alias in parameters:
                para = parameters[opt.parameter_alias]
                para.value = opt.data
                # route the event to the destination plugin queue
                dplugin.queue.put(event)
                # change event type for plugin
                #update GUI
                self.update_meta_data_to_gui(pl_id)
                return 1
        else:
            # destination plugin does not exist
            self.log.printText(1, 'set_paramenter, plugin with id ' + str(pl_id) + ' not found')
            return -1

    def __process_new_block__(self, event):
        """
        Processes new_block event.
        Will try to add a new data block to a DPlugin object

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get event origin id and optional parameter
        opt = event.get_optional_parameter()
        pl_id = event.get_originID()
        # get DPlugin object with origin id of event to add new parameter to THIS DPlugin
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
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
            self.log.printText(1, 'new_block, plugin with id ' + str(pl_id) + ' not found')
            return -1

    def __process_delete_block__(self, event):
        """
        Processes delete_block event.
        Will try to delete a Block of a plugin

        :param event: event to process
        :type event: PapiEventBase
        """
        pl_id = event.get_originID()
        self.core_data.rm_all_subscribers_of_a_dblock(pl_id, event.blockname)

        plugin = self.core_data.get_dplugin_by_id(pl_id)
        dblock = plugin.get_dblock_by_name(event.blockname)
        plugin.rm_dblock(dblock)

        self.update_meta_data_to_gui_for_all()

    def __delete_parameter__(self, event):
        pl_id = event.get_originID()

        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            # get connections of this dplugin
            subscriptions = copy.deepcopy(dplugin.get_subscribtions())
            # iterate over all source plugins by id in subscription dict
            for source_id in subscriptions:
                # iterate over all blocks
                for blockName in subscriptions[source_id]:
                    dSubObject = subscriptions[source_id][blockName]
                    # search for parameter to delete in subscription
                    if dSubObject.alias == event.parameterName:
                        self.core_data.unsubscribe(pl_id, source_id, blockName)

            paraObject = dplugin.get_parameters()[event.parameterName]

            dplugin.rm_parameter(paraObject)
            self.update_meta_data_to_gui_for_all()

    def __process_new_parameter__(self, event):
        """
        Processes new parameter event. Adding a new parameter to DPluign in DCore and updating GUI information

        :param event: event to process
        :type event: PapiEventBase
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
            self.log.printText(1, 'new_parameter, plugin with id ' + str(pl_id) + ' not found')
            return -1

    def __process_pause_plugin__(self, event):
        """
        Processes pause_plugin event. Will add information that a plugin is paused and send event to plugin to pause it.

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin: DPlugin
        """
        pl_id = event.get_destinatioID()

        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            if dplugin.state != PLUGIN_STATE_PAUSE:
                # set pause info
                dplugin.state = PLUGIN_STATE_PAUSE
                # send event to plugin
                event = Event.instruction.PausePlugin(self.core_id, pl_id, None)
                dplugin.queue.put(event)

                # update meta for Gui
                self.update_meta_data_to_gui(pl_id)

    def __process_resume_plugin__(self, event):
        """
        Processes resume_plugin event. Will add information that a plugin is resumed and send event to plugin to resume it.

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin: DPlugin
        """
        pl_id = event.get_destinatioID()

        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            if dplugin.state == PLUGIN_STATE_PAUSE:
                # set resume info
                dplugin.state = PLUGIN_STATE_RESUMED
                # send event to plugin
                event = Event.instruction.ResumePlugin(self.core_id, pl_id, None)
                dplugin.queue.put(event)

                # update meta for Gui
                self.update_meta_data_to_gui(pl_id)