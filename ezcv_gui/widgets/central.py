from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSplitter

from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.media import MediaPanelWidget
from ezcv_gui.widgets.pipeline import PipelineWidget


class CentralWidget(QSplitter):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(Qt.Horizontal ,parent=parent)
        self._controller = controller

        self.media = MediaPanelWidget(self._controller, parent=self)
        self.pipeline = PipelineWidget(self._controller, parent=self)

        self.init_ui()

    def init_ui(self):
        self.addWidget(self.pipeline)
        self.addWidget(self.media)
        self.setSizes([100, 200])
