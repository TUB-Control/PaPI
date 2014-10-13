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
 
Contributors:
<Stefan Ruppin
"""

from papi.constants import PLUGIN_STATE_PAUSE, PLUGIN_VIP_IDENTIFIER, PLUGIN_PCP_IDENTIFIER, \
    GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER, \
    PLUGIN_ROOT_FOLDER_LIST

from papi.PapiEvent import PapiEvent

from papi.ConsoleLog import ConsoleLog

from yapsy.PluginManager import PluginManager

import importlib.machinery


from papi.data.DOptionalData import DOptionalData

__author__ = 'Stefan'

class GuiEventProcessing:

    def __init__(self, gui_data, core_queue, gui_id, gui_queue, scopeArea):
        self.gui_data = gui_data
        self.core_queue = core_queue
        self.gui_id = gui_id
        self.log = ConsoleLog(GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER)
        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(PLUGIN_ROOT_FOLDER_LIST)
        self.gui_queue = gui_queue
        self.scopeArea = scopeArea

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
                # it exists, so call its execute function, but just if it is not paused ( no data delivery when paused )
                if dplugin.state != PLUGIN_STATE_PAUSE:
                    dplugin.plugin.execute(dplugin.plugin.demux(opt.data_source_id, opt.block_name, opt.data))
            else:
                # plugin does not exist in DGUI
                self.log.printText(1,'new_data, Plugin with id  '+str(dID)+'  does not exist in DGui')

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
        # get default startup configuration for merge with user defined startup_configuration
        start_config = plugin.get_startup_configuration()
        config = dict(list(start_config.items()) + list(config.items()) )

        # check if plugin in ViP (includes pcp) or something which is not running in the gui process
        if plugin.get_type() == PLUGIN_VIP_IDENTIFIER or plugin.get_type() == PLUGIN_PCP_IDENTIFIER:
            # plugin in running in gui process
            # add a new dplugin object to DGui and set its type and uname
            dplugin =self.gui_data.add_plugin(None, None, False, self.gui_queue,plugin,id)
            dplugin.uname = uname
            dplugin.type = opt.plugin_type
            dplugin.plugin_identifier = plugin_identifier
            dplugin.startup_config = opt.plugin_config
            # call the init function of plugin and set queues and id
            dplugin.plugin.init_plugin(self.core_queue, self.gui_queue, dplugin.id)

            # call the plugin developers init function with config
            dplugin.plugin.start_init(config)

            # first set meta to plugin
            dplugin.plugin.update_plugin_meta(dplugin.get_meta())

            # add a window to gui for new plugin and show it
            self.scopeArea.addSubWindow(dplugin.plugin.get_sub_window())
            dplugin.plugin.get_sub_window().show()

            # debug print
            self.log.printText(1,'create_plugin, Plugin with name  '+str(uname)+'  was started as ViP')

        else:
            # plugin will not be running in gui process, so we just need to add information to DGui
            # so add a new dplugin to DGUI and set name und type
            dplugin =self.gui_data.add_plugin(None,None,True,None,plugin,id)
            dplugin.plugin_identifier = plugin_identifier
            dplugin.uname = uname
            dplugin.startup_config = opt.plugin_config
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
            # check if plugin runs in gui to update its copy of meta informations
            if dplugin.own_process is False:
                dplugin.plugin.update_plugin_meta(dplugin.get_meta())
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
        if dplugin is not None:
            # it exists, so call its execute function
            #dplugin.plugin.set_parameter_internal(opt.parameter_list)
            #TODO
            pass
        else:
            # plugin does not exist in DGUI
            self.log.printText(1,'set_parameter, Plugin with id  '+str(dID)+'  does not exist in DGui')

    def process_pause_plugin(self, event):
        """
        Core sent event to pause a plugin in GUI, so call the pause function of this plugin
        :param event: event to process
        :type event: PapiEvent
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
        :type event: PapiEvent
        :type dplugin: DPlugin
        """
        pl_id = event.get_destinatioID()

        dplugin = self.gui_data.get_dplugin_by_id(pl_id)
        if dplugin is not None:
            dplugin.plugin.resume()