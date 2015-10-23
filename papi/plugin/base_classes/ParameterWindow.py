__author__ = 'fescycling'

from PyQt5.QtWidgets    import QLineEdit, QMainWindow, QMenu, QAbstractItemView, QAction, QTreeView, QVBoxLayout
from PyQt5.QtCore import Qt, QRegExp

from papi.gui.default.item import DParameterTreeModel, DParameterTreeItem

class ParameterWindow(QMainWindow):

    def __init__(self, dplugin, api ,parent = None):
        QMainWindow.__init__(self, parent)

        self.parameterTree = QTreeView(self)
        self.parameterTree.setObjectName("parameterTree")

        self.setCentralWidget(self.parameterTree)

        self.dparameterModel = DParameterTreeModel()
        self.dparameterModel.setHorizontalHeaderLabels(['Name',''])
        self.parameterTree.setModel(self.dparameterModel)
        self.parameterTree.setUniformRowHeights(True)

        self.dparameterModel.dataChanged.connect(self.data_changed_parameter_model)

        self.dpluign_object = dplugin
        self.api = api

    def show_paramters(self, para_list):
        for dparameter_name in sorted(para_list):
            dparameter = para_list[dparameter_name]
            dparameter_item = DParameterTreeItem(dparameter)
            self.dparameterModel.appendRow(dparameter_item)
            self.parameterTree.resizeColumnToContents(0)
            self.parameterTree.resizeColumnToContents(1)

        self.parameterTree.expandAll()

    def data_changed_parameter_model(self, index, n):
        """
        This function is called when a dparameter value is changed by editing the 'value'-column.

        :param index: Index of current changed dparameter
        :param n: None
        :return:
        """

        dparameter = self.parameterTree.model().data(index, Qt.UserRole)

        self.api.do_set_parameter(self.dpluign_object.id, dparameter.name, dparameter.value)
