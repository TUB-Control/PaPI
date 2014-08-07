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

__author__ = 'control'

class PapiEvent(object):
    count = 0

    def __init__(self,orID,destID,type_,op,optParameter):
        """
        Function used to create a new Event ready to send.

        :param orID: plugin id of sender
        :type orID: int
        :param destID: plugin id of destination
        :type destID: int
        :param type_: event type, see list
        :type type_: string
        """

        self.__originID__ = orID
        self.__destID__ = destID
        self.__eventtype__ = type_
        self.__operation__ = op
        self.__optional_parameter__ = optParameter
        PapiEvent.count += 1

    def get_originID(self):
        return self.__originID__

    def get_destinatioID(self):
        return self.__destID__

    def get_eventtype(self):
        return self.__eventtype__

    def get_event_operation(self):
        return self.__operation__

    def get_optional_parameter(self):
        return self.__optional_parameter__