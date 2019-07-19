import os
from unittest import mock

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QFileDialog

from ezcv.test_utils import parametrize_img, build_img
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


def test_media_widget_pick_file_button_exists(qtbot):
    controller = EzCVController()
    media = MediaWidget(controller)
    assert isinstance(media.pick_file_button, QPushButton)


def test_media_widget_pick_file_button_triggers_OpenFileName(qtbot, datadir):
    controller = EzCVController()
    media = MediaWidget(controller)
    test_img_fname = os.path.join(datadir, 'img.png')
    with mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                    mock.MagicMock(return_value=(test_img_fname, None))) as m:
        qtbot.mouseClick(media.pick_file_button, Qt.LeftButton)

    m.assert_called_once()


def test_media_widget_pick_file_button_triggers_image_update(qtbot, datadir):
    controller = EzCVController()
    media = MediaWidget(controller)

    updated = False

    def on_media_updated(img):
        nonlocal updated
        updated = True

    test_img_fname = os.path.join(datadir, 'img.png')
    controller.media_updated.connect(on_media_updated)
    with qtbot.waitSignal(controller.media_updated, 1000), \
         mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                    mock.MagicMock(return_value=(test_img_fname, None))) as m:
        qtbot.mouseClick(media.pick_file_button, Qt.LeftButton)

    assert updated


def test_media_widget_pick_file_button_cancel_QFileDialog(qtbot):
    controller = EzCVController()
    media = MediaWidget(controller)

    updated = False

    def on_media_updated(img):
        nonlocal updated
        updated = True

    controller.media_updated.connect(on_media_updated)
    with mock.patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                    mock.MagicMock(return_value=(None, None))) as m:
        qtbot.mouseClick(media.pick_file_button, Qt.LeftButton)
        qtbot.wait(1000)

    assert not updated
