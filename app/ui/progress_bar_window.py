from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt


class ProgressBarWindow(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("What a burden for the CPU")
        self.setFixedSize(300, 100)

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)

        self.setWindowModality(Qt.WindowModality.WindowModal)

        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Hush! A procedure is in progress...", self)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setRange(0, 0)

        self.progress_label = QtWidgets.QLabel(self)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        self.setLayout(layout)
