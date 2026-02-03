"""
Head movement-based steering control for RC car.

This script:
- Reads head movement data from Muse headband via LSL stream
- Maps head tilt angles to steering commands
- Handles calibration of neutral head position
- Sends steering commands to Arduino via serial

Usage:
    python head_control.py
"""