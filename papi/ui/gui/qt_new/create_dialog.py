# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/create_dialog.ui'
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

class Ui_CreatePluginDialog(object):
    def setupUi(self, CreatePluginDialog):
        CreatePluginDialog.setObjectName(_fromUtf8("CreatePluginDialog"))
        CreatePluginDialog.resize(498, 384)
        self.verticalLayout = QtGui.QVBoxLayout(CreatePluginDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(CreatePluginDialog)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabSimple = QtGui.QWidget()
        self.tabSimple.setObjectName(_fromUtf8("tabSimple"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tabSimple)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.formSimple = QtGui.QFormLayout()
        self.formSimple.setObjectName(_fromUtf8("formSimple"))
        self.verticalLayout_2.addLayout(self.formSimple)
        self.tabWidget.addTab(self.tabSimple, _fromUtf8(""))
        self.tabAdvance = QtGui.QWidget()
        self.tabAdvance.setObjectName(_fromUtf8("tabAdvance"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tabAdvance)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.formAdvance = QtGui.QFormLayout()
        self.formAdvance.setObjectName(_fromUtf8("formAdvance"))
        self.verticalLayout_3.addLayout(self.formAdvance)
        self.tabWidget.addTab(self.tabAdvance, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(CreatePluginDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.autostartBox = QtGui.QCheckBox(CreatePluginDialog)
        self.autostartBox.setChecked(True)
        self.autostartBox.setObjectName(_fromUtf8("autostartBox"))
        self.verticalLayout.addWidget(self.autostartBox)

        self.retranslateUi(CreatePluginDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CreatePluginDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CreatePluginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CreatePluginDialog)

    def retranslateUi(self, CreatePluginDialog):
        CreatePluginDialog.setWindowTitle(_translate("CreatePluginDialog", "Dialog", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSimple), _translate("CreatePluginDialog", "Simple", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAdvance), _translate("CreatePluginDialog", "Advance", None))
        self.autostartBox.setText(_translate("CreatePluginDialog", "Autostart", None))

