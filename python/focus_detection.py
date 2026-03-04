"""
Real-time focus detection using Alpha/Beta Ratio.
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np
from scipy import signal
import time
from config import FOCUS_THRESHOLD, CHECK_INTERVAL, WINDOW_SIZE, SAMPLING_RATE
from signal_processing import calculate_band_power

def compute_abr(eeg_data, fs=SAMPLING_RATE):
    """
    Compute Alpha/Beta Ratio.
    
    Args:
        eeg_data: 1D array of EEG values
        fs: sampling frequency
    
    Returns:
        abr: Alpha/Beta ratio
        alpha_power: Alpha band power
        beta_power: Beta band power
    """
    alpha_power = calculate_band_power(eeg_data, fs, band_range='alpha')
    print(f"Alpha Power: {alpha_power}")

    beta_power = calculate_band_power(eeg_data, fs, band_range='beta')
    print("Beta Power: ", beta_power)
    
    abr = alpha_power / beta_power if beta_power > 0 else 0
    
    return abr, alpha_power, beta_power

def main():
    print("=== Focus Detection System ===")
    print(f"Metric: Alpha/Beta Ratio (ABR)")
    print(f"Threshold: {FOCUS_THRESHOLD}")
    print(f"ABR < {FOCUS_THRESHOLD} = FOCUSED (steering enabled)")
    print(f"ABR > {FOCUS_THRESHOLD} = UNFOCUSED (steering disabled)\n")
    
    # Connect to EEG stream
    print("Looking for EEG stream...")
    eeg_streams = resolve_byprop('type', 'EEG', timeout=10)
    
    if not eeg_streams:
        print("ERROR: No EEG stream found!")
        print("Make sure 'muselsl stream' is running")
        return
    
    print("Connected to EEG stream!\n")
    inlet = StreamInlet(eeg_streams[0])
    
    # Initialize buffer
    eeg_buffer = []
    last_check_time = time.time()
    
    print("Starting focus detection...")
    print("Try focusing (mental math or stare at point)")
    print("Try unfocusing (soft gaze, mind wander)")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Pull sample
            sample, timestamp = inlet.pull_sample(timeout=1.0)
            
            if sample:
                # Use AF7 channel (index 1) - left forehead
                # Muse channels: [TP9, AF7, AF8, TP10]
                eeg_buffer.append(sample[1])
                
                # Keep buffer at WINDOW_SIZE
                if len(eeg_buffer) > WINDOW_SIZE:
                    eeg_buffer.pop(0)
                
                # Check focus state every CHECK_INTERVAL seconds
                current_time = time.time()
                if (current_time - last_check_time) >= CHECK_INTERVAL:
                    
                    if len(eeg_buffer) >= WINDOW_SIZE:
                        # Compute ABR
                        abr, alpha, beta = compute_abr(np.array(eeg_buffer))
                        
                        # Classify
                        is_focused = abr < FOCUS_THRESHOLD
                        status = "FOCUSED ✓" if is_focused else "UNFOCUSED ✗"
                        
                        # Display
                        print(f"{status} | ABR: {abr:.3f} | Alpha: {alpha:.2e} | Beta: {beta:.2e}")
                    
                    last_check_time = current_time
    
    except KeyboardInterrupt:
        print("\n\nStopping focus detection.")


if __name__ == "__main__":
    main()