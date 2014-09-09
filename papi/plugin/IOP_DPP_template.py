#!/usr/bin/python3
# -*- coding: latin-1 -*-

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
<Stefan Ruppin
"""

__author__ = 'control'

from papi.plugin.plugin_base import plugin_base
from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter


class IOP_DPP_template(plugin_base):

    def start_init(self):
        # do user init
        # define vars, connect to rtai .....

        # create a block object
        #   block1 = DBlock(None,1,10,'SinMit_f1')

        # send block list
        #   self.send_new_block_list([block1, block2, block3])

        # create a parameter object
        #   self.para = DParameter(None,'Frequenz Block SinMit_f3',0.1,[0,1],1)

        # build parameter list to send to Core
        #   para_list = [self.para]
        #   self.send_new_parameter_list(para_list)

        return True

    def pause(self):
        pass

    def resume(self):
        pass

    def execute(self):
        # implement execute and send new data
        #   self.send_new_data(data,'block_name')
        pass


    def set_parameter(self, parameter_list):
        for p in parameter_list:
            if p.name == self.para.name:
                # implement action for value change of parameter "para"
                pass
    def quit(self):
        pass

    def get_type(self):
        # return type: IOP or DPP
        return 'IOP'
