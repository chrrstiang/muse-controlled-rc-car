"""
Pre-flight system check.
Verifies all components are working before running BCI controller.
"""

from pylsl import resolve_byprop, StreamInlet
import time

def check_eeg_stream():
    """Check if EEG stream is available."""
    print("Checking EEG stream...", end=' ')
    streams = resolve_byprop('type', 'EEG', timeout=5)
    
    if streams:
        print("✓ FOUND")
        inlet = StreamInlet(streams[0])
        sample, _ = inlet.pull_sample(timeout=2.0)
        if sample:
            print(f"  Sample quality: {len(sample)} channels detected")
            return True
        else:
            print("  ✗ No data received")
            return False
    else:
        print("✗ NOT FOUND")
        return False

def check_accelerometer_stream():
    """Check if accelerometer stream is available."""
    print("Checking accelerometer stream...", end=' ')
    streams = resolve_byprop('type', 'ACC', timeout=5)
    
    if streams:
        print("✓ FOUND")
        inlet = StreamInlet(streams[0])
        sample, _ = inlet.pull_sample(timeout=2.0)
        if sample:
            print(f"  Sample received: {len(sample)} axes")
            return True
        else:
            print("  ✗ No data received")
            return False
    else:
        print("✗ NOT FOUND")
        return False

def check_arduino():
    """Check if Arduino is connected."""
    print("Checking Arduino connection...", end=' ')
    
    try:
        from serial_comm import ArduinoController
        from config import SERIAL_PORT, BAUD_RATE
        
        arduino = ArduinoController(port=SERIAL_PORT, baud_rate=BAUD_RATE)
        arduino.close()
        print("✓ CONNECTED")
        return True
    except Exception as e:
        print(f"✗ NOT FOUND")
        print(f"  Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("BCI RC CAR - SYSTEM CHECK")
    print("=" * 60 + "\n")
    
    results = {}
    
    # Check Muse streams
    print("=" * 60)
    print("MUSE HEADBAND")
    print("=" * 60)
    results['eeg'] = check_eeg_stream()
    results['accel'] = check_accelerometer_stream()
    
    # Check Arduino
    print("\n" + "=" * 60)
    print("ARDUINO")
    print("=" * 60)
    results['arduino'] = check_arduino()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    required = ['eeg', 'accel']
    optional = ['arduino']
    
    all_required = all(results.get(k, False) for k in required)
    
    if all_required:
        print("✓ All required components working!")
        
        if results['arduino']:
            print("✓ Arduino connected - ready for hardware control")
        else:
            print("⚠ Arduino not connected - can run in simulation mode")
        
        print("\n→ You can run: python python/bci_controller.py")
    else:
        print("✗ Missing required components:")
        for component in required:
            if not results.get(component, False):
                print(f"  - {component}")
        print("\nFix these issues before running the controller.")
    
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()