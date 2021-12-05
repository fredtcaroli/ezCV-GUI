from typing import List, Callable, Any

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QWidget, QListWidget, QPushButton, QVBoxLayout, QDialogButtonBox, QTabWidget

from ezcv.operator import get_available_operators
from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.operator import OperatorConfigWidget


class PipelineWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self.operators_tabs = QTabWidget(self)
        self.operators_tabs.setTabsClosable(True)
        self.operators_tabs.tabCloseRequested.connect(self.on_tab_close_requested)
        self.add_operator_button = QPushButton('Add Operator', parent=self)
        self.add_operator_popup = AddOperatorWidget(self._controller)

        self.add_operator_button.clicked.connect(self.on_add_operator_button_click)
        self.add_operator_button.setShortcut("A")
        self._controller.operators_changed.connect(self.on_operators_changed)

        self.operators_config_widgets: List[OperatorConfigWidget] = list()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(self.add_operator_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.operators_tabs)

        self.setLayout(layout)

    def on_add_operator_button_click(self):
        self.add_operator_popup.show()

    def on_operators_changed(self):
        curr_idx = self.operators_tabs.currentIndex()
        self._clear_tabs()
        self._create_tabs()
        select_index = max(min(curr_idx, len(self._controller.operators) - 1), 0)
        self.operators_tabs.setCurrentIndex(select_index)

    def on_tab_close_requested(self, index: int):
        self._controller.remove_operator(index)

    def _clear_tabs(self):
        for i, operator_config_widget in enumerate(self.operators_config_widgets):
            operator_config_widget.setParent(None)
        self.operators_config_widgets = list()
        self.operators_tabs.clear()

    def _create_tabs(self):
        operators = self._controller.operators
        for operator_name, operator in operators.items():
            op_config_widget = OperatorConfigWidget(operator)
            self.operators_tabs.addTab(op_config_widget, operator_name)
            op_config_widget.updated.connect(self._create_operator_updated_callback(operator_name))
            self.operators_config_widgets.append(op_config_widget)

    def _create_operator_updated_callback(self, operator_name: str) -> Callable[[], None]:
        def callback(param_name: str, param_value: Any):
            self._controller.update_operator(operator_name, param_name, param_value)
        return callback


class AddOperatorWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._controller = controller
        self.operators = {cls.__name__: cls for cls in get_available_operators()}

        self.available_operators_list = QListWidget(self)
        self.available_operators_list.doubleClicked.connect(self.accept_operator)
        self.available_operators_list.installEventFilter(self)

        self.button_box = QDialogButtonBox()
        self.button_box.addButton("Ok", QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
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
        if event.type() == QEvent.Type.KeyPress:
            if event.matches(QKeySequence.StandardKey.InsertParagraphSeparator):
                self.accept_operator()
            elif event.matches(QKeySequence.StandardKey.Cancel):
                self.hide()
        return False
