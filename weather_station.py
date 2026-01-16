#!/usr/bin/env python3
"""Simple Raspberry Pi weather station for DHT sensors."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import time

import adafruit_dht
import board

SENSOR_TYPES = {
    "DHT11": adafruit_dht.DHT11,
    "DHT22": adafruit_dht.DHT22,
    "DHT21": adafruit_dht.DHT21,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read temperature and humidity from a DHT sensor."
    )
    parser.add_argument(
        "--sensor",
        choices=sorted(SENSOR_TYPES.keys()),
        default="DHT22",
        help="DHT sensor model.",
    )
    parser.add_argument(
        "--pin",
        type=int,
        default=4,
        help="BCM GPIO pin number connected to the data line.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between readings.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries for a failed reading.",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
        help="Seconds to wait between retries.",
    )
    parser.add_argument(
        "--fahrenheit",
        action="store_true",
        help="Print temperature in Fahrenheit.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Read a single sample and exit.",
    )
    parser.add_argument(
        "--use-pulseio",
        action="store_true",
        help="Enable pulseio mode for some Raspberry Pi setups.",
    )
    return parser.parse_args()


def resolve_pin(pin_number: int):
    attribute = f"D{pin_number}"
    if not hasattr(board, attribute):
        raise ValueError(
            f"Unsupported BCM pin {pin_number}. Use a BCM pin that exists on your Pi."
        )
    return getattr(board, attribute)


def read_sample(sensor, retries: int, retry_delay: float):
    for attempt in range(1, retries + 1):
        try:
            temperature_c = sensor.temperature
            humidity = sensor.humidity
        except RuntimeError as exc:
            print(
                f"Reading failed (attempt {attempt}/{retries}): {exc}",
                file=sys.stderr,
            )
        else:
            if temperature_c is None or humidity is None:
                print(
                    f"Reading incomplete (attempt {attempt}/{retries}).",
                    file=sys.stderr,
                )
            else:
                return temperature_c, humidity
        time.sleep(retry_delay)
    raise RuntimeError("Failed to read sensor after retries.")


def format_reading(temperature_c: float, humidity: float, fahrenheit: bool) -> str:
    if fahrenheit:
        temperature = temperature_c * 9 / 5 + 32
        unit = "F"
    else:
        temperature = temperature_c
        unit = "C"
    timestamp = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
    return (
        f"{timestamp} temperature_{unit}={temperature:.1f} humidity_percent={humidity:.1f}"
    )


def main() -> int:
    args = parse_args()
    try:
        pin = resolve_pin(args.pin)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    sensor_class = SENSOR_TYPES[args.sensor]
    sensor = sensor_class(pin, use_pulseio=args.use_pulseio)
    try:
        while True:
            temperature_c, humidity = read_sample(
                sensor, retries=args.retries, retry_delay=args.retry_delay
            )
            print(
                format_reading(
                    temperature_c=temperature_c,
                    humidity=humidity,
                    fahrenheit=args.fahrenheit,
                ),
                flush=True,
            )
            if args.once:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    finally:
        sensor.exit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
