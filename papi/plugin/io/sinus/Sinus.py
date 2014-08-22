#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.plugin_base import plugin_base
from papi.PapiEvent import PapiEvent
from papi.data.DOptionalData import DOptionalData
from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter

from copy import deepcopy

import time
import math
import numpy


__author__ = 'knuths'


class Sinus(plugin_base):

    def start_init(self):
        self.t = 0
        self.amax = 100
        self.f =0.1

        block1 = DBlock(None,1,10,'SinMit_f1')
        block2 = DBlock(None,1,10,'SinMit_f2')
        block3 = DBlock(None,1,10,'SinMit_f3')

        self.send_new_block_list([block1, block2, block3])


        para3 = DParameter(None,'Frequenz Block SinMit_f3',0.001,[0,1],1)
        para3.id = 1
        para_l = [para3]

        self.send_new_parameter_list(para_l)




        return True

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self):
        vec = numpy.zeros(self.amax*2)
        vec2 = numpy.zeros(self.amax*2)
        vec3 = numpy.zeros(self.amax*2)
        for i in range(self.amax):
                vec[i] = self.t
                vec[i+self.amax] = math.sin(2*math.pi*0.01*self.t)
                vec2[i] = self.t
                vec2[i+self.amax] = math.sin(2*math.pi*0.15*self.t)
                vec3[i] = self.t
                vec3[i+self.amax] = math.sin(2*math.pi*self.f*self.t)
                self.t += 0.1


        self.send_new_data(vec,'SinMit_f1')
        self.send_new_data(vec2,'SinMit_f2')
        self.send_new_data(vec3,'SinMit_f3')
        time.sleep(0.02)

    def set_parameter(self):
        pass

    def quit(self):
        print('Sinus: will quit')

    def get_type(self):
        return 'IOP'

    def get_output_sizes(self):
        return [2,50]
