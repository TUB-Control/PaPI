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
from papi.gui.manager import Overview
from papi.PapiEvent import PapiEvent
from papi.data.DGui import DGui
from papi.ConsoleLog import ConsoleLog
from papi.data.DOptionalData import DOptionalData
from papi.gui.add_plugin import AddPlugin
from papi.gui.add_subscriber import AddSubscriber
from PySide.QtGui import QIcon
from PySide.QtCore import QSize

from yapsy.PluginManager import PluginManager
import importlib.machinery


from multiprocessing import Queue
import os


class GUI(QMainWindow, Ui_MainGUI):

    def __init__(self, core_queue, gui_queue,gui_id, parent=None):
        super(GUI, self).__init__(parent)
        self.setupUi(self)

        self.create_actions()

        callback_functions = {
            'create_plugin' : self.do_create_plugin,
            'set_parameter' : self.do_set_parameter,
            'subscribe'     : self.do_subsribe,
            'unsubscribe'   : self.do_unsubscribe,
            'set_parameter' : self.do_set_parameter
        }


        self.gui_data = DGui()

        self.manager_overview = Overview(callback_functions)
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


        self.log = ConsoleLog(1, 'Gui-Process: ')

        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["plugin","papi/plugin"])

        self.log.printText(1,'Gui: Gui process id: '+str(os.getpid()))

        self.stefans_text_field.setText('1')
        # -------------------------------------
        # Create actions for buttons
        # -------------------------------------

        self.buttonCreatePlugin.clicked.connect(self.create_plugin)
        self.buttonCreateSubscription.clicked.connect(self.create_subscription)
        self.buttonShowOverview.clicked.connect(self.ap_overview)
        self.buttonExit.clicked.connect(self.close)

        # -------------------------------------
        # Create Icons for buttons
        # -------------------------------------

        addplugin_icon = QIcon.fromTheme("list-add")
        close_icon = QIcon.fromTheme("application-exit")
        overview_icon = QIcon.fromTheme("view-fullscreen")
        addsubscription_icon = QIcon.fromTheme("list-add")

        # -------------------------------------
        # Set Icons for buttons
        # -------------------------------------

        self.buttonCreatePlugin.setIcon(addplugin_icon)
        self.buttonCreatePlugin.setIconSize(QSize(30, 30))

        self.buttonExit.setIcon(close_icon)
        self.buttonExit.setIconSize(QSize(30, 30))

        self.buttonShowOverview.setIcon(overview_icon)
        self.buttonShowOverview.setIconSize(QSize(30, 30))

        self.buttonCreateSubscription.setIcon(addsubscription_icon)
        self.buttonCreateSubscription.setIconSize(QSize(30, 30))

        # -------------------------------------
        # Set Tooltipps for buttons
        # -------------------------------------

        self.buttonExit.setToolTip("Exit PaPI")
        self.buttonCreatePlugin.setToolTip("Add New Plugin")
        self.buttonCreateSubscription.setToolTip("Create New Subscription")
        self.buttonShowOverview.setToolTip("Show Overview")

        # -------------------------------------
        # Set TextName to ''
        # -------------------------------------

        self.buttonExit.setText('')
        self.buttonCreatePlugin.setText('')
        self.buttonCreateSubscription.setText('')
        self.buttonShowLicence.setText('')
        self.buttonShowOverview.setText('')


    def set_dgui_data(self, dgui):
        self.gui_data = dgui
        self.manager_overview.dgui =dgui

    def dbg(self):
        print("Action")

    def create_actions(self):
        self.actionM_License.triggered.connect(self.menu_license)
        self.actionM_Quit.triggered.connect(self.menu_quit)

        self.actionP_Overview.triggered.connect(self.ap_overview)


        self.stefans_button.clicked.connect(self.stefan)
        self.stefans_button_2.clicked.connect(self.stefan_at_his_best)

    def create_plugin(self):
        """
        This function is called to create an QDialog, which is used to create Plugins
        :return:
        """
        AddPlu = AddPlugin()
        AddPlu.setDGui(self.gui_data)
        AddPlu.show()
        AddPlu.raise_()
        AddPlu.activateWindow()
        r = AddPlu.exec_()

        if r == 1 :
            self.do_create_plugin(AddPlu.plugin_name, AddPlu.plugin_uname)

        print("ReturnCode ", str(r))

    def create_subscription(self):
        """
        This function is called to create an QDialog, which is used to create a subscribtion for a single Plugin
        :return:
        """

        AddSub = AddSubscriber()
        AddSub.setDGui(self.gui_data)
        AddSub.show()
        AddSub.raise_()
        AddSub.activateWindow()
        r = AddSub.exec_()

        if r == 1 :
            subscriber_id = AddSub.subscriberID
            target_id = AddSub.targetID
            block_name = AddSub.blockName

            self.do_subsribe(subscriber_id, target_id, block_name)

        print("ReturnCode " , str(r))

    def menu_license(self):
        pass

    def menu_quit(self):
        self.close()
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
        self.close()

    def stefan_at_his_best(self):
        s = self.stefans_text_field.text()
        val = float(s)

        self.do_set_parameter('Add1','Count',val)




    def stefan(self):
        self.count += 1

        op=0

        if op == 0:
            # 1 test uname subsribe

            self.do_create_plugin('Fourier_Rect','Four')    #id 2
            self.do_create_plugin('Add','Add1')             #id 3
            self.do_create_plugin('Plot','Plot1')           #id 4

            time.sleep(0.1)
            self.do_subsribe(3,2,'Rect1')
            self.do_subsribe(4,3,'AddOut1')

        if op == 1:
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

        if op == 2:
            self.do_create_plugin('Sinus','Sinus1') #id 2
            self.do_create_plugin('Plot','Plot1')   #id 3
            self.do_create_plugin('Plot','Plot2')   #id 4

            time.sleep(0.1)

            self.do_subsribe(3,2,'SinMit_f1')
            self.do_subsribe(4,2,'SinMit_f1')





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
        dID_list = event.get_destinatioID()
        opt = event.get_optional_parameter()
        for dID in dID_list:
            dplugin = self.gui_data.get_dplugin_by_id(dID)
            if dplugin != None:
                dplugin.plugin.execute(opt.data)
            else:
                self.log.printText(1,'new_data, Plugin with id  '+str(dID)+'  does not exist in DGui')


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

        self.log.printText(2,'create_plugin, Try to create plugin with Name  '+plugin_identifier+ " and UName " + uname )


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
            dplugin.type = opt.plugin_type

            dplugin.plugin.init_plugin(self.core_queue, self.gui_queue,dplugin.id)

            dplugin.plugin.start_init()

            dplugin.plugin.setConfig(name=dplugin.uname, sampleinterval=1, timewindow=1000., size=(150,150))

            self.scopeArea.addSubWindow(dplugin.plugin.get_sub_window())
            dplugin.plugin.get_sub_window().show()
            print(dplugin.plugin.get_sub_window())
            self.log.printText(1,'create_plugin, Plugin with name  '+str(uname)+'  was started as ViP')

        else:
            dplugin =self.gui_data.add_plugin(None,None,True,None,plugin,id)
            dplugin.uname = uname
            dplugin.type = opt.plugin_type
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

        event = PapiEvent(1,0,'status_event','alive',None)
        self.core_queue.put(event)





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
        print('Create Plugin ' + uname)
        opt = DOptionalData()
        opt.plugin_identifier = plugin_identifier
        opt.plugin_uname = uname
        event = PapiEvent(self.gui_id, 0, 'instr_event','create_plugin',opt)
        self.core_queue.put(event)


    def do_subsribe(self,subscriber_id,source_id,block_name):
        opt = DOptionalData()
        opt.source_ID = source_id
        opt.block_name = block_name
        event = PapiEvent(subscriber_id, 0, 'instr_event', 'subscribe', opt)
        self.core_queue.put(event)

    def do_subscribe_uname(self,subscriber_uname,source_uname,block_name):

        source_id = None
        subscriber_id = None

        dplug = self.gui_data.get_dplugin_by_uname(subscriber_uname)

        if dplug != None:
            subscriber_id = dplug.id
        else:
            self.log.printText(1, 'do_subscribe, sub uname worng')
            return -1

        dplug2 = self.gui_data.get_dplugin_by_uname(source_uname)
        if dplug2 != None:
            source_id = dplug2.id
        else:
            self.log.printText(1, 'do_subscribe, target uname  worng')
            return -1

        opt = DOptionalData()
        opt.source_ID = source_id
        opt.block_name = block_name
        event = PapiEvent(subscriber_id, 0, 'instr_event', 'subscribe', opt)
        self.core_queue.put(event)



    def do_unsubscribe(self,subscriber_id,source_id,block_name):
        opt = DOptionalData()
        opt.source_ID = source_id
        opt.block_name = block_name
        event = PapiEvent(subscriber_id, 0, 'instr_event', 'unsubscribe', opt)
        self.core_queue.put(event)

    def do_unsubscribe_uname(self,subscriber_uname,source_uname,block_name):
        source_id = None
        subscriber_id = None

        dplug = self.gui_data.get_dplugin_by_uname(subscriber_uname)

        if dplug != None:
            subscriber_id = dplug.id
        else:
            self.log.printText(1, 'do_subscribe, sub uname worng')
            return -1

        dplug2 = self.gui_data.get_dplugin_by_uname(source_uname)
        if dplug2 != None:
            source_id = dplug2.id
        else:
            self.log.printText(1, 'do_subscribe, target uname  worng')
            return -1

        opt = DOptionalData()
        opt.source_ID = source_id
        opt.block_name = block_name
        event = PapiEvent(subscriber_id, 0, 'instr_event', 'unsubscribe', opt)
        self.core_queue.put(event)


    def do_set_parameter(self,plugin_uname,parameter_name,value):
        dplug = self.gui_data.get_dplugin_by_uname(plugin_uname)
        if dplug is not None:
            parameters = dplug.get_parameters()
            if parameters is not None:
                p = parameters[parameter_name]
                if p is not None:
                    # TODO: check against range AND type of parameter
                    if self.check_range_of_value(value,p.range):
                        p.value = value
                        opt = DOptionalData()
                        opt.parameter_list = [p]
                        opt.plugin_id = dplug.id
                        e = PapiEvent(self.gui_id,dplug.id,'instr_event','set_parameter',opt)
                        self.core_queue.put(e)
                    else:
                        self.log.printText(1,'do_set_parameter, value out of range')





    def check_range_of_value(self,value,range):
        min = range[0]
        max = range[1]
        if value > max:
            return False
        if value < min:
            return False
        return True




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
