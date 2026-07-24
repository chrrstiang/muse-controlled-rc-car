---
name: offline-replay
description: Test the BCI pipeline without the Muse headset by feeding recorded or synthetic LSL data. Use when the user wants to run bci_controller.py, focus_detection.py, or steering_control.py without wearing/pairing the Muse, iterate on focus/steering logic against reproducible data, or reproduce a scenario (focused/distracted, tilt left/right) on demand.
---

# Offline Replay (mock-data harness)

Two standalone scripts publish LSL streams typed `EEG` and `ACC`, exactly like a
real Muse. Any downstream script (`bci_controller.py`, `focus_detection.py`,
`steering_control.py`, `record_session.py`, `system_check.py`) then runs
unchanged, headset-free.

**Division of labor:** the scripts are fully deterministic — no LLM reasoning is
needed to run them. Only choosing which source/scenario fits the user's goal
needs a decision.

## Choose a source

- **Replay a real recording** — realistic data from a past session:
  ```bash
  python python/replay_stream.py data/recordings/training/training_001
  ```
  Give a directory (uses the newest `eeg_*.csv` + its `acc_*` pair) or a specific
  `eeg_*.csv`. Flags: `--loop` (repeat forever), `--speed 2.0` (faster).

- **Synthesize a controlled scenario** — deterministic focus/tilt on demand:
  ```bash
  python python/synth_stream.py --focus high --tilt left
  ```
  `--focus high` = ALERT (low ABR, steering enabled); `--focus low` = DISTRACTED
  (high ABR, steering locked). `--tilt left|center|right|sweep`. `--duration N`.

## Workflow

1. Start the source **in the background** (it must keep running):
   run `replay_stream.py` or `synth_stream.py` with `run_in_background: true`.
2. Wait ~2s for the LSL outlets to come up.
3. Run the target script in the foreground, e.g. `python python/focus_detection.py`
   or `python python/bci_controller.py --no-serial`.
4. Confirm the output matches the expected scenario (e.g. `--focus high` →
   `ALERT`; `--tilt left` → servo < 90).
5. Stop the background source when done.

## Notes

- LSL discovery uses local networking; this only works on a machine where LSL
  works (the same one `muselsl` runs on).
- Use `synth_stream.py` for pass/fail assertions (deterministic); use
  `replay_stream.py` when you need realistic signal shapes.
