"""
Configuration settings for BCI RC car system.

Contains:
- Serial port configuration (port name, baud rate)
- EEG processing parameters (sampling rate, filter settings)
- Focus detection thresholds (alpha/beta ratio cutoffs)
- Gyroscope calibration parameters (neutral angles, sensitivity)
- LSL stream names and identifiers

Modify these values to tune system behavior without changing core logic.
"""

# Muse device & address, change this to your device if using a different one. Run muselsl list to find your device.
MUSE_DEVICE_NAME = "Muse-DF97"
MAC_ADDRESS = "2B4C914C-27D1-Okay it's B83C-2547-678EB30BA1E4"

# Focus detection thresholds (alpha/beta ratio cutoffs)
FOCUS_THRESHOLD = 0.85
CHECK_INTERVAL = 0.1
SAMPLING_RATE = 256
WINDOW_SIZE = 512

# Steering (enabled only when focused)
STEERING_ENABLED_WHEN = "focused"
MAX_LEFT_ANGLE = -25
MAX_RIGHT_ANGLE = 25
DEADZONE = 7.5

# Safety
UNFOCUS_STEERING = 90  # Center position when unfocused
SMOOTH_TRANSITION = True  # Gradually return to center
TRANSITION_TIME = 0.5  # Seconds to transition

# Arduino
ARDUINO_PORT = '/dev/cu.usbmodem14201'
ARDUINO_BAUD_RATE = 115200

