# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/create_dialog.ui'
#
# Created: Tue Oct 28 15:54:38 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_CreatePluginDialog(object):
    def setupUi(self, CreatePluginDialog):
        CreatePluginDialog.setObjectName("CreatePluginDialog")
        CreatePluginDialog.resize(400, 288)
        self.buttonBox = QtGui.QDialogButtonBox(CreatePluginDialog)
        self.buttonBox.setGeometry(QtCore.QRect(220, 250, 176, 27))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayoutWidget = QtGui.QWidget(CreatePluginDialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(9, 9, 381, 241))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.autostartBox = QtGui.QCheckBox(CreatePluginDialog)
        self.autostartBox.setGeometry(QtCore.QRect(10, 250, 97, 22))
        self.autostartBox.setChecked(True)
        self.autostartBox.setObjectName("autostartBox")

        self.retranslateUi(CreatePluginDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), CreatePluginDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), CreatePluginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CreatePluginDialog)

    def retranslateUi(self, CreatePluginDialog):
        CreatePluginDialog.setWindowTitle(QtGui.QApplication.translate("CreatePluginDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.autostartBox.setText(QtGui.QApplication.translate("CreatePluginDialog", "Autostart", None, QtGui.QApplication.UnicodeUTF8))

