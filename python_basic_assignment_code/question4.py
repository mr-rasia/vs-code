import subprocess
import logging
import sys

logging.basicConfig(
    filename="package_update.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, 
			capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        logging.error("Command failed: {}".format(e))
        return "", str(e), 1


def detect_package_manager():
    apt_check = subprocess.run("which apt", shell=True, 
			capture_output=True)
    yum_check = subprocess.run("which yum", shell=True, 
			capture_output=True)

    if apt_check.returncode == 0:
        return "apt"
    elif yum_check.returncode == 0:
        return "yum"
    else:
        print("No supported package manager found")
        sys.exit(1)


def list_updates(pkg_manager):

    if pkg_manager == "apt":
        print("Checking updates...")
        run_command("sudo apt update")
        output, _, _ = run_command("apt list --upgradable")

    elif pkg_manager == "yum":
        output, _, _ = run_command("yum check-update")

    packages = []
    print("\nAvailable Updates:\n")

    for i, line in enumerate(output.splitlines()):
        if "/" in line or "." in line:
            print("{} {}".format(i, line))
            packages.append(line.split()[0])

    return packages


def install_all(pkg_manager):

    print("\nUpdating all packages...")

    if pkg_manager == "apt":
        cmd = "sudo apt upgrade -y"
    else:
        cmd = "sudo yum update -y"

    out, err, code = run_command(cmd)

    if code == 0:
        print("All packages updated successfully")
        logging.info("All packages updated successfully")
    else:
        print("Error updating packages")
        logging.error(err)


def install_specific(pkg_manager, packages):

    index = int(input("\nEnter package index number: "))

    if index >= len(packages):
        print("Invalid index")
        return

    package = packages[index]
    print("\nUpdating {}\n".format(package))

    if pkg_manager == "apt":
        cmd = "sudo apt install -y {}".format(package)
    else:
        cmd = "sudo yum install -y {}".format(package)

    out, err, code = run_command(cmd)

    if code == 0:
        print("{} updated successfully".format(package))
        logging.info("{} updated successfully".format(package))
    else:
        print("Failed to update {}".format(package))
        logging.error(err)


def main():

    pkg_manager = detect_package_manager()

    packages = list_updates(pkg_manager)

    print("\nChoose an option:")
    print("1. Update all packages")
    print("2. Update specific package")

    choice = input("Enter choice: ")

    if choice == "1":
        install_all(pkg_manager)
    elif choice == "2":
        install_specific(pkg_manager, packages)
    else:
        print("Invalid option")


if __name__ == "__main__":
    main()