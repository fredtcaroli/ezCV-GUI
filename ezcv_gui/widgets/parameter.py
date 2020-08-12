from typing import Dict, Type, Callable, Union, TypeVar, Generic

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLineEdit, QSlider, QHBoxLayout, QComboBox, QVBoxLayout, QLabel, QSpinBox, \
    QDoubleSpinBox, QAbstractSpinBox, QSizePolicy

from ezcv.operator import ParameterSpec, IntegerParameter, DoubleParameter, EnumParameter


class ParameterWidgetMixin:
    value_changed = pyqtSignal()

    def __init__(self, param: ParameterSpec, parent=None):
        super().__init__(parent)
        self.init_ui(param)

    def init_ui(self, param: ParameterSpec):
        raise NotImplementedError()

    def set_value(self, value):
        raise NotImplementedError()

    def get_value(self):
        raise NotImplementedError()


_PARAM2WIDGET: Dict[Type[ParameterSpec], Type[ParameterWidgetMixin]] = dict()


ParameterWidget = Union[QWidget, ParameterWidgetMixin]


def param_widget(param_type: Type[ParameterSpec]) -> Callable[[Type[ParameterWidget]], Type[ParameterWidget]]:
    """ Decorator for registering new param widget factories
    """
    def decorator(c: Type[ParameterWidgetMixin]) -> Type[ParameterWidgetMixin]:
        _PARAM2WIDGET[param_type] = c
        return c
    return decorator


def get_widget_for_parameter(param: ParameterSpec) -> ParameterWidget:
    param_type = type(param)
    if param_type not in _PARAM2WIDGET:
        raise ValueError(f"No parameter widget factory for {param_type}")
    widget = _PARAM2WIDGET[param_type]
    return widget(param)


class _SliderWithMinMaxDisplay(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.valueChanged.connect(self.valueChanged.emit)
        self._label_minimum = QLabel(str(self._slider.minimum()), parent=parent, alignment=Qt.AlignLeft)
        self._label_maximum = QLabel(str(self._slider.maximum()), parent=parent, alignment=Qt.AlignRight)

        self.init_ui()

    def init_ui(self):
        self._slider.setTickPosition(QSlider.NoTicks)
        self._slider.setSingleStep(1)
        self._slider.setMinimumWidth(100)

        main_layout = QVBoxLayout()
        slider_hbox = QHBoxLayout()
        slider_hbox.setContentsMargins(0, 0, 0, 0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._slider)
        main_layout.addLayout(slider_hbox)
        slider_hbox.addWidget(self._label_minimum, Qt.AlignLeft)
        slider_hbox.addWidget(self._label_maximum, Qt.AlignRight)

        self.setLayout(main_layout)

    def setMinimum(self, value: int) -> None:
        self._slider.setMinimum(value)
        self._label_minimum.setText(str(value))

    def setMaximum(self, value: int) -> None:
        self._slider.setMaximum(value)
        self._label_maximum.setText(str(value))

    def setValue(self, value: int):
        self._slider.setValue(value)

    def value(self):
        return self._slider.value()


class _DoubleSliderWithMinMaxDisplay(_SliderWithMinMaxDisplay):
    def value(self):
        return self._slider.value() / 100

    def setValue(self, value: float):
        self._slider.setValue(int(value * 100))

    def setMinimum(self, value: float):
        self._slider.setMinimum(int(value * 100))
        self._label_minimum.setText('%.2f' % value)

    def setMaximum(self, value: float):
        self._slider.setMaximum(int(value * 100))
        self._label_maximum.setText('%.2f' % value)

    def minimum(self) -> float:
        return self._slider.minimum() / 100

    def maximum(self) -> float:
        return self._slider.maximum() / 100


_T = TypeVar('_T', IntegerParameter, DoubleParameter)


class NumberParamWidgetBase(Generic[_T], ParameterWidgetMixin, QWidget):
    slider: _SliderWithMinMaxDisplay
    number_display: QAbstractSpinBox

    def init_ui(self, param: _T):
        self.init_slider(param)
        self.init_number_display(param)

        layout = QHBoxLayout(self)
        layout.addWidget(self.slider, stretch=4)
        layout.addWidget(self.number_display, stretch=1)
        layout.setSpacing(20)
        self.setLayout(layout)

    def init_slider(self, param: _T):
        self.slider = self.get_slider()
        self.slider.setMinimum(param.lower)
        self.slider.setMaximum(param.upper)

        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.slider.valueChanged.connect(self.on_slider_value_changed)

    def init_number_display(self, param: _T):
        self.number_display = self.get_number_display()
        self.number_display.setMinimum(param.lower)
        self.number_display.setMaximum(param.upper)

        self.number_display.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.number_display.valueChanged.connect(self.on_number_display_changed)

    def on_slider_value_changed(self):
        self.number_display.setValue(self.slider.value())
        self.value_changed.emit()

    def on_number_display_changed(self, value):
        self.slider.setValue(value)

    def set_value(self, value):
        self.slider.setValue(value)
        self.number_display.setValue(value)

    def get_value(self):
        return self.slider.value()

    def get_slider(self):
        raise NotImplementedError()

    def get_number_display(self):
        raise NotImplementedError()


@param_widget(IntegerParameter)
class IntegerParamWidget(NumberParamWidgetBase[IntegerParameter]):
    def get_slider(self):
        return _SliderWithMinMaxDisplay()

    def get_number_display(self):
        return QSpinBox()


@param_widget(DoubleParameter)
class DoubleParamWidget(NumberParamWidgetBase[DoubleParameter]):
    def get_slider(self):
        return _DoubleSliderWithMinMaxDisplay()

    def get_number_display(self):
        spin_box = QDoubleSpinBox()
        spin_box.setDecimals(2)
        spin_box.setSingleStep(0.01)
        return spin_box


@param_widget(EnumParameter)
class EnumParameterWidget(ParameterWidgetMixin, QComboBox):
    def init_ui(self, param: EnumParameter):
        for value in param.possible_values:
            self.addItem(value)
        self.currentTextChanged.connect(self.value_changed.emit)
        self.show()

    def set_value(self, value: str):
        self.setCurrentText(value)

    def get_value(self) -> str:
        return self.currentText()
