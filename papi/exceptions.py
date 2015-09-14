#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany
 
This file is part of PaPI.
 
PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.
 
Contributors:
Stefan Ruppin
Sven Knuth
"""




class WrongType(Exception):

    def __init__(self, parameters, expected_type=None):
        self.parameter = parameters
        self.type = None
        self.types = None
        if isinstance(expected_type, list):
            self.types = expected_type
        else:
            self.type = expected_type
    def __str__(self):
        if self.type is not None:
            return 'Wrong type for argument ['+ self.parameter + '], expected type: ' + str(self.type.__name__)
        elif self.types is not None:
            types = []
            for t in self.types:
                types.append(t.__name__)
            return 'Wrong type for argument ['+ self.parameter + '], expected type: ' + str(types)
        else:
            return 'Wrong type for argument '+ self.parameter


class WrongLength(Exception):

    def __init__(self, parameter, isLen, shLen):
        self.parameter = parameter
        self.isLen = isLen
        self.shLen = shLen

    def __str__(self):
        return "Wrong length for " + self.parameter +" got " + str(self.isLen)+", expected " + str(self.shLen)

