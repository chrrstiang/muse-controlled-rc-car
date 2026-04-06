# Python — BCI RC Car Controller

Python scripts for reading Muse headband data, detecting focus state, and sending steering commands to the Arduino over serial.

---

## Prerequisites

- Muse 2 headband (connected via Bluetooth)
- Arduino flashed and connected via USB
- `muselsl stream --acc` running in a separate terminal before any script

Install dependencies from the project root:

```bash
pip install -r requirements.txt
```

---

## Files

### Core Application

#### `bci_controller.py`
The main entry point. Combines focus detection and head-tilt steering into a live control loop.

- Reads EEG (AF7 channel) to compute Alpha/Beta Ratio (ABR)
- Reads accelerometer for head roll angle
- **Safety gate:** steering is only applied when ABR < 0.85 (ALERT state); otherwise servo locks to center (90°)
- Sends `S{angle}` commands to Arduino every loop iteration

```bash
python bci_controller.py
```

#### `controller.py`
Serial interface to the Arduino. Used by `bci_controller.py` and test scripts.

- `ArduinoController(port, baud)` — opens the serial connection
- `send_steering(angle)` — sends `S{0–180}\n`
- `send_throttle(state)` — sends `T{0–1}\n` (future use)
- `read_response()` — reads Arduino acknowledgment

#### `config.py`
Central configuration. Edit this file to change device names, thresholds, and ports before running.

| Setting | Default | Description |
|---------|---------|-------------|
| `FOCUS_THRESHOLD` | `0.85` | ABR cutoff — below = ALERT |
| `ARDUINO_PORT` | `/dev/cu.usbserial-110` | USB serial port |
| `ARDUINO_BAUD` | `57600` | Baud rate |
| `EEG_SAMPLE_RATE` | `256` | Hz |
| `WINDOW_SIZE` | `512` | Samples per ABR calculation (~2s) |
| `STEERING_RANGE` | `±25°` | Max head tilt mapped to servo |
| `DEADZONE` | `7.5°` | Tilt below this = go straight |

---

### Individual Modules (standalone or imported)

#### `muse_stream.py`
Starts LSL streaming from the Muse headband (EEG, accelerometer, PPG, gyroscope). Run this if you need to initialize the stream manually.

```bash
python muse_stream.py
```

#### `signal_processing.py`
EEG band power calculations used by focus detection.

- `calculate_band_power(data, rate, band)` — power in theta / alpha / beta using Welch's method
- `compute_abr(data, rate)` — returns ABR, alpha power, beta power
- `plot_raw_eeg(duration)` — plots raw EEG time series

#### `focus_detection.py`
Standalone real-time attention monitor. Displays ABR, alpha/beta power, and ALERT/DISTRACTED status in the terminal. Useful for calibration before driving.

```bash
python focus_detection.py
```

#### `steering_control.py`
Standalone head-tilt steering demo. Reads accelerometer and prints the mapped servo angle in real time without connecting to the Arduino.

- `calculate_roll(ax, ay, az)` — returns head roll in degrees
- `map_roll_to_steering(roll)` — maps roll to 0–180° servo range

```bash
python steering_control.py
```

---

### Data Recording & Analysis

#### `record_session.py`
Records EEG and accelerometer data to timestamped CSV files in `data/recordings/`.

```bash
python record_session.py --duration 60 --notes "baseline session"
```

Output files: `eeg_{timestamp}.csv`, `acc_{timestamp}.csv`, optional `metadata.txt`.

#### `run_training_session.py`
Runs a structured multi-trial training session (neutral / focus / unfocus trials) with breaks between trials. Saves per-trial data and a `metadata.json` to a session directory.

```bash
python run_training_session.py
```

#### `quick_analysis.py`
Post-session analysis tool. Loads a recorded EEG CSV, computes band powers in 2-second sliding windows, and plots the raw waveform.

```bash
python quick_analysis.py eeg_20240101_120000.csv --channel AF7
```

---

## Signal Flow

```
Muse Headband (Bluetooth)
    ↓
LSL Streams
    ├── EEG (4ch @ 256 Hz)  →  signal_processing.py  →  focus_detection
    └── Accelerometer        →  steering_control.py   →  roll angle

bci_controller.py
    ├── ABR < 0.85  →  ALERT:      apply head-tilt steering
    └── ABR ≥ 0.85  →  DISTRACTED: lock servo to center (90°)
        ↓
controller.py  →  Arduino (USB Serial)  →  Servo / Motors
```

---

## Typical Workflow

```bash
# Terminal 1 — start Muse stream
muselsl stream --acc

# Terminal 2 — verify everything is connected
python ../tests/system_check.py

# Terminal 2 — run the car
python bci_controller.py
```
