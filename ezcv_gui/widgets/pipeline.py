from typing import List, Callable, Any

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QWidget, QListWidget, QPushButton, QVBoxLayout, QDialogButtonBox, QTabWidget, QStyle, \
    QHBoxLayout, QInputDialog

from ezcv.operator import get_available_operators
from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.operator import OperatorConfigWidget


class PipelineWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self.operators_tabs = OperatorsTabsWidget(self._controller, parent=self)
        self.add_operator_button = QPushButton('Add Operator', parent=self)
        self.move_operator_right_button = QPushButton(parent=self)
        self.move_operator_left_button = QPushButton(parent=self)
        self.add_operator_popup = AddOperatorWidget(self._controller)

        self.add_operator_button.clicked.connect(self.on_add_operator_button_click)
        self.add_operator_button.setShortcut("A")
        self.move_operator_left_button.clicked.connect(self.on_move_operator_left)
        self.move_operator_right_button.clicked.connect(self.on_move_operator_right)
        self._controller.operators_list_updated.connect(self.operators_tabs.refresh)

        self.init_ui()

    def init_ui(self):
        self.move_operator_left_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowLeft)
        )
        self.move_operator_right_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        )
        layout = QVBoxLayout(self)

        operators_management_layout = QHBoxLayout(self)
        operators_management_layout.addWidget(self.move_operator_left_button, alignment=Qt.AlignmentFlag.AlignLeft)
        operators_management_layout.addWidget(self.add_operator_button, alignment=Qt.AlignmentFlag.AlignCenter)
        operators_management_layout.addWidget(self.move_operator_right_button, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(operators_management_layout)
        layout.addWidget(self.operators_tabs)

        self.setLayout(layout)

    def on_add_operator_button_click(self):
        self.add_operator_popup.show()

    def on_move_operator_left(self):
        selected_operator = self.operators_tabs.currentIndex()
        if selected_operator <= 0:
            return
        target = selected_operator - 1
        self._controller.move_operator(selected_operator, target)
        self.operators_tabs.setCurrentIndex(target)

    def on_move_operator_right(self):
        selected_operator = self.operators_tabs.currentIndex()
        if selected_operator == -1 or selected_operator == self.operators_tabs.count() - 1:
            return
        target = selected_operator + 1
        self._controller.move_operator(selected_operator, target)
        self.operators_tabs.setCurrentIndex(target)


class OperatorsTabsWidget(QTabWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.on_tab_close_requested)
        self.tabBarDoubleClicked.connect(self.on_tab_bar_double_clicked)

        self.operators_config_widgets: List[OperatorConfigWidget] = list()

    def on_tab_close_requested(self, index: int):
        self._controller.remove_operator(index)

    def on_tab_bar_double_clicked(self, index: int):
        curr_name = self._controller.get_operator_name(index)
        if curr_name is None:
            return
        new_name, ok = QInputDialog.getText(self, 'Edit Operator Name', 'Operator name:', text=curr_name)
        if ok:
            self._controller.rename_operator(index, new_name)

    def refresh(self):
        curr_idx = self.currentIndex()
        self._clear_tabs()
        self._create_tabs()
        select_index = max(min(curr_idx, len(self._controller.operators) - 1), 0)
        self.setCurrentIndex(select_index)

    def _clear_tabs(self):
        for i, operator_config_widget in enumerate(self.operators_config_widgets):
            operator_config_widget.setParent(None)
        self.operators_config_widgets = list()
        self.clear()

    def _create_tabs(self):
        operators = self._controller.operators
        for operator_name, operator in operators.items():
            op_config_widget = OperatorConfigWidget(operator)
            self.addTab(op_config_widget, operator_name)
            op_config_widget.updated.connect(self._create_operator_updated_callback(operator_name))
            self.operators_config_widgets.append(op_config_widget)

    def _create_operator_updated_callback(self, operator_name: str) -> Callable[[], None]:
        def callback(param_name: str, param_value: Any):
            self._controller.update_operator_parameter(operator_name, param_name, param_value)
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
