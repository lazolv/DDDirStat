#!/usr/bin/env python
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow


class DDDirStat(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setGeometry(300, 300, 600, 600)


def main() -> None:
    app = QApplication(sys.argv)
    wnd = DDDirStat()
    wnd.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
