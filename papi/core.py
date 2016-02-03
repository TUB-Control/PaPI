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
    CORE_STOP_CONSOLE_MESSAGE, CORE_ALIVE_CHECK_INTERVAL, CORE_ALIVE_MAX_COUNT, CORE_TIME_SIGNAL

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
        Init function of the PaPI Core.
        Creates all data needed to use core and core.run() functions

        .. document private functions
        .. automethod:: __*
        """

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
                                          'set_parameter_by_uname': self.__process_set_parameter__,
                                          'pause_plugin':           self.__process_pause_plugin__,
                                          'resume_plugin':          self.__process_resume_plugin__,
                                          'start_plugin':           self.__process_start_plugin__
        }

        # Startup parameter to configure core
        self.args = args
        self.is_parent = is_parent

        # creating the main core data object DCore and core queue
        self.core_data = DCore()
        self.core_goOn = 1
        self.core_id = 0

        # setting up the yapsy plugin manager for directory structure
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
        self.alive_interval = CORE_ALIVE_CHECK_INTERVAL
        self.alive_count_max = CORE_ALIVE_MAX_COUNT
        self.alive_timer = Timer(self.alive_interval, self.check_alive_callback)
        self.alive_count = 0
        self.gui_alive_count = 0

        # Setup queues and processes for inter-process communication between core and gui
        self.core_event_queue = None
        self.gui_event_queue = None
        self.gui_process = Process_dummy()
        self.gui_process.pid = gui_process_pid
        self.gui_alive = True

        # Check whether core is set to be parent and then check parameter to be valid
        if is_parent:
            if gui_start_function is None:
                raise Exception('Core started with wrong arguments')
            if use_gui is True and is_parent is False:
                 raise Exception('Core started with wrong arguments')
            if is_parent is False and gui_process_pid is None:
                 raise Exception('Core started with wrong arguments')

            # core is set to be parent, start gui process from core
            self.gui_start_function = gui_start_function
            self.core_event_queue = Queue()
            self.gui_event_queue = Queue()

        # list/queue for events that should be delayed before execution
        self.core_delayed_operation_queue = []

        # connect CTRL+C signaling from cmd to quit PaPI
        signal.signal(signal.SIGINT, lambda sig,frame,core=self: self.signal_handler(sig,frame,core))

    def run(self):
        """
        Main operation function of core.
        Event loop is in here.

        :return:
        """
        # logs: some startup information
        self.log.printText(1, CORE_PAPI_CONSOLE_START_MESSAGE)
        self.log.printText(1, CORE_CORE_CONSOLE_START_MESSAGE + ' .. Process id: ' + str(os.getpid()))

        # start the GUI process to show GUI, set GUI alive status to TRUE
        # don't start GUI in case that CORE is not parent and that the gui should be used
        if self.use_gui and self.is_parent:
            self.gui_process = Process(target=self.gui_start_function,
                                       args=(self.core_event_queue, self.gui_event_queue, self.gui_id, self.args))
            self.gui_process.start()

        # start the check alive timer if heartbeat is activated
        if CORE_ALIVE_CHECK_ENABLED is True:
            self.log.printText(1, 'Alive check of processes is enabled')
            self.alive_timer.start()

        # core main operation loop
        # Receiving and reaction to events
        while self.core_goOn:
            # get event from queue, blocks until there is a new event
            # blocking prevents unnecessary iterations since core is only reacting to events
            event = self.core_event_queue.get()

            # LOG: Debug output
            self.log.printText(2, 'Event->' + event.get_eventtype() + '   ' + event.get_event_operation())

            # process the next event of queue
            # catch error if event is unknown, i.e. no callback function exits for it
            try:
                self.__process_event__(event)
            except Exception as Exc:
                print(Exc)

            # check if there are still plugins alive or gui is still alive before ending core main loop
            self.core_goOn = self.core_data.get_dplugins_count() != 0 or self.gui_alive

        # core main loop ended, so cancel alive timer
        self.alive_timer.cancel()

        # LOG: core finished operation and did clean shutdown
        self.log.printText(1, CORE_STOP_CONSOLE_MESSAGE)

    def signal_handler(self,signal, frame,core):
        """
        Callback-handler for signal from cmd line like e.g. SIGINT
        :return:
        """
        pass

    def send_alive_check_events(self):
        """
        Function for check_alive_status timer to send check_alive events to all running processes
        This will trigger all correctly running processes to send an answer to core.
        Alive response is handled in method '__process_alive__'
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
        This is no callback functions, more a rather periodically called method to check the alive situation.
        Is called by the handler which handles the alive timer callbacks

        It checks the counter of the plugins and compares them against the core counter. A not equal (normally smaller)
        number in the plugin object indicates a dead process. A error handler is called.

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
        Error handler for the case that the gui is dead.
        The handler gets called by the method 'handle_alive_situation' in case the gui counter does not match

        :return:
        """
        self.log.printText(1, 'GUI  is  DEAD')
        self.log.printText(1,
                           'core count: ' + str(self.alive_count) + ' vs. ' + str(self.gui_alive_count) + ' :gui count')

    def plugin_process_is_dead_error_handler(self, dplug):
        """
        Error handler for the case that the a plugin is dead.
        The handler gets called by the method 'handle_alive_situation' in case the plugin counter does not match

        :param dplug: Plugin which is dead
        :type dplug: DPlugin
        :return:
        """
        # LOG: print situation to the console
        self.log.printText(1, 'Plugin ' + dplug.uname + ' is DEAD')
        self.log.printText(1,
                           'core count: ' + str(self.alive_count) + ' vs. ' + str(dplug.alive_count) + ' :plugin count')

        # set the plugin state to DEAD and update meta data to let the GUI know
        dplug.alive_state = PLUGIN_STATE_DEAD
        self.update_meta_data_to_gui(dplug.id)

    def check_alive_callback(self):
        """
        Callback function for check_alive status timer, get called every time the timer triggers, does sth and starts a
        new timer.
        Handles sending events to processes and checking their answer.

        :return:
        """

        # LOG: alive timer triggered
        self.log.printText(2, 'check alive')

        # check for answer status of all plugins
        self.handle_alive_situation()

        # increase the global check_alive counter
        self.alive_count += 1
        self.alive_count = self.alive_count % self.alive_count_max

        # send new check alive events to plugins
        self.send_alive_check_events()

        # start a new one shot timer with this callback function as the next alive interval
        if CORE_ALIVE_CHECK_ENABLED is True:
            self.alive_timer = Timer(self.alive_interval, self.check_alive_callback)
            self.alive_timer.start()

    def update_meta_data_to_gui(self, pl_id, inform_subscriber=False):
        """
        On call, this function sends the meta information of the plugin with pl_id to the GUI
        With meta information is meant: all data in the dplugin object which is not process related (e.g. ids, names,
        states, subscriptions)
        The methods should be called everywhere, where some of those information are changed and a update in other
        processes is required/wanted. Additionally, subscriber of the plugin 'pl_id' are informed/

        The methods takes the dplugin specified by its id and extracts all the meta data. Then, sends the updated meta
        data to the gui. Afterwards, if required, the subscriber will be informed by calling this methods (some kind of
        recursive) again with another id.

        :param pl_id: id of plugin with new meta information
        :type pl_id: int
        :param inform_subscriber: flag used to determine if a meta_update for all subscriber should be initiated
        :type inform_subscriber: bool
        :return:
        """
        # get DPlugin object with id and check if it exists
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            # DPlugin object exists,so build optionalData for Event
            optObj = DOptionalData()
            # get meta information of DPlugin and add it to the event
            optObj.plugin_object = dplugin.get_meta()
            # build event and send it to GUI with meta information
            eventMeta = Event.instruction.UpdateMeta(pl_id,self.gui_id,optObj)
            self.gui_event_queue.put(eventMeta)

            # check if plugin got some subscribers which run in own process
            if dplugin.own_process is True and dplugin.state == PLUGIN_STATE_START_SUCCESFUL:
                dplugin.queue.put(eventMeta)

            # ---------------------------------------------
            # Inform all subscriber if needed and wished
            # ---------------------------------------------
            if inform_subscriber:
                # get all blocks of the plugin to search for subscriber
                dblocks = dplugin.get_dblocks()
                for dblock_name in dblocks:
                    # search in all blocks for subscriber
                    dblock = dblocks[dblock_name]
                    for subscriber_id in dblock.get_subscribers():
                        # for every subscriber of a block of the plugin, check if it runs in its own process (not in gui)
                        # to inform that process by a message (recursive call of this function)
                        dplugin_sub = self.core_data.get_dplugin_by_id(subscriber_id)
                        if dplugin_sub.own_process is False:
                            self.update_meta_data_to_gui(dplugin_sub.id, False)
            # return 1 if plugin exists and everything went fine in the update process
            return 1
        else:
            # Dplugin object with pl_id does not exist in DCore of core
            self.log.printText(1,
                               'update_meta, cannot update meta information because there is no plugin with id: ' + str(
                                   pl_id))
            return -1

    def update_meta_data_to_gui_for_all(self):
        """
        This functions update the meta data of all plugins to the GUI process by iteration over the plugin database
        and calling 'update_meta_data_to_gui' for every plugin id.
        :return:
        """
        # iterate over plugin database
        plugins = self.core_data.get_all_plugins()
        for id in plugins:
            # update meta data of plugin id to gui
            self.update_meta_data_to_gui(id)

    def handle_parameter_change(self, plugin, parameter_name, value):
        """
        This function should be called whenever there is a new_data event for changing a parameter value
        This function changes the value in DCore and updates this information to the GUI via a meta update

        :param plugin: Plugin which owns the parameter
        :type plugin: DPlugin
        :param parameter_name: Name of the parameter which value should be changed
        :type parameter_name: basestring
        :param value: new value for the parameter
        :type value: all possible, depends on plugin
        :return: -1 for error(parameter with parameter_name does not exist in plugin), 1 for o.k., done
        """
        # gets the parameter list of the plugin for witch a parameter was changed
        allparas = plugin.get_parameters()
        if parameter_name in allparas:
            # parameter exists in the plugin, so change its value.
            para = allparas[parameter_name]
            para.value = value
            # Then, update the change to the gui by performing a meta update
            self.update_meta_data_to_gui(plugin.id)
            return 1
        else:
            return -1

    def new_subscription(self, subscriber_id, source_id, block_name, signals, sub_alias, orginal_event=None):
        """
        Gets information of a new and desired subscription.
        This method will try to create the wanted subscription.

        :param subscriber_id: Id of the plugin that want to get data
        :param source_id:  Id of the plugin that will be the data source
        :param block_name:  name of source block of source plugin
        :param signals:  signals to subscribe
        :param sub_alias:  optional alias for parameter
        :return:
        """
        already_sub = False

        # check if already subscribed
        source_pl = self.core_data.get_dplugin_by_id(source_id)
        if source_pl is not None:
            # only check plugins which are started successfully, otherwise delay this operation.
            if source_pl.state != PLUGIN_STATE_START_SUCCESFUL:
                # source for subscription does not exists yet, so delay subscription event again
                self.core_delayed_operation_queue.append(orginal_event)
                self.log.printText(2, 'subscribe, event was placed in delayed queue because plugin with id: '
                                   + str(source_id) + ' is still starting.')
                return 0

            # plugin is running correctly, so get its blocks to check if the subscriber already exists
            blocks = source_pl.get_dblocks()
            if block_name in blocks:
                b = blocks[block_name]
                subs = b.get_subscribers()

                if subscriber_id in subs:
                    # subscriber is already listed, so remember that
                    already_sub = True

        # Check if the subscription is necessary
        if already_sub is False:
            dsubscription = self.core_data.subscribe(subscriber_id, source_id, block_name)
            if dsubscription is None:
                # subscription failed
                # maybe the block does not exists yet, so delay subscription event again
                self.core_delayed_operation_queue.append(orginal_event)
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

        # LOG: successful
        self.log.printText(1, 'subscribe, subscribtion correct: ' + str(subscriber_id) + '->(' + str(source_id) + ',' + str(
            block_name) + ')')

        # update meta data of subscriber and source plugin, since the relation between those two changed due to this method.
        self.update_meta_data_to_gui(subscriber_id)
        self.update_meta_data_to_gui(source_id)
        return ERROR.NO_ERROR

    def checkEventsInDelayedQueue(self):
        """
        Process all events which are in the delayed operation queue by poping them out and inserting them to the main
        core event queue 'core_event_queue'
        :return:
        """
        while len(self.core_delayed_operation_queue) != 0:
            self.core_event_queue.put(self.core_delayed_operation_queue.pop(0))


    # ------- Event processing initial stage ---------
    def __process_event__(self, event):
        """
        Initial stage of event processing, dividing by event type
        Extracts event type and give it to a switch case equivalent

        :param event: event to process
        :type event: PapiEventBase
        """
        t = event.get_eventtype()
        self.__process_event_by_type__[t](event)

    # ------- Event processing first stage ---------
    def __process_status_event__(self, event):
        """
        First stage of event processing, deciding which status_event this is. Therefore, the method extracts the event
        operation and processes it.

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
        First stage of event processing, deciding which instr_event this is. Therefore, the method extracts the event
        operation and processes it.

        :param event: event to process
        :type event: PapiEventBase
        """
        op = event.get_event_operation()
        return self.__process_instr_event_l__[op](event)

    # ------- Event processing second stage: status events ---------
    def __process_start_successfull__(self, event):
        """
        Process start_successful event.

        A start_successful event is sent by plugins after their initialize function returned 'true' indicating a
        successful start of the plugin before continuing with its main execution routine.


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
            self.checkEventsInDelayedQueue()
            return 1
        else:
            # plugin does not exist
            self.log.printText(1, 'start_successfull_event, Event with id ' + str(
                event.get_originID()) + ' but plugin does not exist')
            return -1

    def __process_start_failed__(self, event):
        """
        Process start failed event and do error handling

        This event occurs when a plugin returns false in its initialize routine. Therefore, it means that the start of
        failed but the plugin noticed it itself and was able to return false.

        This method will update the core database with the new state of the plugin. At the moment, no other actions are
        done.

        :param event: event to process
        :type event: PapiEventBase
        """
        # get plugin from DCore with id of event origin and check if it exists
        dplug = self.core_data.get_dplugin_by_id(event.get_originID())
        if (dplug != None):
            # plugin exists but start failed, so change its state
            dplug.state = PLUGIN_STATE_START_FAILED
            return 1
        else:
            # plugin does not exist in DCore
            self.log.printText(1, 'start_failed_event, Event with id ' + str(
                event.get_originID()) + ' but plugin does not exist')
            return -1

    def __process_alive__(self, event):
        """
        Processes alive response from processes/plugins and GUI, organising the counter,
        i.e. increment GUI counter if alive event's origin is GUI, otherwise increment counter stored in dplugin object

        Alive events that were sent by plugins are the response on alive request which were sent by the core alive timer.
        An alive event indicates that the plugin is still running and responding to requests.

        :param event: event to process
        :type event: PapiEventBase
        """
        # get the event origin
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

        A join request is send from a plugin which will close itself. The requests wants the core to join the process of
        the plugin for clean-up reasons. Therefore, the join request is just send by plugins running in an own process
        (and not in the GUI).

        The method is searching for the dplugin object in the core database to get the corresponding process object.
        Then, the method joins the process. Note, that a join request is the last action of a plugin to ensure that the
        core is not blocked by the process join procedure.
        Afterwards, the plugin will be removed from the core's database. A event is send to the GUI process to inform the
        GUI about the closed and removed plugin.

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin: DPlugin
        """
        # get event origin id and its corresponding plugin object
        pl_id = event.get_originID()
        dplugin = self.core_data.get_dplugin_by_id(pl_id)
        # check for existence
        if dplugin is not None:
            # get process of plugin and join it (is blocking but plugin call order ensures that no block can occur)
            dplugin.process.join()
            # remove plugin from DCore, because process was joined and thus, the plugin is identified as 'closed'
            if self.core_data.rm_dplugin(dplugin.id) is False:
                # remove failed
                self.log.printText(1, 'join request, remove plugin with id ' + str(dplugin.id) + 'failed')
                return -1
            else:
                # remove from DCore in core successful
                # Check whether the GUI is still alive to ensure that no new events are put into a queue to a non-existing GUI process
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
                            else:
                                # plugin is paused
                                pass
                        else:
                            # pluign with sub_id does not exist in DCore of core
                            self.log.printText(1, 'new_data, subscriber plugin with id ' + str(
                                sub_id) + ' does not exists')
                            return -1
                    # check if our list with id is longer than 0, which will indicate that there is at least one ViP
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

    def __process_edit_dplugin(self, event):
        """
        Process edit_dplugin event from gui.

        TODO: SVEN

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
                if dblock is not None:
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
        """
        This function processes edit plugin events and acts like a wrapper for the '__process_edit_dplugin' function which
        requires plugin ids instead of unames.

        Documentation of what the method does can be found in the method: __process_edit_dplugin

        :param event:
        :return:
        """
        # Get dplugin object by uname out of core queue.
        dplugin = self.core_data.get_dplugin_by_uname(event.plugin_uname)
        # Check if plugin object exists
        if dplugin is not None:
            pl_id = dplugin.id
            # create a new event with the corresponding id instead of the uname
            idEvent = Event.data.EditDPlugin(self.gui_id, pl_id, event.editedObject, event.changeRequest)
            # pass the event to the function which is wrapped here
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
        if plugin.plugin_object._get_type() != PLUGIN_VIP_IDENTIFIER:
            # So plugin will not run in GUI
            # it will need an own process and queue to function

            # create Queue for plugin process
            plugin_queue = Queue()

            # decide if plugin will need to get Data from another plugin
            if plugin.plugin_object._get_type() == PLUGIN_DPP_IDENTIFIER:
                # plugin will get data from another, so make its execution triggered by events
                eventTriggered = True
            else:
                # stand alone plugin, so it will do its permanent execute loop
                eventTriggered = False

            plugin_config = optData.plugin_config

            if plugin_config is None or plugin_config == {}:
                plugin_config = plugin.plugin_object._get_startup_configuration()
            else:
                plugin_config = dict(list(plugin.plugin_object._get_startup_configuration().items())+list(plugin_config.items()))


            # create Process object for new plugin
            # set parameter for work function of plugin, such as queues, id and eventTriggered
            PluginProcess = Process(target=plugin.plugin_object._work_process, \
                                    args=(self.core_event_queue, plugin_queue, plugin_id, eventTriggered, \
                                          plugin_config, optData.autostart))
            PluginProcess.start()

            #Add new Plugin process to DCore
            dplug = self.core_data.add_plugin(PluginProcess, PluginProcess.pid, True, plugin_queue, plugin, plugin_id)
            dplug.plugin_identifier = plugin.name
            dplug.uname = optData.plugin_uname
            dplug.type = plugin.plugin_object._get_type()
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
            dplug.type = plugin.plugin_object._get_type()
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

        A stop plugin event is sent by the GUI to the core to request the core to stop a plugin.
        'Stop' means that: either the plugin is just stopped and not deleted or the plugin execution is stopped and the
        is deleted from the database (i.e. it is cleaned). It is determines by a flag which of them is used.

        The methods searches for the dplugin object in the core database.
        If the plugin runs in an own process, the stop event is redirected to the corresponding plugin
        (to notify it to close itself). The core will cut all subscriptions&subscribers loose and update the gui data with
        the new plugin state.
        If the plugin is not running in an own process (runs in GUI), the event is checked for the delete flag.
        If the delete flag is set, the method will send a close request to the plugin.
        If not, the plugin will receive a customized stop event. The state will be modified and updated to the GUI.

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
                # tell plugin to stop and update state and GUI
                dplugin.queue.put(event)
                dplugin.state = PLUGIN_STATE_STOPPED
                self.core_data.unsubscribe_all(dplugin.id)
                self.core_data.rm_all_subscribers(dplugin.id)
                self.update_meta_data_to_gui_for_all()
            else:
                # plugin is not running in own process, so process the event completely
                if event.delete is True:
                    # tell gui to close plugin
                    opt = DOptionalData()
                    opt.plugin_id = id
                    dplugin.queue.put(Event.status.PluginClosed(self.core_id, self.gui_id, opt))

                    # remove plugin from DCore
                    if self.core_data.rm_dplugin(id) != ERROR.NO_ERROR:
                        self.log.printText(1, 'stop plugin, unable to remove plugin von core_data')
                        return ERROR.UNKNOWN_ERROR

                else:
                    # Do not delete the plugin from the database, thus just send a stop event to plugin without delete flag.
                    dplugin.queue.put(Event.instruction.StopPlugin(self.core_id, id, None, delete=False))
                    # update plugin state and gui meta database
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

        Just a wrapper function for '__process_stop_plugin__' to use the uname instead of a plugin id.

        :param event:
        :return:
        """

        dplugin = self.core_data.get_dplugin_by_uname(event.plugin_uname)
        # check  if plugin exists in core database
        if dplugin is not None:
            # get plugin id, rebuild event and call original function
            id = dplugin.id
            idEvent = Event.instruction.StopPlugin(self.gui_id, id, None)
            self.__process_stop_plugin__(idEvent)

    def __process_start_plugin__(self, event):
        """
        Processes start event for a plugin.

        The start plugin event is a request for the core to send a start event to a plugin.
        The plugin will be started by receiving the event, i.e. it will call its initialize function and start its
        execution afterwards.

        The methods searches the plugin in the database and checks wheter it has its own process or not.
        Then, it will send an event to the corresponding queue to tell the plugin it should start.

        :param event: Incomming event
        :type event:  PapiEventBase
        :return:
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
        This functions processes a close_program event from GUI and
        sends events to all processes to close themselves

        The GUI can request the close to quit PaPI.

        The method will request all other processes to stop their execution and to close.

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

        The event is sent to create new data connections between plugins.

        The method will call the functional method 'new_subscription' will the necessary arguments,
        like SourceID, Block, Signals, Alias

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin_sub: DPlugin
        :type dplugin_source: DPlugin
        """
        # get event origin id and optional parameters
        opt = event.get_optional_parameter()
        self.new_subscription(event.get_originID(), opt.source_ID, opt.block_name, opt.signals, opt.subscription_alias,
                              orginal_event=event)

    def __process_subscribe_by_uname__(self, event):
        """
        Process subscribe_event. Uses uname instead of IDs

        The event is sent to create new data connections between plugins.

        The method will call the functional method 'new_subscription' will the necessary arguments,
        like SourceID, Block, Signals, Alias

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

        if isinstance(event, Event.instruction.SetParameterByUname):
            dplugin = self.core_data.get_dplugin_by_uname(event.plugin_uname)
            if dplugin is not None:
                if dplugin.state != PLUGIN_STATE_START_SUCCESFUL:
                    # plugin not here yet, put event in delayed queue
                    self.core_delayed_operation_queue.append(event)
                    self.log.printText(2, 'setParameterByUname, event was placed in delayed queue because plugin: '
                                       + event.plugin_uname + ' does not exist yet.')
                    return 0
                # build forward event for gui with ids instead of uname
                forward_event = Event.instruction.SetParameter(event.get_originID(), dplugin.id, event.get_optional_parameter())
        else:
            # get destination id
            pl_id = event.get_destinatioID()
            # get DPlugin object of destination id from DCore and check for existence
            dplugin = self.core_data.get_dplugin_by_id(pl_id)
            forward_event = event
            if dplugin is None:
                #  pluign with id does not exist, so id is wrong.
                self.log.printText(1, 'set_paramenter, plugin with id ' + str(pl_id) + ' not found')
                return -1


        if dplugin is not None:
            opt = event.get_optional_parameter()
            # Plugin exists
            # get parameter list of plugin [hash]
            parameters = dplugin.get_parameters()

            if opt.parameter_alias in parameters:
                para = parameters[opt.parameter_alias]
                para.value = opt.data
                # route the event to the destination plugin queue
                dplugin.queue.put(forward_event)
                # change event type for plugin
                #update GUI
                self.update_meta_data_to_gui(dplugin.id)
                return 1


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
            self.checkEventsInDelayedQueue()
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

        Pause events are request from the GUI to pause a plugin. Paused plugins will not execute its execution function and
        thus, lower the computational load.

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

        Resumes a paused plugin to make it work again. So, the plugin will execute its main functions again.

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