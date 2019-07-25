from PyQt5.QtCore import QRect, QModelIndex
from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QVBoxLayout

from ezcv.operator import get_available_operators, Operator
from ezcv_gui.controller import EzCVController


class PipelineWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self.operators_list = QListWidget(self)
        self.add_operator_button = QPushButton('Add Operator', self)
        self.add_operator_popup = AddOperatorPopup(self._controller)

        self.add_operator_button.clicked.connect(self.on_add_operator_button_click)
        self._controller.operators_updated.connect(self.on_operators_updated)

        self.initUi()

    def initUi(self):
        layout = QVBoxLayout(self)

        layout.addWidget(self.add_operator_button)
        layout.addWidget(self.operators_list)

    def on_add_operator_button_click(self):
        self.add_operator_popup.show()

    def on_operators_updated(self):
        self.operators_list.clear()
        self.operators_list.addItems(self._controller.operators.keys())


class AddOperatorPopup(QWidget):
    def __init__(self, controller: EzCVController):
        super().__init__()
        self._controller = controller

        self.operators = {cls.__name__: cls for cls in get_available_operators()}

        self.operators_list = QListWidget(self)
        self.operators_list.addItems(self.operators.keys())

        self.operators_list.doubleClicked.connect(self.on_operator_selected)

    def on_operator_selected(self, index: QModelIndex):
        selected_operator = self.operators[index.data()]
        self._controller.add_operator(selected_operator)
        self.hide()