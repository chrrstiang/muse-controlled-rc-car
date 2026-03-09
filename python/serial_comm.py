"""
Serial communication with Arduino RC car.

Sends steering commands via USB serial connection.
"""

import serial
import time
from config import ARDUINO_PORT, ARDUINO_BAUD_RATE


class ArduinoController:
    """
    Interface for sending commands to Arduino RC car.
    """
    
    def __init__(self, port=ARDUINO_PORT, baud_rate=ARDUINO_BAUD_RATE):
        """
        Initialize serial connection to Arduino.
        
        Args:
            port: Serial port path (find with 'ls /dev/cu.*')
            baud_rate: Communication speed (must match Arduino)
        """
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset after connection
            print(f"✓ Connected to Arduino on {port}")
            
            # Flush any startup messages
            self.ser.reset_input_buffer()
            
        except serial.SerialException as e:
            print(f"ERROR: Could not connect to Arduino on {port}")
            print(f"  {e}")
            print("\nTroubleshooting:")
            print("  1. Check Arduino is plugged in via USB")
            print("  2. Run 'ls /dev/cu.*' to find correct port")
            print("  3. Close Arduino IDE/Serial Monitor if open")
            print("  4. Update port in config.py or when creating ArduinoController")
            raise
    
    def send_steering(self, angle):
        """
        Send steering command to Arduino.
        
        Args:
            angle: Servo position 0-180
                  (0 = full left, 90 = center, 180 = full right)
        """
        # Validate input
        if not (0 <= angle <= 180):
            print(f"Warning: Invalid steering angle {angle}, clamping to 0-180")
            angle = max(0, min(180, int(angle)))
        
        # Format command: "S90\n"
        command = f"S{angle}\n"
        
        # Send to Arduino
        self.ser.write(command.encode('utf-8'))
    
    def send_throttle(self, state):
        """
        Send throttle command to Arduino (for future use).
        
        Args:
            state: 0 = stop, 1 = forward
        """
        command = f"T{state}\n"
        self.ser.write(command.encode('utf-8'))
    
    def read_response(self):
        """
        Read any response from Arduino (for debugging).
        
        Returns:
            String from Arduino, or None if nothing available
        """
        if self.ser.in_waiting > 0:
            try:
                response = self.ser.readline().decode('utf-8').strip()
                return response
            except:
                return None
        return None
    
    def close(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Arduino connection closed")


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