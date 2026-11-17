PROGRESS_BAR_SIZE = 16
progress_symbols = ["/" * i + "\\" * (PROGRESS_BAR_SIZE - 1 - i) + "\\" for i in range(PROGRESS_BAR_SIZE)] + ["/" * PROGRESS_BAR_SIZE]
progress_symbols = progress_symbols + progress_symbols[::-1][1:-1]
PIE_CHART_MAX_SLICE_COUNT = 8
