"""
Manual firmware test — type commands to steer and control throttle.

Commands:
  S<angle>   — set steering angle (0–180). e.g. S90, S0, S180
  T0 / T1    — throttle stop / forward
  left       — full left  (S0)
  center     — center     (S90)
  right      — full right (S180)
  q / quit   — exit (returns servo to center first)

NOTE: main.cpp uses 115200 baud. If config.py says 57600, update one to match.
"""

import sys
import serial
import time
import os

# Add parent directory to path so we can import python modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from python.config import ARDUINO_PORT, ARDUINO_BAUD_RATE
from python.controller import ArduinoController

SHORTCUTS = {
    'left':   'S0',
    'center': 'S90',
    'right':  'S180',
    'stop':   'T0',
    'go':     'T1',
}

def connect(port, baud):
    print(f"Connecting to {port} @ {baud} baud...")
    try:
        ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)  # wait for Arduino reset
        ser.reset_input_buffer()
        print("Connected.\n")
        return ser
    except serial.SerialException as e:
        print(f"ERROR: {e}")
        print("  1. Check USB cable and port")
        print("  2. Run: ls /dev/cu.*  to find the correct port")
        print("  3. Close Arduino IDE / Serial Monitor if open")
        sys.exit(1)

def drain(ser):
    """Print any waiting lines from Arduino."""
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"  Arduino: {line}")

def send(ser, raw):
    """Send a raw command string (adds newline) and print the response."""
    command = raw.strip() + '\n'
    ser.write(command.encode('utf-8'))
    time.sleep(0.05)
    drain(ser)

def main():
    ser = connect(ARDUINO_PORT, ARDUINO_BAUD_RATE)

    # Print startup banner from Arduino
    time.sleep(0.5)
    drain(ser)

    print("Manual control ready. Type a command (or 'q' to quit).")
    print("  Steering: S0  S45  S90  S135  S180")
    print("  Throttle: T0 (stop)  T1 (forward)")
    print("  Shortcuts: left, center, right, stop, go\n")

    try:
        while True:
            try:
                raw = input("cmd> ").strip()
            except EOFError:
                break

            if not raw:
                continue

            if raw.lower() in ('q', 'quit', 'exit'):
                print("Returning servo to center...")
                send(ser, 'S90')
                break

            # Expand shortcuts
            cmd = SHORTCUTS.get(raw.lower(), raw.upper())

            # Basic client-side validation
            if cmd.startswith('S'):
                try:
                    angle = int(cmd[1:])
                    if not (0 <= angle <= 180):
                        print(f"  Invalid angle {angle} — must be 0–180")
                        continue
                except ValueError:
                    print(f"  Bad steering command: {cmd}")
                    continue
            elif cmd.startswith('T'):
                if cmd[1:] not in ('0', '1', '2'):
                    print(f"  Bad throttle command: {cmd}  (use T0, T1, or T2)")
                    continue
            else:
                print(f"  Unknown command: {cmd}")
                continue

            send(ser, cmd)

    finally:
        ser.close()
        print("Connection closed.")

if __name__ == '__main__':
    main()
