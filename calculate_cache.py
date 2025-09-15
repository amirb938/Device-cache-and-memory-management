import subprocess
import argparse

DEFAULT_TARGET = "."

def run_adb(cmd):
    result = subprocess.run(["adb", "shell"] + cmd, capture_output=True, text=True)
    return result.stdout.strip()

def enable_root():
    print("🔑 Attempting to enable adb root...")
    output = subprocess.run(["adb", "root"], capture_output=True, text=True)
    print(output.stdout.strip())

def get_packages(target):
    output = run_adb(["pm", "list", "packages"])
    packages = [line.replace("package:", "").strip() for line in output.splitlines() if target in line]
    return packages

def get_cache_size(pkg):
    output = run_adb(["du", "-s", f"/data/data/{pkg}/cache"])
    try:
        size_kb = int(output.split()[0])
    except Exception:
        size_kb = 0
    return size_kb

def format_size(kb):
    mb = kb / 1024
    return f"{kb} KB ({mb:.2f} MB)"

def print_sorted_by_cache(packages):
    """Sort packages by cache size (descending) and print."""
    package_sizes = [(pkg, get_cache_size(pkg)) for pkg in packages]
    package_sizes.sort(key=lambda x: x[1], reverse=True)

    total = 0
    print("\n📦 Cache sizes (sorted by size):\n")
    for pkg, size in package_sizes:
        total += size
        print(f"{pkg:<50} {format_size(size)}")
    print("\n=====================================")
    print(f"Total cache size: {format_size(total)}")

def main():
    parser = argparse.ArgumentParser(description="Calculate cache size of apps matching a package string")
    parser.add_argument("-p", "--package", default=DEFAULT_TARGET,
                        help=f"Target string in package name (default: '{DEFAULT_TARGET}')")
    args = parser.parse_args()

    target = args.package
    enable_root()

    packages = get_packages(target)
    if not packages:
        print(f"No packages found containing '{target}'")
        return

    print_sorted_by_cache(packages)

if __name__ == "__main__":
    main()
