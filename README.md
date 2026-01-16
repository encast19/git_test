# Raspberry Pi Weather Station

Read temperature and humidity from a DHT sensor on a Raspberry Pi.

## Hardware
- Raspberry Pi with GPIO header
- DHT11, DHT21, or DHT22 sensor
- 4.7k to 10k pull-up resistor between VCC and DATA
- Jumper wires and breadboard

## Wiring (BCM numbering)
- DHT VCC -> 3.3V (pin 1)
- DHT GND -> GND (pin 6)
- DHT DATA -> BCM 4 (pin 7) by default

## Setup
1. Install system dependencies:
   - sudo apt-get update
   - sudo apt-get install -y libgpiod2
2. Create a virtual environment and install Python dependencies:
   - python3 -m venv .venv
   - source .venv/bin/activate
   - python -m pip install -r requirements.txt

## Run
- Continuous readings every 5 seconds:
  - python weather_station.py --sensor DHT22 --pin 4 --interval 5
- Single reading:
  - python weather_station.py --sensor DHT11 --pin 17 --once

## Output
2026-01-16T15:04:05-08:00 temperature_C=22.4 humidity_percent=48.2

## Notes
- If readings fail, re-check wiring and the pull-up resistor.
- Use --use-pulseio if your Raspberry Pi setup requires it.