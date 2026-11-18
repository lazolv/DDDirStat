from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt


class ProgressBarWindow(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.procedure_is_done = False

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

    def closeEvent(self, event: QtGui.QCloseEvent | None) -> None:
        if event is not None:
            if self.procedure_is_done:
                event.accept()
            else:
                event.ignore()

    def reject(self) -> None:
        pass
