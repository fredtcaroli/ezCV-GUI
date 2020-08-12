from typing import Type, Dict, Optional, Any

import cv2
from PyQt5.QtCore import pyqtSignal, QObject

from ezcv import CompVizPipeline
from ezcv.operator import Operator
from ezcv.typing import Image


class EzCVController(QObject):

    show_media = pyqtSignal(Image)
    operators_changed = pyqtSignal()
    operators_updated = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.cvpipeline = CompVizPipeline()
        self.curr_media: Optional[Image] = None
        self._names_generator = _OperatorNameGenerator()

        self.operators_changed.connect(self._on_operators_changed)
        self.operators_updated.connect(self._on_operators_updated)

    def add_operator(self, operator_cls: Type[Operator]):
        operator = operator_cls()
        operator_name = self._names_generator.generate_name(operator_cls)
        self.cvpipeline.add_operator(operator_name, operator)
        self.operators_changed.emit()

    def process_curr_media(self):
        if self.curr_media is not None:
            result_img, ctx = self.cvpipeline.run(self.curr_media)
            self.show_media.emit(result_img)

    def update_operator(self, name: str, param_name: str, param_value: Any):
        setattr(self.operators[name], param_name, param_value)
        self.operators_updated.emit()

    def load_media(self, fname: str):
        img = cv2.imread(fname)
        if img is None:
            raise ValueError("Couldn't open image located at %s" % fname)
        self.curr_media = img
        self.process_curr_media()

    @property
    def operators(self):
        return self.cvpipeline.operators

    def _on_operators_changed(self):
        self.process_curr_media()

    def _on_operators_updated(self):
        self.process_curr_media()


class _OperatorNameGenerator:
    def __init__(self):
        self._names_repo: Dict[Type[Operator], int] = dict()

    def generate_name(self, op_cls: Type[Operator]) -> str:
        idx = self._names_repo.setdefault(op_cls, 0)
        name = op_cls.__name__ + (f'_{idx}' if idx > 0 else '')
        self._names_repo[op_cls] += 1
        return name
