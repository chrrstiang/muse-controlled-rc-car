# BCI RC Car Setup Guide

## Hardware Requirements

### Components

- Muse EEG headband (Muse 2 or Muse S)
- ELEGOO Smart Robot Car Kit V4.0
- MacBook/laptop with Bluetooth
- USB cable for Arduino connection

### Assembly

1. Assemble the ELEGOO RC car following the kit instructions
2. Do NOT install the WiFi module or stock control electronics
3. Keep the L298N motor driver and connect it to Arduino Uno
4. Mount Arduino securely on the chassis

## Software Setup

### macOS Environment

1. **Install Homebrew** (if not already installed):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install VS Code + PlatformIO**:
   - Download VS Code from https://code.visualstudio.com
   - Install PlatformIO IDE extension

3. **Python Environment**:

```bash
cd ~/muse-controlled-rc-car
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Muse Headband Setup

1. **Pair Muse via Bluetooth**:
   - Go to System Preferences → Bluetooth
   - Power on Muse headband
   - Wait for "Muse-XXXX" to appear
   - Click "Connect"

2. **Test connection**:

```bash
muselsl list
# Should show your Muse device (make sure headband is not connected to any other device)

muselsl stream
# Should start streaming data
```

### Arduino Setup

1. **Connect Arduino via USB**
2. **Find serial port**:

```bash
ls /dev/cu.*
# Look for /dev/cu.usbmodem* or /dev/cu.usbserial*
```

3. **Upload firmware**:
   - Open `arduino/` folder in VS Code
   - PlatformIO: Build and Upload

## Configuration

Edit `python/config.py` to set:

- Serial port name (from step above)
- Focus detection thresholds (start with defaults)
- Accelerometer sensitivity (start with defaults)

## Troubleshooting

### Muse won't connect

- Ensure headband is charged
- Try unpairing and re-pairing
- Restart Bluetooth on Mac

### Arduino not detected

- Check USB cable (must be data cable, not charge-only)
- Try different USB port
- Check permissions (though macOS usually handles this)

### Serial communication errors

- Verify baud rate matches in Python and Arduino (default: 115200)
- Ensure only one program is accessing serial port at a time
- Check that Arduino is powered on

## Next Steps

Once setup is complete, proceed to:

1. Calibration (see demo.md)
2. Testing accelerometer control
3. Testing focus detection
4. Full system integration
