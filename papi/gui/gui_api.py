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


import datetime
import time
import traceback
import os
import json

import papi.event as Event

from papi.data.DOptionalData import DOptionalData
from papi.ConsoleLog import ConsoleLog
from papi.constants import GUI_PROCESS_CONSOLE_IDENTIFIER, GUI_PROCESS_CONSOLE_LOG_LEVEL, CONFIG_LOADER_SUBSCRIBE_DELAY, \
    CONFIG_ROOT_ELEMENT_NAME, CORE_PAPI_VERSION, PLUGIN_VIP_IDENTIFIER, CONFIG_ROOT_ELEMENT_NAME_RELOADED, \
    CONFIG_SAVE_CFG_BLACKLIST, CORE_TIME_SIGNAL

from PyQt5 import QtCore

from papi.data.DSignal import DSignal
from papi.data.DPlugin import DBlock

import papi.error_codes as ERROR

import xml.etree.cElementTree as ET


class Gui_api(QtCore.QObject):
    error_occured = QtCore.pyqtSignal(str, str, str)

    def __init__(self, gui_data, core_queue, gui_id, get_gui_config_function = None, set_gui_config_function = None, TabManager = None, plugin_manager = None):
        super(Gui_api, self).__init__()
        self.gui_id = gui_id
        self.gui_data = gui_data
        self.core_queue = core_queue
        self.log = ConsoleLog(GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER)
        self.get_gui_config_function = get_gui_config_function
        self.set_gui_config_function = set_gui_config_function
        self.tabManager = TabManager
        self.pluginManager = plugin_manager

    def do_create_plugin(self, plugin_identifier, uname, config={}, autostart=True):
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
        opt.autostart = autostart

        # check if plugin with uname already exists
        allPlugins = self.gui_data.get_all_plugins()
        for pluginID in allPlugins:
            plugin = allPlugins[pluginID]
            if plugin.uname == uname:
                return False

        # create event object and sent it to core
        event = Event.instruction.CreatePlugin(self.gui_id, 0, opt)
        self.core_queue.put(event)

    def do_delete_plugin(self, id):
        """
        Delete plugin with given id.

        :param id: Plugin id to delete
        :type id: int
        :return:
        """
        event = Event.instruction.StopPlugin(self.gui_id, id, None)

        self.core_queue.put(event)

    def do_delete_plugin_uname(self, uname):
        """
        Delete plugin with given uname.

        :param uname: Plugin uname to delete
        :type uname: basestring
        :return:
        """
        event =Event.instruction.StopPluginByUname(self.gui_id, uname)
        self.core_queue.put(event)

    def do_edit_plugin(self, pl_id, eObject, changeRequest):
        """
        Edit plugin with given plugin id. Specify attribute of plugin by eObject which should
        be edited e.g. DBlock.
        Specify action by changeRequest e.g. {'edit' : DSignal}.
        Currently only possible to change a DSignal for a given dplugin and dblock.

        :param pl_id: Plugin id to delete
        :type pl_id: int
        :return:
        """
        event = Event.data.EditDPlugin(self.gui_id, pl_id, eObject, changeRequest)

        self.core_queue.put(event)

    def do_edit_plugin_uname(self, uname, eObject, changeRequest):
        """
        Edit plugin with given plugin uname. Specify attribute of plugin by eObject which should
        be edited e.g. DBlock.
        Specify action by changeRequest e.g. {'edit' : DSignal}.
        Currently only possible to change a DSignal for a given dplugin and dblock.

        :param uname:
        :param eObject:
        :param changeRequest:
        :return:
        """
        event = Event.data.EditDPluginByUname(self.gui_id, uname, eObject, changeRequest)

        self.core_queue.put(event)

    def do_stopReset_pluign(self, id):
        """
        Stop and reset plugin with given id without deleting it.

        :param id: Plugin id to stopReset
        :type id: int
        :return:
        """
        event = Event.instruction.StopPlugin(self.gui_id, id, None, delete=False)
        self.core_queue.put(event)

    def do_stopReset_plugin_uname(self, uname):
        """
        Stop and reset plugin with given uname without deleting it.

        :param uname: Plugin uname to stop
        :type uname: basestring
        :return:
        """
        pl_id = self.do_get_plugin_id_from_uname(uname)

        if pl_id is not None:
            self.do_stopReset_pluign(pl_id)
        else:
            self.log.printText(1, " Do stopReset plugin with uname " + uname + ' failed')
            return ERROR.NOT_EXISTING

    def do_start_plugin(self, id):
        """
        Start plugin with given id.

        :param id: Plugin id to start
        :type id: int
        :return:
        """
        event = Event.instruction.StartPlugin(self.gui_id, id, None)
        self.core_queue.put(event)

    def do_start_plugin_uname(self, uname):
        """
        Start plugin with given uname.

        :param uname: Plugin uname to start
        :type uname: basestring
        :return:
        """
        pl_id = self.do_get_plugin_id_from_uname(uname)

        if pl_id is not None:
            self.do_start_plugin(pl_id)
        else:
            self.log.printText(1, " Do start_plugin with uname " + uname + ' failed')
            return ERROR.NOT_EXISTING

    def do_subscribe(self, subscriber_id, source_id, block_name, signals=None, sub_alias=None):
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
        # build optional data object and add id and block name to it
        opt = DOptionalData()
        opt.source_ID = source_id
        opt.block_name = block_name
        opt.signals = signals
        opt.subscription_alias = sub_alias
        # send event with subscriber id as the origin to CORE
        event = Event.instruction.Subscribe(subscriber_id, 0, opt)
        self.core_queue.put(event)

    def do_subscribe_uname(self, subscriber_uname, source_uname, block_name, signals=None, sub_alias=None):
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
        event = Event.instruction.SubscribeByUname(self.gui_id, 0, subscriber_uname, source_uname, block_name,
                                                   signals=signals, sub_alias= sub_alias)
        self.core_queue.put(event)

    def do_unsubscribe(self, subscriber_id, source_id, block_name, signal_index=None):
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
        opt.signals = signal_index
        # sent event to Core with origin subscriber_id
        event = Event.instruction.Unsubscribe(subscriber_id, 0, opt)
        self.core_queue.put(event)

    def do_unsubscribe_uname(self, subscriber_uname, source_uname, block_name, signal_index=None):
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
        subscriber_id = self.do_get_plugin_id_from_uname(subscriber_uname)
        if subscriber_id is None:
            # plugin with uname does not exist
            self.log.printText(1, 'do_unsubscribe, sub uname worng')
            return -1

        source_id = self.do_get_plugin_id_from_uname(source_uname)
        if source_id is None:
            # plugin with uname does not exist
            self.log.printText(1, 'do_unsubscribe, target uname wrong')
            return -1

        # call do_subscribe with ids to subscribe
        self.do_unsubscribe(subscriber_id, source_id, block_name, signal_index)

    def do_set_parameter(self, plugin_id, parameter_name, value, only_db_update = False):
        """
        Something like a callback function for gui triggered events.
        User wants to change a parameter of a plugin
        :param plugin_id: id of plugin which owns the parameter

        :type plugin_id: int
        :param parameter_name: name of parameter to change
        :type parameter_name: basestring
        :param value: new parameter value to set
        :type value:
        :param only_db_update: do_set_parameter of the target plugin will not be called. Updates only the internal database.
        :type boolean:
        """
        # get plugin from DGUI
        dplug = self.gui_data.get_dplugin_by_id(plugin_id)
        # check for existance
        if dplug is not None:
            # it exists
            # get its parameter list
            parameters = dplug.get_parameters()
            # check if there are any parameter
            if parameters is not None:
                # there is a parameter list
                # get the parameter with parameter_name
                if parameter_name in parameters:
                    p = parameters[parameter_name]
                    # check if this specific parameter exists
                    if p is not None:
                        # parameter with name parameter_name exists

                        # build an event to send this information to Core
                        opt = DOptionalData()
                        opt.data = value
                        opt.is_parameter = True
                        opt.parameter_alias = parameter_name
                        opt.block_name = None
                        if only_db_update:
                            e = Event.instruction.UpdateParameter(self.gui_id, dplug.id, opt)
                        else:
                            e = Event.instruction.SetParameter(self.gui_id, dplug.id, opt)
                        self.core_queue.put(e)

    def do_set_parameter_uname(self, plugin_uname, parameter_name, value):
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
        # id = self.do_get_plugin_id_from_uname(plugin_uname)
        # if id is not None:
        #     self.do_set_parameter(id, parameter_name, value)
        #     print(parameter_name, value)
        opt = DOptionalData()
        opt.data = value
        opt.is_parameter = True
        opt.parameter_alias = parameter_name
        opt.block_name = None
        e = Event.instruction.SetParameterByUname(self.gui_id,plugin_uname, opt)
        self.core_queue.put(e)

    def do_pause_plugin_by_id(self, plugin_id):
        """
        Something like a callback function for gui triggered events.
        User wants to pause a plugin, so this method will send an event to core.

        :param plugin_id: id of plugin to pause
        :type plugin_id: int
        """
        if self.gui_data.get_dplugin_by_id(plugin_id) is not None:
            opt = DOptionalData()
            event = Event.instruction.PausePlugin(self.gui_id, plugin_id, opt)
            self.core_queue.put(event)
            return 1
        else:
            return -1

    def do_pause_plugin_by_uname(self, plugin_uname):
        """
        Something like a callback function for gui triggered events.
        User wants to pause a plugin, so this method will send an event to core.

        :param plugin_uname: uname of plugin to pause
        :type plugin_uname: basestring
        """
        plugin_id = self.do_get_plugin_id_from_uname(plugin_uname)
        if plugin_id is not None:
            return self.do_pause_plugin_by_id(plugin_id)
        else:
            # plugin with uname does not exist
            self.log.printText(1, 'do_pause, plugin uname worng')
            return -1

    def do_resume_plugin_by_id(self, plugin_id):
        """
        Something like a callback function for gui triggered events.
        User wants to pause a plugin, so this method will send an event to core.

        :param plugin_id: id of plugin to pause
        :type plugin_id: int
        """
        if self.gui_data.get_dplugin_by_id(plugin_id) is not None:
            opt = DOptionalData()
            event = Event.instruction.ResumePlugin(self.gui_id, plugin_id, opt)
            self.core_queue.put(event)
            return 1
        else:
            return -1

    def do_resume_plugin_by_uname(self, plugin_uname):
        """
        Something like a callback function for gui triggered events.
        User wants to resume a plugin, so this method will send an event to core.

        :param plugin_uname: uname of plugin to resume
        :type plugin_uname: basestring
        """
        plugin_id = self.do_get_plugin_id_from_uname(plugin_uname)
        if plugin_id is not None:
            return self.do_resume_plugin_by_id(plugin_id)
        else:
            # plugin with uname does not exist
            self.log.printText(1, 'do_resume, plugin uname worng')
            return -1

    def do_get_plugin_id_from_uname(self, uname):
        """
        Returns the plugin id of the plugin with unique name uname

        :param uname: uname of plugin
        :type uname: basestring
        :return: None: plugin with uname does not exist, id: id of plugin
        """
        dplugin = self.gui_data.get_dplugin_by_uname(uname)
        # check for existance
        if dplugin is not None:
            # it does exist, so get its id
            return dplugin.id
        else:
            return None

    def do_close_program(self):
        """
        Tell core to close papi. Core will respond and will close all open plugins.
        GUI will close all VIP Plugins due to calling their quit function
        """

        plugins = self.gui_data.get_all_plugins()
        for dplugin_id in plugins:
            dplugin = plugins[dplugin_id]
            if dplugin.type == PLUGIN_VIP_IDENTIFIER:
                try:
                    dplugin.plugin.cb_quit()
                except Exception as E:
                    tb = traceback.format_exc()
                    self.plugin_died.emit(dplugin, E, tb)


        opt = DOptionalData()
        opt.reason = 'User clicked close Button'
        event = Event.instruction.CloseProgram(self.gui_id, 0, opt)
        self.core_queue.put(event)

    def do_set_tab_active_by_name(self, tabName):
        self.tabManager.set_tab_active_by_name(tabName)

    def do_open_new_tabs_with_names_in_order(self, tabNames = None):
        for name in tabNames:
            self.tabManager.add_tab(name)

    def do_load_xml(self, path):
        if path is None or not os.path.isfile(path):
            return False

        tree = ET.parse(path)
        root = tree.getroot()

        if root.tag == 'PaPI':
            self.do_load_xml_reloaded(root)
        else:
            self.do_load_xml_v1(root)

    def do_load_xml_reloaded(self,root):
        """
        Function to load a xml config to papi and apply the configuration.

        :param path: path to xml file to load.
        :type path: basestring
        :return:
        """

        gui_config = {}
        plugins_to_start = []
        parameters_to_change = []
        signals_to_change = []
        subs_to_make = []

        try:
            for root_element in root:
                ##########################
                # Read gui configuration #
                ##########################
                if root_element.tag == 'Configuration':
                    for property in root_element:
                        gui_config[property.tag] = {}
                        for attr in property:
                            if len(attr) == 0:
                                gui_config[property.tag][attr.tag] = attr.text
                            else:
                                gui_config[property.tag][attr.tag] = {}
                                for val in attr:
                                   gui_config[property.tag][attr.tag][val.tag] = val.text



                if root_element.tag == 'Plugins':
                    #############################
                    # Read plugin configuration #
                    #############################
                    for plugin_xml in root_element:
                        plObj = {}
                        plObj['uname'] = self.change_uname_to_uniqe(plugin_xml.attrib['uname'])
                        plObj['identifier'] = plugin_xml.find('Identifier').text
                        config_xml = plugin_xml.find('StartConfig')
                        config_hash = {}
                        for parameter_xml in config_xml.findall('Parameter'):
                            para_name = parameter_xml.attrib['Name']
                            config_hash[para_name] = {}
                            for detail_xml in parameter_xml:
                                detail_name = detail_xml.tag
                                config_hash[para_name][detail_name] = detail_xml.text

                        plObj['cfg'] = config_hash

                        plugins_to_start.append(plObj)

                        # --------------------------------
                        # Load PreviousParameters
                        # --------------------------------

                        prev_parameters_xml = plugin_xml.find('PreviousParameters')
                        if prev_parameters_xml is not None:
                            for prev_parameter_xml in prev_parameters_xml.findall('Parameter'):
                                para_name = prev_parameter_xml.attrib['Name']
                                para_value = prev_parameter_xml.text
                                # pl_uname_new = self.change_uname_to_uniqe(pl_uname)
                                # TODO validate NO FLOAT in parameter
                                parameters_to_change.append([plObj['uname'], para_name, para_value])

                        # --------------------------------
                        # Load DBlocks due to signals name
                        # --------------------------------

                        dblocks_xml = plugin_xml.find('DBlocks')
                        if dblocks_xml is not None:
                            for dblock_xml in dblocks_xml:
                                dblock_name = dblock_xml.attrib['Name']
                                dsignals_xml = dblock_xml.findall('DSignal')
                                for dsignal_xml in dsignals_xml:
                                    dsignal_uname = dsignal_xml.attrib['uname']
                                    dsignal_dname = dsignal_xml.find('dname').text
                                    signals_to_change.append([plObj['uname'], dblock_name, dsignal_uname, dsignal_dname])

                if root_element.tag == 'Subscriptions':
                    for sub_xml in root_element:

                        #TODO: Ask stefan: Why this line?
                        #dest  = self.change_uname_to_uniqe(sub_xml.find('Destination').text)

                        dest  = sub_xml.find('Destination').text
                        for source in sub_xml:
                            if source.tag == 'Source':
                                sourceName =  source.attrib['uname'] #self.change_uname_to_uniqe(source.attrib['uname'])
                                for block_xml in source:
                                    blockName = block_xml.attrib['name']
                                    alias = block_xml.find('Alias').text
                                    signals_xml = block_xml.find('Signals')

                                    signals = []
                                    for sig_xml in signals_xml:
                                        signals.append(sig_xml.text)

                                    subs_to_make.append({'dest':dest, 'source':sourceName, 'block':blockName, 'alias':alias, 'signals':signals})

            self.set_gui_config_function(gui_config)

        except Exception as E:
            tb = traceback.format_exc()
            self.error_occured.emit("Error: Config Loader", "Not loadable", tb)


        # -----------------------------------------------
        # Check: Are there unloadable plugins?
        # -----------------------------------------------

        unloadable_plugins = []
        for pl in plugins_to_start:
            plugin_info = self.pluginManager.getPluginByName(pl['identifier'])

            if plugin_info is None:
                if pl['identifier'] not in unloadable_plugins:
                    unloadable_plugins.append(pl['identifier'])



        if not len(unloadable_plugins):
            for pl in plugins_to_start:
                self.do_create_plugin(pl['identifier'], pl['uname'], pl['cfg'])


            self.config_loader_subs_reloaded(plugins_to_start, subs_to_make, parameters_to_change, signals_to_change)
        else:
            self.error_occured.emit("Error: Loading Plugins", "Can't use: " + str(unloadable_plugins) +
                                    "\nConfiguration will not be used.", None)


    def config_loader_subs_reloaded(self, pl_to_start, subs_to_make, parameters_to_change, signals_to_change):
        """
        Function for callback when timer finished to apply
            subscriptions and parameter changed of config.

        :param pl_to_start: list of plugins to start
        :type pl_to_start: list
        :param subs_to_make:  list of subscriptions to make
        :type subs_to_make: list
        :param parameters_to_change: parameter changes to apply
        :type parameters_to_change: list
        :param signals_to_change: signal name changes to apply
        :type signals_to_change: list
        :return:
        """

        for sub in subs_to_make:
            self.do_subscribe_uname(sub['dest'], sub['source'], sub['block'], sub['signals'], sub['alias'])

        for para in parameters_to_change:
            self.do_set_parameter_uname(para[0], para[1], para[2])

        for sig in signals_to_change:
            plugin_uname = sig[0]
            dblock_name = sig[1]
            dsignal_uname = sig[2]
            dsignal_dname = sig[3]

            self.do_edit_plugin_uname(plugin_uname, DBlock(dblock_name),{'edit': DSignal(dsignal_uname, dsignal_dname)})


    def do_load_xml_v1(self, root):
        """
        Function to load a xml config to papi and apply the configuration.

        :param path: path to xml file to load.
        :type path: basestring
        :return:
        """

        plugins_to_start = []
        subs_to_make = []
        parameters_to_change = []
        signals_to_change = []

        try:
            for plugin_xml in root:
                ##########################
                # Read gui configuration #
                ##########################
                if plugin_xml.tag == 'guiConfig':
                    cfg = {}
                    for property in plugin_xml:
                        cfg[property.tag] =  {}
                        for attr in property:
                            cfg[property.tag][attr.tag] = {}
                            for value in attr:
                                cfg[property.tag][attr.tag][value.tag] = value.text

                    self.set_gui_config_function(cfg)

                #############################
                # Read plugin configuration #
                #############################
                if plugin_xml.tag == 'Plugin':
                    pl_uname = plugin_xml.attrib['uname']
                    identifier = plugin_xml.find('Identifier').text
                    config_xml = plugin_xml.find('StartConfig')
                    config_hash = {}
                    for parameter_xml in config_xml.findall('Parameter'):
                        para_name = parameter_xml.attrib['Name']
                        config_hash[para_name] = {}
                        for detail_xml in parameter_xml:
                            detail_name = detail_xml.tag
                            config_hash[para_name][detail_name] = detail_xml.text

                    pl_uname_new = self.change_uname_to_uniqe(pl_uname)

                    plugins_to_start.append([identifier, pl_uname_new, config_hash])

                    # --------------------------------
                    # Load Subscriptions
                    # --------------------------------

                    subs_xml = plugin_xml.find('Subscriptions')
                    if subs_xml is not None:
                        for sub_xml in subs_xml.findall('Subscription'):
                            data_source = sub_xml.find('data_source').text
                            for block_xml in sub_xml.findall('block'):
                                block_name = block_xml.attrib['Name']
                                signals = []
                                for sig_xml in block_xml.findall('Signal'):
                                    signals.append(str(sig_xml.text))
                                alias_xml = block_xml.find('alias')
                                alias = alias_xml.text
                                pl_uname_new = self.change_uname_to_uniqe(pl_uname)
                                data_source_new = data_source #self.change_uname_to_uniqe(data_source)
                                subs_to_make.append([pl_uname_new, data_source_new, block_name, signals, alias])

                    # --------------------------------
                    # Load PreviousParameters
                    # --------------------------------

                    prev_parameters_xml = plugin_xml.find('PreviousParameters')
                    if prev_parameters_xml is not None:
                        for prev_parameter_xml in prev_parameters_xml.findall('Parameter'):
                            para_name = prev_parameter_xml.attrib['Name']
                            para_value = prev_parameter_xml.text
                            pl_uname_new = self.change_uname_to_uniqe(pl_uname)
                            # TODO validate NO FLOAT in parameter
                            parameters_to_change.append([pl_uname_new, para_name, para_value])

                    # --------------------------------
                    # Load DBlocks due to signals name
                    # --------------------------------

                    dblocks_xml = plugin_xml.find('DBlocks')
                    if dblocks_xml is not None:
                        for dblock_xml in dblocks_xml:
                            dblock_name = dblock_xml.attrib['Name']
                            dsignals_xml = dblock_xml.findall('DSignal')
                            for dsignal_xml in dsignals_xml:
                                dsignal_uname = dsignal_xml.attrib['uname']
                                dsignal_dname = dsignal_xml.find('dname').text
                                signals_to_change.append([pl_uname, dblock_name, dsignal_uname, dsignal_dname])
        except Exception as E:
            tb = traceback.format_exc()
            self.error_occured.emit("Error: Config Loader", "Not loadable", tb)


        # -----------------------------------------------
        # Check: Are there unloadable plugins?
        # -----------------------------------------------

        unloadable_plugins = []
        for pl in plugins_to_start:
            plugin_info = self.pluginManager.getPluginByName(pl[0])

            if plugin_info is None:
                if pl[0] not in unloadable_plugins:
                    unloadable_plugins.append(pl[0])



        if not len(unloadable_plugins):
            for pl in plugins_to_start:
                # 0: ident, 1: uname, 2: config

                self.do_create_plugin(pl[0], pl[1], pl[2])

            # QtCore.QTimer.singleShot(CONFIG_LOADER_SUBSCRIBE_DELAY, \
            #                         lambda: self.config_loader_subs(plugins_to_start, subs_to_make, \
            #                                                         parameters_to_change, signals_to_change))
            self.config_loader_subs(plugins_to_start, subs_to_make, parameters_to_change, signals_to_change)
        else:
            self.error_occured.emit("Error: Loading Plugins", "Can't use: " + str(unloadable_plugins) +
                                    "\nConfiguration will not be used.", None)

    def change_uname_to_uniqe(self, uname):
        """
        Function will search for unames and add an indentifier to it to make it unique in case of existence

        :param uname: uname to make unique
        :type uname: basestring
        :return: uname
        """
        i = 1
        while self.gui_data.get_dplugin_by_uname(uname) is not None:
            i = i + 1
            if i == 2:
                uname = uname + 'X' + str(i)
            else:
                uname = uname[:-1] + str(i)
        return uname

    def config_loader_subs(self, pl_to_start, subs_to_make, parameters_to_change, signals_to_change):
        """
        Function for callback when timer finished to apply
            subscriptions and parameter changed of config.

        :param pl_to_start: list of plugins to start
        :type pl_to_start: list
        :param subs_to_make:  list of subscriptions to make
        :type subs_to_make: list
        :param parameters_to_change: parameter changes to apply
        :type parameters_to_change: list
        :param signals_to_change: signal name changes to apply
        :type signals_to_change: list
        :return:
        """

        for sub in subs_to_make:
            self.do_subscribe_uname(sub[0], sub[1], sub[2], sub[3], sub[4])

        for para in parameters_to_change:
            self.do_set_parameter_uname(para[0], para[1], para[2])

        for sig in signals_to_change:
            plugin_uname = sig[0]
            dblock_name = sig[1]
            dsignal_uname = sig[2]
            dsignal_dname = sig[3]

            self.do_edit_plugin_uname(plugin_uname, DBlock(dblock_name),
                                      {'edit': DSignal(dsignal_uname, dsignal_dname)})

    def do_save_xml_config_reloaded(self,path, plToSave=[], sToSave=[], saveUserSettings=False):
        """

        :param path:
        :param plToSave:
        :param sToSave:
        :return:
        """

        subscriptionsToSave =  {}
        # check for xml extension in path, add .xml if missing
        if path[-4:] != '.xml':
            path += '.xml'

        try:
            root = ET.Element(CONFIG_ROOT_ELEMENT_NAME_RELOADED)
            root.set('Date', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            root.set('PaPI_version', CORE_PAPI_VERSION)

            ##########################
            # Save gui configuration #
            ##########################
            gui_cfg = self.get_gui_config_function(save_user_settings=saveUserSettings)
            gui_cfg_xml = ET.SubElement(root, 'Configuration')

            for cfg_item in gui_cfg:
                item_xml = ET.SubElement(gui_cfg_xml,cfg_item)
                item = gui_cfg[cfg_item]
                for attr_name in item:
                    attr_xml = ET.SubElement(item_xml, attr_name)
                    values = item[attr_name]

                    # check if there is another dict level to explore
                    # if true: exlplore the dict
                    # if false: save the value of values in the parent xml node
                    if isinstance(values,dict):
                        for val in values:
                            value_xml = ET.SubElement(attr_xml, val)
                            value_xml.text = values[val]
                    else:
                        attr_xml.text = values

            # ---------------------------------------
            # save information of plugins
            # for the next start
            # ---------------------------------------
            plugins_xml = ET.SubElement(root,'Plugins')

            plugins = self.gui_data.get_all_plugins()
            for dplugin_id in plugins:
                dplugin = plugins[dplugin_id]

                # check if this plugin should be saved to XML
                if dplugin.uname in plToSave:
                    if dplugin.type == PLUGIN_VIP_IDENTIFIER:
                        dplugin.startup_config = dplugin.plugin.pl_get_current_config()

                    pl_xml = ET.SubElement(plugins_xml, 'Plugin')
                    pl_xml.set('uname', dplugin.uname)

                    identifier_xml = ET.SubElement(pl_xml, 'Identifier')
                    identifier_xml.text = dplugin.plugin_identifier

                    # ---------------------------------------
                    # Save all current config as startup config
                    # for the next start
                    # ---------------------------------------

                    cfg_xml = ET.SubElement(pl_xml, 'StartConfig')
                    for parameter in dplugin.startup_config:
                        para_xml = ET.SubElement(cfg_xml, 'Parameter')
                        para_xml.set('Name', parameter)
                        for detail in dplugin.startup_config[parameter]:
                            if detail not in CONFIG_SAVE_CFG_BLACKLIST:
                                detail_xml = ET.SubElement(para_xml, detail)
                                detail_xml.text = dplugin.startup_config[parameter][detail]

                    # ---------------------------------------
                    # Save all current values for all
                    # parameter
                    # ---------------------------------------

                    last_paras_xml = ET.SubElement(pl_xml, 'PreviousParameters')
                    allparas = dplugin.get_parameters()
                    for para_key in allparas:
                        para = allparas[para_key]
                        last_para_xml = ET.SubElement(last_paras_xml, 'Parameter')
                        last_para_xml.set('Name', para_key)
                        last_para_xml.text = str(para.value)

                    # ---------------------------------------
                    # Save all current values for all
                    # signals of all dblocks
                    # ---------------------------------------

                    dblocks_xml = ET.SubElement(pl_xml, 'DBlocks')

                    alldblock_names = dplugin.get_dblocks()

                    for dblock_name in alldblock_names:
                        dblock = alldblock_names[dblock_name]
                        dblock_xml = ET.SubElement(dblocks_xml, 'DBlock')
                        dblock_xml.set('Name', dblock.name)

                        alldsignals = dblock.get_signals()

                        for dsignal in alldsignals:
                            if dsignal.uname != CORE_TIME_SIGNAL:
                                dsignal_xml = ET.SubElement(dblock_xml, 'DSignal')
                                dsignal_xml.set('uname', dsignal.uname)

                                dname_xml = ET.SubElement(dsignal_xml, 'dname')
                                dname_xml.text = dsignal.dname

                # ---------------------------------------
                # Build temporary subscription objects
                # to remember the subs of all plugins
                # including plugins that are not saved
                # excluding plugins we do not want the subs saved of
                # ---------------------------------------
                if dplugin.uname in sToSave:
                    subsOfPl = {}
                    subs = dplugin.get_subscribtions()
                    for sub in subs:
                        sourcePL = self.gui_data.get_dplugin_by_id(sub).uname
                        subsOfPl[sourcePL] = {}
                        for block in subs[sub]:
                            subsOfPl[sourcePL][block] = {}
                            dsubscription = subs[sub][block]
                            subsOfPl[sourcePL][block]['alias'] = dsubscription.alias

                            signals = []
                            for s in dsubscription.get_signals():
                                signals.append( str(s))

                            subsOfPl[sourcePL][block]['signals'] = signals

                    if len(subsOfPl) != 0:
                        subscriptionsToSave[dplugin.uname] = subsOfPl

            # ---------------------------------------
            # save subs to xml
            #
            # ---------------------------------------
            subs_xml = ET.SubElement(root,'Subscriptions')
            for dest in subscriptionsToSave:
                sub_xml = ET.SubElement(subs_xml,'Subscription')

                # Destination of data
                dest_xml = ET.SubElement(sub_xml,'Destination')
                dest_xml.text = dest

                for source in subscriptionsToSave[dest]:
                    # Source of Data
                    source_xml = ET.SubElement(sub_xml,'Source')
                    source_xml.set('uname',source)

                    for block in subscriptionsToSave[dest][source]:
                        block_xml = ET.SubElement(source_xml,'Block')
                        block_xml.set('name',block)

                        alias_xml = ET.SubElement(block_xml,'Alias')
                        alias_xml.text = subscriptionsToSave[dest][source][block]['alias']

                        signal_xml = ET.SubElement(block_xml,'Signals')
                        for sig in subscriptionsToSave[dest][source][block]['signals']:
                            if sig != CORE_TIME_SIGNAL:
                                sig_xml = ET.SubElement(signal_xml,'Signal')
                                sig_xml.text = sig


            # do transformation for readability and save xml tree to file
            self.indent(root)
            tree = ET.ElementTree(root)
            tree.write(path)

        except Exception as E:
            tb = traceback.format_exc()
            self.error_occured.emit("Error: Config Loader", "Not saveable: " + path, tb)

    def do_save_xml_config(self, path):
        """
        This function will save papis current state to a xml file provided by path.

        :param path: path to save xml to.
        :type path: basestring
        :return:
        """
        if path[-4:] != '.xml':
            path += '.xml'

        try:
            root = ET.Element(CONFIG_ROOT_ELEMENT_NAME)
            root.set('Date', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            root.set('PaPI_version', CORE_PAPI_VERSION)

            ##########################
            # Save gui configuration #
            ##########################
            gui_cfg = self.get_gui_config_function()
            gui_cfg_xml = ET.SubElement(root, 'guiConfig')

            for cfg_item in gui_cfg:
                item_xml = ET.SubElement(gui_cfg_xml,cfg_item)
                item = gui_cfg[cfg_item]
                for attr_name in item:
                    attr_xml = ET.SubElement(item_xml, attr_name)
                    values = item[attr_name]
                    for val in values:
                        value_xml = ET.SubElement(attr_xml, val)
                        value_xml.text = values[val]

            # ---------------------------------------
            # save information of plugins
            # for the next start
            # ---------------------------------------
            plugins = self.gui_data.get_all_plugins()
            for dplugin_id in plugins:
                dplugin = plugins[dplugin_id]

                if dplugin.type == PLUGIN_VIP_IDENTIFIER:
                    dplugin.startup_config = dplugin.plugin.pl_get_current_config()

                pl_xml = ET.SubElement(root, 'Plugin')
                pl_xml.set('uname', dplugin.uname)

                identifier_xml = ET.SubElement(pl_xml, 'Identifier')
                identifier_xml.text = dplugin.plugin_identifier

                # ---------------------------------------
                # Save all current config as startup config
                # for the next start
                # ---------------------------------------

                cfg_xml = ET.SubElement(pl_xml, 'StartConfig')
                for parameter in dplugin.startup_config:
                    para_xml = ET.SubElement(cfg_xml, 'Parameter')
                    para_xml.set('Name', parameter)
                    for detail in dplugin.startup_config[parameter]:
                        detail_xml = ET.SubElement(para_xml, detail)
                        detail_xml.text = dplugin.startup_config[parameter][detail]

                # ---------------------------------------
                # Save all current values for all
                # parameter
                # ---------------------------------------

                last_paras_xml = ET.SubElement(pl_xml, 'PreviousParameters')
                allparas = dplugin.get_parameters()
                for para_key in allparas:
                    para = allparas[para_key]
                    last_para_xml = ET.SubElement(last_paras_xml, 'Parameter')
                    last_para_xml.set('Name', para_key)
                    last_para_xml.text = str(para.value)

                # ---------------------------------------
                # Save all current values for all
                # signals of all dblocks
                # ---------------------------------------

                dblocks_xml = ET.SubElement(pl_xml, 'DBlocks')

                alldblock_names = dplugin.get_dblocks()

                for dblock_name in alldblock_names:
                    dblock = alldblock_names[dblock_name]
                    dblock_xml = ET.SubElement(dblocks_xml, 'DBlock')
                    dblock_xml.set('Name', dblock.name)

                    alldsignals = dblock.get_signals()

                    for dsignal in alldsignals:
                        dsignal_xml = ET.SubElement(dblock_xml, 'DSignal')
                        dsignal_xml.set('uname', dsignal.uname)

                        dname_xml = ET.SubElement(dsignal_xml, 'dname')
                        dname_xml.text = dsignal.dname

                # ---------------------------------------
                # Save all subscriptions for this plugin
                # ---------------------------------------

                subs_xml = ET.SubElement(pl_xml, 'Subscriptions')
                subs = dplugin.get_subscribtions()
                for sub in subs:
                    sub_xml = ET.SubElement(subs_xml, 'Subscription')
                    source_xml = ET.SubElement(sub_xml, 'data_source')
                    source_xml.text = self.gui_data.get_dplugin_by_id(sub).uname
                    for block in subs[sub]:
                        block_xml = ET.SubElement(sub_xml, 'block')
                        block_xml.set('Name', block)

                        dsubscription = subs[sub][block]

                        alias_xml = ET.SubElement(block_xml, 'alias')
                        alias_xml.text = dsubscription.alias

                        for s in dsubscription.get_signals():
                            signal_xml = ET.SubElement(block_xml, 'Signal')
                            signal_xml.text = str(s)

            self.indent(root)
            tree = ET.ElementTree(root)
            tree.write(path)

        except Exception as E:
            tb = traceback.format_exc()
            self.error_occured.emit("Error: Config Loader", "Not saveable: " + path, tb)

    def do_save_json_config_reloaded(self, path, plToSave=[], sToSave=[]):
        if path[-5:] != '.json':
            path += '.json'

        json_config = {}
        to_create = {}
        to_control = {}
        to_sub = {}
        plugins = self.gui_data.get_all_plugins()

        for dplugin_id in plugins:
            dplugin = plugins[dplugin_id]

            # check if this plugin should be saved to XML
            if dplugin.uname in plToSave:
                if dplugin.type == PLUGIN_VIP_IDENTIFIER:
                    dplugin.startup_config = dplugin.plugin.pl_get_current_config()

                to_create[dplugin.uname] = {}

                to_create[dplugin.uname]["identifier"] = {'value' : dplugin.plugin_identifier}
                plugin_config = {}
                for config in dplugin.startup_config:
                    for value in dplugin.startup_config[config]:
                        if value == 'value':
                            plugin_config[config] = {'value' : dplugin.startup_config[config][value]}

                to_create[dplugin.uname]["config"] = plugin_config


            if dplugin.uname in sToSave:
                subsOfPl = {}
                subs = dplugin.get_subscribtions()

                for sub in subs:
                    sourcePL = self.gui_data.get_dplugin_by_id(sub).uname

                    subsOfPl[sourcePL] = {}
                    for block in subs[sub]:

                        subsOfPl[sourcePL][block] = {}
                        dsubscription = subs[sub][block]
                        subsOfPl[sourcePL]['alias'] = dsubscription.alias
                        print(sourcePL)
                        print(block)
                        if dsubscription.alias is not None:
                            if sourcePL not in to_control:
                                to_control[sourcePL] = {}
                            to_control[sourcePL][block] = {'parameter' : dsubscription.alias}
                        else:

                            signals = []
                            for s in dsubscription.get_signals():
                                signals.append( str(s))

                            to_sub[dplugin.uname] = {}
                            to_sub[dplugin.uname]['signals'] = signals
                            to_sub[dplugin.uname]['block']   = block
                            to_sub[dplugin.uname]['plugin']  = sourcePL

        if len(to_create):
            json_config["ToCreate"] = to_create;
        if len(to_control):
            json_config["ToControl"] = to_control
        if len(to_sub):
            json_config["ToSub"] = to_sub

        papi_config = {"PaPIConfig" : json_config}


        try:
            with open(path, 'w') as outfile:
                json.dump(papi_config, outfile, indent='    ')

        except:
            pass



    def indent(self, elem, level=0):
        """
        Function which will apply a nice looking indentiation to xml structure before save. Better readability.
        copied from http://effbot.org/zone/element-lib.htm#prettyprint 06.10.2014 15:53

        :param elem:
        :param level:
        :return:
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def do_reset_papi(self):
        """
        APi call to reset PaPI.
        Reset in this case means to delete all plugins cleanly and keep PaPI running.
        Will free all unames.
        Is using the do_delete_plugin api call and the delete plugin mechanism

        :return: ERROR CODE
        """

        all_plugins = self.gui_data.get_all_plugins()
        if all_plugins is not None:
            for plugin_key in all_plugins:
                plugin = all_plugins[plugin_key]
                self.do_delete_plugin(plugin.id)

    def do_test_name_to_be_unique(self, name):
        """
        Will check if a given name would be a valid, unique name for a plugin.
        :param name: name to check

        :type name: basestring
        :return: True or False
        """
        reg = QtCore.QRegExp('\S[^_][^\W_]+')
        if reg.exactMatch(name):
            if self.gui_data.get_dplugin_by_uname(name) is None:
                return True
            else:
                return False
        else:
            return False

    def do_change_string_to_be_uname(self, name):
        """
        This method will take a string and convert him according to some rules to be an uname

        :param name: name to convert to unmae
        :type name: basestring
        :return: name converted to uname
        """
        uname = name

        # TODO: get more inteligence here!

        forbidden = ['_', ',', '.', '`', ' ']
        for c in forbidden:
            uname = uname.replace(c, 'X')
        return uname