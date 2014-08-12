#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.visual_base import visual_base
from papi.PapiEvent import PapiEvent
import time
import numpy
__author__ = 'knuths'


class Plot(visual_base):

    def start_init(self):
        print("start_init")
        self.max_counter = 0
        self.counter = 0

        pass


    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self,Data):
        #print(Data)

        l = len(Data)

        t = Data[0:l/2]

        #self.sinus_curve = 22
        #y = Data[self.sinus_curve*l/23:(self.sinus_curve + 1)*l/23]
        y = Data[l/2:l]

        if self.counter > self.max_counter:
            self.add_data(t, y)
            self.update()
            self.counter = 0

        self.counter += 1

    def set_parameter(self):
        pass

    def get_type(self):
        return "ViP"

    def get_output_sizes(self):
        return [0,0]


    def quit(self):
        print('Plot: will quit')