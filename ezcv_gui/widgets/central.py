from PyQt5.QtWidgets import QWidget, QHBoxLayout

from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.media import MediaWidget


class CentralWidget(QWidget):
    def __init__(self, controller: EzCVController, parent=None):
        super().__init__(parent=parent)
        self._controller = controller

        self.media = MediaWidget(self._controller, parent=self)

        self.initUi()

    def initUi(self):
        layout = QHBoxLayout(self)

        layout.addWidget(self.media)
