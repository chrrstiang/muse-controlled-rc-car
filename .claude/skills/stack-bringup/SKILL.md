---
name: stack-bringup
description: Bring up the full BCI stack and run a pre-flight check before driving. Use when the user wants to start/connect the system, find or sync the Arduino serial port, verify the Muse stream and Arduino are ready, or troubleshoot "no EEG stream" / wrong-port errors before running bci_controller.py.
---

# Stack Bring-up

Gets the system from "nothing running" to "verified ready" with minimal fuss.
The deterministic steps are scripted; only interpreting a failed check needs
reasoning.

## Steps

1. **Detect & sync the Arduino port** (deterministic script — writes the port
   into both `python/config.py` and `arduino/platformio.ini` so they can't drift):
   ```bash
   python python/detect_arduino.py --write
   ```
   If it reports no port: the board is unplugged, asleep, or the Arduino IDE /
   Serial Monitor is holding the port — resolve that, then rerun.

2. **Start the data source** (background, keep running):
   - Real headset: `python python/muse_stream.py` (requires the Muse paired; uses
     `MAC_ADDRESS` in `config.py`).
   - No headset / mock: use the **offline-replay** skill instead of step 2.

3. **Run the pre-flight check** (foreground):
   ```bash
   python tests/system_check.py
   ```
   It verifies EEG stream, ACC stream, and Arduino connection.

4. **Interpret the result** (this is the reasoning step):
   - All three ✓ → tell the user they can run `python python/bci_controller.py`
     (add `--drive` to move, `--no-serial` for print-only).
   - EEG/ACC ✗ → the source in step 2 isn't up (or LSL can't discover it).
   - Arduino ✗ → re-run step 1; check cable / that no other program holds the port.

## Notes

- `detect_arduino.py` without `--write` just prints the detected port (safe to
  preview). It only edits files with `--write`.
- The MAC address and port are per-machine; step 1 handles the port, and
  `config.py:MAC_ADDRESS` must match the user's Muse.
