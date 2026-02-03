"""
Custom data recording utilities.
"""
import numpy as np
from pylsl import StreamInlet, resolve_byprop
import time
from datetime import datetime
import csv
import os

def record_session(duration=None, output_dir='data/recordings', notes=''):
    """
    Record EEG and gyroscope data to CSV files.
    
    Args:
        duration: Recording duration in seconds (None = until Ctrl+C)
        output_dir: Directory to save recordings
        notes: Optional notes for this recording session
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    eeg_filename = f'{output_dir}/eeg_{timestamp}.csv'
    acc_filename = f'{output_dir}/acc_{timestamp}.csv'
    
    # Save notes to metadata file if provided
    if notes:
        metadata_filename = f'{output_dir}/metadata_{timestamp}.txt'
        with open(metadata_filename, 'w') as f:
            f.write(f"Recording Session: {timestamp}\n")
            f.write(f"Duration: {duration if duration else 'Manual (Ctrl+C to stop)'} seconds\n")
            f.write(f"Notes: {notes}\n")
        print(f"Metadata saved to {metadata_filename}")
    
    # Find streams
    print("Looking for EEG stream...")
    eeg_streams = resolve_byprop('type', 'EEG', timeout=5)
    print("Looking for accelerometer stream...")
    acc_streams = resolve_byprop('type', 'ACC', timeout=5)  # or 'ACC' depending on Muse
    
    if not eeg_streams:
        print("No EEG stream found!")
        return
    
    # Create inlets
    eeg_inlet = StreamInlet(eeg_streams[0])
    acc_inlet = StreamInlet(acc_streams[0]) if acc_streams else None
    
    # Open CSV files
    eeg_file = open(eeg_filename, 'w', newline='')
    eeg_writer = csv.writer(eeg_file)
    eeg_writer.writerow(['timestamp', 'TP9', 'AF7', 'AF8', 'TP10'])  # Muse channels
    
    if acc_inlet:
        acc_file = open(acc_filename, 'w', newline='')
        acc_writer = csv.writer(acc_file)
        acc_writer.writerow(['timestamp', 'accelerometer_x', 'accelerometer_y', 'accelerometer_z'])
    
    print(f"Recording to {eeg_filename}")
    print("Press Ctrl+C to stop" if duration is None else f"Recording for {duration} seconds")
    
    start_time = time.time()
    
    try:
        while True:
            # Check duration
            if duration and (time.time() - start_time) > duration:
                break
            
            # Pull EEG sample
            eeg_sample, eeg_timestamp = eeg_inlet.pull_sample(timeout=0.0)
            if eeg_sample:
                eeg_writer.writerow([eeg_timestamp] + eeg_sample)
            
            # Pull accelerometer sample
            if acc_inlet:
                acc_sample, acc_timestamp = acc_inlet.pull_sample(timeout=0.0)
                if acc_sample:
                    acc_writer.writerow([acc_timestamp] + acc_sample)
            
    except KeyboardInterrupt:
        print("\nStopping recording...")
    
    finally:
        eeg_file.close()
        if acc_inlet:
            acc_file.close()
        
        print(f"Recording saved to {output_dir}/")
        print(f"Duration: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Record Muse data')
    parser.add_argument('--duration', type=int, default=None, 
                       help='Recording duration in seconds (default: until Ctrl+C)')
    parser.add_argument('--output', type=str, default='data/recordings',
                       help='Output directory')
    parser.add_argument('--notes', type=str, default='',
                       help='Optional notes for this recording session')
    
    args = parser.parse_args()
    record_session(duration=args.duration, output_dir=args.output, notes=args.notes)