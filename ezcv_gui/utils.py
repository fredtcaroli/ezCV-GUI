import numpy as np
from PyQt6.QtGui import QImage

from ezcv.utils import is_image


def img2QImage(img: np.ndarray) -> QImage:
    if not is_image(img):
        raise ValueError('Invalid image')

    # Using straight numpy here just so we don't have a direct dependency on opencv
    if img.ndim == 2:
        img = np.repeat(img[..., None], 3, axis=2)
    else:
        img = img[..., ::-1].copy()  # QImage doesn't accept a memoryview. So we make a copy

    height, width, _ = img.shape
    bytes_per_line = 3 * width
    qimg = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
    return qimg
