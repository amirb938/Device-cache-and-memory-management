import os
import random
import string
import subprocess
import sys

DEVICE_CMD = "adb"

FILL_FILE_PREFIX = "fillfile_"

# Default values
DEFAULT_FILE_SIZE_MB = 5
DEFAULT_PACKAGE_COUNT = 10

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

def list_packages(device):
    out, _ = run_adb(device, ["shell", "pm", "list", "packages"])
    return [line.replace("package:", "").strip() for line in out.splitlines()]

def generate_random_name():
    return FILL_FILE_PREFIX + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

def create_file_in_cache(device, package, size_mb):
    size_bytes = size_mb * 1024 * 1024
    file_name = generate_random_name()
    file_paths = [
        f"/data/data/{package}/cache/{file_name}",
        f"/data/user/0/{package}/cache/{file_name}",
    ]
    for path in file_paths:
        print(f"Creating {size_mb}MB file at {path} on {device}...")
        cmd = f"dd if=/dev/zero of={path} bs={size_bytes} count=1"
        out, err = run_adb(device, ["shell", cmd])
        if err:
            print(f"Error creating file in {package}: {err}")
        else:
            print(f"Created file {path} successfully.")

def fill_cache(device, package_count, file_size_mb):
    packages = list_packages(device)
    if not packages:
        print("No packages found.")
        return
    selected = random.sample(packages, min(package_count, len(packages)))
    print(f"Selected packages: {selected}")
    for pkg in selected:
        create_file_in_cache(device, pkg, file_size_mb)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cache_fill.py fill [package_count] [file_size_mb]")
        sys.exit(1)

    action = sys.argv[1]
    devices = list_devices()
    if not devices:
        print("No devices connected.")
        sys.exit(1)

    for device in devices:
        if action == "fill":
            package_count = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PACKAGE_COUNT
            file_size_mb = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_FILE_SIZE_MB
            fill_cache(device, package_count, file_size_mb)
        else:
            print("Unknown action. Only 'fill' is supported.")
