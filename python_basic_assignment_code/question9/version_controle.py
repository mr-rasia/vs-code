import os
import shutil
import time
import difflib

VERSION_DIR = "versions"


def create_version(file_path):

    if not os.path.exists(VERSION_DIR):
        os.makedirs(VERSION_DIR)

    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)

    version_number = 1

    while True:
        version_name = f"{name}_v{version_number}{ext}"
        version_path = os.path.join(VERSION_DIR, version_name)

        if not os.path.exists(version_path):
            shutil.copy(file_path, version_path)
            print("Version saved:", version_name)
            break

        version_number += 1


def restore_version(filename, version_number):

    name, ext = os.path.splitext(filename)
    version_file = f"{name}_v{version_number}{ext}"
    version_path = os.path.join(VERSION_DIR, version_file)

    if os.path.exists(version_path):
        shutil.copy(version_path, filename)
        print("File restored to version", version_number)
    else:
        print("Version not found")


def compare_versions(file1, file2):

    with open(file1) as f1, open(file2) as f2:

        lines1 = f1.readlines()
        lines2 = f2.readlines()

        diff = difflib.unified_diff(lines1, lines2)

        for line in diff:
            print(line)


def cleanup_versions(filename, keep_last):

    name, ext = os.path.splitext(filename)

    files = [f for f in os.listdir(VERSION_DIR) if f.startswith(name)]

    files.sort()

    if len(files) > keep_last:
        remove = files[:-keep_last]

        for f in remove:
            os.remove(os.path.join(VERSION_DIR, f))
            print("Removed old version:", f)


def monitor_directory(directory):

    last_modified = {}

    while True:

        for file in os.listdir(directory):

            path = os.path.join(directory, file)

            if os.path.isfile(path):

                mod_time = os.path.getmtime(path)

                if file not in last_modified:
                    last_modified[file] = mod_time

                elif mod_time != last_modified[file]:

                    print("File modified:", file)

                    create_version(path)

                    last_modified[file] = mod_time

        time.sleep(3)


directory = "test_folder"

monitor_directory(directory)