import pytest

from ezcv_gui.widgets.operator import OperatorConfigWidget


@pytest.fixture
def operator_config_widget(qtbot, controller):
    o = OperatorConfigWidget(controller)
    qtbot.addWidget(o)
    o.resize(800, 600)
    o.show()
    return o
