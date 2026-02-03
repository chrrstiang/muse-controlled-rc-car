"""
Serial communication interface with Arduino.

This script:
- Establishes serial connection to Arduino
- Sends motor control commands (steering angle, throttle state)
- Handles connection errors and reconnection logic
- Provides simple command protocol for Arduino communication

Command format:
- Steering: angle value (0-180)
- Throttle: 0 (stop) or 1 (forward)
"""