#include <Arduino.h>

/**
 * Motor driver (TB6612FNG) - Elegoo Smart Car V4 pin mapping
 *
 * Pinout reference:
 *   Left motor: IN1 (7), IN2 (8), ENA (5)
 *   Right motor: IN3 (9), IN4 (11), ENB (6)
 *   Standby: STBY (3) - must be HIGH to enable motors
 */
#define MOTOR_ENA 5
#define MOTOR_IN1 7
#define MOTOR_IN2 8
#define MOTOR_ENB 6
#define MOTOR_IN3 9
#define MOTOR_IN4 11
#define MOTOR_STBY 3

// initial state of car on start
int currentSteeringAngle = 90;
const int FORWARD_SPEED = 50;
int currentThrottle = 0;

// function declarations
void applyMotorSpeeds();
void handleSteeringCommand(String command);
void handleThrottleCommand(String command);

// initializes pins, sets initial motor state, and prints startup message
void setup()
{
    Serial.begin(115200);

    // pins
    pinMode(MOTOR_IN1, OUTPUT);
    pinMode(MOTOR_IN2, OUTPUT);
    pinMode(MOTOR_IN3, OUTPUT);
    pinMode(MOTOR_IN4, OUTPUT);
    pinMode(MOTOR_ENA, OUTPUT);
    pinMode(MOTOR_ENB, OUTPUT);
    pinMode(MOTOR_STBY, OUTPUT);

    // Enable TB6612
    digitalWrite(MOTOR_STBY, HIGH);

    // motors
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
    digitalWrite(MOTOR_IN3, LOW);
    digitalWrite(MOTOR_IN4, LOW);
    analogWrite(MOTOR_ENA, 0);
    analogWrite(MOTOR_ENB, 0);

    // startup message
    Serial.println("=========================================");
    Serial.println("BCI RC Car - Arduino Controller");
    Serial.println("Steering: differential wheel drive");
    Serial.println("=========================================");
    Serial.println("Ready to receive commands");
    Serial.println("Waiting for serial input...");
    Serial.println();
}

/**
 * Main loop: continuously checks for serial commands and executes them.
 */
void loop()
{
    if (Serial.available() > 0)
    {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command.length() > 0)
        {
            char commandType = command.charAt(0);

            if (commandType == 'S')
            {
                handleSteeringCommand(command);
            }
            else if (commandType == 'T')
            {
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

    // Small delay to prevent serial buffer flooding
    delay(10);
}

/**
 * Apply current throttle + steering state to both motors.
 * Differential steering: bias the wheel speeds based on steering angle.
 *   angle=90 → straight (both equal)
 *   angle<90 → left turn (left wheel slower)
 *   angle>90 → right turn (right wheel slower)
 */
void applyMotorSpeeds()
{
    if (currentThrottle == 0)
    {
        analogWrite(MOTOR_ENA, 0);
        analogWrite(MOTOR_ENB, 0);
        return;
    }

    // bias: -1.0 (full left) to +1.0 (full right)
    float bias = (currentSteeringAngle - 90) / 90.0f;
    int leftSpeed = (int)(FORWARD_SPEED * constrain(1.0f + bias, 0.0f, 1.0f));
    int rightSpeed = (int)(FORWARD_SPEED * constrain(1.0f - bias, 0.0f, 1.0f));

    bool forward = (currentThrottle == 1);
    digitalWrite(MOTOR_IN1, forward ? HIGH : LOW);
    digitalWrite(MOTOR_IN2, forward ? HIGH : LOW);
    digitalWrite(MOTOR_IN3, forward ? HIGH : LOW);
    digitalWrite(MOTOR_IN4, forward ? HIGH : LOW);
    analogWrite(MOTOR_ENA, leftSpeed);
    analogWrite(MOTOR_ENB, rightSpeed);
}

/**
 * Handle steering command.
 * Format: "S<angle>" where angle is 0-180
 * Example: "S90" = straight, "S0" = full left, "S180" = full right
 */
void handleSteeringCommand(String command)
{
    int angle = command.substring(1).toInt();

    if (angle >= 0 && angle <= 180)
    {
        currentSteeringAngle = angle;
        applyMotorSpeeds();

        Serial.print("OK: Steering = ");
        Serial.println(angle);
    }
    else
    {
        Serial.print("ERROR: Invalid steering angle: ");
        Serial.println(angle);
    }
}

/**
 * Handle throttle command.
 * Format: "T<state>" where state is 0 (stop), 1 (forward), 2 (reverse)
 * Example: "T1" = forward, "T0" = stop
 */
void handleThrottleCommand(String command)
{
    int state = command.substring(1).toInt();

    if (state == 0 || state == 1 || state == 2)
    {
        currentThrottle = state;
        applyMotorSpeeds();

        if (state == 0)
            Serial.println("OK: Throttle = STOP");
        else if (state == 1)
            Serial.println("OK: Throttle = FORWARD");
        else
            Serial.println("OK: Throttle = REVERSE");
    }
    else
    {
        Serial.print("ERROR: Invalid throttle state: ");
        Serial.println(state);
    }
}
