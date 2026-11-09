import os
from dataclasses import dataclass, field


@dataclass
class CountStuffResult:
    objects_total: int = 0
    files_total: int = 0
    dirs_total: int = 0
    empty_dir_count: int = 0
    empty_file_count: int = 0
    executable_file_count: int = 0
    extension_counts: dict[str, int] = field(default_factory=dict)


def count_stuff(directory_path: str) -> CountStuffResult:
    result = CountStuffResult()
    for root, dirnames, filenames in os.walk(directory_path):
        result.files_total += len(filenames)
        result.dirs_total += len(dirnames)
        if dirnames == [] and filenames == []:
            result.empty_dir_count += 1
        for filename in filenames:
            filepath = os.path.join(root, filename)
            extension = os.path.splitext(filename)[1]
            statinfo = os.lstat(filepath)

            result.empty_file_count += statinfo.st_size == 0

            if any(int(d) % 2 == 1 for d in oct(statinfo.st_mode)[-3:]):
                result.executable_file_count += 1

            result.extension_counts[extension] = result.extension_counts.get(extension, 0) + 1
    result.objects_total = result.files_total + result.dirs_total
    return result
