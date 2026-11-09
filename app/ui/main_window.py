from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from app import actions, utl


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.directory = ""

        self.init_ui()

    def init_ui(self) -> None:
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle("Dreadfully Dank Directory Stats")

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        master_layout = QtWidgets.QVBoxLayout(central_widget)

        self.select_directory_button = QtWidgets.QPushButton("Select a directory", self)
        self.select_directory_button.clicked.connect(self.select_directory)
        master_layout.addWidget(self.select_directory_button)

        rest_of_the_view_widget = QtWidgets.QWidget()
        master_layout.addWidget(rest_of_the_view_widget)
        rest_of_the_view_layout = QtWidgets.QHBoxLayout(rest_of_the_view_widget)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content_widget)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for action_name in actions.action_registry:
            btn = QtWidgets.QPushButton(action_name)
            btn.clicked.connect(self.run_action)
            scroll_layout.addWidget(btn)

        scroll_area.setWidget(scroll_content_widget)
        rest_of_the_view_layout.addWidget(scroll_area, stretch=1)

        action_result_widget = QtWidgets.QWidget()
        rest_of_the_view_layout.addWidget(action_result_widget, stretch=3)
        self.action_result_layout = QtWidgets.QVBoxLayout(action_result_widget)

    def acquire_directory(self) -> str:
        while not (directory_path := QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory to analyze", "")):
            QtWidgets.QMessageBox.critical(self, "Ugh", "It looks like you have *misclicked*. Please try again")
        return directory_path

    def select_directory(self) -> None:
        self.directory = self.acquire_directory()
        self.cleanup_after_last_action()

    def run_action(self) -> None:
        self.cleanup_after_last_action()

        btn = self.sender()
        if not isinstance(btn, QtWidgets.QPushButton):
            raise TypeError
        action = actions.action_registry[btn.text()]
        action.callback(self.directory, self.action_result_layout)

    def cleanup_after_last_action(self) -> None:
        utl.clear_layout(self.action_result_layout)
