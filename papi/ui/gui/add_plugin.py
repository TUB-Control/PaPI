# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/add_plugin.ui'
#
# Created: Tue Sep 16 10:43:03 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AddPlugin(object):
    def setupUi(self, AddPlugin):
        AddPlugin.setObjectName("AddPlugin")
        AddPlugin.resize(582, 416)
        self.buttonBox = QtGui.QDialogButtonBox(AddPlugin)
        self.buttonBox.setGeometry(QtCore.QRect(230, 380, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.treePlugin = QtGui.QTreeWidget(AddPlugin)
        self.treePlugin.setGeometry(QtCore.QRect(10, 10, 561, 171))
        self.treePlugin.setObjectName("treePlugin")
        self.formLayoutWidget = QtGui.QWidget(AddPlugin)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 190, 561, 181))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.le_uname = QtGui.QLineEdit(self.formLayoutWidget)
        self.le_uname.setObjectName("le_uname")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.le_uname)
        self.label_2 = QtGui.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.le_path = QtGui.QLineEdit(self.formLayoutWidget)
        self.le_path.setReadOnly(True)
        self.le_path.setObjectName("le_path")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.le_path)

        self.retranslateUi(AddPlugin)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AddPlugin.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AddPlugin.reject)
        QtCore.QMetaObject.connectSlotsByName(AddPlugin)

    def retranslateUi(self, AddPlugin):
        AddPlugin.setWindowTitle(QtGui.QApplication.translate("AddPlugin", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.treePlugin.headerItem().setText(0, QtGui.QApplication.translate("AddPlugin", "Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AddPlugin", "UName", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AddPlugin", "Path", None, QtGui.QApplication.UnicodeUTF8))

