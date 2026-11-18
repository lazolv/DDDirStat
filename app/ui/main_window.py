from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt

from app import action_results, actions, utl
from app.ui.progress_bar_window import ProgressBarWindow
from app.worker import Worker


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.directory = ""

        self.progress_wnd: ProgressBarWindow | None = None
        self.worker: Worker | None = None
        self.action_canceled = False

        self.init_ui()

    def init_ui(self) -> None:
        self.setGeometry(300, 100, 1000, 800)
        self.setWindowTitle("Dreadfully Dank Directory Stats")

        self.init_menu()

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        master_layout = QtWidgets.QVBoxLayout(central_widget)

        self.current_directory_label = QtWidgets.QLabel("No directory is selected. Select one at <b>File > Select a directory</b>", self)
        self.current_directory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.current_directory_label.font()
        font.setPixelSize(14)
        self.current_directory_label.setFont(font)
        master_layout.addWidget(self.current_directory_label)

        rest_of_the_view_widget = QtWidgets.QWidget()
        master_layout.addWidget(rest_of_the_view_widget)
        rest_of_the_view_layout = QtWidgets.QHBoxLayout(rest_of_the_view_widget)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content_widget)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.action_buttons: list[QtWidgets.QPushButton] = []
        for action_name in actions.action_registry:
            btn = QtWidgets.QPushButton(action_name)
            btn.clicked.connect(self.begin_action)
            scroll_layout.addWidget(btn)
            self.action_buttons.append(btn)

        scroll_area.setWidget(scroll_content_widget)
        rest_of_the_view_layout.addWidget(scroll_area, stretch=1)

        action_result_widget = QtWidgets.QWidget()
        rest_of_the_view_layout.addWidget(action_result_widget, stretch=3)
        self.action_result_layout = QtWidgets.QVBoxLayout(action_result_widget)

    def init_menu(self) -> None:
        menu_bar = self.menuBar()
        if menu_bar is None:
            raise RuntimeError

        file_menu = menu_bar.addMenu("File")
        if file_menu is None:
            raise RuntimeError

        select_dir_action = QtGui.QAction("Select a directory", self)
        select_dir_action.setShortcut(QtGui.QKeySequence("F"))
        select_dir_action.triggered.connect(self.select_directory)
        file_menu.addAction(select_dir_action)

        quit_action = QtGui.QAction("Quit", self)
        quit_action.setShortcut(QtGui.QKeySequence.StandardKey.Quit)
        quit_action.setMenuRole(QtGui.QAction.MenuRole.QuitRole)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def acquire_directory(self) -> str:
        while not (directory_path := QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory to analyze", "")):
            QtWidgets.QMessageBox.critical(self, "Ugh", "It looks like you have *misclicked*. Please try again")
        return directory_path

    def select_directory(self) -> None:
        self.directory = self.acquire_directory()
        self.cleanup_after_last_action()
        self.current_directory_label.setText(f"<b>{self.directory}</b>")

    def begin_action(self) -> None:
        for action_button in self.action_buttons:
            action_button.setEnabled(False)

        self.cleanup_after_last_action()

        self.action_canceled = False

        btn = self.sender()
        if not isinstance(btn, QtWidgets.QPushButton):
            raise TypeError
        action = actions.action_registry[btn.text()]

        self.progress_wnd = ProgressBarWindow(self)
        self.progress_wnd.on_close = self.cancel_action
        self.progress_wnd.show()

        def job() -> action_results.ComputeResult:
            if self.worker is None:
                raise RuntimeError
            return action.callback(self.directory, self.worker.progress_changed.emit, lambda: self.action_canceled)

        self.worker = Worker(job)
        self.worker.progress_changed.connect(self.progress_wnd.progress_label.setText)
        self.worker.finished.connect(self.finish_action)
        self.worker.start()

    def cancel_action(self) -> None:
        if self.progress_wnd is None:
            raise RuntimeError
        # It must be closed at this point
        self.progress_wnd = None
        self.action_canceled = True

    def finish_action(self, result: action_results.ComputeResult) -> None:
        if not self.action_canceled:
            if self.progress_wnd is None:
                raise RuntimeError
            self.progress_wnd.on_close = None
            self.progress_wnd.close()
            self.progress_wnd = None

            result.present(self.action_result_layout)

        for action_button in self.action_buttons:
            action_button.setEnabled(True)

    def cleanup_after_last_action(self) -> None:
        utl.clear_layout(self.action_result_layout)
