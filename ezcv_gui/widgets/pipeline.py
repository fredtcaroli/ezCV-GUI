from typing import List, Callable, Any

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QVBoxLayout, QDialogButtonBox, QTabWidget

from ezcv.operator import get_available_operators
from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.operator import OperatorConfigWidget


class PipelineWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self.operators_tabs = QTabWidget(self)
        self.add_operator_button = QPushButton('Add Operator', parent=self)
        self.add_operator_popup = AddOperatorWidget(self._controller)

        self.add_operator_button.clicked.connect(self.on_add_operator_button_click)
        self.add_operator_button.setShortcut("A")
        self._controller.operators_changed.connect(self.on_operators_changed)

        self.operators_config_widgets: List[OperatorConfigWidget] = list()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(self.add_operator_button, alignment=Qt.AlignHCenter)
        layout.addWidget(self.operators_tabs)

        self.setLayout(layout)

    def on_add_operator_button_click(self):
        self.add_operator_popup.show()

    def on_operators_changed(self):
        for operator_config_widget in self.operators_config_widgets:
            operator_config_widget.setParent(None)
        self.operators_tabs.clear()

        for operator_name, operator in self._controller.operators.items():
            op_config_widget = OperatorConfigWidget(operator)
            self.operators_tabs.addTab(op_config_widget, operator_name)
            op_config_widget.updated.connect(self._create_operator_updated_callback(operator_name))

    def _create_operator_updated_callback(self, operator_name: str) -> Callable[[], None]:
        def callback(param_name: str, param_value: Any):
            self._controller.update_operator(operator_name, param_name, param_value)
        return callback


class AddOperatorWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self._controller = controller
        self.operators = {cls.__name__: cls for cls in get_available_operators()}

        self.available_operators_list = QListWidget(self)
        self.available_operators_list.doubleClicked.connect(self.accept_operator)
        self.available_operators_list.installEventFilter(self)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_operator)
        self.button_box.rejected.connect(self.hide)

        self.init_ui()

    def init_ui(self):
        self.resize(300, 400)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.available_operators_list, stretch=5)
        main_layout.addWidget(self.button_box, stretch=1)

        self.available_operators_list.addItems(self.operators.keys())
        self.available_operators_list.setCurrentRow(0)

    def accept_operator(self):
        selected_item = self.available_operators_list.currentItem().text()
        selected_operator = self.operators[selected_item]
        self._controller.add_operator(selected_operator)
        self.hide()

    def eventFilter(self, watched, event):
        """ Catch ENTER and ESC key presses
        """
        if event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.InsertParagraphSeparator):
                self.accept_operator()
            elif event.matches(QKeySequence.Cancel):
                self.hide()
        return False
