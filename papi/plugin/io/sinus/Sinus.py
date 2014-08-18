#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.plugin_base import plugin_base
from papi.PapiEvent import PapiEvent
from papi.data.DOptionalData import DOptionalData
from papi.data.DPlugin import DBlock

from copy import deepcopy

import time
import math
import numpy


__author__ = 'knuths'


class Sinus(plugin_base):

    def start_init(self):
        self.t = 0
        self.amax = 100


        block1 = DBlock(None,1,10,'SinMit_f1')
        opt = DOptionalData()
        opt.block_list = [block1]
        event = PapiEvent(self.__id__,0,'data_event','new_block',opt)
        self._Core_event_queue__.put(event)

        print("Sinus  ", opt.block_list[0].name)



        return True

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self):
        vec = numpy.zeros(self.amax*2)
        for i in range(self.amax):
                vec[i] = self.t
                vec[i+self.amax] = math.sin(2*math.pi*0.01*self.t)
                self.t += 0.1


        self.send_new_data(vec,'SinMit_f1')
        time.sleep(0.02)

    def set_parameter(self):
        pass

    def quit(self):
        print('Sinus: will quit')

    def get_type(self):
        return 'IOP'

    def get_output_sizes(self):
        return [2,50]
