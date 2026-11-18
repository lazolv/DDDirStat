import os
import platform

import statx
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


def birth_time(filepath: str, st: os.stat_result) -> float | None:
    if platform.system() == "Windows":
        return st.st_ctime  # `ctime` is creation time on Windows
    try:
        # `birthtime` may be available on Mac and other Unix-based OSes
        return st.st_birthtime  # pyright: ignore[reportAttributeAccessIssue]
    except AttributeError:
        btime = statx.statx(filepath).btime  # Attempt this if on Linux
        if btime is not None:
            return btime
    return None
