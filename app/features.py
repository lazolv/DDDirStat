import os


def count_everything(directory_path: str) -> int:
    count = 0
    for _dirpath, dirnames, filenames in os.walk(directory_path):
        count += len(filenames) + len(dirnames)
    return count


def count_files(directory_path: str) -> int:
    file_count = 0
    for _dirpath, _dirnames, filenames in os.walk(directory_path):
        file_count += len(filenames)
    return file_count


def count_directories(directory_path: str) -> int:
    file_count = 0
    for _dirpath, dirnames, _filenames in os.walk(directory_path):
        file_count += len(dirnames)
    return file_count
