# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/create.ui'
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

class Ui_Create(object):
    def setupUi(self, Create):
        Create.setObjectName(_fromUtf8("Create"))
        Create.resize(800, 601)
        self.centralwidget = QtGui.QWidget(Create)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pluginTree = QtGui.QTreeView(self.centralwidget)
        self.pluginTree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.pluginTree.setObjectName(_fromUtf8("pluginTree"))
        self.pluginTree.header().setCascadingSectionResizes(True)
        self.horizontalLayout.addWidget(self.pluginTree)
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setEnabled(False)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 385, 532))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.nameLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.nameLabel.setObjectName(_fromUtf8("nameLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.nameLabel)
        self.authorLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.authorLabel.setObjectName(_fromUtf8("authorLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.authorLabel)
        self.pathLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.pathLabel.setObjectName(_fromUtf8("pathLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.pathLabel)
        self.descriptionLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.descriptionLabel.setObjectName(_fromUtf8("descriptionLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.descriptionLabel)
        self.descriptionText = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        self.descriptionText.setObjectName(_fromUtf8("descriptionText"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.descriptionText)
        self.nameEdit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.nameEdit.setObjectName(_fromUtf8("nameEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.nameEdit)
        self.authorEdit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.authorEdit.setObjectName(_fromUtf8("authorEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.authorEdit)
        self.pathEdit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.pathEdit.setObjectName(_fromUtf8("pathEdit"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.pathEdit)
        self.modulesLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.modulesLabel.setObjectName(_fromUtf8("modulesLabel"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.modulesLabel)
        self.modulesList = QtGui.QListWidget(self.scrollAreaWidgetContents)
        self.modulesList.setObjectName(_fromUtf8("modulesList"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.modulesList)
        self.verticalLayout.addLayout(self.formLayout)
        self.createButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.createButton.setObjectName(_fromUtf8("createButton"))
        self.verticalLayout.addWidget(self.createButton)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        Create.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(Create)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        Create.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(Create)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        Create.setStatusBar(self.statusbar)

        self.retranslateUi(Create)
        QtCore.QMetaObject.connectSlotsByName(Create)

    def retranslateUi(self, Create):
        Create.setWindowTitle(_translate("Create", "MainWindow", None))
        self.nameLabel.setText(_translate("Create", "Name", None))
        self.authorLabel.setText(_translate("Create", "Author", None))
        self.pathLabel.setText(_translate("Create", "Path", None))
        self.descriptionLabel.setText(_translate("Create", "Description", None))
        self.modulesLabel.setText(_translate("Create", "Missing\n"
"Modules", None))
        self.createButton.setText(_translate("Create", "Create Plugin", None))

