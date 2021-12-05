import sys

from PyQt6.QtWidgets import QApplication

from ezcv_gui.main import EzCV


def main():
    app = QApplication([])
    main_widget = EzCV()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
