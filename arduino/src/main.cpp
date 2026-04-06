#include <Arduino.h>
#include <Servo.h>

// ==================== PIN CONFIGURATION ====================
// Steering servo — moved to pin 4 (pin 7 is used by motor IN1)
#define SERVO_PIN 4

// Motor driver (TB6612FNG) - Elegoo Smart Car V4 pin mapping
#define MOTOR_ENA 5  // Left motor speed (PWM)
#define MOTOR_IN1 7  // Left motor direction
#define MOTOR_IN2 8  // Left motor direction
#define MOTOR_ENB 6  // Right motor speed (PWM)
#define MOTOR_IN3 9  // Right motor direction
#define MOTOR_IN4 11 // Right motor direction
#define MOTOR_STBY 3 // TB6612 standby pin — must be HIGH to enable motors

// ==================== CONFIGURATION ====================
const int FORWARD_SPEED = 50; // Start with 0 (motors off for initial testing)
                              // Increase to 80-120 once steering works

// ==================== OBJECTS ====================
Servo steeringServo;

// ==================== STATE ====================
int currentSteeringAngle = 90; // Start at center
int currentThrottle = 0;       // Start stopped

// ==================== FUNCTION DECLARATIONS ====================
void handleSteeringCommand(String command);
void handleThrottleCommand(String command);

// ==================== SETUP ====================
void setup()
{
    // Initialize serial communicatio
    Serial.begin(115200);

    // Attach and initialize servo
    steeringServo.attach(SERVO_PIN);
    steeringServo.write(90); // Center position

    // Setup motor pins
    pinMode(MOTOR_IN1, OUTPUT);
    pinMode(MOTOR_IN2, OUTPUT);
    pinMode(MOTOR_IN3, OUTPUT);
    pinMode(MOTOR_IN4, OUTPUT);
    pinMode(MOTOR_ENA, OUTPUT);
    pinMode(MOTOR_ENB, OUTPUT);
    pinMode(MOTOR_STBY, OUTPUT);

    // Enable TB6612 (pull standby HIGH)
    digitalWrite(MOTOR_STBY, HIGH);

    // Initialize motors (stopped)
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
    digitalWrite(MOTOR_IN3, LOW);
    digitalWrite(MOTOR_IN4, LOW);
    analogWrite(MOTOR_ENA, 0);
    analogWrite(MOTOR_ENB, 0);

    // Small delay for servo to reach position
    delay(500);

    // Startup message
    Serial.println("=========================================");
    Serial.println("BCI RC Car - Arduino Controller");
    Serial.println("=========================================");
    Serial.println("Ready to receive commands");
    Serial.println("Waiting for serial input...");
    Serial.println();
}

// ==================== MAIN LOOP ====================
void loop()
{
    // Check for incoming serial commands
    if (Serial.available() > 0)
    {
        // Read command until newline
        String command = Serial.readStringUntil('\n');
        command.trim(); // Remove whitespace

        // Parse and execute command
        if (command.length() > 0)
        {
            char commandType = command.charAt(0);

            if (commandType == 'S')
            {
                // Steering command: "S90"
                handleSteeringCommand(command);
            }
            else if (commandType == 'T')
            {
                // Throttle command: "T1" or "T0"
                handleThrottleCommand(command);
            }
            else
            {
                // Unknown command
                Serial.print("ERROR: Unknown command type: ");
                Serial.println(commandType);
            }
        }
    }

    // Small delay to prevent overwhelming the servo
    delay(10);
}

// ==================== COMMAND HANDLERS ====================
void handleSteeringCommand(String command)
{
    /**
     * Handle steering command.
     * Format: "S<angle>" where angle is 0-180
     * Example: "S90" = center, "S0" = full left, "S180" = full right
     */

    // Extract angle from command (skip 'S' character)
    String angleStr = command.substring(1);
    int angle = angleStr.toInt();

    // Validate range
    if (angle >= 0 && angle <= 180)
    {
        currentSteeringAngle = angle;
        steeringServo.write(angle);

        // Send confirmation (useful for debugging)
        Serial.print("OK: Steering = ");
        Serial.println(angle);
    }
    else
    {
        Serial.print("ERROR: Invalid steering angle: ");
        Serial.println(angle);
    }
}

void handleThrottleCommand(String command)
{
    /**
     * Handle throttle command.
     * Format: "T<state>" where state is 0 (stop) or 1 (forward)
     * Example: "T1" = forward, "T0" = stop
     */

    // Extract state from command
    String stateStr = command.substring(1);
    int state = stateStr.toInt();

    if (state == 1)
    {
        // Forward — Elegoo shield inverts right channel internally, HIGH/HIGH on both = forward
        digitalWrite(MOTOR_IN1, HIGH);
        digitalWrite(MOTOR_IN2, HIGH);
        digitalWrite(MOTOR_IN3, HIGH);
        digitalWrite(MOTOR_IN4, HIGH);
        analogWrite(MOTOR_ENA, FORWARD_SPEED);
        analogWrite(MOTOR_ENB, FORWARD_SPEED);

        currentThrottle = 1;
        Serial.println("OK: Throttle = FORWARD");
    }
    else if (state == 0)
    {
        // Stop
        analogWrite(MOTOR_ENA, 0);
        analogWrite(MOTOR_ENB, 0);

        currentThrottle = 0;
        Serial.println("OK: Throttle = STOP");
    }
    else if (state == 2)
    {
        // Reverse
        digitalWrite(MOTOR_IN1, LOW);
        digitalWrite(MOTOR_IN2, LOW);
        digitalWrite(MOTOR_IN3, LOW);
        digitalWrite(MOTOR_IN4, LOW);
        analogWrite(MOTOR_ENA, FORWARD_SPEED);
        analogWrite(MOTOR_ENB, FORWARD_SPEED);

        currentThrottle = 2;
        Serial.println("OK: Throttle = REVERSE");
    }
    else
    {
        Serial.print("ERROR: Invalid throttle state: ");
        Serial.println(state);
    }
}