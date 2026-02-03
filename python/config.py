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

MUSE_STREAM_NAME = "Muse-DF97"
MAC_ADDRESS = "2B4C914C-27D1-B83C-2547-678EB30BA1E4"
