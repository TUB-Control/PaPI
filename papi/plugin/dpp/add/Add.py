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

        self.vec = numpy.zeros((2, self.amax))


        self.block1 = DBlock(None,1,10,'AddOut1',['t','Sum'])

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
#        self.vec[1] = 0
#        self.vec[0] = Data[0]

#        vec = numpy.zeros( (1, 2) )

        #for i in range(self.amax):
            #for k in range(1,self.approx):
               # self.vec[i+self.amax] += Data[i + (k+1)*self.amax]
                #self.vec[1, i] = Data[k, i]

        # Get Time Vector

#        vec[0, :] = Data['t']

        # n_rows = Data.shape[0]
        # n_cols = Data.shape[1]

        first_element = True

        for signal_name in Data:
            if signal_name is not 't':
                signal = Data[signal_name]

                if first_element is True:
                    first_element = False

                    result = signal
                else:
                    result = numpy.add(result, signal)


        vec = numpy.zeros((2, len(result)))

        vec[0,:] = Data['t']
        vec[1,:] = result

        self.send_new_data(vec,'AddOut1')



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
