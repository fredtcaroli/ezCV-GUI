import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject

from ezcv import CompVizPipeline
from ezcv.operator.implementations.blur import GaussianBlur
from ezcv.operator.implementations.color_space import ColorSpaceChange


class EzCVController(QObject):

    media_updated = pyqtSignal(np.ndarray)
    new_media_loaded = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()

        self.cvpipeline = CompVizPipeline()

        # testing
        blur = GaussianBlur()
        self.cvpipeline.add_operator('blur', blur)
        to_gray = ColorSpaceChange()
        to_gray.src = 'BGR'
        to_gray.target = 'GRAY'
        self.cvpipeline.add_operator('to_gray', to_gray)

        self.new_media_loaded.connect(self.on_new_media_loaded)

    def on_new_media_loaded(self, img: np.ndarray):
        result_img, ctx = self.cvpipeline.run(img)
        self.media_updated.emit(result_img)
