from enum import Enum
from typing import Dict, Type, Callable, Union, TypeVar, Generic

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QSlider, QHBoxLayout, QComboBox, QVBoxLayout, QLabel, QSpinBox, \
    QDoubleSpinBox, QSizePolicy, QCheckBox

from ezcv.operator import ParameterSpec, IntegerParameter, DoubleParameter, EnumParameter, BooleanParameter


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


class _SliderWithIntervalSize(QSlider):
    """ Copied from https://stackoverflow.com/questions/4827885/qslider-stepping"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._min = 0
        self._max = 99
        self.interval = 1

    def setValue(self, value: int):
        index = round((value - self._min) / self.interval)
        return super().setValue(index)

    def value(self):
        return super().value() * self.interval + self._min

    def setMinimum(self, value):
        self._min = value
        self._range_adjusted()

    def setMaximum(self, value):
        self._max = value
        self._range_adjusted()

    def setInterval(self, value: int):
        # To avoid division by zero
        if value == 0:
            raise ValueError('Interval can\'t be zero')
        self.interval = value
        self._range_adjusted()

    def _range_adjusted(self):
        number_of_steps = int((self._max - self._min) / self.interval)
        super().setMaximum(number_of_steps)


class _SliderWithMinMaxDisplay(QWidget):
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._slider = _SliderWithIntervalSize(Qt.Orientation.Horizontal, self)
        self._slider.valueChanged.connect(self.valueChanged.emit)
        self._label_minimum = QLabel(str(self._slider.minimum()), parent=parent)
        self._label_minimum.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._label_maximum = QLabel(str(self._slider.maximum()), parent=parent)

        self.init_ui()

    def init_ui(self):
        self._slider.setTickPosition(QSlider.TickPosition.NoTicks)
        self._slider.setMinimumWidth(100)
        self._label_minimum.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._label_maximum.setAlignment(Qt.AlignmentFlag.AlignRight)

        main_layout = QVBoxLayout()
        slider_hbox = QHBoxLayout()
        slider_hbox.setContentsMargins(0, 0, 0, 0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._slider)
        main_layout.addLayout(slider_hbox)
        slider_hbox.addWidget(self._label_minimum, Qt.AlignmentFlag.AlignLeft)
        slider_hbox.addWidget(self._label_maximum, Qt.AlignmentFlag.AlignRight)

        self.setLayout(main_layout)

    def setMinimum(self, value: int) -> None:
        self._slider.setMinimum(value)
        self._label_minimum.setText(str(value))

    def setMaximum(self, value: int) -> None:
        self._slider.setMaximum(value)
        self._label_maximum.setText(str(value))

    def setValue(self, value: int):
        self._slider.setValue(value)

    def setInterval(self, step_size: int):
        self._slider.setInterval(step_size)

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
    number_display: Union[QSpinBox, QDoubleSpinBox]

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
        self.slider.setInterval(param.step_size)

        self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.slider.valueChanged.connect(self.on_slider_value_changed)

    def init_number_display(self, param: _T):
        self.number_display = self.get_number_display()
        self.number_display. setMinimum(param.lower)
        self.number_display.setMaximum(param.upper)
        self.number_display.setSingleStep(param.step_size)

        self.number_display.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

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


@param_widget(BooleanParameter)
class BooleanParameterWidget(ParameterWidgetMixin, QCheckBox):
    def init_ui(self, param: BooleanParameter):
        self.stateChanged.connect(self._on_state_changed)

    def set_value(self, value: bool):
        check_state = Qt.CheckState.Checked if value else Qt.CheckState.Unchecked
        self.setCheckState(check_state)

    def get_value(self) -> bool:
        return self.checkState().value == Qt.CheckState.Checked.value

    def _on_state_changed(self, state: Enum):
        self.value_changed.emit()
