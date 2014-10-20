# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/main.ui'
#
# Created: Mon Oct 20 13:32:23 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_QtNewMain(object):
    def setupUi(self, QtNewMain):
        QtNewMain.setObjectName("QtNewMain")
        QtNewMain.resize(800, 600)
        self.centralwidget = QtGui.QWidget(QtNewMain)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 781, 531))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.loadButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.loadButton.setObjectName("loadButton")
        self.horizontalLayout.addWidget(self.loadButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.widgetArea = QtGui.QMdiArea(self.verticalLayoutWidget)
        self.widgetArea.setObjectName("widgetArea")
        self.verticalLayout.addWidget(self.widgetArea)
        QtNewMain.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(QtNewMain)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        QtNewMain.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(QtNewMain)
        self.statusbar.setObjectName("statusbar")
        QtNewMain.setStatusBar(self.statusbar)

        self.retranslateUi(QtNewMain)
        QtCore.QMetaObject.connectSlotsByName(QtNewMain)

    def retranslateUi(self, QtNewMain):
        QtNewMain.setWindowTitle(QtGui.QApplication.translate("QtNewMain", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("QtNewMain", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.loadButton.setText(QtGui.QApplication.translate("QtNewMain", "Save", None, QtGui.QApplication.UnicodeUTF8))

