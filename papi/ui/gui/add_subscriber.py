# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/add_subscriber.ui'
#
# Created: Mon Aug 25 12:23:51 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AddSubscriber(object):
    def setupUi(self, AddSubscriber):
        AddSubscriber.setObjectName("AddSubscriber")
        AddSubscriber.resize(400, 148)
        self.buttonBox = QtGui.QDialogButtonBox(AddSubscriber)
        self.buttonBox.setGeometry(QtCore.QRect(20, 110, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.listSubscriber = QtGui.QListWidget(AddSubscriber)
        self.listSubscriber.setGeometry(QtCore.QRect(10, 30, 111, 71))
        self.listSubscriber.setObjectName("listSubscriber")
        self.listTarget = QtGui.QListWidget(AddSubscriber)
        self.listTarget.setGeometry(QtCore.QRect(140, 30, 111, 71))
        self.listTarget.setObjectName("listTarget")
        self.label = QtGui.QLabel(AddSubscriber)
        self.label.setGeometry(QtCore.QRect(30, 10, 81, 17))
        self.label.setObjectName("label")
        self.listBlock = QtGui.QListWidget(AddSubscriber)
        self.listBlock.setGeometry(QtCore.QRect(270, 30, 111, 71))
        self.listBlock.setObjectName("listBlock")
        self.label_2 = QtGui.QLabel(AddSubscriber)
        self.label_2.setGeometry(QtCore.QRect(170, 10, 81, 17))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(AddSubscriber)
        self.label_3.setGeometry(QtCore.QRect(310, 10, 81, 17))
        self.label_3.setObjectName("label_3")

        self.retranslateUi(AddSubscriber)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AddSubscriber.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AddSubscriber.reject)
        QtCore.QMetaObject.connectSlotsByName(AddSubscriber)

    def retranslateUi(self, AddSubscriber):
        AddSubscriber.setWindowTitle(QtGui.QApplication.translate("AddSubscriber", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AddSubscriber", "Subscriber", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AddSubscriber", "Target", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("AddSubscriber", "Block", None, QtGui.QApplication.UnicodeUTF8))

