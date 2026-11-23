import platform
from abc import abstractmethod
from dataclasses import dataclass, field

import pyqtgraph
from PyQt6 import QtCharts, QtGui, QtWidgets
from PyQt6.QtCore import Qt

COUNT_STUFF_PIE_CHART_MAX_SLICE_COUNT = 8


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
    symlink_count: int = 0
    extension_counts: dict[str, int] = field(default_factory=dict)

    def present(self, destination: QtWidgets.QVBoxLayout) -> None:
        injected_windows_note = ' <span style="color: #B8860B;">(unreliable on Windows)</span>' if platform.system() == "Windows" else ""
        for text in (
            f"Count of files & directories: <b>{self.objects_total:,}</b>",
            f"Count of files: <b>{self.files_total:,}</b>",
            f"Count of directories: <b>{self.dirs_total:,}</b>",
            f"Empty directory count: <b>{self.empty_dir_count:,}</b>",
            f"Empty file count: <b>{self.empty_file_count:,}</b>",
            f"Executable file count{injected_windows_note}: <b>{self.executable_file_count:,}</b>",
            f"Symlink count: <b>{self.symlink_count:,}</b>",
        ):
            label = QtWidgets.QLabel()
            label.setText(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = label.font()
            font.setPixelSize(22)
            label.setFont(font)
            destination.addWidget(label)

        most_frequent_extensions = sorted(((c, e) for e, c in self.extension_counts.items()), reverse=True)

        series = QtCharts.QPieSeries()
        end = min(COUNT_STUFF_PIE_CHART_MAX_SLICE_COUNT - 1, len(most_frequent_extensions))
        for count, extension in most_frequent_extensions[:end]:
            series.append(extension, count)
        if end < len(most_frequent_extensions):
            series.append("Other ext.", most_frequent_extensions[end][0])
        for sl in series.slices():
            if sl.percentage() > 30 / 360:
                sl.setLabelVisible(True)
            sl.setLabel(f'<b>{"No ext." if sl.label() == "" else sl.label()}</b> ({int(sl.value())})')

        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("File extensions")
        title_font = chart.titleFont()
        title_font.setPixelSize(22)
        chart.setTitleFont(title_font)
        legend = chart.legend()
        if legend is None:
            raise RuntimeError
        legend.setAlignment(Qt.AlignmentFlag.AlignRight)

        chart_view = QtCharts.QChartView(chart)
        chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        destination.addWidget(chart_view)


@dataclass
class MCADateGraphResult(ComputeResult):
    m_ox: list[int] = field(default_factory=list)
    m_oy: list[int] = field(default_factory=list)

    c_ox: list[int] = field(default_factory=list)
    c_oy: list[int] = field(default_factory=list)

    a_ox: list[int] = field(default_factory=list)
    a_oy: list[int] = field(default_factory=list)

    b_ox: list[int] = field(default_factory=list)
    b_oy: list[int] = field(default_factory=list)

    def present(self, destination: QtWidgets.QVBoxLayout) -> None:
        tab_widget = QtWidgets.QTabWidget()
        for tab_title, ox, oy, clr in (
            ("Modification", self.m_ox, self.m_oy, (0, 255, 255)),
            ("Change", self.c_ox, self.c_oy, (255, 0, 255)),
            ("Access", self.a_ox, self.a_oy, (255, 255, 0)),
            ("Birth", self.b_ox, self.b_oy, (0, 255, 0)),
        ):
            if platform.system() == "Windows" and tab_title == "Change":  # `ctime` is creation time on Windows
                continue
            plot_widget = pyqtgraph.PlotWidget(axisItems={"bottom": pyqtgraph.DateAxisItem(orientation="bottom")})

            plot_widget.showGrid(x=True, y=True)
            plot_widget.setLabel("left", "Count of files")
            plot_widget.setLabel("bottom", "Timestamp")

            plot_widget.plot(ox, oy, pen=clr)

            tab_widget.addTab(plot_widget, tab_title)

        destination.addWidget(tab_widget)


@dataclass
class FindDeceptiveExtensionsResult(ComputeResult):
    mismatching_extension_and_magic_number_mimes: list[str] = field(default_factory=list)

    def present(self, destination: QtWidgets.QVBoxLayout) -> None:
        message_one = "Files whose extension is possibly deceptive"
        message_two = "Found nothing interesting"

        title_label = QtWidgets.QLabel()
        title_label.setText(
            f'<span style="color: blue;">'
            f"{message_one if len(self.mismatching_extension_and_magic_number_mimes) > 0 else message_two}"
            "</span>",
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPixelSize(20)
        title_label.setFont(font)
        destination.addWidget(title_label)

        for string in self.mismatching_extension_and_magic_number_mimes:
            label = QtWidgets.QLabel()
            label.setText(string)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = label.font()
            font.setPixelSize(15)
            label.setFont(font)
            destination.addWidget(label)
