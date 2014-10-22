#!/usr/bin/python3
#-*- coding: utf-8 -*-

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

from papi.plugin.plugin_base import plugin_base
from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter


import time
import math
import numpy
import csv

class ToHDD(plugin_base):

    def start_init(self, config=None):

        default_config = self.get_startup_configuration()

        if config is None:
            self.config = default_config
        else:
            self.config = dict(list(default_config.items()) + list(config.items()))

        self.set_event_trigger_mode(True)

        self.file = open(self.config['file']['value']+'.csv', 'w+')

        self.csvw = csv.writer(self.file, delimiter=self.config['delimiter']['value'],
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)


        print('toHDD started working')

        return True

    def pause(self):
        self.file.close()
        print('toHDD pause')
        pass

    def resume(self):
        self.file = open(self.config['file']['value']+'.csv', 'a')
        print('toHDD resume')
        pass

    def execute(self, Data=None, block_name = None):
        t = Data['t']



        rows = []

        #self.csvw.writerows([[1,2], [3,4]])

        for i in range(len(t)):
            row = []
            row.append(t[i])
            for k in Data:
                if k != 't':
                    vals = Data[k][i]
                    row.append(vals)
            rows.append(row)

        self.csvw.writerows(rows)


    def set_parameter(self, name, value):
       pass


    def get_startup_configuration(self):
        config = {
            "log-type": {
                'value': 1,
                'regex': '[0-9]+'
        }, "file": {
                'value': 'log1',
        }, "delimiter": {
                'value': ' ',
        }}
        return config

    def quit(self):
        self.file.close()
        print('toHDD: will quit')

    def get_type(self):
        return 'DPP'
