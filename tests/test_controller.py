import numpy as np

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
