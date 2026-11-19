from collections.abc import Callable

from PyQt6 import QtCore

from app import action_results


class Worker(QtCore.QThread):
    progress_changed = QtCore.pyqtSignal(str)  # pyright: ignore[reportCallIssue]
    finished = QtCore.pyqtSignal(action_results.ComputeResult)  # pyright: ignore[reportCallIssue]

    def __init__(self, job: Callable[[], action_results.ComputeResult], parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.job = job

    def run(self) -> None:
        self.finished.emit(self.job())
