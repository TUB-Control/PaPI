# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/manager.ui'
#
# Created: Tue Aug 12 14:30:37 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Manager(object):
    def setupUi(self, Manager):
        Manager.setObjectName("Manager")
        Manager.resize(654, 467)
        self.centralwidget = QtGui.QWidget(Manager)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 641, 431))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listPlugin = QtGui.QListWidget(self.horizontalLayoutWidget)
        self.listPlugin.setObjectName("listPlugin")
        self.horizontalLayout.addWidget(self.listPlugin)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.pushButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.pushButton)
        self.horizontalLayout.addLayout(self.formLayout)
        Manager.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(Manager)
        self.statusbar.setObjectName("statusbar")
        Manager.setStatusBar(self.statusbar)

        self.retranslateUi(Manager)
        QtCore.QMetaObject.connectSlotsByName(Manager)

    def retranslateUi(self, Manager):
        Manager.setWindowTitle(QtGui.QApplication.translate("Manager", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Manager", "PushButton", None, QtGui.QApplication.UnicodeUTF8))

