# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/default/PluginCreateDialog.ui'
#
# Created: Wed Dec 16 15:44:24 2015
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
        self.tabWidget.setCurrentIndex(-1)
        self.buttonBox.accepted.connect(CreatePluginDialog.accept)
        self.buttonBox.rejected.connect(CreatePluginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CreatePluginDialog)

    def retranslateUi(self, CreatePluginDialog):
        _translate = QtCore.QCoreApplication.translate
        CreatePluginDialog.setWindowTitle(_translate("CreatePluginDialog", "Dialog"))
        self.autostartBox.setText(_translate("CreatePluginDialog", "Autostart"))

