"""
Structured recording sessions with metadata.
"""
import os
import json
from datetime import datetime
from record_session import record_session  # Import your recording function

def run_training_session(session_name, trials):
    """
    Run a structured training session with multiple trials.
    
    Args:
        session_name: Name for this session (e.g., 'training_001')
        trials: List of trial dicts with 'type', 'duration', 'notes'
    """
    # Create session directory
    session_dir = f'data/recordings/training/{session_name}'
    os.makedirs(session_dir, exist_ok=True)
    
    # Create metadata
    metadata = {
        'session_id': session_name,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'subject': 'Christian',
        'tasks': trials
    }
    
    # Save metadata
    with open(f'{session_dir}/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Starting session: {session_name}")
    print(f"Total trials: {len(trials)}")
    
    # Run each trial
    for i, trial in enumerate(trials, 1):
        print(f"\n--- Trial {i}/{len(trials)} ---")
        print(f"Type: {trial['type']}")
        print(f"Duration: {trial['duration']}s")
        print(f"Task: {trial['notes']}")
        
        input("Press Enter when ready to start...")
        
        # Record trial
        filename_prefix = f"eeg_{trial['type']}_trial_{i}"
        record_session(
            duration=trial['duration'],
            output_dir=session_dir
        )
        
        print(f"Trial {i} complete!")
        
        # Short break between trials
        if i < len(trials):
            print("Take a 30-second break...")
            import time
            time.sleep(30)
    
    print(f"\nSession complete! Data saved to {session_dir}")


if __name__ == "__main__":
    # Example: Focus detection training session
    trials = [
        {'type': 'focus', 'duration': 30, 'notes': 'Mental math (counting by 7s)'},
        {'type': 'unfocus', 'duration': 30, 'notes': 'Eyes closed, relaxed'},
        {'type': 'focus', 'duration': 30, 'notes': 'Visual focus on object'},
        {'type': 'unfocus', 'duration': 30, 'notes': 'Mind wandering'},
        {'type': 'focus', 'duration': 30, 'notes': 'Mental math again'},
    ]
    
    run_training_session('training_001', trials)