import mimetypes
import os
import stat
from collections.abc import Callable
from dataclasses import dataclass

import magic

from app import action_results as ar
from app import utl
from app.progress import Progress

SKIPPED_DIRS = ("/proc", "/sys", "/dev", "/tmp")  # noqa: S108


def path_is_skipped(path: str) -> bool:
    return any(path.startswith(skipped_dir) for skipped_dir in SKIPPED_DIRS)


def count_stuff(directory_path: str, set_progress: Callable[[str], None], stop: Callable[[], bool]) -> ar.CountStuffResult:
    result = ar.CountStuffResult()
    progress = Progress(16)

    objects_scanned = 0
    for root, dirnames, filenames in os.walk(directory_path):
        if stop():
            return result
        if path_is_skipped(root):
            continue
        if (string := progress.tick(objects_scanned)) is not None:
            set_progress(string)

        result.dirs_total += len(dirnames)
        if dirnames == [] and filenames == []:
            result.empty_dir_count += 1
        for filename in filenames:
            filepath = os.path.join(root, filename)
            extension = os.path.splitext(filename)[1]
            try:
                stat_result = os.lstat(filepath)
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue

            if stat.S_ISREG(stat_result.st_mode):
                result.files_total += 1
                result.empty_file_count += stat_result.st_size == 0
                if bool(stat_result.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)):
                    result.executable_file_count += 1
            elif stat.S_ISLNK(stat_result.st_mode):
                result.symlink_count += 1

            result.extension_counts[extension] = result.extension_counts.get(extension, 0) + 1
        objects_scanned = result.files_total + result.dirs_total

    result.objects_total = objects_scanned
    return result


def mca_date_graph(directory_path: str, set_progress: Callable[[str], None], stop: Callable[[], bool]) -> ar.MCADateGraphResult:
    result = ar.MCADateGraphResult()
    progress = Progress(16)

    mtime_registry: dict[int, int] = {}
    ctime_registry: dict[int, int] = {}
    atime_registry: dict[int, int] = {}
    btime_registry: dict[int, int] = {}

    objects_scanned = 0
    for root, dirnames, filenames in os.walk(directory_path):
        if stop():
            return result
        if path_is_skipped(root):
            continue
        if (string := progress.tick(objects_scanned)) is not None:
            set_progress(string)

        for name in dirnames + filenames:
            path = os.path.join(root, name)
            try:
                st = os.lstat(path)
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            mtime = round(st.st_mtime / 3600)
            ctime = round(st.st_ctime / 3600)
            atime = round(st.st_atime / 3600)
            btime = utl.birth_time(path, st)

            if btime is not None:
                btime = round(btime / 3600)
                btime_registry[btime] = btime_registry.get(btime, 0) + 1

            mtime_registry[mtime] = mtime_registry.get(mtime, 0) + 1
            ctime_registry[ctime] = ctime_registry.get(ctime, 0) + 1
            atime_registry[atime] = atime_registry.get(atime, 0) + 1
        objects_scanned += len(dirnames) + len(filenames)

    def make_ox_oy(registry: dict[int, int]) -> tuple[list[int], list[int]]:
        if not registry:
            return [], []
        earliest_timestamp = min(registry.keys())
        latest_timestamp = max(registry.keys())

        timeline = [0] * (latest_timestamp - earliest_timestamp + 1)
        for timestamp, file_count in registry.items():
            timeline[timestamp - earliest_timestamp] = file_count

        return [(earliest_timestamp + h) * 3600 for h in range(len(timeline))], timeline

    result.m_ox, result.m_oy = make_ox_oy(mtime_registry)
    result.c_ox, result.c_oy = make_ox_oy(ctime_registry)
    result.a_ox, result.a_oy = make_ox_oy(atime_registry)
    result.b_ox, result.b_oy = make_ox_oy(btime_registry)

    return result


FIND_DECEPTIVE_EXTENSIONS_INSPECTED_MIME_TYPES = ("image", "video")


def find_deceptive_extensions(
    directory_path: str,
    set_progress: Callable[[str], None],
    stop: Callable[[], bool],
) -> ar.FindDeceptiveExtensionsResult:
    result = ar.FindDeceptiveExtensionsResult()
    progress = Progress(16)

    files_scanned = 0
    for root, _dirnames, filenames in os.walk(directory_path):
        if stop():
            return result
        if path_is_skipped(root):
            continue
        if (string := progress.tick(files_scanned)) is not None:
            set_progress(string)

        for filename in filenames:
            filepath = os.path.join(root, filename)
            try:
                stat_result = os.lstat(filepath)
                if not stat.S_ISREG(stat_result.st_mode):
                    continue
                guessed_mime, _encoding = mimetypes.guess_file_type(filepath)
                actual_mime = magic.from_file(filepath, mime=True)
                actual_mime_type = actual_mime[: actual_mime.index("/")]
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue

            if (
                guessed_mime is not None
                and actual_mime is not None
                and guessed_mime != actual_mime
                and actual_mime_type in FIND_DECEPTIVE_EXTENSIONS_INSPECTED_MIME_TYPES
            ):
                result.mismatching_extension_and_magic_number_mimes.append(
                    f'{filepath} <span style="color: blue;">|</span> '
                    "<b>"
                    f"{guessed_mime} "
                    '<span style="color: red;">vs.</span> '
                    f"{actual_mime}"
                    "</b>",
                )
        files_scanned += len(filenames)
    return result


@dataclass
class Action:
    name: str
    callback: Callable[[str, Callable[[str], None], Callable[[], bool]], ar.ComputeResult]


action_array = (
    Action("Count stuff", count_stuff),
    Action("Modification/Change/Access dates", mca_date_graph),
    Action("Find deceptive extensions", find_deceptive_extensions),
)
action_registry = {action.name: action for action in action_array}
