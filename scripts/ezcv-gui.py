import sys

from PyQt5.QtWidgets import QApplication

from ezcv_gui.main import EzCV


def main():
    app = QApplication([])
    main_widget = EzCV()
    main_widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
