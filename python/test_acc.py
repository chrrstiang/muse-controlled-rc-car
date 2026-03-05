"""
Tilt-based steering using accelerometer.
Works like a real steering wheel - position-based.
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np
import time

def calculate_roll(accel_y, accel_z):
    """Calculate head tilt angle (roll)."""
    return np.arctan2(accel_y, accel_z) * 180 / np.pi

def map_roll_to_steering(roll, max_angle=40):
    """Map roll angle to servo position."""
    # Clamp to max angles
    roll = max(-max_angle, min(max_angle, roll))
    
    # Map to servo: -40° → 0, 0° → 90, +40° → 180
    steering = int(np.interp(roll, [-max_angle, max_angle], [0, 180]))
    return steering

def main():
    # Connect to accelerometer
    accel_streams = resolve_byprop('type', 'ACC', timeout=10)
    inlet = StreamInlet(accel_streams[0])
    
    print("=== Tilt-Based Steering ===")
    print("Tilt head LEFT (ear to shoulder) → Turn left")
    print("Head upright → Go straight")
    print("Tilt head RIGHT → Turn right\n")
    
    try:
        while True:
            sample, timestamp = inlet.pull_sample(timeout=1.0)
            
            if sample:
                accel_x, accel_y, accel_z = sample
                
                roll = calculate_roll(accel_y, accel_z)
                steering = map_roll_to_steering(roll)
                
                if steering < 80:
                    direction = "LEFT ◀"
                elif steering > 100:
                    direction = "RIGHT ▶"
                else:
                    direction = "STRAIGHT ●"
                
                print(f"Roll: {roll:6.1f}° | Servo: {steering:3d} | {direction}")
                
    
    except KeyboardInterrupt:
        print("\n\nStopped.")

if __name__ == "__main__":
    main()