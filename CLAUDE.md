# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a brain-computer interface (BCI) project that controls a RC car using a Muse 2 EEG headband. Head tilt (accelerometer) controls steering direction, and EEG focus detection (Alpha/Beta Ratio) acts as a safety gate — steering is only enabled when the user is alert.

**Hardware**: Muse 2 headband → macOS laptop (Bluetooth/LSL) → Arduino Uno (USB serial) → TB6612FNG motor driver → ELEGOO Smart Robot Car V4.

## Setup

```bash
# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Find Muse device
muselsl list

# Start Muse data stream (must be running before any Python scripts)
muselsl stream
# or use the helper script:
python python/muse_stream.py
```

## Running the System

All Python scripts in `python/` must be run from the repo root with the venv active. `python/` scripts import from each other using bare module names (no package prefix), so they rely on being in `sys.path`.

```bash
# Pre-flight check (verifies Muse streams + Arduino)
python tests/system_check.py

# Full BCI controller (main entry point)
python python/bci_controller.py

# Test individual components
python python/focus_detection.py      # EEG-only focus monitor
python python/steering_control.py     # Accelerometer-only steering

# Test Arduino hardware without BCI
python tests/manual_control.py        # Interactive serial command prompt

# Record training data
python python/record_session.py --duration 60 --output data/recordings
python python/run_training_session.py # Structured multi-trial sessions
```

## Arduino Firmware

The firmware lives in `arduino/` and is managed by PlatformIO.

```bash
# Build and upload (from arduino/ directory or via PlatformIO VS Code extension)
pio run --target upload

# Find Arduino serial port
ls /dev/cu.*   # Look for /dev/cu.usbserial-* or /dev/cu.usbmodem-*
```

The firmware targets Arduino Uno at 115200 baud. Serial command protocol:
- `S<angle>\n` — steering angle 0–180 (90 = center, 0 = full left, 180 = full right)
- `T<state>\n` — throttle: 0=stop, 1=forward, 2=reverse

## Configuration

All tunable parameters are in `python/config.py`. Key values to adjust:

- `ARDUINO_PORT` — must match your USB port (run `ls /dev/cu.*`)
- `MUSE_DEVICE_NAME` / `MAC_ADDRESS` — must match your Muse headband
- `FOCUS_THRESHOLD` — Alpha/Beta Ratio cutoff (default 0.85); lower = stricter alertness required
- `MAX_LEFT_ANGLE` / `MAX_RIGHT_ANGLE` / `DEADZONE` — steering sensitivity

## Architecture

The system has two concurrent data pipelines connected via LSL (Lab Streaming Layer):

```
Muse headband
  ├── EEG stream (type='EEG', 256 Hz, 4 channels: TP9, AF7, AF8, TP10)
  │     └── signal_processing.py: compute_abr() → Alpha/Beta Ratio → focus gate
  └── Accelerometer stream (type='ACC', 3-axis)
        └── steering_control.py: calculate_roll() + map_roll_to_steering() → servo angle

bci_controller.py: fuses both streams → if alert: send steering; else: lock to center
controller.py (ArduinoController): sends S<angle>/T<state> commands over serial
arduino/src/main.cpp: receives commands → differential motor speeds via TB6612FNG
```

**Focus detection** (`focus_detection.py`, `signal_processing.py`): Uses Welch's method on a rolling 512-sample (2s) window of channel AF7. Alpha/Beta Ratio (ABR) < `FOCUS_THRESHOLD` means alert/focused; higher ABR (more alpha) means distracted → steering locked.

**Steering** (`steering_control.py`): Computes roll angle via `arctan2(accel_y, accel_z)`, applies deadzone (±7.5°), then linearly maps ±25° to servo range 0–180.

**Arduino motor control** (`arduino/src/main.cpp`): Differential drive — steering bias shifts power between left/right motors. Both motors run at `FORWARD_SPEED=50` straight, with bias applied as `±(angle-90)/90`.

## Data

Training recordings are saved to `data/recordings/training/<session_name>/` as paired `eeg_<timestamp>.csv` and `acc_<timestamp>.csv` files alongside a `metadata.json`. EEG CSV columns: `timestamp, TP9, AF7, AF8, TP10`.
