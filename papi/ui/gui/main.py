# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/main.ui'
#
# Created: Thu Jul 31 13:08:38 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainGUI(object):
    def setupUi(self, MainGUI):
        MainGUI.setObjectName("MainGUI")
        MainGUI.resize(1084, 918)
        self.centralwidget = QtGui.QWidget(MainGUI)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.stefans_button = QtGui.QPushButton(self.centralwidget)
        self.stefans_button.setObjectName("stefans_button")
        self.verticalLayout_2.addWidget(self.stefans_button)
        self.scopeArea = QtGui.QMdiArea(self.centralwidget)
        self.scopeArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scopeArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scopeArea.setObjectName("scopeArea")
        self.verticalLayout_2.addWidget(self.scopeArea)
        MainGUI.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainGUI)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1084, 25))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        self.menuAvailablePlugins = QtGui.QMenu(self.menubar)
        self.menuAvailablePlugins.setObjectName("menuAvailablePlugins")
        self.menuRunningPlugins = QtGui.QMenu(self.menubar)
        self.menuRunningPlugins.setObjectName("menuRunningPlugins")
        MainGUI.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainGUI)
        self.statusbar.setObjectName("statusbar")
        MainGUI.setStatusBar(self.statusbar)
        self.actionAP_Visual = QtGui.QAction(MainGUI)
        self.actionAP_Visual.setObjectName("actionAP_Visual")
        self.actionAP_IO = QtGui.QAction(MainGUI)
        self.actionAP_IO.setObjectName("actionAP_IO")
        self.actionRP_Visual = QtGui.QAction(MainGUI)
        self.actionRP_Visual.setObjectName("actionRP_Visual")
        self.actionRP_IO = QtGui.QAction(MainGUI)
        self.actionRP_IO.setObjectName("actionRP_IO")
        self.actionM_License = QtGui.QAction(MainGUI)
        self.actionM_License.setObjectName("actionM_License")
        self.actionM_Quit = QtGui.QAction(MainGUI)
        self.actionM_Quit.setObjectName("actionM_Quit")
        self.actionAP_Parameter = QtGui.QAction(MainGUI)
        self.actionAP_Parameter.setObjectName("actionAP_Parameter")
        self.menuMenu.addAction(self.actionM_License)
        self.menuMenu.addAction(self.actionM_Quit)
        self.menuAvailablePlugins.addAction(self.actionAP_Visual)
        self.menuAvailablePlugins.addAction(self.actionAP_IO)
        self.menuAvailablePlugins.addAction(self.actionAP_Parameter)
        self.menuRunningPlugins.addAction(self.actionRP_Visual)
        self.menuRunningPlugins.addAction(self.actionRP_IO)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuAvailablePlugins.menuAction())
        self.menubar.addAction(self.menuRunningPlugins.menuAction())

        self.retranslateUi(MainGUI)
        QtCore.QMetaObject.connectSlotsByName(MainGUI)

    def retranslateUi(self, MainGUI):
        MainGUI.setWindowTitle(QtGui.QApplication.translate("MainGUI", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.stefans_button.setText(QtGui.QApplication.translate("MainGUI", "Action", None, QtGui.QApplication.UnicodeUTF8))
        self.menuMenu.setTitle(QtGui.QApplication.translate("MainGUI", "Menu", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAvailablePlugins.setTitle(QtGui.QApplication.translate("MainGUI", "AvailablePlugins", None, QtGui.QApplication.UnicodeUTF8))
        self.menuRunningPlugins.setTitle(QtGui.QApplication.translate("MainGUI", "RunningPlugins", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAP_Visual.setText(QtGui.QApplication.translate("MainGUI", "Visual", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAP_IO.setText(QtGui.QApplication.translate("MainGUI", "IO", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRP_Visual.setText(QtGui.QApplication.translate("MainGUI", "Visual", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRP_IO.setText(QtGui.QApplication.translate("MainGUI", "IO", None, QtGui.QApplication.UnicodeUTF8))
        self.actionM_License.setText(QtGui.QApplication.translate("MainGUI", "License", None, QtGui.QApplication.UnicodeUTF8))
        self.actionM_Quit.setText(QtGui.QApplication.translate("MainGUI", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAP_Parameter.setText(QtGui.QApplication.translate("MainGUI", "Parameter", None, QtGui.QApplication.UnicodeUTF8))

