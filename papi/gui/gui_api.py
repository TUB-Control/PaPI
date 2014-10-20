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

Contributors
Stefan Ruppin
"""
__author__ = 'stefan'

from papi.PapiEvent import PapiEvent

import papi.event as Event

from papi.data.DOptionalData import DOptionalData
from papi.ConsoleLog import ConsoleLog
from papi.constants import GUI_PROCESS_CONSOLE_IDENTIFIER, GUI_PROCESS_CONSOLE_LOG_LEVEL, CONFIG_LOADER_SUBCRIBE_DELAY, \
    CONFIG_ROOT_ELEMENT_NAME, CORE_PAPI_VERSION

from pyqtgraph import QtCore

import papi.error_codes as ERROR

import datetime
import time

import xml.etree.cElementTree as ET

class Gui_api:
    def __init__(self, gui_data, core_queue, gui_id):
        self.gui_id = gui_id
        self.gui_data = gui_data
        self.core_queue = core_queue
        self.log = ConsoleLog(GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER)

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

    def do_delete_plugin(self, id):
        """
        Delete plugin with given id.
        :param id: Plugin id to delete
        :type id: int
        :return:
        """

        opt = DOptionalData()

        #event = PapiEvent(self.gui_id, id, 'instr_event', 'delete_plugin', opt)

        event = Event.instruction.StopPlugin(self.gui_id, id, None)

        self.core_queue.put(event)

    def do_delete_plugin_uname(self, uname):
        """
        Delete plugin with given uname.
        :param uname: Plugin uname to delete
        :type uname: basestring
        :return:
        """
        pl_id = self.do_get_plugin_id_from_uname(uname)

        if pl_id is not None:
            self.do_delete_plugin(pl_id)
        else:
            self.log.printText(1, " Do delete plugin with uname " + uname + ' failed')

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

    def do_subscribe(self, subscriber_id, source_id, block_name, signal_index=None, sub_alias = None):
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
        opt             = DOptionalData()
        opt.source_ID   = source_id
        opt.block_name  = block_name
        opt.signals     = signal_index
        opt.subscription_alias =  sub_alias
        # send event with subscriber id as the origin to CORE
        event = PapiEvent(subscriber_id, 0, 'instr_event', 'subscribe', opt)
        self.core_queue.put(event)

    def do_subscribe_uname(self,subscriber_uname,source_uname,block_name, signal_index=None, sub_alias = None):
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
        subscriber_id = self.do_get_plugin_id_from_uname(subscriber_uname)
        if subscriber_id is None:
            # plugin with uname does not exist
            self.log.printText(1, 'do_subscribe, sub uname worng')
            return -1

        source_id = self.do_get_plugin_id_from_uname(source_uname)
        if source_id is None:
            # plugin with uname does not exist
            self.log.printText(1, 'do_subscribe, target uname wrong')
            return -1

        # call do_subscribe with ids to subscribe
        self.do_subscribe(subscriber_id, source_id, block_name, signal_index, sub_alias)

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
        opt             = DOptionalData()
        opt.source_ID   = source_id
        opt.block_name  = block_name
        opt.signals     = signal_index
        # sent event to Core with origin subscriber_id
        event = PapiEvent(subscriber_id, 0, 'instr_event', 'unsubscribe', opt)
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

    def do_set_parameter(self, plugin_id, parameter_name, value):
        """
        Something like a callback function for gui triggered events.
        User wants to change a parameter of a plugin
        :param plugin_id: id of plugin which owns the parameter
        :type plugin_id: int
        :param parameter_name: name of parameter to change
        :type parameter_name: basestring
        :param value: new parameter value to set
        :type value:
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
                        e = PapiEvent(self.gui_id,dplug.id,'instr_event','set_parameter',opt)
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
        id = self.do_get_plugin_id_from_uname(plugin_uname)
        if id is not None:
            self.do_set_parameter(id, parameter_name, value)

    def do_pause_plugin_by_id(self, plugin_id):
        """
        Something like a callback function for gui triggered events.
        User wants to pause a plugin, so this method will send an event to core.
        :param plugin_id: id of plugin to pause
        :type plugin_id: int
        """

        if self.gui_data.get_dplugin_by_id(plugin_id) is not None:
            opt = DOptionalData()
            event = PapiEvent(self.gui_id, plugin_id, 'instr_event', 'pause_plugin', opt)
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
        # # get plugin from DGui with given uname
        # # purpose: get its id
        # dplug = self.gui_data.get_dplugin_by_uname(plugin_uname)
        #  # check for existance
        # if dplug is not None:
        #     # it does exist, so get its id
        #     self.do_pause_plugin_by_id(dplug.id)
        # else:
        #     # plugin with uname does not exist
        #     self.log.printText(1, 'do_pause, plugin uname worng')
        #     return -1

        #TODO: Check new code
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
            event = PapiEvent(self.gui_id, plugin_id, 'instr_event', 'resume_plugin', opt)
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
        # # get plugin from DGui with given uname
        # # purpose: get its id
        # dplug = self.gui_data.get_dplugin_by_uname(plugin_uname)
        #  # check for existance
        # if dplug is not None:
        #     # it does exist, so get its id
        #     self.do_resume_plugin_by_id(dplug.id)
        # else:
        #     # plugin with uname does not exist
        #     self.log.printText(1, 'do_resume, plugin uname worng')
        #     return -1

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
        opt = DOptionalData()
        opt.reason = 'User clicked close Button'
        event = PapiEvent(self.gui_id, 0, 'instr_event','close_program',opt)
        self.core_queue.put(event)

    def do_load_xml(self, path):
        tree = ET.parse(path)

        root = tree.getroot()

        plugins_to_start = []
        subs_to_make = []
        parameters_to_change = []

        for plugin_xml in root:
            pl_uname = plugin_xml.attrib['uname']
            identifier = plugin_xml.find('Identifier').text
            config_xml = plugin_xml.find('StartConfig')
            config_hash = {}
            for parameter_xml in config_xml.findall('Parameter'):
                para_name = parameter_xml.attrib['Name']
                config_hash[para_name] = {}
                for detail_xml in parameter_xml:
                    detail_name = detail_xml.tag
                    config_hash[para_name][detail_name]= detail_xml.text

            plugins_to_start.append([identifier, pl_uname, config_hash])

            subs_xml = plugin_xml.find('Subscriptions')
            for sub_xml in subs_xml.findall('Subscription'):
                data_source = sub_xml.find('data_source').text
                for block_xml in sub_xml.findall('block'):
                    block_name = block_xml.attrib['Name']
                    signals = []
                    for sig_xml in block_xml.findall('Signal'):
                        signals.append(int(sig_xml.text))
                    alias_xml = block_xml.find('alias')
                    alias = alias_xml.text
                    subs_to_make.append([pl_uname,data_source,block_name,signals, alias])


            prev_parameters_xml = plugin_xml.find('PreviousParameters')
            for prev_parameter_xml in prev_parameters_xml.findall('Parameter'):
                para_name = prev_parameter_xml.attrib['Name']
                para_value = prev_parameter_xml.text
                parameters_to_change.append([pl_uname, para_name, float(para_value)])

        for pl in plugins_to_start:
            self.do_create_plugin(pl[0], pl[1], pl[2])

        QtCore.QTimer.singleShot(CONFIG_LOADER_SUBCRIBE_DELAY,\
                                 lambda: self.config_loader_subs(plugins_to_start, subs_to_make, parameters_to_change) )

    def config_loader_subs(self, pl_to_start, subs_to_make, parameters_to_change ):
        for sub in subs_to_make:
            self.do_subscribe_uname(sub[0], sub[1], sub[2], sub[3], sub[4])

        for para in parameters_to_change:
            self.do_set_parameter(para[0], para[1], para[2])

    def do_save_xml_config(self, path):
        root = ET.Element(CONFIG_ROOT_ELEMENT_NAME)
        root.set('Date', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        root.set('PaPI_version',CORE_PAPI_VERSION)

        # get plugins #
        plugins = self.gui_data.get_all_plugins()
        for dplugin_id in plugins:
            dplugin = plugins[dplugin_id]
            pl_xml = ET.SubElement(root,'Plugin')
            pl_xml.set('uname',dplugin.uname)

            identifier_xml =ET.SubElement(pl_xml,'Identifier')
            identifier_xml.text = dplugin.plugin_identifier

            cfg_xml = ET.SubElement(pl_xml,'StartConfig')
            for parameter in dplugin.startup_config:
                para_xml = ET.SubElement(cfg_xml, 'Parameter')
                para_xml.set('Name',parameter)
                for detail in dplugin.startup_config[parameter]:
                    detail_xml = ET.SubElement(para_xml, detail)
                    detail_xml.text = dplugin.startup_config[parameter][detail]

            last_paras_xml = ET.SubElement(pl_xml, 'PreviousParameters')
            allparas = dplugin.get_parameters()
            for para_key in allparas:
                para = allparas[para_key]
                last_para_xml = ET.SubElement(last_paras_xml,'Parameter')
                last_para_xml.set('Name',para_key)
                last_para_xml.text = str(para.value)

            subs_xml = ET.SubElement(pl_xml, 'Subscriptions')
            subs = dplugin.get_subscribtions()
            for sub in subs:
                sub_xml = ET.SubElement(subs_xml, 'Subscription')
                source_xml = ET.SubElement(sub_xml, 'data_source')
                source_xml.text = self.gui_data.get_dplugin_by_id(sub).uname
                for block in subs[sub]:
                    block_xml = ET.SubElement(sub_xml, 'block')
                    block_xml.set('Name',block)

                    alias_xml = ET.SubElement(block_xml,'alias')
                    alias_xml.text = subs[sub][block].alias

                    for s in subs[sub][block].get_signals():
                        signal_xml = ET.SubElement(block_xml,'Signal')
                        signal_xml.text = str(s)

        self.indent(root)
        tree = ET.ElementTree(root)
        tree.write(path)

    def indent(self,elem, level=0):
    # copied from http://effbot.org/zone/element-lib.htm#prettyprint 06.10.2014 15:53
      i = "\n" + level*"  "
      if len(elem):
        if not elem.text or not elem.text.strip():
          elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
          elem.tail = i
        for elem in elem:
          self.indent(elem, level+1)
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