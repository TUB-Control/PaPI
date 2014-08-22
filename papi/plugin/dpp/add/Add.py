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

__author__ = 'ruppins'


from papi.plugin.plugin_base import plugin_base
from papi.PapiEvent import PapiEvent
from papi.data.DOptionalData import DOptionalData
from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter

import time
import math
import numpy
import os

class Add(plugin_base):

    def start_init(self):
        self.t = 0
        print(['ADD: process id: ',os.getpid()] )
        self.approx_max = 300
        self.fac= 1
        self.amax = 20
        self.approx = self.approx_max*self.fac
        self.vec = numpy.zeros(self.amax*2)


        self.block1 = DBlock(None,1,10,'AddOut1')

        self.para1 = DParameter(None,'Count',1, [0, 1] ,1)

        self.send_new_block_list([self.block1])
        self.send_new_parameter_list([self.para1])


        return True

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self,Data):
        self.approx = round(self.approx_max*self.para1.value)
        self.vec[:] = 0
        self.vec[0:self.amax] = Data[0:self.amax]

        for i in range(self.amax):
            for k in range(self.approx):
                self.vec[i+self.amax] += Data[i + (k+1)*self.amax]

        #event = PapiEvent(self.__id__,0,'data_event','new_data',DOptionalData(DATA=self.vec))
        #self._Core_event_queue__.put(event)
        self.send_new_data(self.vec,'AddOut1')

    def set_parameter(self,parameter_list):
        for p in parameter_list:
            if p.name == self.para1.name:
                self.para1 = p

    def quit(self):
        print('Add: will quit')

    def get_type(self):
        return 'DPP'

    def get_output_sizes(self):
        return None
