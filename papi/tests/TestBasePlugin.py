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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""



import unittest

from papi.plugin.base_classes.base_plugin import base_plugin
from papi.data.DPlugin import DBlock, DEvent
from papi.data.DParameter import DParameter
import papi.exceptions as pe

class TestBasePlugin(unittest.TestCase):

    def setUp(self):
        self.basePlugin = base_plugin()

    def tearDown(self):
        pass

    def test_inheritedFunctions(self):

        self.assertRaises(NotImplementedError, self.basePlugin.get_type)
        self.assertRaises(NotImplementedError, self.basePlugin.cb_execute, None, None, None)
        self.assertRaises(NotImplementedError, self.basePlugin._get_configuration_base)
        self.assertRaises(NotImplementedError, self.basePlugin.get_startup_configuration)
        self.assertRaises(NotImplementedError, self.basePlugin.get_plugin_configuration)

        self.assertRaises(NotImplementedError, self.basePlugin.cb_pause)
        self.assertRaises(NotImplementedError, self.basePlugin.resume)
        self.assertRaises(NotImplementedError, self.basePlugin.quit)
        self.assertRaises(NotImplementedError, self.basePlugin.set_parameter, None, None)
        self.assertRaises(NotImplementedError, self.basePlugin._set_parameter_internal, None, None)

    def test_parameterChanges(self):

        self.assertRaises(pe.WrongType, self.basePlugin.pl_emit_event, None, None)
        self.assertRaises(AttributeError, self.basePlugin.pl_send_parameter_change, None, "DBlock")
        self.assertRaises(AttributeError, self.basePlugin.pl_emit_event, None, "DEvent")
        self.assertRaises(AttributeError, self.basePlugin.pl_send_parameter_change, None, DBlock("Block"))
        self.assertRaises(AttributeError, self.basePlugin.pl_emit_event, None, DEvent("Event"))

    # def test_createNewBlock(self):
    #     self.assertRaises(pe.Wrong_type, self.basePlugin.create_new_block, None, None, None, None)
    #     self.assertRaises(pe.Wrong_type, self.basePlugin.create_new_block, 'Name', None, None, None)
    #     self.assertRaises(pe.Wrong_type, self.basePlugin.create_new_block, 'Name', [1,2], None, None)
    #     #self.assertRaises(pe.Wrong_type, self.basePlugin.create_new_block, 'Name', None, None, None)
    #
    #     self.assertIsInstance(
    #         self.basePlugin.create_new_block('Name',['s1','s2'],[1,1],5)
    #     )

    def test_pl_send_new_event_list(self):

        self.assertRaises(pe.WrongType, self.basePlugin.pl_send_new_event_list, None)
        self.assertRaises(pe.WrongLength, self.basePlugin.pl_send_new_event_list, [])

        events = [
            DEvent('1'), DEvent('2'), DEvent('3')
        ]
        self.assertRaises(AttributeError, self.basePlugin.pl_send_new_event_list, events)

    def test_pl_send_new_block_list(self):
        self.assertRaises(pe.WrongType, self.basePlugin.pl_send_new_block_list, None)
        self.assertRaises(pe.WrongLength, self.basePlugin.pl_send_new_block_list, [])

        blocks = [
            DBlock('1'), 1, DBlock('3')
        ]
        self.assertRaises(pe.WrongType, self.basePlugin.pl_send_new_block_list, blocks)

        blocks = [
            DBlock('1'), DBlock('2'), DBlock('3')
        ]
        self.assertRaises(AttributeError, self.basePlugin.pl_send_new_block_list, blocks)

    def test_pl_send_new_parameter_list(self):
        self.assertRaises(pe.WrongType, self.basePlugin.pl_send_new_parameter_list, None)
        self.assertRaises(pe.WrongLength, self.basePlugin.pl_send_new_parameter_list, [])

        parameters = [
            DParameter('1'), DParameter('2'), 3
        ]
        self.assertRaises(pe.WrongType, self.basePlugin.pl_send_new_parameter_list, parameters)

        parameters = [
            DParameter('1'), DParameter('2'), DParameter('3')
        ]
        self.assertRaises(AttributeError, self.basePlugin.pl_send_new_parameter_list, parameters)

    def test_delete_block(self):
        self.assertRaises(pe.WrongType, self.basePlugin.pl_send_delete_block, None)
        self.assertRaises(AttributeError, self.basePlugin.pl_send_delete_block, 'DBlock')
        self.assertRaises(AttributeError, self.basePlugin.pl_send_delete_block, DBlock('DBlock'))

    def pl_send_delete_parameter(self):
        self.assertRaises(pe.WrongType, self.basePlugin.pl_send_delete_parameter, None)
        self.assertRaises(AttributeError, self.basePlugin.pl_send_delete_parameter, 'DParameter')
        self.assertRaises(AttributeError, self.basePlugin.pl_send_delete_parameter, DParameter('DParameter'))

    def test_controlFunctions(self):
        pass