import traceback
from typing import Type, Dict, Optional, Any

import cv2
from PyQt6.QtCore import pyqtSignal, QObject

from ezcv import CompVizPipeline
from ezcv.config import ConfigParsingError
from ezcv.operator import Operator
from ezcv.pipeline.core import OperatorFailedError
from ezcv.typing import Image


class EzCVController(QObject):

    show_media = pyqtSignal(Image)
    operators_list_updated = pyqtSignal()
    operator_parameter_updated = pyqtSignal()
    operator_failed = pyqtSignal(OperatorFailedError)
    loading_failed = pyqtSignal(ConfigParsingError)
    error = pyqtSignal(Exception)

    def __init__(self):
        super().__init__()

        self.cvpipeline = CompVizPipeline()
        self.curr_media: Optional[Image] = None
        self._names_generator = _OperatorNameGenerator()

        self.operators_list_updated.connect(self._on_operators_list_updated)
        self.operator_parameter_updated.connect(self._on_operator_parameter_updated)

    def add_operator(self, operator_cls: Type[Operator]):
        operator = operator_cls()
        operator_name = self._names_generator.generate_name(operator_cls)
        self.cvpipeline.add_operator(operator_name, operator)
        self.operators_list_updated.emit()

    def remove_operator(self, index: int):
        try:
            self.cvpipeline.remove_operator(index)
            self.operators_list_updated.emit()
        except ValueError as e:
            print(traceback.format_exc())
            self.error.emit(e)

    def move_operator(self, src: int, target: int):
        try:
            self.cvpipeline.move_operator(src, target)
            self.operators_list_updated.emit()
        except ValueError as e:
            print(traceback.format_exc())
            self.error.emit(e)

    def get_operator_name(self, index: int) -> str:
        try:
            name = self.cvpipeline.get_operator_name(index)
            return name
        except ValueError as e:
            print(traceback.format_exc())
            self.error.emit(e)

    def rename_operator(self, index: int, new_name: str):
        try:
            self.cvpipeline.rename_operator(index, new_name)
            self.operators_list_updated.emit()
        except ValueError as e:
            print(traceback.format_exc())
            self.error.emit(e)

    def process_curr_media(self):
        if self.curr_media is not None:
            try:
                result_img, ctx = self.cvpipeline.run(self.curr_media)
                self.show_media.emit(result_img)
            except OperatorFailedError as e:
                print(traceback.format_exc())
                self.operator_failed.emit(e)
                self.show_media.emit(self.curr_media)

    def update_operator_parameter(self, name: str, param_name: str, param_value: Any):
        setattr(self.operators[name], param_name, param_value)
        self.operator_parameter_updated.emit()

    def load_media(self, fname: str):
        img = cv2.imread(fname)
        if img is None:
            raise ValueError("Couldn't open image located at %s" % fname)
        self.curr_media = img
        self.process_curr_media()

    def load_config(self, fname: str):
        with open(fname, 'r') as fin:
            try:
                self.cvpipeline = CompVizPipeline.load(fin)
                self.operators_list_updated.emit()
            except ConfigParsingError as e:
                self.loading_failed.emit(e)

    def save_config(self, fname: str):
        with open(fname, 'w') as fout:
            try:
                self.cvpipeline.save(fout)
            except Exception as e:
                print(traceback.format_exc())
                self.error.emit(e)

    @property
    def operators(self):
        return self.cvpipeline.operators

    def _on_operators_list_updated(self):
        self.process_curr_media()

    def _on_operator_parameter_updated(self):
        self.process_curr_media()


class _OperatorNameGenerator:
    def __init__(self):
        self._names_repo: Dict[Type[Operator], int] = dict()

    def generate_name(self, op_cls: Type[Operator]) -> str:
        idx = self._names_repo.setdefault(op_cls, 0)
        name = op_cls.__name__ + (f'_{idx}' if idx > 0 else '')
        self._names_repo[op_cls] += 1
        return name
