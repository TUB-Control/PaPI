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


class toHDD(plugin_base):

    def start_init(self, config=None):

        default_config = self.get_startup_configuration()

        if config is None:
            config = default_config
        else:
            config = dict(list(default_config.items()) + list(config.items()))



        print('toHDD started working')

        return True

    def pause(self):
        print('toHDD pause')
        pass

    def resume(self):
        print('toHDD resume')
        pass

    def execute(self):
        pass

    def set_parameter(self, name, value):
       pass


    def get_startup_configuration(self):
        config = {
            "log-type": {
                'value': 1,
                'regex': '[0-9]+'
        }}
        return config

    def quit(self):
        print('toHDD: will quit')

    def get_type(self):
        return 'DPP'
