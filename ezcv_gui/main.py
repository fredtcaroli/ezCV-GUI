from PyQt5.QtWidgets import QMainWindow

from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.central import CentralWidget


class EzCV(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._controller = EzCVController()

        self.central = CentralWidget(self._controller, parent=self)

        self.initUI()

    def initUI(self):
        self.statusBar()
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('EzCV')

        self.setCentralWidget(self.central)
