#!/usr/bin/env python
import sys

from PyQt6 import QtWidgets

from app.ui import main_window


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    wnd = main_window.MainWindow()
    wnd.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
