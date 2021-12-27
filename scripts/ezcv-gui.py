import sys
import importlib_metadata

from PyQt6.QtWidgets import QApplication

from ezcv_gui.main import EzCV


def main():
    load_operators()
    app = QApplication([])
    main_widget = EzCV()
    sys.exit(app.exec())


def load_operators():
    entry_points = importlib_metadata.entry_points(group='ezcv_operators')
    for entry_point in entry_points:
        print(f'Loading operators library "{entry_point.name}"')
        entry_point.load()


if __name__ == '__main__':
    main()
