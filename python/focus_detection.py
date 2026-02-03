"""
Focus state detection from EEG signals.

This script:
- Receives EEG data from Muse headband via LSL stream
- Computes band power ratios (alpha/beta) for focus detection
- Applies filtering and signal processing to clean EEG data
- Determines binary focus state (focused/unfocused) based on thresholds
- Returns focus state for motor control (forward when focused, stop otherwise)

Key functions:
- compute_band_power(): Calculate power in specific frequency bands
- detect_focus(): Determine if user is in focused state
"""