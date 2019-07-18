from PyQt5.QtWidgets import QMainWindow

from ezcv import CompVizPipeline


class EzCV(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._pipeline = CompVizPipeline()

        self.initUI()

    def initUI(self):
        self.statusBar()

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('EzCV')
