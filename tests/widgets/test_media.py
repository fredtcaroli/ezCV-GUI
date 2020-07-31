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
def test_show_media(controller, media_widget, img):
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


class TestFilePopup:
    def test_dialog_call(self, qtbot, media_widget, test_img_fname):
        with mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName') as m:
            m.return_value = (test_img_fname, None)
            qtbot.mouseClick(media_widget.pick_file_button, Qt.LeftButton)
            m.assert_called_once()

    def test_load_media(self, qtbot, media_widget, controller, test_img_fname):
        with mock.patch.object(controller, 'load_media') as m:
            with mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                            mock.Mock(return_value=(test_img_fname, None))):
                qtbot.mouseClick(media_widget.pick_file_button, Qt.LeftButton)
                qtbot.wait(100)
        m.assert_called_with(test_img_fname)

    def test_cancel_dialog(self, qtbot, media_widget, controller):
        with mock.patch.object(controller, 'load_media') as m:
            with mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName') as dialog_m:
                dialog_m.return_value = ('', None)
                qtbot.mouseClick(media_widget.pick_file_button, Qt.LeftButton)
                qtbot.wait(100)
        m.assert_not_called()
