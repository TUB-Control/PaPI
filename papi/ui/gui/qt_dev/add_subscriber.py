# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_dev/add_subscriber.ui'
#
# Created: Mon Jan  5 14:03:51 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AddSubscriber(object):
    def setupUi(self, AddSubscriber):
        AddSubscriber.setObjectName("AddSubscriber")
        AddSubscriber.resize(531, 197)
        self.buttonBox = QtGui.QDialogButtonBox(AddSubscriber)
        self.buttonBox.setGeometry(QtCore.QRect(10, 160, 511, 32))
        self.buttonBox.setAutoFillBackground(False)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayoutWidget = QtGui.QWidget(AddSubscriber)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 511, 141))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.treeSubscriber = QtGui.QTreeWidget(self.horizontalLayoutWidget)
        self.treeSubscriber.setObjectName("treeSubscriber")
        self.horizontalLayout.addWidget(self.treeSubscriber)
        self.treeTarget = QtGui.QTreeWidget(self.horizontalLayoutWidget)
        self.treeTarget.setObjectName("treeTarget")
        self.horizontalLayout.addWidget(self.treeTarget)
        self.treeBlock = QtGui.QTreeWidget(self.horizontalLayoutWidget)
        self.treeBlock.setObjectName("treeBlock")
        self.horizontalLayout.addWidget(self.treeBlock)
        self.treeSignal = QtGui.QTreeWidget(self.horizontalLayoutWidget)
        self.treeSignal.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.treeSignal.setObjectName("treeSignal")
        self.horizontalLayout.addWidget(self.treeSignal)

        self.retranslateUi(AddSubscriber)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AddSubscriber.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AddSubscriber.reject)
        QtCore.QMetaObject.connectSlotsByName(AddSubscriber)

    def retranslateUi(self, AddSubscriber):
        AddSubscriber.setWindowTitle(QtGui.QApplication.translate("AddSubscriber", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.treeSubscriber.headerItem().setText(0, QtGui.QApplication.translate("AddSubscriber", "Subscriber", None, QtGui.QApplication.UnicodeUTF8))
        self.treeTarget.headerItem().setText(0, QtGui.QApplication.translate("AddSubscriber", "Target", None, QtGui.QApplication.UnicodeUTF8))
        self.treeBlock.headerItem().setText(0, QtGui.QApplication.translate("AddSubscriber", "Block", None, QtGui.QApplication.UnicodeUTF8))
        self.treeSignal.headerItem().setText(0, QtGui.QApplication.translate("AddSubscriber", "Signal", None, QtGui.QApplication.UnicodeUTF8))

