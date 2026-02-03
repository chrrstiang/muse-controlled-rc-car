# Wiring Diagram and Connections

## Overview

The system has three main components:

1. **Muse headband** → Bluetooth → **Laptop**
2. **Laptop** → USB/Serial → **Arduino**
3. **Arduino** → Motor driver → **RC car motors/servos**

## Arduino Connections

### L298N Motor Driver to Arduino

**Motor control pins**:

```
L298N          Arduino
IN1      →     Digital Pin 5
IN2      →     Digital Pin 6
IN3      →     Digital Pin 9
IN4      →     Digital Pin 10
ENA      →     Digital Pin 3 (PWM)
ENB      →     Digital Pin 11 (PWM)
```

**Power**:

```
L298N          Power Source
+12V     →     Battery positive
GND      →     Battery negative and Arduino GND (common ground)
5V       →     Arduino 5V (if using L298N's onboard regulator)
```

### Servo Motor (Steering)

```
Servo          Arduino
Signal   →     Digital Pin 7
VCC      →     5V
GND      →     GND
```

### Motor Connections to L298N

**Left motors**:

```
L298N OUT1  →  Left motor +
L298N OUT2  →  Left motor -
```

**Right motors**:

```
L298N OUT3  →  Right motor +
L298N OUT4  →  Right motor -
```

## Pin Summary

| Function                | Arduino Pin | Component    |
| ----------------------- | ----------- | ------------ |
| Left motor forward      | 5           | L298N IN1    |
| Left motor backward     | 6           | L298N IN2    |
| Right motor forward     | 9           | L298N IN3    |
| Right motor backward    | 10          | L298N IN4    |
| Left motor speed (PWM)  | 3           | L298N ENA    |
| Right motor speed (PWM) | 11          | L298N ENB    |
| Steering servo          | 7           | Servo signal |

## Important Notes

### Power Considerations

- **DO NOT** power motors from Arduino 5V pin
- Motors draw too much current and will damage Arduino
- Use separate battery pack for motors (typically 7-12V)
- **MUST** connect Arduino GND to motor battery GND (common ground)

### PWM Pins

- Pins 3, 5, 6, 9, 10, 11 are PWM-capable on Arduino Uno
- Use these for speed control (ENA, ENB)

### Servo Power

- Small servos can be powered from Arduino 5V
- For larger servos, use separate 5V regulator from battery

## Wiring Checklist

Before powering on:

- [ ] All GND connections tied together (Arduino, motor driver, battery)
- [ ] Motor power comes from battery, not Arduino
- [ ] No short circuits between power and ground
- [ ] All connections secure and insulated
- [ ] Serial cable (USB) connected to laptop

## Visual Diagram

```
┌─────────────┐
│    Muse     │
│  Headband   │
└──────┬──────┘
       │ Bluetooth
       │
┌──────▼──────────────┐
│  MacBook/Laptop     │
│  - Python scripts   │
│  - Serial comm      │
└──────┬──────────────┘
       │ USB/Serial
       │
┌──────▼──────────┐      ┌──────────────┐
│  Arduino Uno    │      │   Battery    │
│                 │      │   (7-12V)    │
│  Pins 3,5,6,    │      └───┬──────────┘
│  7,9,10,11      │          │
└────┬───┬────┬───┘          │
     │   │    │              │
     │   │    └──────────┐   │
     │   │               │   │
┌────▼───▼────┐    ┌─────▼───▼─────┐
│   Servo     │    │ L298N Driver  │
│  (Steering) │    │               │
└─────────────┘    └───┬───────┬───┘
                       │       │
                  ┌────▼───┐ ┌─▼────┐
                  │ Left   │ │Right │
                  │ Motors │ │Motors│
                  └────────┘ └──────┘
```

## Safety

⚠️ **WARNING**:

- Disconnect battery before modifying wiring
- Check polarity before connecting power
- Start testing with motors disconnected
- Add fuse to battery connection for protection
