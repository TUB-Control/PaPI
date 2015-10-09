#!/usr/bin/python3
# -*- coding: latin-1 -*-

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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""



from papi.data.DObject import DObject


class DSignal(DObject):
    """
    DSignal is used for the internal description of a signal.

    """
    def __init__(self, uname, dname = None):
        """
        A signal is described by uname, a unique identifier in the context of DBlock.
        The display name dname is used as visual representation. If now dname is given, the uname is used.

        :param uname: Unique name in the context of this signals block
        :param dname: Display name
        :return:
        """
        super(DObject, self).__init__()
        self.uname = uname
        if dname is None:
            self.dname = uname
        else:
            self.dname = dname