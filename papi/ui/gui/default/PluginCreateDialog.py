# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/default/PluginCreateDialog.ui'
#
# Created: Wed Sep  9 15:39:31 2015
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CreatePluginDialog(object):
    def setupUi(self, CreatePluginDialog):
        CreatePluginDialog.setObjectName("CreatePluginDialog")
        CreatePluginDialog.resize(498, 384)
        self.verticalLayout = QtWidgets.QVBoxLayout(CreatePluginDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(CreatePluginDialog)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tabSimple = QtWidgets.QWidget()
        self.tabSimple.setObjectName("tabSimple")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tabSimple)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formSimple = QtWidgets.QFormLayout()
        self.formSimple.setObjectName("formSimple")
        self.verticalLayout_2.addLayout(self.formSimple)
        self.tabWidget.addTab(self.tabSimple, "")
        self.tabAdvance = QtWidgets.QWidget()
        self.tabAdvance.setObjectName("tabAdvance")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tabAdvance)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formAdvance = QtWidgets.QFormLayout()
        self.formAdvance.setObjectName("formAdvance")
        self.verticalLayout_3.addLayout(self.formAdvance)
        self.tabWidget.addTab(self.tabAdvance, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(CreatePluginDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.autostartBox = QtWidgets.QCheckBox(CreatePluginDialog)
        self.autostartBox.setChecked(True)
        self.autostartBox.setObjectName("autostartBox")
        self.verticalLayout.addWidget(self.autostartBox)

        self.retranslateUi(CreatePluginDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(CreatePluginDialog.accept)
        self.buttonBox.rejected.connect(CreatePluginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CreatePluginDialog)

    def retranslateUi(self, CreatePluginDialog):
        _translate = QtCore.QCoreApplication.translate
        CreatePluginDialog.setWindowTitle(_translate("CreatePluginDialog", "Dialog"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSimple), _translate("CreatePluginDialog", "Simple"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAdvance), _translate("CreatePluginDialog", "Advance"))
        self.autostartBox.setText(_translate("CreatePluginDialog", "Autostart"))

