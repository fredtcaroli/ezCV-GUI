import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QResizeEvent
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QSizePolicy, QBoxLayout, QLayout

from ezcv_gui.controller import EzCVController
from ezcv_gui.utils import img2QImage


class MediaDisplay(QWidget):
    """ Adapted from:
        https://stackoverflow.com/questions/14107144/how-do-i-make-an-image-resize-to-scale-in-qt
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._img_label = QLabel(self)
        self._img_label.setFixedSize(0, 0)
        self._img_label.setScaledContents(True)

    def resize_img(self):
        pixmap = self._img_label.pixmap()
        if pixmap is None:
            return
        pixsize = pixmap.size()
        pixsize.scale(self.size(), Qt.KeepAspectRatio)
        self._img_label.setFixedSize(pixsize)

    def setPixmap(self, pixmap: QPixmap):
        self._img_label.setPixmap(pixmap)
        self.resize_img()

    def pixmap(self):
        return self._img_label.pixmap()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.resize_img()


class MediaPanelWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self.media_display = MediaDisplay(self)
        self.pick_file_button = QPushButton('Load Image', self)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.pick_file_button, alignment=Qt.AlignHCenter)
        layout.addWidget(self.media_display)

        self._controller.show_media.connect(self.on_show_media)
        self.pick_file_button.clicked.connect(self.pick_file_popup)
        self.pick_file_button.setShortcut('L')

    def on_show_media(self, img: np.ndarray):
        qimg = img2QImage(img)
        pix = QPixmap(qimg)
        self.media_display.setPixmap(pix)

    def pick_file_popup(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pick Image File', '~', 'Image Files(*.png *.jpg *.bmp *.jpeg)')
        if fname is None or fname.strip() == '':
            return
        self._controller.load_media(fname)
