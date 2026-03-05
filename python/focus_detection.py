"""
Real-time focus detection using Alpha/Beta Ratio.
"""

from pylsl import StreamInlet, resolve_byprop
import numpy as np
import time
from config import FOCUS_THRESHOLD, CHECK_INTERVAL, WINDOW_SIZE
from signal_processing import compute_abr

def main():
    print("=== Focus Detection System ===")
    print(f"Metric: Alpha/Beta Ratio (ABR)")
    print(f"Threshold: {FOCUS_THRESHOLD}")
    print(f"ABR < {FOCUS_THRESHOLD} = ALERT (steering enabled)")
    print(f"ABR > {FOCUS_THRESHOLD} = DISTRACTED (steering disabled)\n")
    
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
                        status = "ALERT ✓" if is_focused else "DISTRACTED ✗"
                        
                        # Display
                        print(f"{status} | ABR: {abr:.3f} | Alpha: {alpha:.2e} | Beta: {beta:.2e}")
                    
                    last_check_time = current_time
    
    except KeyboardInterrupt:
        print("\n\nStopping focus detection.")


if __name__ == "__main__":
    main()