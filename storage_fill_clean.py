import os
import random
import string
import subprocess
import sys

DEVICE_CMD = "adb"

FILL_FILE_PREFIX = "fillfile_"
FILL_DIR = "/sdcard/"

def run_adb(device, command):
    full_cmd = [DEVICE_CMD, "-s", device] + command
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def list_devices():
    out, _ = run_adb("", ["devices"])
    devices = []
    for line in out.splitlines()[1:]:
        if line.strip() and "device" in line:
            devices.append(line.split()[0])
    return devices

def generate_random_name():
    return FILL_FILE_PREFIX + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

def fill_storage(device, size_mb):
    file_name = generate_random_name()
    size_bytes = size_mb * 1024 * 1024
    file_path = os.path.join(FILL_DIR, file_name)
    print(f"Filling storage on {device} with file {file_path} ({size_mb} MB)...")
    cmd = f"dd if=/dev/zero of={file_path} bs={size_bytes} count=1"
    out, err = run_adb(device, ["shell", cmd])
    if err:
        print(f"Error: {err}")
    else:
        print(f"Filled {file_path} successfully.")

def clean_storage(device):
    print(f"Cleaning storage on {device}...")
    cmd = f"rm {FILL_DIR}{FILL_FILE_PREFIX}*"
    out, err = run_adb(device, ["shell", cmd])
    if err:
        print(f"Error: {err}")
    else:
        print("Cleaned all fill files successfully.")

def show_free_storage(device):
    out, _ = run_adb(device, ["shell", "df", "/sdcard"])
    print(f"Free storage on {device}:\n{out}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python storage_fill_clean.py [fill <MB> | clean | free]")
        sys.exit(1)

    action = sys.argv[1]
    devices = list_devices()
    if not devices:
        print("No devices connected.")
        sys.exit(1)

    for device in devices:
        if action == "fill":
            if len(sys.argv) < 3:
                print("Specify size in MB for fill.")
                sys.exit(1)
            size_mb = int(sys.argv[2])
            fill_storage(device, size_mb)
        elif action == "clean":
            clean_storage(device)
        elif action == "free":
            show_free_storage(device)
        else:
            print("Unknown action. Use fill, clean, or free.")
