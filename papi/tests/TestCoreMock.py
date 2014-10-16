__author__ = 'stefan'


import unittest
from papi.data.DCore import DCore
from papi.data.DGui import DGui
from papi.core import Core
from papi.gui.gui_main import startGUI_TESTMOCK
from papi.gui.gui_api import Gui_api

from papi.PapiEvent import PapiEvent
from papi.data.DOptionalData import DOptionalData
from threading import Thread
from multiprocessing import Queue

import os
import time

from PySide import QtCore

class dummyProcess(object):
    def __init__(self):
        self.pid = 10
    def join(self):
        pass


class gui_data_mock(object):
    def __init__(self):
        self.gui_data = None


class TestCoreMock(unittest.TestCase):


    def test_create_plugin(self):
        # create a Plot plugin
        opt = DOptionalData()
        opt.plugin_identifier = 'Plot'
        opt.plugin_uname = 'Plot1'
        create_event = PapiEvent(1, 1, 'instr_event', 'create_plugin',opt)
        self.core_queue.put(create_event)

        # create a Plot plugin
        opt = DOptionalData()
        opt.plugin_identifier = 'Sinus'
        opt.plugin_uname = 'Sin1'
        create_event = PapiEvent(1, 1, 'instr_event', 'create_plugin',opt)
        self.core_queue.put(create_event)


        time.sleep(1)
        #
        self.assertIsNotNone(self.core_data.get_dplugin_by_uname('Plot1'))
        self.assertIsNotNone(self.gui_data.get_dplugin_by_uname('Plot1'))
        self.assertIsNotNone(self.core_data.get_dplugin_by_uname('Sin1'))
        self.assertIsNotNone(self.gui_data.get_dplugin_by_uname('Sin1'))


    def test_create_plugin_sub(self):
        # create a Plot plugin
        opt = DOptionalData()
        opt.plugin_identifier = 'Plot'
        opt.plugin_uname = 'Plot1'
        create_event = PapiEvent(1, 1, 'instr_event', 'create_plugin',opt)
        self.core_queue.put(create_event)

        # create a Plot plugin
        opt = DOptionalData()
        opt.plugin_identifier = 'Sinus'
        opt.plugin_uname = 'Sin1'
        create_event = PapiEvent(1, 1, 'instr_event', 'create_plugin',opt)
        self.core_queue.put(create_event)


        time.sleep(1)
        #
        self.assertIsNotNone(self.core_data.get_dplugin_by_uname('Plot1'))
        self.assertIsNotNone(self.gui_data.get_dplugin_by_uname('Plot1'))
        self.assertIsNotNone(self.core_data.get_dplugin_by_uname('Sin1'))
        self.assertIsNotNone(self.gui_data.get_dplugin_by_uname('Sin1'))

        self.gui_api.do_subscribe_uname('Plot1','Sin1','SinMit_f3',[1])

        time.sleep(1)

        subs = self.gui_data.get_dplugin_by_uname('Plot1').get_subscribtions()
        for id in subs:
            dsub = self.gui_data.get_dplugin_by_id(id)
            self.assertEqual('Sin1',dsub.uname)



    def test_do_create_api(self):


        self.gui_api.do_create_plugin('Plot','Plot1')
        self.gui_api.do_create_plugin('Sinus','Sin1')


        time.sleep(1)
        #
        self.assertIsNotNone(self.core_data.get_dplugin_by_uname('Plot1'))
        self.assertIsNotNone(self.gui_data.get_dplugin_by_uname('Plot1'))
        self.assertIsNotNone(self.core_data.get_dplugin_by_uname('Sin1'))
        self.assertIsNotNone(self.gui_data.get_dplugin_by_uname('Sin1'))

        self.assertIsNone(self.core_data.get_dplugin_by_uname('Sinus'))
        self.assertIsNone(self.gui_data.get_dplugin_by_uname('Sinus'))



    def setUp(self):
        core = Core(use_gui=False)
        core.gui_process = dummyProcess()
        core.gui_alive = True

        self.core_thread = Thread(target=core.run)
        self.core_thread.start()

        #self.gui_data_m = gui_data_mock()

        self.gui_data = DGui()

        self.gui_thread = Thread(target=startGUI_TESTMOCK, args=[core.core_event_queue, core.gui_event_queue, core.gui_id, self.gui_data])
        self.gui_thread.start()


        # get data and queues
        self.core_queue = core.core_event_queue
        self.gui_queue = core.gui_event_queue
        self.core_data = core.core_data
        #self.gui_data = self.gui_data_m.gui_data

        self.gui_api = Gui_api(self.gui_data, self.core_queue, core.gui_id)

    def tearDown(self):
        # close Gui
        self.gui_queue.put(  PapiEvent(1,1,'instr_event','test_close',DOptionalData())  )

        # wait for close
        # time.sleep(1)

        # join threads
        self.gui_thread.join()
        self.core_thread.join()



















if __name__ == "__main__":
    unittest.main();