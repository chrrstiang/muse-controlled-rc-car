# Arduino — RC Car Firmware

PlatformIO project for the Arduino UNO firmware. Receives serial commands from the Python BCI controller and drives the steering servo and motors.

---

## Hardware

| Component                                | Pin(s)      |
| ---------------------------------------- | ----------- |
| Steering servo                           | 7           |
| Motor driver EN_A (left enable)          | 3 (PWM)     |
| Motor driver IN1 / IN2 (left direction)  | 5, 6        |
| Motor driver EN_B (right enable)         | 11 (PWM)    |
| Motor driver IN3 / IN4 (right direction) | 9, 10       |
| Serial (USB)                             | 115200 baud |

Motor driver: L298N (or compatible).

---

## Files

### `src/main.cpp`

Main firmware loop. Reads newline-terminated commands from serial and dispatches to the appropriate handler.

**Commands:**

| Command  | Format       | Example | Response            |
| -------- | ------------ | ------- | ------------------- |
| Steering | `S{0–180}\n` | `S90\n` | `OK: Steering = 90` |
| Throttle | `T{0–1}\n`   | `T1\n`  | `OK: Throttle = 1`  |

- Servo starts at center (90°) on boot
- Motors start stopped
- Invalid angles or states are ignored
- 10 ms loop delay prevents servo oscillation

**Key constants (edit in `main.cpp`):**

| Constant        | Value    | Description        |
| --------------- | -------- | ------------------ |
| `SERVO_PIN`     | `7`      | Steering servo pin |
| `FORWARD_SPEED` | `150`    | Motor PWM (0–255)  |
| `SERIAL_BAUD`   | `115200` | Serial baud rate   |

### `platformio.ini`

PlatformIO build and upload configuration.

```ini
[env:uno]
platform  = atmelavr
board     = uno
lib_deps  = arduino-libraries/Servo@^1.2.2
upload_port = /dev/cu.usbserial-110
```

Change `upload_port` to match your system if needed.

---

## Upload

```bash
# From the arduino/ directory
pio run --target upload

# Verbose output
pio run --target upload -v
```

Find your Arduino's port first:

```bash
ls /dev/cu.*
```

Then update `upload_port` in `platformio.ini` and `ARDUINO_PORT` in `python/config.py` to match.

---

## Serial Protocol

Commands are plain ASCII strings terminated with `\n`. The Arduino echoes a confirmation line back.

```
Python sends:   S90\n
Arduino replies: OK: Steering = 90

Python sends:   T1\n
Arduino replies: OK: Throttle = 1
```

The Python `controller.py` script handles this protocol automatically.

---

## Wiring Notes

See `docs/wiring.md` in the project root for a full diagram.

- Servo signal wire → Pin 7; power from an external 5V supply (not the Arduino 5V pin)
- L298N motor driver powered from the battery pack; logic powered from Arduino 5V
- GND must be shared between Arduino, L298N, and servo power supply
