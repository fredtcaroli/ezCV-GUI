from unittest import mock

import pytest
from PyQt5.QtCore import Qt

from ezcv.operator import get_available_operators
from ezcv.operator.implementations.blur import GaussianBlur
from ezcv_gui.widgets.pipeline import PipelineWidget, AddOperatorWidget


@pytest.fixture
def pipeline_widget(qtbot, controller):
    p = PipelineWidget(controller)
    qtbot.addWidget(p)
    p.resize(800, 600)
    p.show()
    return p


@pytest.fixture
def operators_list_widget(pipeline_widget):
    return pipeline_widget.operators_list


class TestOperatorsList:
    def test_start_empty(self, operators_list_widget):
        size = operators_list_widget.count()
        assert size == 0

    def test_add_operator(self, operators_list_widget, controller):
        controller.add_operator(GaussianBlur)
        size = operators_list_widget.count()
        assert size == 1

        operator_name = list(controller.operators.keys())[0]
        name_in_list = operators_list_widget.item(0).text()
        assert name_in_list == operator_name


def test_add_operator_button(qtbot, pipeline_widget):
    with qtbot.waitExposed(pipeline_widget.add_operator_popup, 100):
        qtbot.mouseClick(pipeline_widget.add_operator_button, Qt.LeftButton)


@pytest.fixture
def add_operator_widget(qtbot, controller):
    a = AddOperatorWidget(controller)
    qtbot.addWidget(a)
    a.resize(800, 600)
    a.show()
    return a


@pytest.fixture
def available_operators_list_widget(add_operator_widget):
    return add_operator_widget.available_operators_list


@pytest.fixture
def available_operators():
    return get_available_operators()


class TestAddOperatorPopup:
    def test_operators_list(self, available_operators_list_widget, available_operators):
        size = available_operators_list_widget.count()
        assert size == len(available_operators)

        expected_list = {cls.__name__ for cls in available_operators}
        actual_list = set()
        for i in range(size):
            name = available_operators_list_widget.item(i).text()
            actual_list.add(name)
        assert expected_list == actual_list

    def test_select_operator(self, qtbot, controller, available_operators_list_widget, available_operators):
        row = 1
        item = available_operators_list_widget.item(row)
        rect = available_operators_list_widget.visualItemRect(item)
        item_center = rect.center()

        expected_operator = next(op for op in available_operators if op.__name__ == item.text())

        with mock.patch.object(controller, 'add_operator') as m:
            qtbot.mouseClick(
                available_operators_list_widget.viewport(),
                Qt.LeftButton,
                pos=item_center,
                delay=100
            )
            qtbot.mouseDClick(
                available_operators_list_widget.viewport(),
                Qt.LeftButton,
                pos=item_center,
                delay=100
            )

        m.assert_called_with(expected_operator)
