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

from papi.data.DPlugin import DBlock
from papi.data.DSignal import DSignal

from papi.data.DParameter import DParameter
from papi.plugin.base_classes.iop_base import iop_base

import time
import math
import numpy


class Trigger(iop_base):
    def __init__(self):
        self.initialized = False

    def start_init(self, config=None):



        self.block1 = DBlock('Progress')
        signal = DSignal('percent')
        self.block1.add_signal(signal)

        self.block2 = DBlock('Trigger')
        signal = DSignal('trigger')
        self.block2.add_signal(signal)

        self.block3 = DBlock('ResetTrigger')
        signal = DSignal('reset')
        self.block3.add_signal(signal)

        blockList = [self.block1, self.block2, self.block3]
        self.send_new_block_list(blockList)

        self.para3 = DParameter('Choose', default=0, Regex='\d+')
        para_l = [self.para3]

        self.send_new_parameter_list(para_l)

        self.initialized = True

        return True

    def pause(self):
        pass

    def resume(self):
        pass

    def execute(self, Data=None, block_name = None):
        pass

    def set_parameter(self, name, value):
        if not self.initialized:
            return
        value = int(value)
        if name == self.para3.name:
            if value == 0:
                print(value)
                self.send_new_data('Progress', [0], {'percent': [20]})

            if value == 1:
                print(value)
                self.send_new_data('Trigger', [0], {'trigger': [0]})

            if value == 2:
                print(value)
                self.send_new_data('ResetTrigger', [0], {'reset': [0]})


    def get_plugin_configuration(self):
        config = {
        }
        return config

    def quit(self):
        print('Trigger: will quit')

    def plugin_meta_updated(self):
        pass
