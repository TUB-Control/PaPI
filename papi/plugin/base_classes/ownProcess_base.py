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


from papi.plugin.base_classes.base_plugin import base_plugin
import papi.event as Event

class ownProcess_base(base_plugin):

    def work_process(self, CoreQueue, pluginQueue, id, defaultEventTriggered=False, config=None, autostart=True):
        # set queues and id
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        self.EventTriggered = defaultEventTriggered
        self.user_event_triggered = 'default'
        self.paused = False

        self.papi_init()

        # working should go at least one time
        self.goOn = 1

        self.plugin_stopped = False

        if autostart is True:
            # call start_init function to use developers init
            self.starting_sequence(config)
        else:
            self.plugin_stopped = True

        # main working loop
        while self.goOn:
            self.evaluate_event_trigger(defaultEventTriggered)
            event = None
            try:
                event = self.__plugin_queue__.get( self.paused or self.EventTriggered or self.plugin_stopped)
                #process event
            except:
                event = None


            if event is not None:
                op = event.get_event_operation()
                if op=='stop_plugin' :
                    self.quit()
                    if event.delete is True:
                        # delete plugin, so work_progress will stop completely
                        self.goOn = 0
                        event = Event.status.JoinRequest(self.__id__, 0, None)
                        self._Core_event_queue__.put(event)
                    else:
                        # plugin should stop but is not getting deleted
                        # response to core and rm_all_subs, blocks, paras
                        self.plugin_stopped = True
                        event = Event.status.PluginStopped(self.__id__, 0, None)
                        self._Core_event_queue__.put(event)

                if op=='start_plugin' and self.plugin_stopped is True:
                    # maybe new config?
                    self.starting_sequence(config)
                    self.plugin_stopped = False


                if op=='pause_plugin' and self.paused is False and self.plugin_stopped is False:
                    self.paused = True
                    self.pause()
                if op=='resume_plugin' and self.paused is True and self.plugin_stopped is False:
                    self.paused = False
                    self.resume()
                if op=='check_alive_status':
                    alive_event = Event.status.Alive(self.__id__, 0, None)
                    self._Core_event_queue__.put(alive_event)
                if op=='new_data' and self.paused is False and self.plugin_stopped is False:
                    opt = event.get_optional_parameter()
                    if opt.is_parameter is False:
                        data = self.demux(opt.data_source_id, opt.block_name, opt.data)
                        self.execute(Data=data, block_name = opt.block_name)
                    if opt.is_parameter is True:
                        self.set_parameter_internal(opt.parameter_alias, opt.data)
                if op == 'set_parameter' and self.plugin_stopped is False:
                    opt = event.get_optional_parameter()
                    self.set_parameter_internal(opt.parameter_alias, opt.data)

                if op == 'update_meta' and self.plugin_stopped is False:
                    opt = event.get_optional_parameter()
                    self.update_plugin_meta(opt.plugin_object)

            else:
                if self.paused or self.EventTriggered or self.plugin_stopped:
                    pass
                else:
                    self.execute()

    def starting_sequence(self, config):
        if self.start_init(config):
            # report start successfull event
            event = Event.status.StartSuccessfull(self.__id__, 0, None)
            self._Core_event_queue__.put(event)
        else:
            # init failed, so report it to core
            event = Event.status.StartFailed(self.__id__, 0, None)
            self._Core_event_queue__.put(event)
            # end plugin
            self.goOn = 0
            # sent join request to core
            event = Event.status.JoinRequest(self.__id__, 0, None)
            self._Core_event_queue__.put(event)

    def start_init(self, config):
        raise NotImplementedError("Please Implement this method")
