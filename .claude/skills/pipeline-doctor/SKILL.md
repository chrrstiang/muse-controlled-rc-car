---
name: pipeline-doctor
description: Diagnose why the car misbehaves mid-run by tracing every pipeline stage. Use when steering/focus behaves wrong, the car does not respond as expected, or the user needs to isolate whether the fault is EEG focus detection, accelerometer steering, serial commands, or firmware.
---

# Pipeline Doctor

`python/pipeline_doctor.py` prints one line per update covering every stage:

```
EEG[buf .. AF7=.. ABR=.. a=.. b=.. -> ALERT/DISTRACT] | ACC[y=.. z=.. roll=.. servo=.. gated=..] | SER[dry-run/sent S..]
```

**Division of labor:** the script collects the trace deterministically. Reading
the trace to decide which subsystem is broken is the reasoning step.

## Workflow

1. **Reproduce deterministically first.** Start a known input via the
   **offline-replay** skill (prefer `synth_stream.py --focus high --tilt left`
   so you know the expected output), in the background.
2. Run the doctor (dry-run sends nothing to the car):
   ```bash
   python python/pipeline_doctor.py
   ```
   Add `--serial` to also send real commands to the Arduino.
3. **Bisect using the columns** (the reasoning):
   - `AF7` flat/zero or `ABR` NaN/constant → EEG side (stream, buffer, or
     electrode contact on live runs).
   - `focus` stuck wrong vs. the known scenario → threshold / `compute_abr`.
   - `roll`/`servo` wrong for the known tilt → accelerometer mapping
     (`steering_control.calculate_roll` / `map_roll_to_steering`).
   - `gated` differs from `servo` unexpectedly → the focus gate is locking
     steering (expected when DISTRACTED).
   - Trace correct but the car still misbehaves with `--serial` → serial or
     firmware (`arduino/src/main.cpp`); confirm with the **manual_control** test.
4. Once the failing stage is known, fix it and re-run against the same synth
   scenario to confirm.

## Notes

- Compare live behavior against the identical synth scenario: if synth is
  correct but live is wrong, the fault is upstream of the code (headset signal,
  wiring, or the physical car), not the pipeline logic.
