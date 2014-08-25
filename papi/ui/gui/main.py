# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/main.ui'
#
# Created: Mon Aug 25 12:23:51 2014
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
        self.stefans_button_2 = QtGui.QPushButton(self.centralwidget)
        self.stefans_button_2.setObjectName("stefans_button_2")
        self.verticalLayout_2.addWidget(self.stefans_button_2)
        self.stefans_text_field = QtGui.QLineEdit(self.centralwidget)
        self.stefans_text_field.setObjectName("stefans_text_field")
        self.verticalLayout_2.addWidget(self.stefans_text_field)
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
        MainGUI.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainGUI)
        self.statusbar.setObjectName("statusbar")
        MainGUI.setStatusBar(self.statusbar)
        self.actionP_Available = QtGui.QAction(MainGUI)
        self.actionP_Available.setObjectName("actionP_Available")
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
        self.actionP_Overview = QtGui.QAction(MainGUI)
        self.actionP_Overview.setObjectName("actionP_Overview")
        self.menuMenu.addAction(self.actionM_License)
        self.menuMenu.addAction(self.actionM_Quit)
        self.menuAvailablePlugins.addAction(self.actionP_Available)
        self.menuAvailablePlugins.addSeparator()
        self.menuAvailablePlugins.addAction(self.actionP_Overview)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuAvailablePlugins.menuAction())

        self.retranslateUi(MainGUI)
        QtCore.QMetaObject.connectSlotsByName(MainGUI)

    def retranslateUi(self, MainGUI):
        MainGUI.setWindowTitle(QtGui.QApplication.translate("MainGUI", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.stefans_button.setText(QtGui.QApplication.translate("MainGUI", "Action", None, QtGui.QApplication.UnicodeUTF8))
        self.stefans_button_2.setText(QtGui.QApplication.translate("MainGUI", "Wayne", None, QtGui.QApplication.UnicodeUTF8))
        self.menuMenu.setTitle(QtGui.QApplication.translate("MainGUI", "Menu", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAvailablePlugins.setTitle(QtGui.QApplication.translate("MainGUI", "Plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.actionP_Available.setText(QtGui.QApplication.translate("MainGUI", "Available", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAP_IO.setText(QtGui.QApplication.translate("MainGUI", "IO", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRP_Visual.setText(QtGui.QApplication.translate("MainGUI", "Visual", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRP_IO.setText(QtGui.QApplication.translate("MainGUI", "IO", None, QtGui.QApplication.UnicodeUTF8))
        self.actionM_License.setText(QtGui.QApplication.translate("MainGUI", "License", None, QtGui.QApplication.UnicodeUTF8))
        self.actionM_Quit.setText(QtGui.QApplication.translate("MainGUI", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAP_Parameter.setText(QtGui.QApplication.translate("MainGUI", "Parameter", None, QtGui.QApplication.UnicodeUTF8))
        self.actionP_Overview.setText(QtGui.QApplication.translate("MainGUI", "Overview", None, QtGui.QApplication.UnicodeUTF8))

