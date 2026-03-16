import os
import hashlib
import shutil

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of a file"""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def scan_directory(directory, min_size):
    """Scan directory and return checksum dictionary"""
    file_hashes = {}
    duplicates = {}

    for root, dirs, files in os.walk(directory):
        for name in files:

            path = os.path.join(root, name)

            try:
                if os.path.getsize(path) < min_size:
                    continue
            except:
                continue

            checksum = calculate_checksum(path)

            if not checksum:
                continue

            if checksum in file_hashes:
                duplicates.setdefault(checksum, [file_hashes[checksum]])
                duplicates[checksum].append(path)
            else:
                file_hashes[checksum] = path

    return duplicates


def print_duplicates(duplicates):
    """Display duplicate files"""
    if not duplicates:
        print("No duplicate files found.")
        return

    print("\nDuplicate Files:\n")

    for checksum, files in duplicates.items():
        print(f"Checksum: {checksum}")
        for i, file in enumerate(files):
            print(f"  {i}. {file}")
        print()


def delete_duplicates(duplicates):
    """Delete duplicate files except the first"""
    for checksum, files in duplicates.items():
        for file in files[1:]:
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")


def move_duplicates(duplicates, target_dir):
    """Move duplicate files"""
    os.makedirs(target_dir, exist_ok=True)

    for checksum, files in duplicates.items():
        for file in files[1:]:
            try:
                destination = os.path.join(target_dir, os.path.basename(file))
                shutil.move(file, destination)
                print(f"Moved: {file} -> {destination}")
            except Exception as e:
                print(f"Error moving {file}: {e}")


def create_report(duplicates, report_file):
    """Generate duplicate report"""
    with open(report_file, "w") as f:
        for checksum, files in duplicates.items():
            f.write(f"Checksum: {checksum}\n")
            for file in files:
                f.write(f"  {file}\n")
            f.write("\n")

    print(f"\nReport saved to {report_file}")


def main():

    directory = input("Enter directory to scan: ")

    size_mb = float(input("Minimum file size to scan (MB): "))
    min_size = size_mb * 1024 * 1024

    duplicates = scan_directory(directory, min_size)

    print_duplicates(duplicates)

    if not duplicates:
        return

    print("\nOptions:")
    print("1. Delete duplicate files")
    print("2. Move duplicate files")
    print("3. Just create report")

    choice = input("Enter choice: ")

    if choice == "1":
        delete_duplicates(duplicates)

    elif choice == "2":
        target = input("Enter folder to move duplicates: ")
        move_duplicates(duplicates, target)

    create_report(duplicates, "duplicate_report.txt")


if __name__ == "__main__":
    main()