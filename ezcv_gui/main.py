from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtGui import QAction

from ezcv_gui.controller import EzCVController
from ezcv_gui.widgets.central import CentralWidget


class EzCV(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._controller = EzCVController()

        self.central = CentralWidget(self._controller, parent=self)

        self.init_ui()
        self.init_menu_bar()
        self.init_signals()

    def init_ui(self):
        self.statusBar()
        self.setWindowTitle('EzCV')

        self.setCentralWidget(self.central)
        self.showMaximized()

    def init_menu_bar(self):
        load_action = QAction('&Open', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.on_load_action)

        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.on_save_action)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)

    def init_signals(self):
        self._controller.operator_failed.connect(self.on_operator_failed)
        self._controller.loading_failed.connect(self.on_loading_failed)
        self._controller.error.connect(self.on_unexpected_error)

    def on_load_action(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Pick Config File', 'config.yaml', 'YAML Files(*.yaml *.yml)')
        if fname is not None:
            self._controller.load_config(fname)

    def on_operator_failed(self, exception: Exception):
        QMessageBox.critical(self, "Operator Error", str(exception))

    def on_loading_failed(self, exception: Exception):
        msgs = [str(a) for a in exception.args]
        QMessageBox.critical(self, "Loading Error", '\n'.join(msgs))

    def on_unexpected_error(self, exception: Exception):
        msgs = [str(a) for a in exception.args]
        QMessageBox.critical(self, 'Unexpected Error', '\n'.join(msgs))

    def on_save_action(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Choose File Name', 'config.yaml', 'YAML Files(*.yaml *.yml)')
        if fname is not None:
            self._controller.save_config(fname)
