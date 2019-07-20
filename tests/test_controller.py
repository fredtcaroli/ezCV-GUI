from unittest import mock

import numpy as np

from ezcv.pipeline import PipelineContext
from ezcv.test_utils import build_img
from ezcv_gui.controller import EzCVController


def test_controller_instantiation():
    controller = EzCVController()
    assert controller is not None


def test_controller_media_updated_signal():
    controller = EzCVController()

    all_good = False
    img = np.zeros((3, 3), dtype='uint8')

    def slot(x):
        nonlocal all_good
        all_good = x is img

    controller.media_updated.connect(slot)
    controller.media_updated.emit(img)
    assert all_good


def test_controller_new_media_loaded_signal():
    controller = EzCVController()

    all_good = False
    img = np.zeros((3, 3), dtype='uint8')

    def slot(x):
        nonlocal all_good
        all_good = x is img

    controller.new_media_loaded.connect(slot)
    controller.new_media_loaded.emit(img)
    assert all_good


def test_controller_has_cvpipeline():
    controller = EzCVController()
    assert controller.cvpipeline is not None


def test_controller_run_cvpipeline_on_new_media_loaded():
    controller = EzCVController()
    img = build_img((4, 4), rgb=True)
    with mock.patch('ezcv.CompVizPipeline.run',
                    mock.MagicMock(return_value=(img, None))) as m:
        controller.new_media_loaded.emit(img)
    m.assert_called_once()


def test_controller_new_media_loaded_emits_media_updated(qtbot):
    controller = EzCVController()
    img = build_img((4, 4), rgb=True)
    with qtbot.waitSignal(controller.media_updated, 1000):
        controller.new_media_loaded.emit(img)


def test_controller_new_media_loaded_emits_media_updated_with_run_return_value():
    controller = EzCVController()
    input_img = build_img((4, 4), rgb=True)
    output_img = build_img((4, 4), rgb=True, kind='random')
    ctx = PipelineContext(input_img)

    all_okay = False

    def slot(img: np.ndarray):
        nonlocal all_okay
        all_okay = img is output_img

    controller.media_updated.connect(slot)
    with mock.patch('ezcv.CompVizPipeline.run',
                    mock.MagicMock(return_value=(output_img, ctx))):
        controller.new_media_loaded.emit(input_img)

    assert all_okay
