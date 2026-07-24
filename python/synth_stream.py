"""
Synthesize controllable Muse LSL streams for deterministic scenario testing.

Unlike replay_stream.py (which replays real recordings), this generates fake
EEG + ACC data whose focus state and head-tilt are set by flags, so you can
test exactly the conditions you care about without a headset or a recording.

Focus mapping (steering gate uses Alpha/Beta Ratio, alert when ABR < threshold):
    --focus high  -> beta-dominant EEG  -> low ABR  -> ALERT   (steering enabled)
    --focus low   -> alpha-dominant EEG -> high ABR -> DISTRACTED (steering locked)

Tilt mapping (roll = arctan2(accel_y, accel_z)):
    --tilt left | center | right | sweep

Usage:
    python python/synth_stream.py --focus high --tilt left
    python python/synth_stream.py --focus low --tilt center --duration 30
    python python/synth_stream.py --focus high --tilt sweep

Deterministic tool: no LLM interaction required once started.
"""
import argparse
import math
import sys
import threading
import time

import numpy as np
from pylsl import StreamInfo, StreamOutlet, local_clock

EEG_SRATE = 256
ACC_SRATE = 52
EEG_CHANNELS = 5   # TP9, AF7, AF8, TP10, AUX (AF7 = index 1, used downstream)
GRAVITY = 0.98     # steady-state accel_z magnitude


def eeg_worker(focus, stop_event):
    # Alert/focused -> emphasize beta (~22 Hz); distracted -> emphasize alpha (~10 Hz).
    if focus == "high":
        strong_freq, strong_amp, weak_freq, weak_amp = 22.0, 60.0, 10.0, 10.0
    else:
        strong_freq, strong_amp, weak_freq, weak_amp = 10.0, 60.0, 22.0, 10.0

    info = StreamInfo("MuseSynthEEG", "EEG", EEG_CHANNELS, EEG_SRATE, "float32", "synth_eeg")
    outlet = StreamOutlet(info)
    print(f"  [EEG] focus={focus} (strong {strong_freq} Hz) -> LSL outlet 'MuseSynthEEG'")

    n = 0
    period = 1.0 / EEG_SRATE
    start = local_clock()
    while not stop_event.is_set():
        t = n / EEG_SRATE
        af7 = (strong_amp * math.sin(2 * math.pi * strong_freq * t)
               + weak_amp * math.sin(2 * math.pi * weak_freq * t)
               + np.random.normal(0, 5))
        # Only AF7 (index 1) is consumed downstream; fill others with light noise.
        sample = list(np.random.normal(0, 5, EEG_CHANNELS))
        sample[1] = af7
        outlet.push_sample(sample)
        n += 1
        drift = (n * period) - (local_clock() - start)
        if drift > 0:
            time.sleep(min(drift, 0.5))


def acc_worker(tilt, stop_event):
    info = StreamInfo("MuseSynthACC", "ACC", 3, ACC_SRATE, "float32", "synth_acc")
    outlet = StreamOutlet(info)
    print(f"  [ACC] tilt={tilt} -> LSL outlet 'MuseSynthACC'")

    fixed_angles = {"left": -20.0, "center": 0.0, "right": 20.0}
    n = 0
    period = 1.0 / ACC_SRATE
    start = local_clock()
    while not stop_event.is_set():
        if tilt == "sweep":
            angle = 22.0 * math.sin(2 * math.pi * 0.2 * (n / ACC_SRATE))  # +/-22 deg, 0.2 Hz
        else:
            angle = fixed_angles[tilt]
        rad = math.radians(angle)
        accel_y = GRAVITY * math.sin(rad)
        accel_z = GRAVITY * math.cos(rad)
        outlet.push_sample([0.0, accel_y, accel_z])
        n += 1
        drift = (n * period) - (local_clock() - start)
        if drift > 0:
            time.sleep(min(drift, 0.5))


def main():
    parser = argparse.ArgumentParser(description="Synthesize Muse EEG + ACC LSL streams")
    parser.add_argument("--focus", choices=["high", "low"], default="high",
                        help="high = alert/steering-enabled, low = distracted/locked")
    parser.add_argument("--tilt", choices=["left", "center", "right", "sweep"], default="center")
    parser.add_argument("--duration", type=float, default=None,
                        help="seconds to stream (default: until Ctrl+C)")
    args = parser.parse_args()

    # Line-buffer stdout so status shows immediately when run in the background.
    sys.stdout.reconfigure(line_buffering=True)

    print("Synthesizing Muse LSL streams (Ctrl+C to stop):")
    stop_event = threading.Event()
    threads = [
        threading.Thread(target=eeg_worker, args=(args.focus, stop_event), daemon=True),
        threading.Thread(target=acc_worker, args=(args.tilt, stop_event), daemon=True),
    ]
    for t in threads:
        t.start()

    try:
        if args.duration:
            time.sleep(args.duration)
            stop_event.set()
        else:
            while True:
                time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping synthetic streams...")
        stop_event.set()
    for t in threads:
        t.join(timeout=2.0)


if __name__ == "__main__":
    main()
