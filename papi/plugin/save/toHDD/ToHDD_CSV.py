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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
Stefan Ruppin
"""

from papi.plugin.base_classes.dpp_base import dpp_base
from papi.constants import CORE_TIME_SIGNAL


import csv

class ToHDD_CSV(dpp_base):

    def cb_initialize_plugin(self):

        default_config = self.get_startup_configuration()


        self.config = self.pl_get_current_config()

        self.pl_set_event_trigger_mode(True)

        self.known_blocks = {}

        print('toHDD started working')

        return True

    def cb_pause(self):
        for b in self.known_blocks.values():
            b['file'].close()
        print('toHDD pause')
        pass

    def cb_resume(self):
        for b in self.known_blocks.values():
            b['file'] = open(self.config['file']['value']+'.csv', 'a')
            b['csv'] =  csv.writer( b['file'], delimiter=self.config['delimiter']['value'],
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        print('toHDD resume')
        pass

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):
        t = Data[CORE_TIME_SIGNAL]

        if block_name not in self.known_blocks.keys():
            self.known_blocks[block_name] = {}
            self.known_blocks[block_name]['file'] = open(self.config['file']['value']+'_'+block_name+'.csv', 'w+')
            self.known_blocks[block_name]['csv'] =  csv.writer( self.known_blocks[block_name]['file'], delimiter=self.config['delimiter']['value'],
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        else:
            rows = []

            for i in range(len(t)):
                row = []
                row.append(t[i])
                for k in Data:
                    if k != CORE_TIME_SIGNAL:
                        vals = Data[k][i]
                        row.append(vals)
                rows.append(row)

            self.known_blocks[block_name]['csv'].writerows(rows)


    def cb_set_parameter(self, name, value):
       pass


    def cb_get_plugin_configuration(self):
        config = {
            "log-type": {
                'value': 1,
                'regex': '[0-9]+',
                 'advanced' : '1'
        }, "file": {
                'value': 'log',
                 'advanced' : '0'
        }, "delimiter": {
                'value': ' ',
                 'advanced' : '1'
        }}
        return config

    def cb_quit(self):
        for b in self.known_blocks.values():
            b['file'].close()

        print('toHDD: will quit')

    def cb_plugin_meta_updated(self):
        pass
