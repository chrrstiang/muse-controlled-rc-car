---
name: calibrate-thresholds
description: Derive a FOCUS_THRESHOLD from recorded data instead of guessing. Use when focus detection fires too often or not enough, the user wants to tune/calibrate the alertness cutoff, or needs to know the ABR distribution for focused vs unfocused trials.
---

# Calibrate Thresholds

`python/calibrate_threshold.py` reads a session of labeled recordings, computes
the Alpha/Beta Ratio (ABR) distribution for focused vs unfocused trials, and
suggests a `FOCUS_THRESHOLD` midway between the two group means.

**Division of labor:** the script produces the number deterministically. Sanity-
checking it and editing `config.py` are the confirmation steps.

## Workflow

1. Ensure a session with **labeled** focused and unfocused recordings exists
   (use the **labeled-recording** skill). Without both groups the script can't
   suggest a threshold.
2. Run it:
   ```bash
   python python/calibrate_threshold.py data/recordings/training/<session>
   ```
3. Read the output (reasoning step):
   - It prints per-group ABR mean/std/range and a `Suggested FOCUS_THRESHOLD`.
   - If it warns that focused ABR is **not** below unfocused ABR, the groups
     don't separate — don't apply the number; check data quality/labels first.
4. If the suggestion is reasonable, update `FOCUS_THRESHOLD` in
   `python/config.py` (one-line edit) and confirm with the user.
5. Verify by replaying a focused and an unfocused recording through
   `focus_detection.py` (via the **offline-replay** skill) and checking the gate
   flips at the new threshold.

## Related

- `python/quick_analysis.py <eeg_csv>` gives a deeper single-file band-power
  breakdown (theta/alpha/beta + plot) if you want to inspect one recording.
