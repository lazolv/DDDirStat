import os
from collections.abc import Callable
from dataclasses import dataclass

from app import action_results as ar
from app import gbl


def count_stuff(directory_path: str, set_progress: Callable[[str], None]) -> ar.CountStuffResult:
    result = ar.CountStuffResult()
    for root, dirnames, filenames in os.walk(directory_path):
        result.dirs_total += len(dirnames)
        if dirnames == [] and filenames == []:
            result.empty_dir_count += 1
        for filename in filenames:
            filepath = os.path.join(root, filename)
            extension = os.path.splitext(filename)[1]
            statinfo = os.lstat(filepath)
            mode = oct(statinfo.st_mode)

            if mode[2:4] == "10":
                result.files_total += 1
                result.empty_file_count += statinfo.st_size == 0
                if any(int(d) % 2 == 1 for d in mode[-3:]):
                    result.executable_file_count += 1
            elif mode[2:4] == "12":
                result.symlink_count += 1

            result.extension_counts[extension] = result.extension_counts.get(extension, 0) + 1

        if result.objects_total % 123 == 0:
            set_progress(f'<span style="color: green; font-weight: bold;">{result.objects_total}</span>')
        result.objects_total = result.files_total + result.dirs_total
    return result


def modification_date_graph(directory_path: str, set_progress: Callable[[str], None]) -> ar.ModificationDateGraphResult:
    result = ar.ModificationDateGraphResult()

    timestamp_registry: dict[int, int] = {}
    number_scanned = 0
    mod = 1337
    for root, dirnames, filenames in os.walk(directory_path):
        for dirname in dirnames:
            dirpath = os.path.join(root, dirname)
            st = os.lstat(dirpath)
            timestamp = round(st.st_mtime / 3600)
            timestamp_registry[timestamp] = timestamp_registry.get(timestamp, 0) + 1
        for filename in filenames:
            filepath = os.path.join(root, filename)
            st = os.lstat(filepath)
            timestamp = round(st.st_mtime / 3600)
            timestamp_registry[timestamp] = timestamp_registry.get(timestamp, 0) + 1
        if number_scanned % mod == 0:
            slashes = gbl.progress_symbols[number_scanned // mod % len(gbl.progress_symbols)]
            set_progress(
                f'<span style="color: green; font-weight: bold;">{slashes}</span>',
            )
        number_scanned += len(dirnames) + len(filenames)

    earliest_timestamp = min(timestamp_registry.keys())
    latest_timestamp = max(timestamp_registry.keys())

    timeline = [0] * (latest_timestamp - earliest_timestamp + 1)
    for timestamp, file_count in timestamp_registry.items():
        timeline[timestamp - earliest_timestamp] = file_count

    result.ox = [(earliest_timestamp + h) * 3600 for h in range(len(timeline))]
    result.oy = timeline

    return result


@dataclass
class Action:
    name: str
    callback: Callable[[str, Callable[[str], None]], ar.ComputeResult]


action_array = (
    Action("Count stuff", count_stuff),
    Action("Modification date graph", modification_date_graph),
)
action_registry = {action.name: action for action in action_array}
