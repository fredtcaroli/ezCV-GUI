from unittest import mock

import numpy as np

from ezcv.operator.implementations.blur import GaussianBlur
from ezcv.operator.implementations.color_space import ColorSpaceChange


class TestAddOperator:
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

    def test_emit_signal(self, controller, qtbot):
        with qtbot.waitSignal(controller.operators_changed, timeout=100):
            controller.add_operator(GaussianBlur)

    def test_process_media_if_available(self, controller, test_img):
        controller.curr_media = test_img
        with mock.patch.object(controller, 'process_curr_media') as m:
            controller.add_operator(GaussianBlur)
            m.assert_called_once()


class TestProcessCurrMedia:
    def test_call_pipeline_run(self, controller, test_img):
        controller.curr_media = test_img
        with mock.patch.object(controller.cvpipeline, 'run') as m:
            m.return_value = (test_img, None)
            controller.process_curr_media()
        m.assert_called_with(test_img)

    def test_emit_show_media_signal(self, qtbot, controller, test_img):
        controller.curr_media = test_img

        def on_media_show(img):
            assert img is test_img

        controller.show_media.connect(on_media_show)
        with qtbot.waitSignal(controller.show_media, timeout=100):
            controller.process_curr_media()

    def test_dont_process_media_if_not_available(self, controller):
        controller.curr_media = None
        with mock.patch.object(controller.cvpipeline, 'run') as m:
            controller.process_curr_media()
            m.assert_not_called()

    def test_dont_emit_show_media_if_curr_media_is_not_available(self, controller, qtbot):
        controller.curr_media = None

        called = False

        def on_media_show(_):
            nonlocal called
            called = True

        controller.show_media.connect(on_media_show)
        controller.process_curr_media()
        qtbot.wait(100)

        assert not called


class TestLoadMedia:
    def test_run_cvpipeline_on_loaded_media(self, controller, test_img_fname):
        with mock.patch.object(controller.cvpipeline, 'run') as m:
            m.side_effect = lambda i: (i, None)
            controller.load_media(test_img_fname)
        m.assert_called_once()

    def test_set_curr_media(self, controller, test_img_fname, test_img):
        controller.load_media(test_img_fname)
        assert np.all(np.isclose(controller.curr_media, test_img))

    def test_process_media(self, controller, test_img_fname):
        with mock.patch.object(controller, 'process_curr_media') as m:
            controller.load_media(test_img_fname)
        m.assert_called_once()


class TestUpdateOperator:
    def test_golden(self, controller):
        controller.add_operator(GaussianBlur)
        updated_value = 123
        controller.update_operator('GaussianBlur', 'kernel_size', updated_value)
        assert controller.operators['GaussianBlur'].kernel_size == updated_value

    def test_emit_operators_changed(self, controller, qtbot):
        controller.add_operator(GaussianBlur)
        with qtbot.waitSignal(controller.operators_changed, timeout=100):
            controller.update_operator('GaussianBlur', 'kernel_size', 123)
