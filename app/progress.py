import time

from app import gbl


class Progress:
    def __init__(self, timepoint_scale_factor: float) -> None:
        self.time_of_start = time.time()
        self.last_scaled_timepoint: int = -1
        self.ticks_elapsed = 0

        self.timepoint_scale_factor = timepoint_scale_factor

    def tick(self, progress: int) -> str | None:
        new_scaled_timepoint = int((time.time() - self.time_of_start) * self.timepoint_scale_factor)
        if new_scaled_timepoint != self.last_scaled_timepoint:
            self.last_scaled_timepoint = new_scaled_timepoint
            slashes = gbl.progress_symbols[self.ticks_elapsed % len(gbl.progress_symbols)]
            self.ticks_elapsed += 1
            return f'<span style="color: green; font-weight: bold;">{slashes} {progress}</span>'
        return None
