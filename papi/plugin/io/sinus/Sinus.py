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


class Sinus(iop_base):

    def start_init(self, config=None):
        self.t = 0
        self.amax = int(config['amax']['value'])
        self.f = float(config['f']['value'])


        self.block1 = DBlock('SinMit_f1')
        signal = DSignal('f1_1')
        signal.dname = 'f1_f1DNAME'
        self.block1.add_signal(signal)

        self.block2 = DBlock('SinMit_f2')
        signal = DSignal('f2_1')
        self.block2.add_signal(signal)

        self.block3 = DBlock('SinMit_f3')
        signal = DSignal('f3_1')
        self.block3.add_signal(signal)
        signal = DSignal('f3_2')
        self.block3.add_signal(signal)
        signal = DSignal('f3_scalar')
        self.block3.add_signal(signal)


        #self.block4 = self.create_new_block('Sin4', ['t','f3_1','f3_2', 'Scalar'], [ 'numpy_vec', 'numpy_vec', 'numpy_vec', 'int'], 100 )

        blockList = [self.block1, self.block2, self.block3]
        self.send_new_block_list(blockList)

        self.para3 = DParameter('Frequenz Block SinMit_f3', default= 0.3, Regex='[0-9]+.[0-9]+')
        para_l = [self.para3]

        self.send_new_parameter_list(para_l)

        print('Sinus started working')

        return True

    def pause(self):
        print('Sinus pause')
        pass

    def resume(self):
        print('Sinus resume')
        pass

    def execute(self, Data=None, block_name = None, plugin_uname = None):
        vec = numpy.zeros( (2,self.amax))
        vec2 = numpy.zeros((2,self.amax))
        vec3 = numpy.zeros((3,self.amax))
        for i in range(self.amax):
            vec[0, i] = self.t
            vec[1, i] = math.sin(2*math.pi*0.8*self.t)
            vec2[0, i] = self.t
            vec2[1, i] = math.sin(2*math.pi*0.5*self.t)
            vec3[0, i] = self.t
            vec3[1, i] = math.sin(2*math.pi*self.para3.value*self.t)
            vec3[2, i] = math.sin(2*math.pi*0.1*self.t)
            self.t += 0.005

        self.send_new_data('SinMit_f1' , vec[0] , {'f1_1': vec[1] } )
        self.send_new_data('SinMit_f2', vec2[0], {'f2_1': vec2[1]} )
        self.send_new_data('SinMit_f3', vec3[0], {'f3_1': vec3[1], 'f3_2': vec3[2], 'f3_scalar': [10,10,10] } )

        time.sleep(self.amax*0.005)

    def set_parameter(self, name, value):
        if name == self.para3.name:
            self.para3.value = float(value)


    def get_plugin_configuration(self):
        config = {
            "amax": {
                'value': 3,
                'regex': '[0-9]+'
        }, 'f': {
                'value': "1",
                'regex': '\d+.{0,1}\d*'
        }}
        return config

    def quit(self):
        print('Sinus: will quit')

    def plugin_meta_updated(self):
        pass
