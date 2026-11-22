from typing import TYPE_CHECKING, override

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from collections.abc import Callable


class ProgressBarWindow(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.on_close: Callable[[], None] | None = None

        self.setWindowTitle("What a burden for the CPU")
        self.setFixedSize(300, 100)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setWindowModality(Qt.WindowModality.WindowModal)

        master_layout = QtWidgets.QVBoxLayout()
        upper_label = QtWidgets.QLabel("Hush! A procedure is in progress...")
        progress_bar = self.make_progress_bar()
        self.progress_label = QtWidgets.QLabel()

        master_layout.addWidget(upper_label)
        master_layout.addWidget(progress_bar)
        master_layout.addWidget(self.progress_label)
        self.setLayout(master_layout)

    def make_progress_bar(self) -> QtWidgets.QProgressBar:
        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setRange(0, 0)
        return progress_bar

    @override
    def closeEvent(self, event: QtGui.QCloseEvent | None) -> None:
        if event is not None:
            if self.on_close is not None:
                self.on_close()
            event.accept()

    def reject(self) -> None:
        self.close()
