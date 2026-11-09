from collections.abc import Callable
from dataclasses import dataclass

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from app import features


def count_everything_action(directory_path: str, destination: QtWidgets.QVBoxLayout) -> None:
    label = QtWidgets.QLabel()
    label.setText(f"Total count of files & directories: {features.count_everything(directory_path)}")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    font = label.font()
    font.setPixelSize(22)
    label.setFont(font)
    destination.addWidget(label)


def count_files_action(directory_path: str, destination: QtWidgets.QVBoxLayout) -> None:
    label = QtWidgets.QLabel()
    label.setText(f"Total count of files: {features.count_files(directory_path)}")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    font = label.font()
    font.setPixelSize(22)
    label.setFont(font)
    destination.addWidget(label)


def count_directories_action(directory_path: str, destination: QtWidgets.QVBoxLayout) -> None:
    label = QtWidgets.QLabel()
    label.setText(f"Total count of directories: {features.count_directories(directory_path)}")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    font = label.font()
    font.setPixelSize(22)
    label.setFont(font)
    destination.addWidget(label)


@dataclass
class Action:
    name: str
    callback: Callable[[str, QtWidgets.QVBoxLayout], None]


action_array = (
    Action("Count everything", count_everything_action),
    Action("Count files", count_files_action),
    Action("Count directories", count_directories_action),
)
action_registry = {action.name: action for action in action_array}
