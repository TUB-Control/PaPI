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

Contributors
Sven Knuth
"""

__author__ = 'knuths'

from papi.data.dcore.DPlugin import DPlugin


class DBuffer():
    def __init__(self, bid, writer=None):
        self.id = bid
        self.readers = {}
        self.writer = DPlugin

    def add_reader(self, reader):
        '''
        This function is used to add a plugin as reader for this buffer

        :param reader:DPlugin
        :return:
        '''
        assert(isinstance(reader), DPlugin)
        self.readers[reader.id] = reader

    def del_reader(self, plid):
        del_plugin = self.readers[plid]
        del self.readers[plid]
        return del_plugin