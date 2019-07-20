import cv2
import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QFileDialog

from ezcv_gui.controller import EzCVController
from ezcv_gui.utils import img2QImage


class MediaWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self._controller.media_updated.connect(self.on_media_updated)

        self.loaded_media_fname = None
        self.loaded_media = None

        self.media_shower = QLabel(self)
        self.pick_file_button = QPushButton(self)

        self.pick_file_button.clicked.connect(self.on_pick_file_button_click)

    def on_media_updated(self, img: np.ndarray):
        qimg = img2QImage(img)
        pix = QPixmap(qimg)
        self.media_shower.setPixmap(pix)

    def on_pick_file_button_click(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pick Image File', '~', 'Image Files(*.png *.jpg *.bmp)')
        if fname is None:
            return
        img = cv2.imread(fname)
        if img is None:
            raise ValueError("Couldn't open image located at %s" % fname)

        self.loaded_media_fname = fname
        self.loaded_media = img
        self._controller.new_media_loaded.emit(img)
