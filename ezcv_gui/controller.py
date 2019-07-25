from typing import Type

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject

from ezcv import CompVizPipeline
from ezcv.operator import Operator
from ezcv.pipeline import PipelineContext


class EzCVController(QObject):

    media_processed = pyqtSignal(np.ndarray, PipelineContext)
    new_media_loaded = pyqtSignal(np.ndarray)
    operators_updated = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.cvpipeline = CompVizPipeline()
        self.curr_media = None

        self.new_media_loaded.connect(self.on_new_media_loaded)
        self.operators_updated.connect(self.process_curr_media)

    def add_operator(self, operator_cls: Type[Operator]):
        operator = operator_cls()
        operator_name = operator_cls.__name__
        self.cvpipeline.add_operator(operator_name, operator)
        self.operators_updated.emit()

    def on_new_media_loaded(self, img: np.ndarray):
        self.curr_media = img
        self.process_curr_media()

    def process_curr_media(self):
        # TODO Handle curr media is None
        result_img, ctx = self.cvpipeline.run(self.curr_media)
        self.media_processed.emit(result_img, ctx)

    @property
    def operators(self):
        return self.cvpipeline.operators
