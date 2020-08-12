from typing import Dict, Callable

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGroupBox, QLabel, QSizePolicy, QGridLayout

from ezcv.operator import Operator
from ezcv.operator.core.config import get_parameters_specs
from ezcv_gui.widgets.parameter import get_widget_for_parameter, ParameterWidgetMixin


class OperatorConfigWidget(QGroupBox):
    updated = pyqtSignal(str, object)

    def __init__(self, operator: Operator, parent=None):
        super().__init__(parent)
        self._operator = operator

        self.parameters_widgets: Dict[str, ParameterWidgetMixin] = dict()

        self.init_ui(operator)

    def init_ui(self, operator: Operator):
        layout = QGridLayout()
        self.setLayout(layout)

        self.setStyleSheet("""
        QGroupBox {
            font: bold;
            border: 1px solid silver;
            border-radius: 6px;
            margin-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 7px;
            padding: 0px 5px 0px 5px;
        }
        """)

        self._set_operator(operator)

    def _set_operator(self, operator: Operator):
        operator_type = type(operator)
        self.setTitle(type(operator).__name__)
        layout: QGridLayout = self.layout()
        params = get_parameters_specs(operator_type)

        for row_nb, (param_name, param) in enumerate(params.items()):
            param_widget = get_widget_for_parameter(param)
            param_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.parameters_widgets[param_name] = param_widget
            param_value = getattr(operator, param_name)
            param_widget.set_value(param_value)
            param_widget.value_changed.connect(self._create_parameter_updated_callback(param_name))
            label = QLabel(param_name)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(label, row_nb, 0)
            layout.addWidget(param_widget, row_nb, 1)

    def _create_parameter_updated_callback(self, param_name: str) -> Callable[[], None]:
        def callback():
            param_value = self.parameters_widgets[param_name].get_value()
            self.updated.emit(param_name, param_value)
        return callback
