from PyQt6 import QtWidgets


def clear_layout(layout: QtWidgets.QLayout) -> None:
    if layout is not None:
        while layout.count() > 0:
            item = layout.takeAt(0)
            if item is None:
                raise RuntimeError

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    clear_layout(sub_layout)
