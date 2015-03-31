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

__author__ = 'stefan'

from papi.event.instruction.InstructionBase import InstructionBase

class SubscribeByUname(InstructionBase):
    def __init__(self, oID, destID, subscriber_uname, source_uname, block_name, signals=None, sub_alias=None):
        super().__init__(oID, destID, 'subscribe_by_uname', None)
        self.source_uname = source_uname
        self.subscriber_uname = subscriber_uname
        self.block_name = block_name
        self.signals = signals
        self.sub_alias = sub_alias
