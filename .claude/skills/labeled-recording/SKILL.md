---
name: labeled-recording
description: Record EEG+ACC training data with labels that persist in the filenames, feeding the offline-replay and calibrate-thresholds skills. Use when the user wants to collect/record a session, capture focused vs unfocused/neutral trials, or build reusable mock data.
---

# Labeled Recording

Records `eeg_<label>_<timestamp>.csv` + `acc_<label>_<timestamp>.csv`, so trial
type is preserved, files never collide, and recordings stay replay-compatible
(the `eeg_`/`acc_` prefixes are intact).

**Division of labor:** recording is a deterministic script. Deciding the trial
structure (labels, durations, tasks) with the user is the only reasoning part.

## Options

- **Single labeled clip:**
  ```bash
  python python/record_session.py --duration 30 --label focus \
      --output data/recordings/training/<session> --notes "mental math"
  ```

- **Structured multi-trial session** (prompts between trials, writes
  `metadata.json`, labels each trial `<type>_trial<i>`):
  ```bash
  python python/run_training_session.py
  ```
  Edit the `trials` list at the bottom of the file to change task types /
  durations before running.

## Workflow

1. Make sure a data source is up: real Muse via the **stack-bringup** skill.
   (Recording from replayed/synth data is possible but only reproduces existing
   data — record from the headset for new data.)
2. Use meaningful labels — `calibrate-thresholds` groups by them: names
   containing `focus` → focused; `unfocus`/`neutral`/`distract` → unfocused.
3. After recording, the session directory can be replayed directly with the
   **offline-replay** skill and analyzed with **calibrate-thresholds**.

## Notes

- Label goes in the filename only; keep it short and lowercase.
- For a balanced calibration set, record both focused and unfocused trials.
