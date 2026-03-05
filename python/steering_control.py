"""
Head tilt-based steering control using accelerometer.
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np
import time
from config import MAX_LEFT_ANGLE, MAX_RIGHT_ANGLE, DEADZONE

def calculate_roll(accel_y, accel_z):
    """Calculate head tilt angle (roll) from accelerometer."""
    roll = np.arctan2(accel_y, accel_z) * 180 / np.pi
    return roll

def map_roll_to_steering(roll):
    """
    Map roll angle to servo position with deadzone.
    
    Args:
        roll: Head tilt angle in degrees (negative = left, positive = right)
    
    Returns:
        steering: Servo position 0-180
    """
    # Apply deadzone
    if abs(roll) < DEADZONE:
        return 90  # Center
    
    # Clamp to max angles
    roll_clamped = max(MAX_LEFT_ANGLE, min(MAX_RIGHT_ANGLE, roll))
    
    # Map to servo range
    # Roll: -15° (left) → Servo: 0
    # Roll:   0° (center) → Servo: 90
    # Roll: +15° (right) → Servo: 180
    steering = int(np.interp(roll_clamped, 
                            [MAX_LEFT_ANGLE, MAX_RIGHT_ANGLE], 
                            [0, 180]))
    
    return steering

def main():
    print("=== Head Tilt Steering Control ===")
    print(f"Range: {MAX_LEFT_ANGLE}° to {MAX_RIGHT_ANGLE}°")
    print(f"Deadzone: ±{DEADZONE}°")
    print(f"Tilt LEFT → Turn left | Upright → Straight | Tilt RIGHT → Turn right\n")
    
    # Connect to accelerometer
    print("Looking for accelerometer stream...")
    accel_streams = resolve_byprop('type', 'ACC', timeout=10)
    
    if not accel_streams:
        print("ERROR: No accelerometer stream found!")
        return
    
    print("Connected!\n")
    inlet = StreamInlet(accel_streams[0])
    
    print("Starting steering control...")
    print("Press Ctrl+C to stop\n")
    
    sample_count = 0
    
    try:
        while True:
            sample, timestamp = inlet.pull_sample(timeout=1.0)
            
            if sample:
                accel_x, accel_y, accel_z = sample
                
                # Calculate roll
                roll = calculate_roll(accel_y, accel_z)
                
                # Map to steering
                steering = map_roll_to_steering(roll)
                
                # Print occasionally (every 5th sample = ~10 Hz)
                sample_count += 1
                if sample_count % 5 == 0:
                    if steering < 85:
                        direction = "LEFT ◀◀"
                    elif steering > 95:
                        direction = "RIGHT ▶▶"
                    else:
                        direction = "STRAIGHT ●"
                    
                    print(f"\rRoll: {roll:5.1f}° | Servo: {steering:3d} | {direction}   ", 
                          end='', flush=True)
    
    except KeyboardInterrupt:
        print("\n\nStopped.")

if __name__ == "__main__":
    main()