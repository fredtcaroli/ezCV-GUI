from unittest import mock

import numpy as np

from ezcv.operator.implementations.blur import GaussianBlur
from ezcv.operator.implementations.color_space import ColorSpaceChange
from ezcv.test_utils import build_img
from ezcv_gui.controller import EzCVController


class TestControllerOperators:
    def test_add_operator_call(self, controller):
        with mock.patch('ezcv.CompVizPipeline.add_operator') as m:
            controller.add_operator(GaussianBlur)
        m.assert_called_once()

    def test_operators_list(self, controller):
        controller.add_operator(GaussianBlur)
        operators = list(controller.operators.values())
        assert len(operators) == 1
        assert isinstance(operators[0], GaussianBlur)

    def test_add_multiple_operators(self, controller):
        controller.add_operator(GaussianBlur)
        controller.add_operator(ColorSpaceChange)

        operators = list(controller.operators.values())
        assert len(operators) == 2
        assert isinstance(operators[0], GaussianBlur)
        assert isinstance(operators[1], ColorSpaceChange)

    def test_add_same_operator_twice(self, controller):
        controller.add_operator(GaussianBlur)
        controller.add_operator(GaussianBlur)

        operators = list(controller.operators.values())
        assert len(operators) == 2
        assert operators[0] != operators[1]


def test_controller_run_cvpipeline_on_new_media_loaded(test_img_fname):
    controller = EzCVController()
    with mock.patch('ezcv.CompVizPipeline.run') as m:
        m.side_effect = lambda i: (i, None)
        controller.load_media(test_img_fname)
    m.assert_called_once()


def test_controller_new_media_loaded_emits_show_media(qtbot, test_img_fname):
    controller = EzCVController()
    with qtbot.waitSignal(controller.show_media, 1000):
        controller.load_media(test_img_fname)


def test_controller_new_media_loaded_emits_media_updated_with_run_return_value(test_img_fname):
    controller = EzCVController()
    output_img = build_img((4, 4), rgb=True, kind='random')

    all_okay = False

    def slot(img: np.ndarray):
        nonlocal all_okay
        all_okay = img is output_img

    controller.show_media.connect(slot)
    with mock.patch('ezcv.CompVizPipeline.run') as m:
        m.return_value = (output_img, None)
        controller.load_media(test_img_fname)

    assert all_okay
