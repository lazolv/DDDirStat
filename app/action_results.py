from abc import abstractmethod
from dataclasses import dataclass, field

from PyQt6 import QtCharts, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget

from app import gbl


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
        for text in (
            f"Count of files & directories: <b>{self.objects_total:,}</b>",
            f"Count of files: <b>{self.files_total:,}</b>",
            f"Count of directories: <b>{self.dirs_total:,}</b>",
            f"Empty directory count: <b>{self.empty_dir_count:,}</b>",
            f"Empty file count: <b>{self.empty_file_count:,}</b>",
            f"Executable file count: <b>{self.executable_file_count:,}</b>",
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
        end = min(gbl.PIE_CHART_MAX_SLICE_COUNT - 1, len(most_frequent_extensions))
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
