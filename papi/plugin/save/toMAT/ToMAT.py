#!/usr/bin/python3
#-*- coding: utf-8 -*-

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
Sven Knuth
"""

from papi.plugin.base_classes.dpp_base import dpp_base
from papi.constants import CORE_TIME_SIGNAL

from papi.data.DParameter import DParameter
import papi.constants as pc

import scipy.io as sio
import numpy as np
import time

current_milli_time = lambda: int(round(time.time() * 1000))

class ToMAT(dpp_base):

    def __init__(self):
        super(ToMAT, self).__init__()
        self.parameters = {}

    def start_init(self, config=None):

        self.config = config

        self.set_event_trigger_mode(True)

        self.name_mat_file = self.config['file']['value']

        # Open/Create mat file


        self.data_to_save = {}

        self.parameters['start_saving'] = DParameter('start_saving',default='0', Regex=pc.REGEX_BOOL_BIN)
        self.parameters['save_data_for_x_ms'] = DParameter('save_data_for_x_ms',default='0', Regex=pc.REGEX_SINGLE_INT)
        self.parameters['file'] = DParameter('file',default='')

        self.send_new_parameter_list(list(self.parameters.values()))

        self.time_slot = 0
        self.time_start = 0;

        self.saving = False

        print('toMAT started working')

        return True

    def pause(self):
        print('toMAT pause')
        pass

    def resume(self):
        print('toMAT resume')
        pass

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):

        if self.saving:
            t = Data[CORE_TIME_SIGNAL]


            to_save = {plugin_uname : {block_name : Data }}

            if plugin_uname not in self.data_to_save:
                self.data_to_save[plugin_uname] = {}

            if block_name not in self.data_to_save[plugin_uname]:
                self.data_to_save[plugin_uname][block_name] = {}

            for d in Data:
                if d not in self.data_to_save[plugin_uname][block_name]:
                    self.data_to_save[plugin_uname][block_name][d] = []

                self.data_to_save[plugin_uname][block_name][d].extend(Data[d])

            if current_milli_time() - self.time_start >= self.time_slot:
                self.saving = False
                self.save_data_as_mat_file()

    def set_parameter(self, name, value):
        if name == 'start_saving':
            if value == '0':
                if self.saving:
                    self.save_data_as_mat_file()

                self.saving = False

            if value == '1':
                self.time_start = current_milli_time()
                self.saving = True

        if name == 'file':
            self.name_mat_file = value

        if name == 'save_data_for_x_ms':
            if not self.saving:
                self.time_slot = int(value)

    def save_data_as_mat_file(self):

        print("ToMAT: Saved data in " + self.name_mat_file)
        sio.savemat(self.name_mat_file, {'PaPI' : self.data_to_save})

        self.data_to_save = {}

    def get_plugin_configuration(self):
        config = {
             "file": {
                'value': 'log.mat',
                 'type' : 'file',
                 'advanced' : '0'
        }}
        return config

    def quit(self):

        # quit during save process
        # save already known data
        if self.saving:
            self.save_data_as_mat_file()

        print('toMAT: will quit')

    def plugin_meta_updated(self):
        pass
