"""
Serial communication with Arduino RC car.

Sends steering commands via USB serial connection.
"""

import time
from config import ARDUINO_PORT
from controller import ArduinoController


def test_steering():
    """Test serial communication with Arduino."""
    print("=== Arduino Steering Communication Test ===\n")
    
    print(f"Attempting to connect to Arduino on {ARDUINO_PORT}...")
    print("(Update ARDUINO_PORT in config.py if this fails)\n")
    
    try:
        arduino = ArduinoController(port=ARDUINO_PORT)
    except Exception as e:
        print(f"\nConnection failed: {e}")
        print("\nSteps to fix:")
        print("1. Plug in Arduino via USB")
        print("2. Run: ls /dev/cu.*")
        print("3. Find the /dev/cu.usbmodem* entry")
        print("4. Update PORT in this script")
        return
    
    print("\n✓ Connection successful!")
    print("\nTesting steering commands...")
    print("Watch the servo move!\n")
    
    try:
        # Test sequence
        test_positions = [
            (90, "Center"),
            (0, "Full Left"),
            (90, "Center"),
            (180, "Full Right"),
            (90, "Center"),
            (45, "Half Left"),
            (135, "Half Right"),
            (90, "Center"),
        ]
        
        for angle, name in test_positions:
            print(f"→ {name:15s} (Servo: {angle:3d}°)", end='')
            arduino.send_steering(angle)
            time.sleep(1.5)
            
            # Check for Arduino responses
            response = arduino.read_response()
            if response:
                print(f"  |  Arduino: {response}")
            else:
                print()
        
        print("\n" + "=" * 60)
        print("✓ Test complete!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    
    finally:
        # Return to center before closing
        print("\nReturning servo to center...")
        arduino.send_steering(90)
        time.sleep(0.5)
        arduino.close()


if __name__ == "__main__":
    test_steering()