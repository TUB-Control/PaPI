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
 
Contributors:
<Stefan Ruppin
"""


from papi.plugin.base_classes.base_plugin import base_plugin
import papi.event as Event


class ownProcess_base(base_plugin):
    """
    This plugin base should be used by a plugin if should run in an own process.
    It is not possible to create a widget which is displayed in the graphical interface of PaPI.
    """

    def _work_process(self, CoreQueue, pluginQueue, id, defaultEventTriggered=False, config=None, autostart=True):
        """
        This is the main working function of plugins running in their own process.

        :param CoreQueue:   multiprocessing queue of core for plugin to send data
        :param pluginQueue: multiprocessing queue for plugin to receive data
        :param id: Plugin id
        :param defaultEventTriggered: event mode
        :param config:    Pluign intial cfg
        :param autostart: Should plugin start immediately after call?
        :return:
        """

        # set queues and id and remember them
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        self.__EventTriggered = defaultEventTriggered
        self.__user_event_triggered = 'default'
        self.__paused = False

        # initialize the base class and all objects
        self._papi_init()

        # working should go at least one time/cycle
        self.__goOn = 1

        # plugin will start so it is not stopped yet
        self.__plugin_stopped = False

        # will check if plugin shall be started immediately after creation
        if autostart is True:
            # call _start_plugin_base function to use developers init
            self._starting_sequence(config)
        else:
            self.__plugin_stopped = True

        # main working loop
        while self.__goOn:
            # check event trigger mode
            self._evaluate_event_trigger(defaultEventTriggered)
            # Check for new event in plugin queue
            event = None
            try:
                # do blocked checking of queue if:
                # plugin is paused or
                # plugin is stopped or
                # plugin mode is event triggered
                event = self.__plugin_queue__.get( self.__paused or self.__EventTriggered or self.__plugin_stopped)
            except:
                # no new event
                event = None

            # there is a new event
            if event is not None:
                op = event.get_event_operation()

                # plugin shall stop operation
                if op=='stop_plugin' :
                    self.cb_quit()
                    if event.delete is True:
                        # delete plugin, so work_progress will stop completely
                        self.__goOn = 0
                        event = Event.status.JoinRequest(self.__id__, 0, None)
                        self._Core_event_queue__.put(event)
                    else:
                        # plugin should stop but is not getting deleted
                        # response to core and rm_all_subs, blocks, paras
                        self.__plugin_stopped = True
                        event = Event.status.PluginStopped(self.__id__, 0, None)
                        self._Core_event_queue__.put(event)

                # plugin should start again after it was stopped once
                if op=='start_plugin' and self.__plugin_stopped is True:
                    # maybe new config?
                    self._starting_sequence(config)
                    self.__plugin_stopped = False

                # pause this plugin
                if op=='pause_plugin' and self.__paused is False and self.__plugin_stopped is False:
                    self.__paused = True
                    self.cb_pause()

                # resume this plugin if it was paused
                if op=='resume_plugin' and self.__paused is True and self.__plugin_stopped is False:
                    self.__paused = False
                    self.cb_resume()

                # answer the check alive call from the core
                if op=='check_alive_status':
                    alive_event = Event.status.Alive(self.__id__, 0, None)
                    self._Core_event_queue__.put(alive_event)

                # there is new data routed from the core to this plugin, maybe this data is a parameter change
                # check and process data according to type
                # The parameter type will appear when another plugin sends parameter updates to this plugin through a
                # parameter subscription
                if op=='new_data' and self.__paused is False and self.__plugin_stopped is False:
                    opt = event.get_optional_parameter()
                    if opt.is_parameter is False:
                        data = self._demux(opt.data_source_id, opt.block_name, opt.data)
                        self.cb_execute(Data=data, block_name = opt.block_name, plugin_uname= event.source_plugin_uname)
                    if opt.is_parameter is True:
                        self._set_parameter_internal(opt.parameter_alias, opt.data)

                # This case appears when a parameter gets changed through an api call e.g. in the overview menu
                if op == 'set_parameter' and self.__plugin_stopped is False:
                    opt = event.get_optional_parameter()
                    self._set_parameter_internal(opt.parameter_alias, opt.data)

                # process a update with meta information from the core
                if op == 'update_meta' and self.__plugin_stopped is False:
                    opt = event.get_optional_parameter()
                    self._update_plugin_meta(opt.plugin_object)

            else: # there was no new event
                if self.__paused or self.__EventTriggered or self.__plugin_stopped:
                    pass
                else:
                    # call the plugin cb_execute function if event mode allows it.
                    self.cb_execute()

    def _starting_sequence(self, config):
        """
        This is the starting point for the operation of a plugin.
        This function will start the plugin. Therefore it will call the setup function and will report
        the success of the start to the core by sending an event.

        :param config:
        :return:
        """
        self._config = config
        if self._start_plugin_base():
            # report start successfull event
            event = Event.status.StartSuccessfull(self.__id__, 0, None)
            self._Core_event_queue__.put(event)
        else:
            # init failed, so report it to core
            event = Event.status.StartFailed(self.__id__, 0, None)
            self._Core_event_queue__.put(event)
            # end plugin
            self.__goOn = 0
            # sent join request to core
            event = Event.status.JoinRequest(self.__id__, 0, None)
            self._Core_event_queue__.put(event)

    def _start_plugin_base(self):
        """
        Needs to be implemented by plugin base class

        :return:
        """
        raise NotImplementedError("Please Implement this method")

    def _evaluate_event_trigger(self,default):
        """
        Will evaluate the event trigger mode and set it to the needed value

        :param default:
        :return:
        """
        if self.__user_event_triggered == 'default':
            self.__EventTriggered = default
        if self.__user_event_triggered is True:
            self.__EventTriggered = True
        if self.__user_event_triggered is False:
            self.__EventTriggered = False

    def pl_set_event_trigger_mode(self, mode):
        """
        Enables the plugin developer to set the event_trigger_mode. This meas that when set to TRUE, the
        plugin is set to be event triggered which means that the cb_execute function will only be called when
        a new event (newData) arrives.

        default will mean the default value for the specific plugin type.

        :param mode: True, False, or 'default'
        :return:
        """
        if mode is True or mode is False or mode == 'default':
            self.__user_event_triggered = mode

    def pl_get_current_config(self):
        """
        Used to get the current configuration.

        :return:
        """
        return self._config