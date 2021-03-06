#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universitšt Berlin,
Fakultšt IV - Elektrotechnik und Informatik,
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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""



from papi.data.DObject import DObject


class DParameter(DObject):
    """
    DParameter is used for the internal description of a parameter which are provided by a plugin.
    Parameters are used to interact with plugin.
    """
    def __init__(self, name, default=0, Regex = None, OptionalObject=None):
        """
        A Parameter must be described by a name. It optionally possible to set a default value, a Regex object and an OptionalObject.

        :param name: Parameter name
        :param default: Default value
        :param Regex: Used to limit user input
        :param OptionalObject: Can be used by plugin developer to store other internal information
        :return:
        """
        super(DParameter, self).__init__()

        self.default = default
        self.value = default
        self.name = name
        self.plugin_id = None
        self.plugin_identifier = None
        self.regex = Regex
        self.OptionalObject = OptionalObject
        self.callback_function_handler = None

    def connect(self, function_handler):
        # Not allowed to be copied or to be send by queue
        if hasattr(function_handler, '__call__'):
            self.callback_function_handler = function_handler


    def update_meta(self, parameter):
        self.value = parameter.value

        if self.id != parameter.id:
            raise ValueError('DParameter ID: ' +self.id + ' != ' + parameter.id)
