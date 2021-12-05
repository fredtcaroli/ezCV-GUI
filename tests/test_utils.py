import numpy as np
import pytest
from PyQt6.QtGui import QImage

from ezcv.test_utils import parametrize_img, assert_terms_in_exception
from ezcv_gui.utils import img2QImage


@parametrize_img
def test_img2qimg_return_type(img):
    qimg = img2QImage(img)
    assert isinstance(qimg, QImage)


@parametrize_img(include_invalid=True, include_valid=False)
def test_img2qimg_invalid_img(img):
    with pytest.raises(ValueError) as e:
        img2QImage(img)
    assert_terms_in_exception(e, ['invalid', 'image'])


@parametrize_img
def test_img2qimg_shape(img):
    qimg = img2QImage(img)
    assert qimg.height() == img.shape[0] and qimg.width() == img.shape[1]


@parametrize_img
def test_img2qimg_content(img):
    qimg = img2QImage(img)
    if img.ndim == 2:
        img = np.repeat(img[..., None], 3, axis=2)
    else:
        img = img[..., ::-1].copy()
    channels_count = 3
    b = qimg.bits()
    b.setsize(qimg.height() * qimg.width() * channels_count)
    arr = np.frombuffer(b, np.uint8).reshape((qimg.height(), qimg.width(), channels_count))
    assert np.all(np.isclose(img, arr))
