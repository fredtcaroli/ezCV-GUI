import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout

from ezcv_gui.controller import EzCVController
from ezcv_gui.utils import img2QImage


class MediaWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self.media_shower = QLabel(self)
        self.pick_file_button = QPushButton('Load Image', self)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.pick_file_button)
        layout.addWidget(self.media_shower)

        self._controller.show_media.connect(self.on_show_media)
        self.pick_file_button.clicked.connect(self.pick_file_popup)

    def on_show_media(self, img: np.ndarray):
        qimg = img2QImage(img)
        pix = QPixmap(qimg)
        self.media_shower.setPixmap(pix)

    def pick_file_popup(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pick Image File', '~', 'Image Files(*.png *.jpg *.bmp *.jpeg)')
        if fname is None or fname.strip() == '':
            return
        self._controller.load_media(fname)
