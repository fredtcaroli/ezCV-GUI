from PyQt5.QtWidgets import QMainWindow, QMessageBox

from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.central import CentralWidget


class EzCV(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._controller = EzCVController()

        self._controller.operator_failed.connect(self.on_operator_failed)

        self.central = CentralWidget(self._controller, parent=self)

        self.init_ui()

    def init_ui(self):
        self.statusBar()
        self.setWindowTitle('EzCV')

        self.setCentralWidget(self.central)
        self.showMaximized()

    def on_operator_failed(self, exception):
        QMessageBox.critical(self, "Error", str(exception))
