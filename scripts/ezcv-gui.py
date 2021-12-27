import importlib
import sys
from typing import List

import click
import importlib_metadata

from PyQt6.QtWidgets import QApplication

from ezcv_gui.main import EzCV


@click.command(name='ezCV-GUI')
@click.option('--include', '-i', multiple=True)
def ezcv_gui(include):
    load_operators()
    load_includes(include)
    app = QApplication([])
    main_widget = EzCV()
    sys.exit(app.exec())


def load_operators():
    entry_points = importlib_metadata.entry_points(group='ezcv_operators')
    for entry_point in entry_points:
        print(f'Loading operators library "{entry_point.name}"')
        entry_point.load()


def load_includes(includes: List[str]):
    for include in includes:
        print(f'Loading module "{include}"')
        importlib.import_module(include)


if __name__ == '__main__':
    ezcv_gui()
