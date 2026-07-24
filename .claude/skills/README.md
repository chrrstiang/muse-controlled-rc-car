# Dev & Test Skills

Five Claude Code skills that streamline development and testing of the
Muse-controlled RC car. Each skill lives in its own folder as a `SKILL.md` and
is backed by deterministic scripts in `python/`, so Claude runs a script for the
mechanical work and only reasons about the parts that need judgment (which
scenario to use, what a diagnostic trace means, whether a suggested threshold is
sane). This keeps token usage low.

Claude discovers these automatically. You can also invoke one by name, e.g.
`/offline-replay`.

## The skills

| Skill | Use it to… | Backed by |
|-------|-----------|-----------|
| **offline-replay** | Test the pipeline **without the Muse headset** | `python/replay_stream.py`, `python/synth_stream.py` |
| **stack-bringup** | Detect/sync the Arduino port, start the stream, run a pre-flight check | `python/detect_arduino.py`, `tests/system_check.py` (fixed) |
| **pipeline-doctor** | Trace every stage to find why a live run misbehaves | `python/pipeline_doctor.py` |
| **labeled-recording** | Record training data with labels that persist | `python/record_session.py`, `python/run_training_session.py` (fixed) |
| **calibrate-thresholds** | Derive `FOCUS_THRESHOLD` from labeled data | `python/calibrate_threshold.py` |

Recommended order to adopt: **offline-replay** first (it unblocks headset-free
testing of everything else), then the rest as needed.

## Quick start — test without the headset

The highest-value workflow. In one terminal, publish mock LSL streams:

```bash
# Realistic data from a past recording
python python/replay_stream.py data/recordings/training/training_001 --loop

# …or a deterministic scenario
python python/synth_stream.py --focus high --tilt left
```

In a second terminal, run any consumer unchanged:

```bash
python python/focus_detection.py           # expect ALERT with --focus high
python python/bci_controller.py --no-serial # full fusion, print-only
python python/pipeline_doctor.py            # per-stage trace
```

`--focus high` → ALERT (steering enabled); `--focus low` → DISTRACTED (locked).
`--tilt left|center|right|sweep` drives the steering angle.

## New scripts (reference)

- **`replay_stream.py <dir|eeg_csv>`** — replays recorded CSVs as `EEG`/`ACC`
  LSL streams. `--loop`, `--speed N`. Reads CSVs positionally (EEG has an unnamed
  5th AUX channel).
- **`synth_stream.py`** — synthetic `EEG`/`ACC`. `--focus high|low`,
  `--tilt left|center|right|sweep`, `--duration N`.
- **`detect_arduino.py`** — finds the serial port; `--write` syncs it into
  `python/config.py` **and** `arduino/platformio.ini`.
- **`pipeline_doctor.py`** — verbose per-stage telemetry; `--serial` to actually
  drive the Arduino (default dry-run).
- **`calibrate_threshold.py <session_dir>`** — suggests `FOCUS_THRESHOLD` from
  labeled focused/unfocused recordings.

## Fixes made along the way

Building the skills required repairing existing breakage:

- `config.py` — removed a dictation artifact embedded in `MAC_ADDRESS`.
- `tests/system_check.py` — Arduino check imported names that don't exist; now
  imports `ArduinoController`/`ARDUINO_PORT`/`ARDUINO_BAUD_RATE` correctly.
- `signal_processing.py` — removed `print()` calls in `compute_abr()` that spammed
  every real-time iteration.
- `bci_controller.py` — now actually sends `S`/`T` commands to the Arduino
  (guarded: runs print-only if no board). Flags: `--no-serial`, `--drive`.
- `record_session.py` / `run_training_session.py` — trial labels now persist in
  filenames (previously dropped).
- `quick_analysis.py` — no longer hardcodes the `training_001` path.

## Verifying on your machine

Some checks can't run in every environment (LSL needs local multicast; scipy/
matplotlib import may vary). To verify end-to-end where LSL works:

```bash
source venv/bin/activate
# Terminal A
python python/synth_stream.py --focus high --tilt left
# Terminal B
python python/focus_detection.py     # should print ALERT
python python/synth_stream.py --focus low   # re-run A with this; B should print DISTRACTED
```
