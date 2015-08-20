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

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""

from papi.data import DParameter

__author__ = 'knuths'

from papi.data.DObject import DObject
import copy


class DBlock(DObject):
    """
    DBlock is used for the internal description of a block.
    Contains a bunch of signals of a the same data source.
    """
    def __init__(self, name):
        """
        A block is described by name, which has to be unique within the context of the plugin owning this block.

        :param name: name of the block
        :return:
        """
        super(DObject, self).__init__()

        self.subscribers = {}
        self.dplugin_id = None
        self.name = name
        self.signals = []

    def add_subscribers(self, dplugin):
        """
        Add dplugin as subscriber for this dblock.

        :param dplugin:
        :return:
        :rtype boolean:
        """
        if dplugin.id not in self.subscribers:
            self.subscribers[dplugin.id] = dplugin.id
            return True
        else:
            return False

    def rm_subscriber(self, dplugin):
        """
        Remove dplugin as subscriber of this dblock.

        :param dplugin:
        :return:
        :rtype boolean:
        """
        if dplugin.id in self.subscribers:
            del self.subscribers[dplugin.id]
            return True
        else:
            return False

    def add_signal(self, signal):
        """
        Add Signal for this DBlock

        :param signal:
        :return:
        """
        if signal not in self.signals:
            self.signals.append(signal)
            return True
        return False

    def rm_signal(self, signal):
        """
        Remove Signal for this DBlock

        :param signal:
        :return:
        """
        if signal in self.signals:
            signal.uname = signal.uname + "_deleted"
            signal.dname = signal.dname + "_deleted"
            signal.remove()
            self.signals.remove(signal)

            return True
        return False

    def get_subscribers(self):
        """
        Returns all subscribers of this plugin. Returns a copy that means
        changes have no effect on the PaPI data structure.

        :return:
        :rtype []:
        """
        return copy.deepcopy(self.subscribers)

    def get_signal_by_uname(self, uname):
        """
        Returns a signal object by a signal's uname.

        :param uname:
        :return DSignal:
        """

        for signal in self.signals:
            if signal.uname == uname:
                return signal

        return None

    def get_signals(self):
        """
        Returns a copy of the internal signal names

        :return:
        """
        return copy.deepcopy(self.signals)


class DEvent(DBlock):
    pass

class DPlugin(DObject):
    """
    DPlugin is used for the internal description of a plugin.

    """
    def __init__(self):
        """
        Used to create the plugin data object.

        :return:
        """
        super(DPlugin, self).__init__()
        self.process = None
        self.pid = None
        self.queue = None
        self.plugin = None
        self.plugin_identifier = None
        self.startup_config = None
        self.__subscriptions = {}
        self.state = None
        self.alive_state = None
        self.paused = False
        self.own_process = None
        self.uname = None
        #self.display_name = None
        self.__parameters = {}
        self.__blocks = {}
        self.type = None
        self.alive_count = 0
        self.path = None

    def subscribe_signals(self, dblock, signals):
        """
        This function is used to subscribe a bunch of signals.

        :param dblock:
        :param signals:
        :return:
        :rtype DSubscription:
        """

        if dblock.dplugin_id in self.__subscriptions:
            if dblock.name in self.__subscriptions[dblock.dplugin_id]:
                subscription = self.__subscriptions[dblock.dplugin_id][dblock.name]
                for signal in signals:
                    subscription.add_signal(signal)
                return subscription
            else:
                return None
        else:
            return None

    def unsubscribe_signals(self, dblock, signals):
        """
        This function is used to unsubscribe a bunch of signals.

        :param dblock:
        :param signals:
        :return:
        :rtype DSubscription:
        """

        if dblock.dplugin_id in self.__subscriptions:
            if dblock.name in self.__subscriptions[dblock.dplugin_id]:
                subscription = self.__subscriptions[dblock.dplugin_id][dblock.name]
                for signal in signals:
                    subscription.rm_signal(signal)

                return subscription
            else:
                return None
        else:
            return None

    def subscribe(self, dblock):
        """
        This plugin subscribes a 'dblock' by remembering the dblog id.

        :param dblock: DBlock which should be subscribed
        :return:
        :rtype boolean:
        """

        if dblock.dplugin_id not in self.__subscriptions:
            self.__subscriptions[dblock.dplugin_id] = {}
            self.__subscriptions[dblock.dplugin_id][dblock.name] = DSubscription(dblock)
            return self.__subscriptions[dblock.dplugin_id][dblock.name]
        else:
            if dblock.name not in self.__subscriptions[dblock.dplugin_id]:
                self.__subscriptions[dblock.dplugin_id][dblock.name] = DSubscription(dblock)
                return self.__subscriptions[dblock.dplugin_id][dblock.name]
            else:
                return None
        return None

    def unsubscribe(self, dblock):
        """
        This plugin unsubscribes a 'dblock' by forgetting the dblog id.

        :param dblock: DBlock which should be unsubscribed
        :return:
        :rtype boolean:
        """

        if dblock.dplugin_id not in self.__subscriptions:
            return False
        else:

            if dblock.name in self.__subscriptions[dblock.dplugin_id]:
                del self.__subscriptions[dblock.dplugin_id][dblock.name]

                if len(self.__subscriptions[dblock.dplugin_id]) is 0:
                    del self.__subscriptions[dblock.dplugin_id]
                return True
            else:
                return False
        return False

    def get_subscribtions(self):
        """
        Returns a reference to a dictionary of all subscribtions.

        :return {}{} of DPlugin ids to DBlock names :
        :rtype: {}{}
        """
        return self.__subscriptions

    def add_parameter(self, parameter):
        """
        Used to add a parameter for this plugin.
        Returns true if parameter doesn't existed and was added,
        returns false if parameter already exists.

        :param parameter:
        :return:
        :rtype boolean:
        """
        if parameter.name not in self.__parameters:
            self.__parameters[parameter.name] = parameter
            return True
        else:
            return False

    def rm_parameter(self, parameter):
        """
        Used to remove a parameter for this plugin.
        Returns true if parameter existed and was deleted,
        returns false if parameter doesn't exist.

        :param parameter: Parameter which should be removed.
        :return:
        :rtype boolean:
        """

        if parameter.name in self.__parameters:
            self.__parameters[parameter.name].remove()
            del self.__parameters[parameter.name]
            return True
        else:
            return False

    def get_parameters(self):
        """
        Returns a list of all parameters.

        :return:
        :rtype {}:
        """
        return self.__parameters

    def add_dblock(self, dblock):
        """
        Used to add a block for this plugin.
        Returns true if parameter doesn't existed and was deleted,
        returns false if parameter already exists.

        :param dblock: Block which should be added.
        :return:
        :rtype boolean:
        """
        dblock.dplugin_id = self.id
        if dblock.name not in self.__blocks:
            self.__blocks[dblock.name] = dblock
            return True
        else:
            return False

    def rm_dblock(self, dblock):
        """
        Used to remove a block for this plugin.
        Returns true if block existed and was deleted,
        returns false if block doesn't exist.

        :param dblock:
        :return:
        :rtype boolean:
        """
        if dblock.name in self.__blocks:
            del self.__blocks[dblock.name]
            dblock.name += "_deleted"
            dblock.remove()
            return True
        else:
            return False

    def get_dblocks(self):
        """
        Returns a list of all blocks.

        :return:
        :rtype {}:
        """
        return self.__blocks

    def get_dblock_by_name(self, dblock_name):
        """
        Returns a single block by its unique name of all parameters.

        :param dblock_name: Uniqueder identifier for this block.
        :return:
        """

        if dblock_name in self.__blocks:
            return self.__blocks[dblock_name]
        else:
            return None

    def get_meta(self):
        """

        :return:
        :rtype DPlugin:
        """

        DPlugin_new = DPlugin()
        DPlugin_new.id = self.id
        DPlugin_new.pid = self.pid
        DPlugin_new.state = self.state
        DPlugin_new.alive_state = self.alive_state
        DPlugin_new.own_process = self.own_process
        DPlugin_new.uname = self.uname
        DPlugin_new.type = self.type
        DPlugin_new.path = self.path

        DPlugin_new.__parameters = copy.deepcopy(self.__parameters)
        DPlugin_new.__subscriptions = copy.deepcopy(self.__subscriptions)
        DPlugin_new.__blocks = copy.deepcopy(self.__blocks)

        return DPlugin_new

    def update_meta(self, meta):
        """

        :param meta: of type DPlugin
        :return:
        """

        # --------------------------
        # Update DPlugin Attributes
        # --------------------------

        self.id = meta.id
        self.pid = meta.pid
        self.state = meta.state
        self.alive_state = meta.alive_state
        self.own_process = meta.own_process
        self.uname = meta.uname
        self.type = meta.type
        self.path = meta.path

        # -----------------------------
        # Update DParameters of DPlugin
        # -----------------------------

        copy_parameters = copy.deepcopy(self.__parameters)

        for parameter_name in meta.__parameters:
            if parameter_name in self.__parameters:
                self.__parameters[parameter_name].update_meta(meta.__parameters[parameter_name])

            if parameter_name not in copy_parameters:
                self.add_parameter(meta.__parameters[parameter_name])

        for parameter_name in copy_parameters:
            if parameter_name not in meta.__parameters:
                self.rm_parameter(self.__parameters[parameter_name])

        # -----------------------------
        # Update DSubscriptions of DPlugin
        # -----------------------------

        copy_subscriptions = copy.deepcopy(self.__subscriptions)
        meta_subscriptions = meta.__subscriptions

        #self.__subscriptions = meta_subscriptions

        # ---------------------------------------
        # Create missing subscriptions
        # Update existing subscriptions
        # ---------------------------------------

        for dplugin_uname in meta_subscriptions:

            if dplugin_uname in copy_subscriptions:

                for dblock_name in meta_subscriptions[dplugin_uname]:

                    if dblock_name in copy_subscriptions[dplugin_uname]:
                        self.__subscriptions[dplugin_uname][dblock_name].update_meta(copy_subscriptions[dplugin_uname][dblock_name])
                    else:
                        self.__subscriptions[dplugin_uname][dblock_name] = {}
                        self.__subscriptions[dplugin_uname][dblock_name] = meta_subscriptions[dplugin_uname][dblock_name]
            else:
                self.__subscriptions[dplugin_uname] = meta_subscriptions[dplugin_uname]

        # -----------------------------------------
        # Remove no more needed subscriptions
        # -----------------------------------------

        for dplugin_uname in copy_subscriptions:

            if dplugin_uname in meta_subscriptions:

                for dblock_name in copy_subscriptions[dplugin_uname]:

                    if dblock_name not in meta_subscriptions[dplugin_uname]:
                        # Remove old subscription for dblock_name of dplugin_name
                        self.__subscriptions[dplugin_uname][dblock_name].remove()
                        del self.__subscriptions[dplugin_uname][dblock_name]

            else:
                for dblock_name in copy_subscriptions[dplugin_uname]:
                    # Remove old subscritions for dplugin_uname
                    self.__subscriptions[dplugin_uname][dblock_name].remove()
                    del self.__subscriptions[dplugin_uname][dblock_name]

                del self.__subscriptions[dplugin_uname]


        # -----------------------------
        # Update DBlocks of DPlugin
        # -----------------------------
        self.__blocks = meta.__blocks


class DSubscription(DObject):
    """
    DSubscription is used for the internal description of a subscription.

    """
    def __init__(self, dblock):
        self.dblock = dblock
        self.dblock_name = dblock.name
        self.dplugin_id = dblock.dplugin_id

        self.alias = None
        self.signals = []

    def add_signal(self, signal):
        """
        Add Signal for this Subscription

        :param signal:
        :return:
        """
        if signal not in self.signals:
            self.signals.append(signal)
            return True
        return False

    def rm_signal(self, signal):
        """
        Remove Signal for this Subscription

        :param signal:
        :return:
        """
        if signal in self.signals:
            self.signals.remove(signal)
            return True

        return False

    def get_dblock(self):
        """
        Returns the block whose signals are subscribed.

        :return:
        :rtype: DBlock
        """
        return self.dblock

    def get_signals(self):
        """
        Returns a copy of all signals which are subscribed.

        :return:
        :rtype: []
        """
        return copy.copy(self.signals)

    def update_meta(self, subscription):
        print('update_meta')

    def attach_signal(self, signal):
        raise NotImplementedError("Stop Using this function.")

    def remove_signal(self, signal):
        raise NotImplementedError("Stop Using this function.")

