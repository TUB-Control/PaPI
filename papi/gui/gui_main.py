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

import sys
import time

from PySide.QtGui import QMainWindow, QApplication

import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=False)

from papi.ui.gui.main import Ui_MainGUI
from papi.gui.manager import Available, Overview
from papi.PapiEvent import PapiEvent
from papi.data.DGui import DGui
from papi.ConsoleLog import ConsoleLog
from papi.data.DOptionalData import DOptionalData

from yapsy.PluginManager import PluginManager
import importlib.machinery


from multiprocessing import Queue
import os


class GUI(QMainWindow, Ui_MainGUI):

    def __init__(self, core_queue, gui_queue,gui_id, parent=None):
        super(GUI, self).__init__(parent)
        self.setupUi(self)

        self.create_actions()

        self.manager_available = Available()
        self.gui_data = DGui()

        self.manager_overview = Overview()
        self.manager_overview.dgui = self.gui_data
        self.setWindowTitle('PaPI')

        self.core_queue = core_queue
        self.gui_queue = gui_queue

        self.gui_id = gui_id

        self.count = 0

        QtCore.QTimer.singleShot(40,self.gui_working_v2)

        self.process_event = {  'new_data': self.process_new_data_event,
                                'close_programm': self.process_close_program_event,
                                'check_alive_status': self.process_check_alive_status,
                                'create_plugin':self.process_create_plugin,
                                'update_meta': self.process_update_meta,
                                'test': self.test
        }


        self.log = ConsoleLog(1,'Gui-Process: ')

        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["plugin","papi/plugin"])

        self.log.printText(1,'Gui: Gui process id: '+str(os.getpid()))


    def set_dgui_data(self, dgui):
        self.gui_data = dgui
        self.manager_overview.dgui =dgui

    def dbg(self):
        print("Action")

    def create_actions(self):
        self.actionM_License.triggered.connect(self.menu_license)
        self.actionM_Quit.triggered.connect(self.menu_quit)

        self.actionP_Available.triggered.connect(self.ap_available)

        self.actionP_Overview.triggered.connect(self.ap_overview)


        self.stefans_button.clicked.connect(self.stefan)
        self.stefans_button_2.clicked.connect(self.stefan_at_his_best)

    def menu_license(self):
        pass

    def menu_quit(self):
        self.close()
        pass

    def ap_visual(self):
        self.manager_available.show()

        pass

    def ap_available(self):
        self.manager_available.show()
        pass

    def ap_overview(self):
        self.manager_overview.show()
        pass

    def rp_visual(self):
        pass

    def rp_io(self):
        pass

    def closeEvent(self, *args, **kwargs):
        opt = DOptionalData()
        opt.reason = 'User clicked close Button'
        event = PapiEvent(self.gui_id, 0, 'instr_event','close_program',opt)
        self.core_queue.put(event)

        self.manager_overview.close()
        self.manager_available.close()
        self.close()





    def stefan_at_his_best(self):
        name = 'Sinus1'
        print('Plugin Information System - Today: '+name)
        print('===========================================')
        p = self.gui_data.get_dplugin_by_uname(name)
        blocks = p.get_dblocks()
        for k in blocks:
            b = blocks[k]
            print('Block: ',b.name)
        paras = p.get_parameters()

        for i in paras:
             p = paras[i]
             print('Parameter: ',p.name)


        # opt = DOptionalData()
        # opt.plugin_id =4
        # opt.parameter_list = 9/300
        # event = PapiEvent(3,0,'instr_event','set_parameter',opt)
        # self.core_queue.put(event)
        # self.log.printText(1,'gui was closed')

    def stefan(self):
        self.count += 1

        op=2

        if op == 0:
            # 1 test uname subsribe
            opt = DOptionalData()

            opt.plugin_identifier = 'Fourier_Rect'
            opt.plugin_uname = 'Four'

            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt)  #id 2
            self.core_queue.put(event)

            opt = DOptionalData()
            opt.plugin_identifier = 'Plot'
            opt.plugin_uname = 'Plot1'
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt) #id 3
            self.core_queue.put(event)

            opt = DOptionalData()
            opt.plugin_identifier = 'Add'
            opt.plugin_uname = 'Add1'
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt) #id 4
            self.core_queue.put(event)

            opt = DOptionalData()
            opt.source_ID = 2
            event = PapiEvent(4,0,'instr_event','subscribe',opt)
            self.core_queue.put(event)

            opt = DOptionalData()
            opt.source_ID = 4
            event = PapiEvent(3,0,'instr_event','subscribe',opt)
            self.core_queue.put(event)



        if op==1:
            # 1 Sinus IOP und 1 Plot
            opt = DOptionalData()
            opt.plugin_identifier = 'Sinus'
            opt.plugin_uname = 'Sinus1'
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt)  #id 2
            self.core_queue.put(event)

            opt = DOptionalData()
            opt.plugin_identifier = 'Plot'
            opt.plugin_uname = 'Plot'
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt) #id 3
            self.core_queue.put(event)

            time.sleep(2)

            opt =  DOptionalData()
            opt.source_ID = 2
            opt.block_name = 'SinMit_f1'
            event = PapiEvent(3,0,'instr_event','subscribe',opt)
            self.core_queue.put(event)


        if op==2:
            self.do_create_plugin('Sinus','Sinus1') #id 2
            self.do_create_plugin('Plot','Plot1')   #id 3
            self.do_create_plugin('Plot','Plot2')   #id 4

            time.sleep(0.1)

            self.do_subsribe(3,2,'SinMit_f1')
            self.do_subsribe(4,2,'SinMit_f3')


        if op==3:
            # 2x Sinus und 5 Plots
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 2
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 3
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 4
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 5
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 6
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 7
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 8
            self.core_queue.put(event)
            event = PapiEvent(4,0,'instr_event','subscribe',2)
            self.core_queue.put(event)
            event = PapiEvent(5,0,'instr_event','subscribe',3)
            self.core_queue.put(event)
            event = PapiEvent(6,0,'instr_event','subscribe',2)
            self.core_queue.put(event)
            event = PapiEvent(7,0,'instr_event','subscribe',3)
            self.core_queue.put(event)
            event = PapiEvent(8,0,'instr_event','subscribe',2)
            self.core_queue.put(event)


        if op==4:
            # Sinus und Plot, Fourier Server und Plot+Add
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 2
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 3
            self.core_queue.put(event)

            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Fourier_Rect'])  #id 4
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Add',4]) #id 5
            self.core_queue.put(event)

            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 6
            self.core_queue.put(event)

            event = PapiEvent(3,0,'instr_event','subscribe',2)
            self.core_queue.put(event)

            event = PapiEvent(6,0,'instr_event','subscribe',5)
            self.core_queue.put(event)


        if op==5:
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 2
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 3
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 4
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Fourier_Rect'])  #id 5
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Fourier_Rect'])  #id 6
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Add',5]) #id 7
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Add',6]) #id 8
            self.core_queue.put(event)

        if op==6:
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 2
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 3
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Sinus'])  #id 4
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Fourier_Rect'])  #id 5
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Fourier_Rect'])  #id 6
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Add',5]) #id 7
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Add',6]) #id 8
            self.core_queue.put(event)

            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 9
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 10
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 11
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 12
            self.core_queue.put(event)
            event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',['Plot']) #id 13
            self.core_queue.put(event)

            event = PapiEvent(9,0,'instr_event','subscribe',2)
            self.core_queue.put(event)
            event = PapiEvent(10,0,'instr_event','subscribe',3)
            self.core_queue.put(event)
            event = PapiEvent(11,0,'instr_event','subscribe',4)
            self.core_queue.put(event)
            event = PapiEvent(12,0,'instr_event','subscribe',7)
            self.core_queue.put(event)
            event = PapiEvent(13,0,'instr_event','subscribe',8)
            self.core_queue.put(event)



    def gui_working(self):
        """
         :type event: PapiEvent
         :type dplugin: DPlugin
        """

        try:
            while (True):
                event = self.gui_queue.get_nowait()
                op = event.get_event_operation()
                self.log.printText(2,'Event: '+ op)
                self.process_event[op](event)


            #TODO: wenn 1 Quelle zu 2 Plots geht, nur 1 Event benutzen!
        except:
            pass

        finally:
            QtCore.QTimer.singleShot(40,self.gui_working)

    def gui_working_v2(self):
        """
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        isEvent = True
        event = None
        while(isEvent):
            try:
                event = self.gui_queue.get_nowait()
                isEvent = True
            except:
                isEvent = False

            if(isEvent):
                op = event.get_event_operation()
                self.log.printText(2,'Event: '+ op)
                self.process_event[op](event)

        QtCore.QTimer.singleShot(40,self.gui_working)







    def process_new_data_event(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """

        self.log.printText(2,'new data event')
        dID = event.get_destinatioID()
        opt = event.get_optional_parameter()
        dplugin = self.gui_data.get_dplugin_by_id(dID)
        if dplugin != None:
            dplugin.plugin.execute(opt.data)
            return 1
        else:
            self.log.printText(1,'new_data, Plugin with id  '+str(dID)+'  does not exist in DGui')
            return -1


    def process_create_plugin(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        opt = event.get_optional_parameter()
        id = opt.plugin_id
        plugin_identifier = opt.plugin_identifier
        uname = opt.plugin_uname


        self.plugin_manager.collectPlugins()
        plugin_orginal = self.plugin_manager.getPluginByName(plugin_identifier)

        if plugin_orginal is None:
            self.log.printText(1,'create_plugin, Plugin with Name  '+plugin_identifier+'  does not exist in file system')
            return -1

        imp_path = plugin_orginal.path + ".py"

        loader = importlib.machinery.SourceFileLoader(plugin_orginal.name.lower(), imp_path)
        current_modul = loader.load_module()

        class_name = plugin_orginal.name[:1].upper() + plugin_orginal.name[1:]

        plugin = getattr(current_modul, class_name)()

        if plugin.get_type() == "ViP":
            dplugin =self.gui_data.add_plugin(None,None,False,self.gui_queue,plugin,id)
            dplugin.uname = uname

            dplugin.plugin.init_plugin(self.core_queue, self.gui_queue,dplugin.id)

            dplugin.plugin.start_init()

            dplugin.plugin.setConfig(name=dplugin.uname, sampleinterval=1, timewindow=1000., size=(150,150))

            self.scopeArea.addSubWindow(dplugin.plugin.get_sub_window())
            dplugin.plugin.get_sub_window().show()
            self.log.printText(1,'create_plugin, Plugin with name  '+str(uname)+'  was started as ViP')
        else:
            dplugin =self.gui_data.add_plugin(None,None,True,None,plugin,id)
            dplugin.uname = uname
            self.log.printText(1,'create_plugin, Plugin with name  '+str(uname)+'  was added as non ViP')




    def process_close_program_event(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        pass


    def process_check_alive_status(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        pass


    def test(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        self.log.printText(1,'Test Execute')

    def process_update_meta(self,event):
        """
         :param event: event to process
         :type event: PapiEvent
         :type dplugin: DPlugin
        """
        opt = event.get_optional_parameter()
        pl_id = event.get_originID()

        dplugin = self.gui_data.get_dplugin_by_id(pl_id)
        if dplugin != None:
            dplugin.update_meta(opt.plugin_object)
        else:
            self.log.printText(1,'update_meta, Plugin with id  '+str(pl_id)+'  does not exist')


    def do_create_plugin(self,plugin_identifier,uname):
        opt = DOptionalData()
        opt.plugin_identifier = plugin_identifier
        opt.plugin_uname = uname
        event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt)
        self.core_queue.put(event)


    def do_subsribe(self,subcriber_id,source_id,block_name):
        opt = DOptionalData()
        opt.source_ID = source_id
        opt.block_name = block_name
        event = PapiEvent(subcriber_id, 0, 'instr_event', 'subscribe', opt)
        self.core_queue.put(event)

    def do_unsubscribe(self,subscriber_id,source_id,block_name):
        pass


def startGUI(CoreQueue, GUIQueue,gui_id):
    app = QApplication(sys.argv)
#    mw = QtGui.QMainWindow
    gui = GUI(CoreQueue, GUIQueue,gui_id)
    gui.show()
    app.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
#    mw = QtGui.QMainWindow
    frame = GUI(None,None,None)
    frame.show()
    app.exec_()
