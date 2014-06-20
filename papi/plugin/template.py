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

__author__ = 'Knuth'

from uuid import uuid4


class Template:
    description = "Used as template for plugins"
    author = "Knuth"

    name = "PluginTemplate"
    uuid = 0;

    def __init__(self,name):
        self.uuid = uuid4()
        self.name = name

    def create(foo, bar=True):
        """
        Function used to create a plot.

        :param foo: used to foo
        :type foo: String
        :param bar: used to bar
        :type bar: bool
        :rtype bool:
        """

        print("initialize PaPI - Plugin based Process Interaction")
        return True

    def destroy(foo, bar=True):
        """
        Function used to delete this plot

        :param foo: used to foo
        :type foo: String
        :param bar: used to bar
        :type bar: bool
        :rtype bool:
        """

        print("initialize PaPI - Plugin based Process Interaction")
        return True