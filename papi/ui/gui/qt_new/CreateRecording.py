# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/CreateRecording.ui'
#
# Created: Thu Apr 16 19:34:59 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_CreateRecording(object):
    def setupUi(self, CreateRecording):
        CreateRecording.setObjectName("CreateRecording")
        CreateRecording.resize(800, 600)
        self.centralwidget = QtGui.QWidget(CreateRecording)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.Fields = QtGui.QWidget()
        self.Fields.setObjectName("Fields")
        self.horizontalLayout = QtGui.QHBoxLayout(self.Fields)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.customFieldTable = QtGui.QTableView(self.Fields)
        self.customFieldTable.setObjectName("customFieldTable")
        self.verticalLayout.addWidget(self.customFieldTable)
        self.addFieldButton = QtGui.QPushButton(self.Fields)
        self.addFieldButton.setObjectName("addFieldButton")
        self.verticalLayout.addWidget(self.addFieldButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.structureView = QtGui.QTreeView(self.Fields)
        self.structureView.setObjectName("structureView")
        self.verticalLayout_2.addWidget(self.structureView)
        self.previewButton = QtGui.QPushButton(self.Fields)
        self.previewButton.setObjectName("previewButton")
        self.verticalLayout_2.addWidget(self.previewButton)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.Fields, "")
        self.Subscription = QtGui.QWidget()
        self.Subscription.setObjectName("Subscription")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.Subscription)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.structureView_sub = QtGui.QTreeView(self.Subscription)
        self.structureView_sub.setObjectName("structureView_sub")
        self.verticalLayout_3.addWidget(self.structureView_sub)
        self.previewButton_sub = QtGui.QPushButton(self.Subscription)
        self.previewButton_sub.setObjectName("previewButton_sub")
        self.verticalLayout_3.addWidget(self.previewButton_sub)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.selectionGrid = QtGui.QGridLayout()
        self.selectionGrid.setObjectName("selectionGrid")
        self.verticalLayout_4.addLayout(self.selectionGrid)
        self.sendConfigButton = QtGui.QPushButton(self.Subscription)
        self.sendConfigButton.setObjectName("sendConfigButton")
        self.verticalLayout_4.addWidget(self.sendConfigButton)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.tabWidget.addTab(self.Subscription, "")
        self.horizontalLayout_2.addWidget(self.tabWidget)
        CreateRecording.setCentralWidget(self.centralwidget)

        self.retranslateUi(CreateRecording)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(CreateRecording)

    def retranslateUi(self, CreateRecording):
        CreateRecording.setWindowTitle(QtGui.QApplication.translate("CreateRecording", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.addFieldButton.setText(QtGui.QApplication.translate("CreateRecording", "AddField", None, QtGui.QApplication.UnicodeUTF8))
        self.previewButton.setText(QtGui.QApplication.translate("CreateRecording", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Fields), QtGui.QApplication.translate("CreateRecording", "Fields", None, QtGui.QApplication.UnicodeUTF8))
        self.previewButton_sub.setText(QtGui.QApplication.translate("CreateRecording", "PreviewButton", None, QtGui.QApplication.UnicodeUTF8))
        self.sendConfigButton.setText(QtGui.QApplication.translate("CreateRecording", "SendConfig", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Subscription), QtGui.QApplication.translate("CreateRecording", "Subscription", None, QtGui.QApplication.UnicodeUTF8))

