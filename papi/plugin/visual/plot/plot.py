#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.visual_base import visual_base
from papi.PapiEvent import PapiEvent
from papi.data.DParameter import DParameter
import time
import numpy
__author__ = 'knuths'


class Plot(visual_base):

    def start_init(self, config=None):
        super(Plot,self).start_init(config)


        print("Plot: start_init")
        self.max_counter = 0
        self.counter = 0


        self.para1 = DParameter(None,'Singale',1,[1,2],1)
        self.para1.id = 1
        para_l = [self.para1]

        self.send_new_parameter_list(para_l)


        pass


    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self,Data):
        #print(Data)

        l = len(Data)

        t = Data[0]

        #self.sinus_curve = 22
        #y = Data[self.sinus_curve*l/23:(self.sinus_curve + 1)*l/23]
        y = Data[self.para1.value]

        if self.counter > self.max_counter:
            self.add_data(t, y)
            self.update()
            self.counter = 0

        self.counter += 1

    def set_parameter(self, parameter_list):
        for p in parameter_list:
            if p.name == self.para1.name:
                self.para1 = p


    def get_type(self):
        return "ViP"

    def get_output_sizes(self):
        return [0,0]


    def quit(self):
        print('Plot: will quit')