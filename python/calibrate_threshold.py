"""
Suggest a FOCUS_THRESHOLD from labeled recordings instead of guessing.

Given a session directory containing labeled EEG recordings (see labeled-recording
/ run_training_session.py, which name files eeg_<label>_<timestamp>.csv), this
groups files into "focused" vs "unfocused" by their label, computes the
Alpha/Beta Ratio (ABR) distribution for each group over 2-second windows, and
suggests a threshold midway between the two group means.

Recall the gate: ABR < FOCUS_THRESHOLD = ALERT. Focused trials should sit below
the threshold, unfocused above it.

Usage:
    python python/calibrate_threshold.py data/recordings/training/training_001

Deterministic tool: it prints a suggested number. Applying it to config.py
(FOCUS_THRESHOLD) is a one-line edit you confirm.
"""
import argparse
import glob
import os
import sys

import numpy as np
import pandas as pd

from signal_processing import calculate_band_power
from config import FOCUS_THRESHOLD, SAMPLING_RATE

AF7_COL = 2  # positional: col0=timestamp, col1=TP9, col2=AF7


def file_abrs(csv_path, window_s=2, fs=SAMPLING_RATE):
    """Mean-per-window ABR values for the AF7 channel of one recording."""
    df = pd.read_csv(csv_path, header=None, skiprows=1)
    af7 = df.iloc[:, AF7_COL].to_numpy(dtype=float)
    win = int(window_s * fs)
    abrs = []
    for i in range(len(af7) // win):
        seg = af7[i * win:(i + 1) * win]
        alpha = calculate_band_power(seg, fs, "alpha")
        beta = calculate_band_power(seg, fs, "beta")
        if beta > 0:
            abrs.append(alpha / beta)
    return abrs


def classify(filename):
    name = os.path.basename(filename).lower()
    if "unfocus" in name or "neutral" in name or "distract" in name:
        return "unfocused"
    if "focus" in name:
        return "focused"
    return None


def main():
    parser = argparse.ArgumentParser(description="Suggest FOCUS_THRESHOLD from labeled recordings")
    parser.add_argument("session_dir", help="directory containing eeg_*.csv recordings")
    parser.add_argument("--window", type=float, default=2.0, help="analysis window seconds")
    args = parser.parse_args()

    eeg_files = sorted(glob.glob(os.path.join(args.session_dir, "eeg_*.csv")))
    if not eeg_files:
        sys.exit(f"ERROR: no eeg_*.csv files in {args.session_dir}")

    groups = {"focused": [], "unfocused": []}
    unlabeled = []
    for f in eeg_files:
        label = classify(f)
        if label is None:
            unlabeled.append(f)
            continue
        groups[label].extend(file_abrs(f, args.window))

    print(f"Current config FOCUS_THRESHOLD = {FOCUS_THRESHOLD}\n")
    for label in ("focused", "unfocused"):
        vals = groups[label]
        if vals:
            arr = np.array(vals)
            print(f"{label:10s}: n={len(arr):3d}  ABR mean={arr.mean():.3f}  "
                  f"std={arr.std():.3f}  range=[{arr.min():.3f}, {arr.max():.3f}]")
        else:
            print(f"{label:10s}: no labeled recordings found")
    if unlabeled:
        print(f"\n(skipped {len(unlabeled)} unlabeled file(s): "
              f"{', '.join(os.path.basename(f) for f in unlabeled)})")

    if groups["focused"] and groups["unfocused"]:
        f_mean = np.mean(groups["focused"])
        u_mean = np.mean(groups["unfocused"])
        suggested = (f_mean + u_mean) / 2
        print(f"\nSuggested FOCUS_THRESHOLD = {suggested:.3f}  "
              f"(midpoint of focused {f_mean:.3f} and unfocused {u_mean:.3f})")
        if f_mean >= u_mean:
            print("WARNING: focused ABR is not below unfocused ABR - the groups do not "
                  "separate. Check data quality / labels before trusting this number.")
    else:
        print("\nNeed both focused and unfocused labeled recordings to suggest a threshold.")
        print("Record labeled data first (see the labeled-recording skill).")


if __name__ == "__main__":
    main()
