#!/usr/bin/python3
#-*- coding: latin-1 -*-

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
Stefan Ruppin
"""


import unittest
from papi.core import Core
from papi.PapiEvent import PapiEvent


class TestCore(unittest.TestCase):

    def setUp(self):
        self.core = Core()


    def test_process_event_alive(self):
        event = PapiEvent(1,2,'status_event','alive','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'alive'

    def test_process_event_check_alive(self):
        event = PapiEvent(1,2,'status_event','check_alive_status','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'check_alive_status'

    def test_process_event_start_successfull(self):
        event = PapiEvent(1,2,'status_event','start_successfull','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'start_successfull'

    def test_process_event_join_request(self):
        event = PapiEvent(1,2,'status_event','join_request','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'join_request'

    def test_process_event_start_failed(self):
        event = PapiEvent(1,2,'status_event','start_failed','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'start_failed'

    def test_process_event_new_data(self):
        event = PapiEvent(1,2,'data_event','new_data','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'new_data'

    def test_process_event_get_output_size(self):
        event = PapiEvent(1,2,'data_event','get_output_size','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'get_output_size'

    def test_process_event_response_output_size(self):
        event = PapiEvent(1,2,'data_event','response_output_size','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'response_output_size'

    def test_process_event_create_plugin(self):
        event = PapiEvent(1,2,'instr_event','create_plugin','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'create_plugin'

    def test_process_event_stop_plugin(self):
        event = PapiEvent(1,2,'instr_event','stop_plugin','')
        self.core.__process_event__(event)
        assert self.core.__debug_var__ == 'stop_plugin'









if __name__ == "__main__":
    unittest.main();

