import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

from ezcv_gui.controller import EzCVController
from ezcv_gui.utils import img2QImage


class MediaWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self._controller.media_updated.connect(self.on_media_updated)

        self.media_shower = QLabel()

    def on_media_updated(self, img: np.ndarray):
        qimg = img2QImage(img)
        pix = QPixmap(qimg)
        self.media_shower.setPixmap(pix)
