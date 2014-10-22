# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_dev/add_plugin.ui'
#
# Created: Wed Oct 22 17:00:03 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AddPlugin(object):
    def setupUi(self, AddPlugin):
        AddPlugin.setObjectName("AddPlugin")
        AddPlugin.resize(579, 558)
        self.buttonBox = QtGui.QDialogButtonBox(AddPlugin)
        self.buttonBox.setGeometry(QtCore.QRect(230, 510, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.treePlugin = QtGui.QTreeWidget(AddPlugin)
        self.treePlugin.setGeometry(QtCore.QRect(10, 10, 561, 171))
        self.treePlugin.setObjectName("treePlugin")
        self.formLayoutWidget = QtGui.QWidget(AddPlugin)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 190, 561, 62))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
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
        self.formLayoutWidget_2 = QtGui.QWidget(AddPlugin)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(10, 270, 561, 241))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.customFormLayout = QtGui.QFormLayout(self.formLayoutWidget_2)
        self.customFormLayout.setContentsMargins(0, 0, 0, 0)
        self.customFormLayout.setObjectName("customFormLayout")
        self.line = QtGui.QFrame(AddPlugin)
        self.line.setGeometry(QtCore.QRect(7, 250, 561, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")

        self.retranslateUi(AddPlugin)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AddPlugin.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AddPlugin.reject)
        QtCore.QMetaObject.connectSlotsByName(AddPlugin)

    def retranslateUi(self, AddPlugin):
        AddPlugin.setWindowTitle(QtGui.QApplication.translate("AddPlugin", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.treePlugin.headerItem().setText(0, QtGui.QApplication.translate("AddPlugin", "Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AddPlugin", "UName", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AddPlugin", "Path", None, QtGui.QApplication.UnicodeUTF8))

