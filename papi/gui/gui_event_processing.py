#!/usr/bin/python3
# -*- coding: latin-1 -*-

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
 
Contributors:
<Stefan Ruppin
"""

import copy
import traceback
import importlib.machinery
import sys

from papi.constants import PLUGIN_STATE_PAUSE, PLUGIN_VIP_IDENTIFIER, \
    GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER, GUI_WOKRING_INTERVAL, \
    PLUGIN_ROOT_FOLDER_LIST, PLUGIN_STATE_START_SUCCESFUL, PLUGIN_STATE_STOPPED, \
    PLUGIN_STATE_START_FAILED
from papi.gui.plugin_api import Plugin_api
import papi.error_codes as ERROR
import papi.event as Event
from papi.event.event_base import PapiEventBase
from papi.ConsoleLog import ConsoleLog
from papi.yapsy.PluginManager import PluginManager
from papi.data.DPlugin import DPlugin
from PyQt5 import QtCore




class GuiEventProcessing(QtCore.QObject):
    """
    This class will do all the event handling for a GUI process. It should be created and initialized with database and
    queues.
    To get all the functionality, one should link the callback functions (slots) for the needed signals.

    """
    added_dplugin = QtCore.pyqtSignal(DPlugin)
    removed_dplugin = QtCore.pyqtSignal(DPlugin)
    dgui_changed = QtCore.pyqtSignal()
    plugin_died = QtCore.pyqtSignal(DPlugin, Exception, str)

    def __init__(self, gui_data, core_queue, gui_id, gui_queue, TabManager, plugin_manager):
        """
        Init for eventProcessing

        :param gui_data:    Data object for all the plugin data
        :type gui_data: DGui
        :param core_queue:  multiprocessing queue for process interaction with core process
        :type core_queue: multiprocessing.Queue
        :param gui_id: id of gui process
        :type gui_id: int
        :param gui_queue:  multiprocessing queue for process interaction with gui process
        :type gui_queue: multiprocessing.Queue
        :return:
        """
        super(GuiEventProcessing, self).__init__()
        self.gui_data = gui_data
        self.core_queue = core_queue
        self.gui_id = gui_id
        self.log = ConsoleLog(GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER)
        self.plugin_manager = plugin_manager
        self.log.lvl = 0

        self.gui_queue = gui_queue
        self.TabManger = TabManager
        # switch case for event processing
        self.process_event = {'new_data': self.process_new_data_event,
                              'close_programm': self.process_close_program_event,
                              'check_alive_status': self.process_check_alive_status,
                              'create_plugin': self.process_create_plugin,
                              'update_meta': self.process_update_meta,
                              'plugin_closed': self.process_plugin_closed,
                              'set_parameter': self.process_set_parameter,
                              'pause_plugin': self.process_pause_plugin,
                              'resume_plugin': self.process_resume_plugin,
                              'stop_plugin': self.process_stop_plugin,
                              'start_plugin': self.process_start_plugin,
                              'parameter_info': self.process_parameter_info
        }

    def gui_working(self, close_mock, workingTimer):
        """
         Event processing loop of gui. Build to get called every 40ms after a run through.
         Will process all events of the queue at the time of call.
         Procedure was built this way, so that the processing of an event is not covered by the try/except structure.

         :type event: PapiEventBase
         :type dplugin: DPlugin
        """
        # event flag, true for first loop iteration to enter loop
        isEvent = True
        # event object, if there is an event
        event = None
        while (isEvent):
            # look at queue and try to get a new element
            try:
                event = self.gui_queue.get_nowait()
                # if there is a new element, event flag remains true
                isEvent = True
            except:
                # there was no new element, so event flag is set to false
                isEvent = False


            # check if there was a new element to process it
            if isEvent:
                # get the event operation
                op = event.get_event_operation()
                # debug out
                self.log.printText(2, 'Event: ' + op)
                # process this event
                if op == 'test_close':
                    close_mock()
                else:
                    self.process_event[op](event)
        # after the loop ended, which means that there are no more new events, a new timer will be created to start
        # this method again in a specific time

        workingTimer.start(GUI_WOKRING_INTERVAL)
        #QtCore.QTimer.singleShot(GUI_WOKRING_INTERVAL, lambda: self.gui_working(close_mock))

    def process_new_data_event(self, event):
        """
        Core sent a new data event to gui. Gui now needs to find the destination plugin and call its execute function
        with the new data.

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin: DPlugin
        """
        # debug print
        self.log.printText(2, 'new data event')
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
                # it exists, so call its execute function, but just if it is not paused ( no data delivery when paused )
                if dplugin.state != PLUGIN_STATE_PAUSE and dplugin.state != PLUGIN_STATE_STOPPED:
                    # check if new_data is a parameter or new raw data
                    try:
                        if opt.is_parameter is False:
                            dplugin.plugin.execute(
                                Data=dplugin.plugin.demux(opt.data_source_id, opt.block_name, opt.data),
                                block_name=opt.block_name, plugin_uname=event.source_plugin_uname)
                        else:
                            dplugin.plugin.set_parameter_internal(opt.parameter_alias, opt.data)
                    except Exception as E:
                        tb = traceback.format_exc()

                        self.plugin_died.emit(dplugin, E, tb)

            else:
                # plugin does not exist in DGUI
                self.log.printText(1, 'new_data, Plugin with id  ' + str(dID) + '  does not exist in DGui')

    def process_plugin_closed(self, event):
        """
        Processes plugin_closed event.
        Gui now knows, that a plugin was closed by core and needs to update its DGui data base

        :param event:
        :type event: PapiEventBase
        :return:
        """
        opt = event.get_optional_parameter()

        dplugin = self.gui_data.get_dplugin_by_id(opt.plugin_id)
        if dplugin is not None:
            if dplugin.own_process is False:
                try:
                    dplugin.plugin.quit()
                except Exception as E:
                    tb = traceback.format_exc()
                    self.plugin_died.emit(dplugin, E, tb)

        if self.gui_data.rm_dplugin(opt.plugin_id) == ERROR.NO_ERROR:
            self.log.printText(1, 'plugin_closed, Plugin with id: ' + str(opt.plugin_id) + ' was removed in GUI')
            self.dgui_changed.emit()
            self.removed_dplugin.emit(dplugin)
        else:
            self.log.printText(1, 'plugin_closed, Plugin with id: ' + str(opt.plugin_id) + ' was NOT removed in GUI')

    def process_stop_plugin(self, event):
        """
        Processes plugin_stop events.
        Quit plugin, emit DPlugin was removed -> necessary signal for the GUI.

        :param event:
        :return:
        """
        id = event.get_destinatioID()
        dplugin = self.gui_data.get_dplugin_by_id(id)
        if dplugin is not None:
            try:
                dplugin.plugin.quit()
                dplugin.state = PLUGIN_STATE_STOPPED
                self.removed_dplugin.emit(dplugin)
                self.dgui_changed.emit()
            except Exception as E:
                tb = traceback.format_exc()
                self.plugin_died.emit(dplugin, E, tb)

    def process_start_plugin(self, event):
        """
        Processes plugin_start event.
        Used to start a plugin after the plugin was stopped. Emit DPlugin was added -> necessary signal for the GUI.

        :param event:
        :return:
        """
        id = event.get_destinatioID()
        dplugin = self.gui_data.get_dplugin_by_id(id)
        if dplugin is not None:
            try:
                if dplugin.plugin.start_init(dplugin.plugin.get_current_config()) is True:
                    dplugin.state = PLUGIN_STATE_START_SUCCESFUL
                    self.added_dplugin.emit(dplugin)
                else:
                    dplugin.state = PLUGIN_STATE_START_FAILED
            except Exception as E:
                tb = traceback.format_exc()
                self.plugin_died.emit(dplugin, E, tb)

            self.dgui_changed.emit()


    def process_create_plugin(self, event):
        """
        Processes the create Plugin event. This event got sent by core to GUI.
        Gui now needs to add a new plugin to DGUI and decide whether it is a plugin running in the GUI process or not.

        :param event: event to process
        :type event: PapiEventBase
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
        self.log.printText(2,
                           'create_plugin, Try to create plugin with Name  ' + plugin_identifier + " and UName " + uname)

        # get the plugin object from yapsy manager
        plugin_orginal = self.plugin_manager.getPluginByName(plugin_identifier)

        # check for existance
        if plugin_orginal is None:
            # plugin with given identifier does not exist
            self.log.printText(1,
                               'create_plugin, Plugin with Name  ' + plugin_identifier + '  does not exist in file system')
            # end function
            return -1

        # plugin seems to exist, so get the path of the plugin file
        imp_path = plugin_orginal.path + ".py"
        # build a loader object for this plugin
        module_name = plugin_orginal.name.lower()

        spec = importlib.util.find_spec(module_name)
        #Module was not yet loaded
        if spec is None:
            loader = importlib.machinery.SourceFileLoader(module_name, imp_path)
            current_modul = loader.load_module()
            #Add path to sys path otherwise importlib.import_module will not find the module
            sys_path = "/".join(plugin_orginal.path.split('/')[0:-1])
            sys.path.append(sys_path)
        else:
            #Import module
            current_modul = importlib.import_module(module_name)

        # build the plugin class name for usage
        class_name = plugin_orginal.name[:1].upper() + plugin_orginal.name[1:]
        # get the plugin class of the source code loaded and init class as a new object
        plugin = getattr(current_modul, class_name)()
        # get default startup configuration for merge with user defined startup_configuration
        start_config = plugin.get_startup_configuration()
        config = dict(list(start_config.items()) + list(config.items()))

        # check if plugin in ViP (includes pcp) or something which is not running in the gui process
        if plugin.get_type() == PLUGIN_VIP_IDENTIFIER:
            # plugin in running in gui process
            # add a new dplugin object to DGui and set its type and uname
            dplugin = self.gui_data.add_plugin(None, None, False, self.gui_queue, plugin, id)
            dplugin.uname = uname
            dplugin.type = opt.plugin_type
            dplugin.plugin_identifier = plugin_identifier
            dplugin.startup_config = config
            dplugin.path = plugin_orginal.path
            # call the init function of plugin and set queues and id
            api = Plugin_api(self.gui_data, self.core_queue, self.gui_id, uname + ' API:', tabManager=self.TabManger)

            # call the plugin developers init function with config
            try:
                dplugin.plugin.init_plugin(self.core_queue, self.gui_queue, dplugin.id, api,
                                           dpluginInfo=dplugin.get_meta(),TabManger=self.TabManger)
                if dplugin.plugin.start_init(copy.deepcopy(config)) is True:
                    # start succcessfull
                    self.core_queue.put(Event.status.StartSuccessfull(dplugin.id, 0, None))
                else:
                    self.core_queue.put(Event.status.StartFailed(dplugin.id, 0, None))

                # first set meta to plugin (meta infos in plugin)
                if dplugin.state not in [PLUGIN_STATE_STOPPED]:
                    dplugin.plugin.update_plugin_meta(dplugin.get_meta())

            except Exception as E:
                dplugin.state = PLUGIN_STATE_STOPPED
                tb = traceback.format_exc()
                self.plugin_died.emit(dplugin, E, tb)



            # debug print
            self.log.printText(1, 'create_plugin, Plugin with name  ' + str(uname) + '  was started as ViP')
        else:
            # plugin will not be running in gui process, so we just need to add information to DGui
            # so add a new dplugin to DGUI and set name und type
            dplugin = self.gui_data.add_plugin(None, None, True, None, plugin, id)
            dplugin.plugin_identifier = plugin_identifier
            dplugin.uname = uname
            dplugin.startup_config = opt.plugin_config
            dplugin.type = opt.plugin_type
            dplugin.path = plugin_orginal.path
            # debug print
            self.log.printText(1, 'create_plugin, Plugin with name  ' + str(uname) + '  was added as non ViP')

        self.added_dplugin.emit(dplugin)
        self.dgui_changed.emit()

    def process_close_program_event(self, event):
        """
        Processes close programm event.
        Nothing important happens.

         :param event: event to process
         :type event: PapiEventBase
         :type dplugin: DPlugin
        """
        self.log.printText(1, 'event: close_progam was received but there is no action for it')
        pass

    def process_check_alive_status(self, event):
        """
        Gui received check_alive request form core, so gui will respond to it

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin: DPlugin
        """
        # send event from GUI to Core
        event = Event.status.Alive(1,0,None)
        self.core_queue.put(event)

    def process_update_meta(self, event):
        """
        Core sent new meta information of an existing plugin. This function will update DGui with these information

        :param event: event to process
        :type event: PapiEventBase
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
            # check if plugin runs in gui to update its copy of meta informations
            if dplugin.own_process is False:
                if dplugin.state not in [PLUGIN_STATE_STOPPED]:
                    # try:
                        dplugin.plugin.update_plugin_meta(dplugin.get_meta())
                    # except Exception as E:
                    #     dplugin.state = PLUGIN_STATE_STOPPED
                    #     tb = traceback.format_exc()
                    #     self.plugin_died.emit(dplugin, E, tb)

            self.dgui_changed.emit()
        else:
            # plugin does not exist
            self.log.printText(1, 'update_meta, Plugin with id  ' + str(pl_id) + '  does not exist')

    def process_update_parameter(self, event):
        print('Just update')

    def process_set_parameter(self, event):
        """
        Processes set_parameter event.
        Used to handle parameter sets by the gui or other plugins.

        :param event:
        :return:
        """
        # debug print
        self.log.printText(2, 'set parameter event')

        dID = event.get_destinatioID()
        # get optional data of event
        opt = event.get_optional_parameter()

        if isinstance(event, Event.instruction.UpdateParameter):
            return

        # get destination plugin from DGUI
        dplugin = self.gui_data.get_dplugin_by_id(dID)
        # check if it exists
        if dplugin is not None:
            # it exists, so call its execute function
            dplugin.plugin.set_parameter_internal(opt.parameter_alias, opt.data)
        else:
            # plugin does not exist in DGUI
            self.log.printText(1, 'set_parameter, Plugin with id  ' + str(dID) + '  does not exist in DGui')

    def process_pause_plugin(self, event):
        """
        Core sent event to pause a plugin in GUI, so call the pause function of this plugin

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin: DPlugin
        """
        pl_id = event.get_destinatioID()

        dplugin = self.gui_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            dplugin.plugin.pause()

    def process_resume_plugin(self, event):
        """
        Core sent event to resume a plugin in GUI, so call the resume function of this plugin

        :param event: event to process
        :type event: PapiEventBase
        :type dplugin: DPlugin
        """
        pl_id = event.get_destinatioID()

        dplugin = self.gui_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            dplugin.plugin.resume()

    def process_parameter_info(self, event):
        """

        :param event:
        :return:
        """
        pl_id = event.get_destinatioID()

        dplugin = self.gui_data.get_dplugin_by_id(pl_id)

        if dplugin is not None:
            dplugin.plugin.new_parameter_info(event.dparameter_object)
