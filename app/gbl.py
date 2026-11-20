PROGRESS_BAR_SIZE = 16
progress_symbols = ["/" * i + "\\" * (PROGRESS_BAR_SIZE - 1 - i) + "\\" for i in range(PROGRESS_BAR_SIZE)] + ["/" * PROGRESS_BAR_SIZE]
progress_symbols = progress_symbols + progress_symbols[::-1][1:-1]
PIE_CHART_MAX_SLICE_COUNT = 8
INSPECTED_MIME_TYPES = ("image", "video")

COUNT_STUFF_CHECK_STOP_CONDITION_FILE_COUNT_INTERVAL = 123
COUNT_STUFF_SET_PROGRESS_FILE_COUNT_INTERVAL = 123

FIND_DECEPTIVE_EXTENSIONS_CHECK_STOP_CONDITION_FILE_COUNT_INTERVAL = 13
FIND_DECEPTIVE_EXTENSIONS_SET_PROGRESS_FILE_COUNT_INTERVAL = 13


SKIPPED_DIRS = ("/proc", "/sys", "/dev", "/tmp")  # noqa: S108


def path_is_skipped(path: str) -> bool:
    return any(path.startswith(skipped_dir) for skipped_dir in SKIPPED_DIRS)
