"""
Replay recorded Muse sessions as live LSL streams (no headset required).

Reads paired eeg_*.csv / acc_*.csv recordings and re-publishes them as LSL
outlets typed 'EEG' and 'ACC'. Because the stream *types* match what the real
Muse produces, every downstream script (bci_controller.py, focus_detection.py,
steering_control.py, record_session.py, system_check.py) runs unchanged.

Usage:
    # Replay the newest recording in a directory
    python python/replay_stream.py data/recordings/training/training_001

    # Replay a specific EEG file (its acc_ pair is auto-matched)
    python python/replay_stream.py data/recordings/training/training_001/eeg_20260301_230435.csv

    # Loop forever at 2x speed
    python python/replay_stream.py <dir> --loop --speed 2.0

This is a deterministic tool: it needs no LLM interaction once started.
"""
import argparse
import glob
import os
import sys
import threading
import time

import pandas as pd
from pylsl import StreamInfo, StreamOutlet, local_clock

# Nominal sample rates (metadata only; actual pacing uses recorded timestamps).
EEG_SRATE = 256
ACC_SRATE = 52


def resolve_pair(path):
    """Return (eeg_csv, acc_csv_or_None) from a directory or an eeg_*.csv path."""
    if os.path.isdir(path):
        eeg_files = sorted(glob.glob(os.path.join(path, "eeg_*.csv")))
        if not eeg_files:
            sys.exit(f"ERROR: no eeg_*.csv files found in {path}")
        eeg_csv = eeg_files[-1]  # newest by name (timestamps sort lexically)
    elif os.path.isfile(path):
        eeg_csv = path
    else:
        sys.exit(f"ERROR: path not found: {path}")

    # Match acc file by swapping the eeg_ prefix for acc_.
    acc_csv = os.path.join(
        os.path.dirname(eeg_csv),
        os.path.basename(eeg_csv).replace("eeg_", "acc_", 1),
    )
    return eeg_csv, (acc_csv if os.path.isfile(acc_csv) else None)


def load_positional(csv_path):
    """Load a recording CSV positionally (col 0 = timestamp, rest = channels).

    Read positionally on purpose: EEG recordings carry a 5th (AUX) channel that
    the header row does not name, which would misalign a header-based read.
    """
    df = pd.read_csv(csv_path, header=None, skiprows=1)
    timestamps = df.iloc[:, 0].to_numpy(dtype=float)
    channels = df.iloc[:, 1:].to_numpy(dtype=float)
    return timestamps, channels


def stream_csv(csv_path, stream_type, name, srate, loop, speed, stop_event):
    timestamps, channels = load_positional(csv_path)
    n_channels = channels.shape[1]
    info = StreamInfo(name, stream_type, n_channels, srate, "float32", f"{name}_replay")
    outlet = StreamOutlet(info)
    print(f"  [{stream_type}] {os.path.basename(csv_path)} "
          f"({len(channels)} samples, {n_channels} ch) -> LSL outlet '{name}'")

    while not stop_event.is_set():
        t0 = timestamps[0]
        start = local_clock()
        for i in range(len(channels)):
            if stop_event.is_set():
                return
            target = (timestamps[i] - t0) / speed
            drift = target - (local_clock() - start)
            if drift > 0:
                time.sleep(min(drift, 1.0))  # cap to stay responsive to Ctrl+C
            outlet.push_sample(channels[i])
        if not loop:
            print(f"  [{stream_type}] finished")
            return


def main():
    parser = argparse.ArgumentParser(description="Replay recorded Muse data as LSL streams")
    parser.add_argument("path", help="recording directory or an eeg_*.csv file")
    parser.add_argument("--loop", action="store_true", help="replay continuously")
    parser.add_argument("--speed", type=float, default=1.0, help="playback speed multiplier")
    args = parser.parse_args()

    # Line-buffer stdout so status shows immediately when run in the background.
    sys.stdout.reconfigure(line_buffering=True)

    eeg_csv, acc_csv = resolve_pair(args.path)
    print("Replaying recorded session as LSL streams (Ctrl+C to stop):")

    stop_event = threading.Event()
    threads = [threading.Thread(
        target=stream_csv,
        args=(eeg_csv, "EEG", "MuseReplayEEG", EEG_SRATE, args.loop, args.speed, stop_event),
        daemon=True,
    )]
    if acc_csv:
        threads.append(threading.Thread(
            target=stream_csv,
            args=(acc_csv, "ACC", "MuseReplayACC", ACC_SRATE, args.loop, args.speed, stop_event),
            daemon=True,
        ))
    else:
        print("  WARNING: no matching acc_*.csv found; steering scripts will not see ACC data")

    for t in threads:
        t.start()

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping replay...")
        stop_event.set()
    for t in threads:
        t.join(timeout=2.0)


if __name__ == "__main__":
    main()
