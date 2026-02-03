# Running the BCI RC Car Demo

## Prerequisites

- Complete hardware setup (see setup.md)
- Wiring verified (see wiring.md)
- Software environment installed
- Muse headband paired and charged
- RC car assembled and powered

## Quick Start

### 1. Activate Python Environment

```bash
cd ~/bci-rc-car
source venv/bin/activate
```

### 2. Start Muse Stream

```bash
muselsl stream --address YOUR_MUSE_MAC_ADDRESS
```

Leave this terminal running.

### 3. Connect Arduino

- Plug Arduino into laptop via USB
- Verify connection: `ls /dev/cu.*`
- Upload firmware if not already done

### 4. Run Calibration

```bash
python python/gyro_control.py --calibrate
```

Follow on-screen instructions:

- Sit with head in neutral position
- Press Enter to capture baseline
- Calibration saved to `data/calibration/gyro_neutral.json`

### 5. Test Gyroscope Steering (Motors Off)

```bash
python python/gyro_control.py --test
```

- Tilt head left/right
- Terminal should show steering angles
- Verify angles are responding correctly
- Press Ctrl+C to stop

### 6. Test Focus Detection (Motors Off)

```bash
python python/focus_detection.py --test
```

- Try to focus (e.g., mental math, visual focus)
- Try to relax/unfocus
- Terminal should show focus state
- Press Ctrl+C to stop

### 7. Full System Test (Motors On)

⚠️ **Place car on blocks or hold it off the ground first!**

```bash
python python/gyro_control.py --run
```

- Head tilt controls steering
- Focus state controls forward/stop
- Press Ctrl+C to emergency stop

### 8. Drive on Ground

Once comfortable with controls:

- Place car on flat, open surface
- Run the system
- Focus to move forward
- Tilt head to steer
- Unfocus to stop

## Command Reference

### Calibration Commands

```bash
# Calibrate gyroscope neutral position
python python/gyro_control.py --calibrate

# Calibrate focus threshold
python python/focus_detection.py --calibrate
```

### Testing Commands

```bash
# Test gyro steering only (no motors)
python python/gyro_control.py --test

# Test focus detection only (no motors)
python python/focus_detection.py --test

# Test serial communication
python python/serial_comm.py --test
```

### Running the System

```bash
# Full system with gyro + focus control
python python/gyro_control.py --run

# Verbose mode (shows debug info)
python python/gyro_control.py --run --verbose

# Record session data
python python/gyro_control.py --run --record
```

## Expected Behavior

### Gyroscope Control

- **Neutral**: Head facing forward → Car goes straight
- **Left tilt**: Head tilted left → Car turns left
- **Right tilt**: Head tilted right → Car turns right
- **Sensitivity**: ~15-30 degrees of tilt for full steering range

### Focus Control

- **Focused**: Alpha/beta ratio below threshold → Car moves forward
- **Unfocused**: Alpha/beta ratio above threshold → Car stops
- **Transition delay**: ~0.5-1 second response time

## Troubleshooting

### Car doesn't respond

- Check Arduino serial monitor for incoming commands
- Verify serial port in config.py matches actual port
- Ensure Arduino is powered and firmware uploaded

### Erratic steering

- Recalibrate gyroscope neutral position
- Reduce sensitivity in config.py
- Ensure Muse is fitted snugly on head

### Focus detection not working

- Recalibrate focus threshold
- Check EEG signal quality (Muse should have good contact)
- Try more deliberate focusing/unfocusing
- Adjust threshold in config.py

### Car only goes in circles

- Check motor wiring polarity
- Verify left/right motor pins in Arduino code
- Test motors individually

### Muse disconnects

- Ensure headband is charged
- Keep laptop within Bluetooth range (~10 feet)
- Restart muselsl stream if connection drops

## Recording Data

To save session data for analysis:

```bash
python python/gyro_control.py --run --record
```

Files saved to `data/recordings/` with timestamp.

## Safety Tips

- ⚠️ Always test with car elevated first
- Keep emergency stop ready (Ctrl+C)
- Use in open area away from obstacles
- Have someone spot you during first attempts
- Start with low motor speeds, increase gradually

## Demo Video Checklist

For creating project demo videos:

1. Show calibration process
2. Demonstrate gyroscope steering (elevated)
3. Demonstrate focus detection (elevated)
4. Show full system driving on ground
5. Include terminal output overlay showing data
6. Highlight head movements clearly
7. Show successful navigation around simple course

## Next Steps

Once basic demo works:

- Tune sensitivity parameters for smoother control
- Add motor imagery classification (MI phase)
- Implement more complex control schemes
- Create obstacle course for demonstrations
