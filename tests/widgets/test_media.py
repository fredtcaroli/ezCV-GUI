from unittest import mock

import numpy as np
import pytest
from PyQt5.QtCore import Qt

from ezcv.test_utils import parametrize_img
from ezcv_gui.widgets.media import MediaWidget


@pytest.fixture
def media_widget(qtbot, controller):
    w = MediaWidget(controller)
    qtbot.addWidget(w)
    w.resize(800, 600)
    w.show()
    return w


@parametrize_img
def test_media_widget_media_processed_signal(controller, media_widget, img):
    controller.show_media.emit(img)
    pix = media_widget.media_shower.pixmap()
    qimg = pix.toImage()
    if img.ndim == 2:
        img = np.repeat(img[..., None], 3, axis=2)
    channels_count = 4
    b = qimg.bits()
    b.setsize(qimg.height() * qimg.width() * channels_count)
    arr = np.frombuffer(b, np.uint8).reshape((qimg.height(), qimg.width(), channels_count))
    assert np.all(np.isclose(img, arr[..., :3]))


def test_media_widget_pick_file_button_triggers_pick_file_widget(qtbot, media_widget, test_img_fname):
    with mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName') as m:
        m.return_value = (test_img_fname, None)
        qtbot.mouseClick(media_widget.pick_file_button, Qt.LeftButton)
        m.assert_called_once()


def test_media_widget_pick_file_button_triggers_show_media(qtbot, media_widget, controller, test_img_fname):
    with qtbot.waitSignal(controller.show_media, 1000), \
         mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                    mock.Mock(return_value=(test_img_fname, None))):
        qtbot.mouseClick(media_widget.pick_file_button, Qt.LeftButton)


def test_media_widget_pick_file_button_cancel_QFileDialog(qtbot, media_widget, controller):
    loaded = False

    def on_new_media_loaded(img):
        nonlocal loaded
        loaded = True

    controller.show_media.connect(on_new_media_loaded)
    with mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName') as m:
        m.return_value = ('', None)
        qtbot.mouseClick(media_widget.pick_file_button, Qt.LeftButton)
        qtbot.wait(1000)

    assert not loaded
