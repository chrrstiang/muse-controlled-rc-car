"""
Detect the Arduino serial port and (optionally) sync it into both config files.

The port lives in two places that must agree:
  - python/config.py        (ARDUINO_PORT)      -> used by the Python side
  - arduino/platformio.ini  (upload_port)       -> used by firmware upload

Manually editing both is error-prone, so this script finds the port and writes
it to both, keeping them from drifting.

Usage:
    python python/detect_arduino.py           # detect and print (no changes)
    python python/detect_arduino.py --write    # detect and update both files

Deterministic tool: no LLM interaction required.
"""
import argparse
import glob
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PY = os.path.join(REPO_ROOT, "python", "config.py")
PLATFORMIO_INI = os.path.join(REPO_ROOT, "arduino", "platformio.ini")


def detect_ports():
    """Return candidate Arduino serial ports (usbserial / usbmodem)."""
    ports = sorted(glob.glob("/dev/cu.usbserial-*") + glob.glob("/dev/cu.usbmodem-*"))
    return ports


def update_config_py(port):
    with open(CONFIG_PY) as f:
        text = f.read()
    new_text, n = re.subn(r"ARDUINO_PORT\s*=\s*['\"][^'\"]*['\"]",
                          f"ARDUINO_PORT = '{port}'", text)
    if n == 0:
        print(f"  WARNING: ARDUINO_PORT not found in {CONFIG_PY}")
        return False
    with open(CONFIG_PY, "w") as f:
        f.write(new_text)
    print(f"  updated {os.path.relpath(CONFIG_PY, REPO_ROOT)} -> ARDUINO_PORT = '{port}'")
    return True


def update_platformio_ini(port):
    with open(PLATFORMIO_INI) as f:
        text = f.read()
    new_text, n = re.subn(r"upload_port\s*=\s*\S+", f"upload_port = {port}", text)
    if n == 0:
        print(f"  WARNING: upload_port not found in {PLATFORMIO_INI}")
        return False
    with open(PLATFORMIO_INI, "w") as f:
        f.write(new_text)
    print(f"  updated {os.path.relpath(PLATFORMIO_INI, REPO_ROOT)} -> upload_port = {port}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Detect and sync the Arduino serial port")
    parser.add_argument("--write", action="store_true",
                        help="write the detected port into config.py and platformio.ini")
    args = parser.parse_args()

    ports = detect_ports()
    if not ports:
        print("No Arduino serial port found (looked for /dev/cu.usbserial-* and /dev/cu.usbmodem-*).")
        print("Is the Arduino plugged in via USB? Is the Arduino IDE/Serial Monitor closed?")
        sys.exit(1)

    if len(ports) > 1:
        print("Multiple candidate ports found:")
        for p in ports:
            print(f"  {p}")
        print(f"Using the first: {ports[0]}")
    port = ports[0]
    print(f"Detected Arduino port: {port}")

    if args.write:
        update_config_py(port)
        update_platformio_ini(port)
    else:
        print("(run with --write to sync this into config.py and platformio.ini)")


if __name__ == "__main__":
    main()
