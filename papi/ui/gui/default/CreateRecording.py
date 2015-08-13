# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/default/CreateRecording.ui'
#
# Created: Thu Aug 13 18:34:29 2015
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CreateRecording(object):
    def setupUi(self, CreateRecording):
        CreateRecording.setObjectName("CreateRecording")
        CreateRecording.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(CreateRecording)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.Fields = QtWidgets.QWidget()
        self.Fields.setObjectName("Fields")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.Fields)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.customFieldTable = QtWidgets.QTableView(self.Fields)
        self.customFieldTable.setObjectName("customFieldTable")
        self.verticalLayout.addWidget(self.customFieldTable)
        self.addFieldButton = QtWidgets.QPushButton(self.Fields)
        self.addFieldButton.setObjectName("addFieldButton")
        self.verticalLayout.addWidget(self.addFieldButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.structureView = QtWidgets.QTreeView(self.Fields)
        self.structureView.setObjectName("structureView")
        self.verticalLayout_2.addWidget(self.structureView)
        self.previewButton = QtWidgets.QPushButton(self.Fields)
        self.previewButton.setObjectName("previewButton")
        self.verticalLayout_2.addWidget(self.previewButton)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.Fields, "")
        self.Subscription = QtWidgets.QWidget()
        self.Subscription.setObjectName("Subscription")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.Subscription)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.structureView_sub = QtWidgets.QTreeView(self.Subscription)
        self.structureView_sub.setObjectName("structureView_sub")
        self.verticalLayout_3.addWidget(self.structureView_sub)
        self.previewButton_sub = QtWidgets.QPushButton(self.Subscription)
        self.previewButton_sub.setObjectName("previewButton_sub")
        self.verticalLayout_3.addWidget(self.previewButton_sub)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.selectionGrid = QtWidgets.QGridLayout()
        self.selectionGrid.setObjectName("selectionGrid")
        self.verticalLayout_4.addLayout(self.selectionGrid)
        self.sendConfigButton = QtWidgets.QPushButton(self.Subscription)
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
        _translate = QtCore.QCoreApplication.translate
        CreateRecording.setWindowTitle(_translate("CreateRecording", "MainWindow"))
        self.addFieldButton.setText(_translate("CreateRecording", "AddField"))
        self.previewButton.setText(_translate("CreateRecording", "Preview"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Fields), _translate("CreateRecording", "Fields"))
        self.previewButton_sub.setText(_translate("CreateRecording", "PreviewButton"))
        self.sendConfigButton.setText(_translate("CreateRecording", "SendConfig"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Subscription), _translate("CreateRecording", "Subscription"))

