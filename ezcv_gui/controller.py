import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject


class EzCVController(QObject):

    media_updated = pyqtSignal(np.ndarray)
    new_media_loaded = pyqtSignal(np.ndarray)
