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
