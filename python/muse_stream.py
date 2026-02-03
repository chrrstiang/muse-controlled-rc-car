"""
Muse headband data acquisition utilities.

This script:
- Connects to Muse headband via Bluetooth and LSL
- Sets up LSL streams for EEG and gyroscope data
- Provides helper functions to read real-time data buffers
- Handles stream initialization and error checking

Data streams:
- EEG: 4 channels (TP9, AF7, AF8, TP10) at 256 Hz
- Gyroscope: 3-axis accelerometer data for head movement
"""
from muselsl import stream, list_muses
from config import MAC_ADDRESS

muses = list_muses()

if not muses:
    print("No Muse devices found.")
    exit(1)
print(muses)

print("Starting stream...")
stream(MAC_ADDRESS, ppg_enabled=True, acc_enabled=True)

print("Streaming is now over.")