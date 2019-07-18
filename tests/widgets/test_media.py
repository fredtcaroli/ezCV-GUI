import numpy as np

from ezcv.test_utils import parametrize_img
from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.media import MediaWidget


def test_media_widget_instantiation(qtbot):
    media = MediaWidget(EzCVController())
    assert media is not None


def test_media_widget_shower_is_not_none(qtbot):
    media = MediaWidget(EzCVController())
    assert media.media_shower is not None


@parametrize_img
def test_media_widget_media_updated_signal(qtbot, img):
    controller = EzCVController()
    media = MediaWidget(controller)
    controller.media_updated.emit(img)
    pix = media.media_shower.pixmap()
    qimg = pix.toImage()
    if img.ndim == 2:
        img = np.repeat(img[..., None], 3, axis=2)
    channels_count = 4
    b = qimg.bits()
    b.setsize(qimg.height() * qimg.width() * channels_count)
    arr = np.frombuffer(b, np.uint8).reshape((qimg.height(), qimg.width(), channels_count))
    assert np.all(np.isclose(img, arr[..., :3]))
