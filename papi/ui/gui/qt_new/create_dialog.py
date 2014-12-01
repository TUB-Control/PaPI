# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/create_dialog.ui'
#
# Created: Mon Dec  1 17:42:16 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_CreatePluginDialog(object):
    def setupUi(self, CreatePluginDialog):
        CreatePluginDialog.setObjectName("CreatePluginDialog")
        CreatePluginDialog.resize(498, 384)
        self.verticalLayout = QtGui.QVBoxLayout(CreatePluginDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtGui.QTabWidget(CreatePluginDialog)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tabSimple = QtGui.QWidget()
        self.tabSimple.setObjectName("tabSimple")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tabSimple)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formSimple = QtGui.QFormLayout()
        self.formSimple.setObjectName("formSimple")
        self.verticalLayout_2.addLayout(self.formSimple)
        self.tabWidget.addTab(self.tabSimple, "")
        self.tabAdvance = QtGui.QWidget()
        self.tabAdvance.setObjectName("tabAdvance")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tabAdvance)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formAdvance = QtGui.QFormLayout()
        self.formAdvance.setObjectName("formAdvance")
        self.verticalLayout_3.addLayout(self.formAdvance)
        self.tabWidget.addTab(self.tabAdvance, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(CreatePluginDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.autostartBox = QtGui.QCheckBox(CreatePluginDialog)
        self.autostartBox.setChecked(True)
        self.autostartBox.setObjectName("autostartBox")
        self.verticalLayout.addWidget(self.autostartBox)

        self.retranslateUi(CreatePluginDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), CreatePluginDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), CreatePluginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CreatePluginDialog)

    def retranslateUi(self, CreatePluginDialog):
        CreatePluginDialog.setWindowTitle(QtGui.QApplication.translate("CreatePluginDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSimple), QtGui.QApplication.translate("CreatePluginDialog", "Simple", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAdvance), QtGui.QApplication.translate("CreatePluginDialog", "Advance", None, QtGui.QApplication.UnicodeUTF8))
        self.autostartBox.setText(QtGui.QApplication.translate("CreatePluginDialog", "Autostart", None, QtGui.QApplication.UnicodeUTF8))

