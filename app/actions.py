import os
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget

PROGRESS_BAR_SIZE = 16
progress_symbols = ["/" * i + "\\" * (PROGRESS_BAR_SIZE - 1 - i) + "\\" for i in range(PROGRESS_BAR_SIZE)] + ["/" * PROGRESS_BAR_SIZE]


@dataclass
class ComputeResult:
    @abstractmethod
    def present(self, destination: QtWidgets.QVBoxLayout) -> None:
        pass


@dataclass
class CountStuffResult(ComputeResult):
    objects_total: int = 0
    files_total: int = 0
    dirs_total: int = 0
    empty_dir_count: int = 0
    empty_file_count: int = 0
    executable_file_count: int = 0
    extension_counts: dict[str, int] = field(default_factory=dict)

    def present(self, destination: QtWidgets.QVBoxLayout) -> None:
        for text in (
            f"Count of files & directories: <b>{self.objects_total:,}</b>",
            f"Count of files: <b>{self.files_total:,}</b>",
            f"Count of directories: <b>{self.dirs_total:,}</b>",
            f"Empty directory count: <b>{self.empty_dir_count:,}</b>",
            f"Empty file count: <b>{self.empty_file_count:,}</b>",
            f"Executable file count: <b>{self.executable_file_count:,}</b>",
        ):
            label = QtWidgets.QLabel()

            label.setText(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            font = label.font()
            font.setPixelSize(22)
            label.setFont(font)

            destination.addWidget(label)


def count_stuff(directory_path: str, set_progress: Callable[[str], None]) -> CountStuffResult:
    result = CountStuffResult()
    for root, dirnames, filenames in os.walk(directory_path):
        result.files_total += len(filenames)
        result.dirs_total += len(dirnames)
        result.objects_total = result.files_total + result.dirs_total
        if dirnames == [] and filenames == []:
            result.empty_dir_count += 1
        for filename in filenames:
            filepath = os.path.join(root, filename)
            extension = os.path.splitext(filename)[1]
            statinfo = os.lstat(filepath)

            result.empty_file_count += statinfo.st_size == 0

            if any(int(d) % 2 == 1 for d in oct(statinfo.st_mode)[-3:]):
                result.executable_file_count += 1

            result.extension_counts[extension] = result.extension_counts.get(extension, 0) + 1

        if result.objects_total % 123 == 0:
            set_progress(f'<span style="color: green; font-weight: bold;">{result.objects_total}</span>')
    return result


@dataclass
class ModificationDateGraphResult(ComputeResult):
    ox: list[int] = field(default_factory=list)
    oy: list[int] = field(default_factory=list)

    def present(self, destination: QtWidgets.QVBoxLayout) -> None:
        plot_widget = PlotWidget()

        plot_widget.showGrid(x=True, y=True)
        plot_widget.setLabel("left", "Count of files")
        plot_widget.setLabel("bottom", "Timestamp")

        plot_widget.plot(self.ox, self.oy)

        destination.addWidget(plot_widget)


def modification_date_graph(directory_path: str, set_progress: Callable[[str], None]) -> ModificationDateGraphResult:
    result = ModificationDateGraphResult()

    modification_date_registry: dict[int, int] = {}
    number_scanned = 0
    mod = 1337
    for root, dirnames, filenames in os.walk(directory_path):
        for dirname in dirnames:
            dirpath = os.path.join(root, dirname)
            mtime = int(os.lstat(dirpath).st_mtime)
            modification_date_registry[mtime] = modification_date_registry.get(mtime, 0) + 1
        for filename in filenames:
            filepath = os.path.join(root, filename)
            mtime = int(os.lstat(filepath).st_mtime)
            modification_date_registry[mtime] = modification_date_registry.get(mtime, 0) + 1
        if number_scanned % mod == 0:
            set_progress(
                f'<span style="color: green; font-weight: bold;">{progress_symbols[number_scanned // mod % len(progress_symbols)]}</span>',
            )
        number_scanned += len(dirnames) + len(filenames)
    sorted_entries = sorted(modification_date_registry.items())
    earliest_timestamp = sorted_entries[0][0]
    result.ox = [mtime - earliest_timestamp for mtime, _file_count in sorted_entries]
    result.oy = [file_count for _mtime, file_count in sorted_entries]
    return result


@dataclass
class Action:
    name: str
    callback: Callable[[str, Callable[[str], None]], ComputeResult]


action_array = (
    Action("Count stuff", count_stuff),
    Action("Modification date graph", modification_date_graph),
)
action_registry = {action.name: action for action in action_array}
