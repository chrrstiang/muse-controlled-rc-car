"""
Complete BCI RC Car Controller.

Combines:
- Attention monitoring (EEG) - safety gate
- Head tilt steering (Accelerometer) - position control

Control logic:
- When ALERT (ABR < 0.85): Steering responds to head tilt
- When DISTRACTED (ABR > 0.85): Steering locked to center (safety)
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np
import time
from signal_processing import compute_abr
from steering_control import calculate_roll, map_roll_to_steering
from config import FOCUS_THRESHOLD, MAX_LEFT_ANGLE, MAX_RIGHT_ANGLE, DEADZONE, WINDOW_SIZE, CHECK_INTERVAL, SAMPLING_RATE

def main():
    print("=" * 60)
    print("BCI RC CAR CONTROLLER")
    print("=" * 60)
    print("\nCONTROL SCHEME:")
    print("  EEG (Alpha/Beta):  Attention monitoring")
    print("  Accelerometer:      Head tilt steering")
    print("\nPARAMETERS:")
    print(f"  Attention threshold: ABR < {FOCUS_THRESHOLD} (alert)")
    print(f"  Steering range:      {MAX_LEFT_ANGLE}° to {MAX_RIGHT_ANGLE}°")
    print(f"  Deadzone:            ±{DEADZONE}°")
    print("\nBEHAVIOR:")
    print("  ALERT + Tilt left   → Car steers left")
    print("  ALERT + Upright     → Car goes straight")
    print("  ALERT + Tilt right  → Car steers right")
    print("  DISTRACTED          → Steering DISABLED (safety lock)")
    print("\n" + "=" * 60 + "\n")
    
    # Connect to streams
    print("Connecting to streams...")
    
    print("  Looking for EEG stream...")
    eeg_streams = resolve_byprop('type', 'EEG', timeout=10)
    if not eeg_streams:
        print("  ERROR: No EEG stream found!")
        return
    print("  ✓ EEG connected")
    
    print("  Looking for accelerometer stream...")
    accel_streams = resolve_byprop('type', 'ACC', timeout=10)
    if not accel_streams:
        print("  ERROR: No accelerometer stream found!")
        return
    print("  ✓ Accelerometer connected")
    
    eeg_inlet = StreamInlet(eeg_streams[0])
    accel_inlet = StreamInlet(accel_streams[0])
    
    print("\n" + "=" * 60)
    print("SYSTEM READY!")
    print("=" * 60)
    print("\nMonitoring attention and steering...")
    print("Press Ctrl+C to stop\n")
    
    # Initialize state
    eeg_buffer = []
    last_check_time = time.time()
    is_alert = True
    current_abr = 0.0
    sample_count = 0
    
    try:
        while True:
            # === EEG Processing (Attention Monitoring) ===
            eeg_sample, _ = eeg_inlet.pull_sample(timeout=0.01)
            if eeg_sample:
                # Add to buffer (AF7 channel)
                eeg_buffer.append(eeg_sample[1])
                
                # Maintain buffer size
                if len(eeg_buffer) > WINDOW_SIZE:
                    eeg_buffer.pop(0)
                
                # Check attention state periodically
                current_time = time.time()
                if (current_time - last_check_time) >= CHECK_INTERVAL:
                    if len(eeg_buffer) >= WINDOW_SIZE:
                        eeg_array = np.array(eeg_buffer)
                        abr, alpha, beta = compute_abr(eeg_array, fs=SAMPLING_RATE)
                        
                        # Update attention state
                        is_alert = abr < FOCUS_THRESHOLD
                        current_abr = abr
                        
                        last_check_time = current_time
            
            # === Accelerometer Processing (Steering) ===
            accel_sample, _ = accel_inlet.pull_sample(timeout=1.0)
            
            if accel_sample:
                # Calculate head tilt
                accel_x, accel_y, accel_z = accel_sample
                roll = calculate_roll(accel_y, accel_z)
                
                # Calculate desired steering from tilt
                desired_steering = map_roll_to_steering(roll)
                
                # === Gate Steering with Attention State ===
                if is_alert:
                    # Alert - steering responds to head tilt
                    final_steering = desired_steering
                    attention_status = "ALERT ✓"
                else:
                    # Distracted - lock steering to center (safety)
                    final_steering = 90
                    attention_status = "DISTRACTED ✗ - STEERING DISABLED"
                
                # === Display (Occasional) ===
                sample_count += 1
                if sample_count % 10 == 0:
                    # Determine direction
                    if final_steering < 90 - DEADZONE:
                        direction = "LEFT ◀◀"
                    elif final_steering > 90 + DEADZONE:
                        direction = "RIGHT ▶▶"
                    else:
                        direction = "STRAIGHT ●"
                    
                    # Format output
                    print(f"\r{attention_status:40s} | ABR: {current_abr:.2f} | Roll: {roll:5.1f}° | Servo: {final_steering:3d} | {direction}   ",
                          end='', flush=True)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("SYSTEM STOPPED")
        print("=" * 60)


if __name__ == "__main__":
    main()