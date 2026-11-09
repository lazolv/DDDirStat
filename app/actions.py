from collections.abc import Callable
from dataclasses import dataclass

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from app import features


def count_stuff_action(directory_path: str, destination: QtWidgets.QVBoxLayout) -> None:
    result = features.count_stuff(directory_path)
    for text in (
        f"Count of files & directories: <b>{result.objects_total:,}</b>",
        f"Count of files: <b>{result.files_total:,}</b>",
        f"Count of directories: <b>{result.dirs_total:,}</b>",
        f"Empty directory count: <b>{result.empty_dir_count:,}</b>",
        f"Empty file count: <b>{result.empty_file_count:,}</b>",
        f"Executable file count: <b>{result.executable_file_count:,}</b>",
    ):
        label = QtWidgets.QLabel()

        label.setText(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = label.font()
        font.setPixelSize(22)
        label.setFont(font)

        destination.addWidget(label)


@dataclass
class Action:
    name: str
    callback: Callable[[str, QtWidgets.QVBoxLayout], None]


action_array = (Action("Count stuff", count_stuff_action),)
action_registry = {action.name: action for action in action_array}
