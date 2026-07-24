"""
Pipeline doctor - verbose, per-stage telemetry for debugging live runs.

Prints one line per update showing every stage of the pipeline so you can see
exactly where a misbehaving run goes wrong:

  EEG:  raw AF7 -> ABR (alpha/beta) -> focus gate (ALERT/DISTRACTED)
  ACC:  raw y,z -> roll -> mapped servo angle -> gated angle
  SER:  the exact command bytes that would be / were sent to the Arduino

Works identically against live hardware, replay_stream.py, or synth_stream.py -
run one of those first, then run this. Reproduce bugs against replay/synth
(deterministic) before blaming the headset.

Usage:
    python python/pipeline_doctor.py              # dry-run (prints serial, sends nothing)
    python python/pipeline_doctor.py --serial      # also send commands to Arduino

Which stage is wrong tells you which subsystem to fix (EEG focus, ACC steering,
serial, or firmware). The data collection is scripted; deciding what the trace
means is where reasoning comes in.
"""
import argparse
import sys
import time

import numpy as np
from pylsl import StreamInlet, resolve_byprop

from signal_processing import compute_abr
from steering_control import calculate_roll, map_roll_to_steering
from config import FOCUS_THRESHOLD, WINDOW_SIZE, CHECK_INTERVAL, SAMPLING_RATE


def main(use_serial=False):
    # Force line-buffered stdout so telemetry appears immediately even when this
    # is piped, backgrounded, or run in an IDE console (default block buffering
    # otherwise hides all output until the buffer fills - looks "totally blank").
    sys.stdout.reconfigure(line_buffering=True)

    print("=== PIPELINE DOCTOR ===")
    print(f"Focus threshold: ABR < {FOCUS_THRESHOLD} = ALERT")
    print("Looking for streams (run replay_stream.py / synth_stream.py / muselsl first)...")

    eeg_streams = resolve_byprop("type", "EEG", timeout=10)
    acc_streams = resolve_byprop("type", "ACC", timeout=10)
    if not eeg_streams:
        print("ERROR: no EEG stream found")
        return
    if not acc_streams:
        print("ERROR: no ACC stream found")
        return
    eeg_inlet = StreamInlet(eeg_streams[0])
    acc_inlet = StreamInlet(acc_streams[0])
    print("Connected. Streaming telemetry (Ctrl+C to stop)\n")

    arduino = None
    if use_serial:
        from controller import ArduinoController
        try:
            arduino = ArduinoController()
        except Exception:
            print("⚠ Arduino not available - continuing in dry-run\n")

    eeg_buffer = []
    last_check = time.time()
    abr = alpha = beta = 0.0
    is_alert = True

    try:
        while True:
            # Drain ALL available EEG samples each iteration. The loop is paced by
            # the ACC pull below (~52 Hz), while EEG arrives at ~256 Hz - pulling
            # only one per iteration starves the window so ABR never computes.
            while True:
                eeg_sample, _ = eeg_inlet.pull_sample(timeout=0.0)
                if not eeg_sample:
                    break
                eeg_buffer.append(eeg_sample[1])  # AF7
                if len(eeg_buffer) > WINDOW_SIZE:
                    eeg_buffer.pop(0)
            if (time.time() - last_check) >= CHECK_INTERVAL and len(eeg_buffer) >= WINDOW_SIZE:
                abr, alpha, beta = compute_abr(np.array(eeg_buffer), fs=SAMPLING_RATE)
                is_alert = abr < FOCUS_THRESHOLD
                last_check = time.time()

            acc_sample, _ = acc_inlet.pull_sample(timeout=1.0)
            if acc_sample:
                _, ay, az = acc_sample
                roll = calculate_roll(ay, az)
                mapped = map_roll_to_steering(roll)
                gated = mapped if is_alert else 90

                cmd = f"S{gated}"
                if arduino:
                    arduino.send_steering(gated)
                    ser = f"sent {cmd}"
                else:
                    ser = f"dry-run {cmd}"

                focus = "ALERT" if is_alert else "DISTRACT"
                buf = f"{len(eeg_buffer)}/{WINDOW_SIZE}"
                print(f"EEG[buf {buf:>7s} AF7={eeg_buffer[-1] if eeg_buffer else 0:8.1f} "
                      f"ABR={abr:5.2f} a={alpha:.1e} b={beta:.1e} -> {focus:8s}] | "
                      f"ACC[y={ay:+.2f} z={az:+.2f} roll={roll:+6.1f} servo={mapped:3d} "
                      f"gated={gated:3d}] | SER[{ser}]")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if arduino:
            try:
                arduino.send_throttle(0)
                arduino.send_steering(90)
            finally:
                arduino.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Per-stage pipeline telemetry")
    parser.add_argument("--serial", action="store_true",
                        help="actually send commands to the Arduino (default: dry-run)")
    args = parser.parse_args()
    main(use_serial=args.serial)
