# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/create.ui'
#
# Created: Mon Mar 16 16:42:19 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Create(object):
    def setupUi(self, Create):
        Create.setObjectName("Create")
        Create.resize(800, 601)
        self.centralwidget = QtGui.QWidget(Create)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pluginTree = QtGui.QTreeView(self.centralwidget)
        self.pluginTree.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.pluginTree.setObjectName("pluginTree")
        self.pluginTree.header().setCascadingSectionResizes(True)
        self.horizontalLayout.addWidget(self.pluginTree)
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setEnabled(False)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 385, 532))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.nameLabel)
        self.authorLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.authorLabel.setObjectName("authorLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.authorLabel)
        self.pathLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.pathLabel.setObjectName("pathLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.pathLabel)
        self.descriptionLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.descriptionLabel)
        self.descriptionText = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        self.descriptionText.setObjectName("descriptionText")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.descriptionText)
        self.nameEdit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.nameEdit.setObjectName("nameEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.nameEdit)
        self.authorEdit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.authorEdit.setObjectName("authorEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.authorEdit)
        self.pathEdit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.pathEdit.setObjectName("pathEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.pathEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.createButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.createButton.setObjectName("createButton")
        self.verticalLayout.addWidget(self.createButton)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        Create.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(Create)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        Create.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(Create)
        self.statusbar.setObjectName("statusbar")
        Create.setStatusBar(self.statusbar)

        self.retranslateUi(Create)
        QtCore.QMetaObject.connectSlotsByName(Create)

    def retranslateUi(self, Create):
        Create.setWindowTitle(QtGui.QApplication.translate("Create", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.nameLabel.setText(QtGui.QApplication.translate("Create", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.authorLabel.setText(QtGui.QApplication.translate("Create", "Author", None, QtGui.QApplication.UnicodeUTF8))
        self.pathLabel.setText(QtGui.QApplication.translate("Create", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.descriptionLabel.setText(QtGui.QApplication.translate("Create", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.createButton.setText(QtGui.QApplication.translate("Create", "Create Plugin", None, QtGui.QApplication.UnicodeUTF8))

