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
        master_layout = QtWidgets.QVBoxLayout()
        self.current_directory_label = self.make_current_directory_label()
        main_view_layout = QtWidgets.QHBoxLayout()

        action_list_scroll_area = self.make_action_list_scroll_area()
        action_list_widget = QtWidgets.QWidget()
        action_list_layout = self.make_action_list_layout()
        self.action_buttons = self.make_action_buttons()

        action_result_scroll_area = self.make_action_result_scroll_area()
        action_result_widget = QtWidgets.QWidget()
        self.action_result_layout = QtWidgets.QVBoxLayout()

        # Parenting the widgets
        self.setCentralWidget(central_widget)
        central_widget.setLayout(master_layout)
        master_layout.addWidget(self.current_directory_label)
        master_layout.addLayout(main_view_layout)

        action_list_widget.setLayout(action_list_layout)
        for action_button in self.action_buttons:
            action_list_layout.addWidget(action_button)
        action_list_scroll_area.setWidget(action_list_widget)
        main_view_layout.addWidget(action_list_scroll_area, stretch=1)

        action_result_widget.setLayout(self.action_result_layout)
        action_result_scroll_area.setWidget(action_result_widget)
        main_view_layout.addWidget(action_result_scroll_area, stretch=3)

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

    def make_current_directory_label(self) -> QtWidgets.QLabel:
        current_directory_label = QtWidgets.QLabel("No directory is selected. Select one at <b>File > Select a directory</b>", self)
        current_directory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = current_directory_label.font()
        font.setPixelSize(14)
        current_directory_label.setFont(font)
        return current_directory_label

    def make_action_list_layout(self) -> QtWidgets.QVBoxLayout:
        action_list_layout = QtWidgets.QVBoxLayout()
        action_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        return action_list_layout

    def make_action_list_scroll_area(self) -> QtWidgets.QScrollArea:
        action_list_scroll_area = QtWidgets.QScrollArea()
        action_list_scroll_area.setWidgetResizable(True)
        return action_list_scroll_area

    def make_action_buttons(self) -> list[QtWidgets.QPushButton]:
        action_buttons: list[QtWidgets.QPushButton] = []
        for action_name in actions.action_registry:
            button = QtWidgets.QPushButton(action_name)
            button.clicked.connect(self.begin_action)
            action_buttons.append(button)
        return action_buttons

    def make_action_result_scroll_area(self) -> QtWidgets.QScrollArea:
        action_result_scroll_area = QtWidgets.QScrollArea()
        action_result_scroll_area.setWidgetResizable(True)
        return action_result_scroll_area

    def acquire_directory(self) -> str:
        while not (directory_path := QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory to analyze", "")):
            QtWidgets.QMessageBox.critical(self, "Ugh", "It looks like you have *misclicked*. Please try again")
        return directory_path

    def select_directory(self) -> None:
        self.directory = self.acquire_directory()
        self.cleanup_after_last_action()
        self.set_action_cancellation(False)

    def update_selected_directory_label(self) -> None:
        if self.action_canceled:
            self.current_directory_label.setText(f'<b>{self.directory}</b> <span style="color: red;">*</span>')
        else:
            self.current_directory_label.setText(f"<b>{self.directory}</b>")

    def set_action_cancellation(self, to: bool) -> None:  # noqa: FBT001
        self.action_canceled = to
        self.update_selected_directory_label()

    def begin_action(self) -> None:
        for action_button in self.action_buttons:
            action_button.setEnabled(False)

        self.cleanup_after_last_action()

        self.set_action_cancellation(False)

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
        self.set_action_cancellation(True)

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
