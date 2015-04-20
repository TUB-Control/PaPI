# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/CreateRecording.ui'
#
# Created: Mon Apr 20 15:47:05 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_CreateRecording(object):
    def setupUi(self, CreateRecording):
        CreateRecording.setObjectName(_fromUtf8("CreateRecording"))
        CreateRecording.resize(800, 600)
        self.centralwidget = QtGui.QWidget(CreateRecording)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.Fields = QtGui.QWidget()
        self.Fields.setObjectName(_fromUtf8("Fields"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.Fields)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.customFieldTable = QtGui.QTableView(self.Fields)
        self.customFieldTable.setObjectName(_fromUtf8("customFieldTable"))
        self.verticalLayout.addWidget(self.customFieldTable)
        self.addFieldButton = QtGui.QPushButton(self.Fields)
        self.addFieldButton.setObjectName(_fromUtf8("addFieldButton"))
        self.verticalLayout.addWidget(self.addFieldButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.structureView = QtGui.QTreeView(self.Fields)
        self.structureView.setObjectName(_fromUtf8("structureView"))
        self.verticalLayout_2.addWidget(self.structureView)
        self.previewButton = QtGui.QPushButton(self.Fields)
        self.previewButton.setObjectName(_fromUtf8("previewButton"))
        self.verticalLayout_2.addWidget(self.previewButton)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.Fields, _fromUtf8(""))
        self.Subscription = QtGui.QWidget()
        self.Subscription.setObjectName(_fromUtf8("Subscription"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.Subscription)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.structureView_sub = QtGui.QTreeView(self.Subscription)
        self.structureView_sub.setObjectName(_fromUtf8("structureView_sub"))
        self.verticalLayout_3.addWidget(self.structureView_sub)
        self.previewButton_sub = QtGui.QPushButton(self.Subscription)
        self.previewButton_sub.setObjectName(_fromUtf8("previewButton_sub"))
        self.verticalLayout_3.addWidget(self.previewButton_sub)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.subView = QtGui.QTableView(self.Subscription)
        self.subView.setObjectName(_fromUtf8("subView"))
        self.verticalLayout_4.addWidget(self.subView)
        self.pushButton_2 = QtGui.QPushButton(self.Subscription)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.verticalLayout_4.addWidget(self.pushButton_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.tabWidget.addTab(self.Subscription, _fromUtf8(""))
        self.horizontalLayout_2.addWidget(self.tabWidget)
        CreateRecording.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(CreateRecording)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        CreateRecording.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(CreateRecording)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        CreateRecording.setStatusBar(self.statusbar)

        self.retranslateUi(CreateRecording)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(CreateRecording)

    def retranslateUi(self, CreateRecording):
        CreateRecording.setWindowTitle(_translate("CreateRecording", "MainWindow", None))
        self.addFieldButton.setText(_translate("CreateRecording", "AddField", None))
        self.previewButton.setText(_translate("CreateRecording", "Preview", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Fields), _translate("CreateRecording", "Fields", None))
        self.previewButton_sub.setText(_translate("CreateRecording", "PreviewButton", None))
        self.pushButton_2.setText(_translate("CreateRecording", "SendConfig", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Subscription), _translate("CreateRecording", "Subscription", None))

