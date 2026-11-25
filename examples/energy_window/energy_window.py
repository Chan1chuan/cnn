"""Integrate linearly interpolated CSV power samples over a time window."""

import argparse
import csv
import json
from math import fsum, isfinite
from pathlib import Path
from typing import Iterable, TextIO


def read_samples(stream: TextIO) -> list[tuple[float, float]]:
    reader = csv.DictReader(stream, strict=True)
    columns = reader.fieldnames or []
    if any(columns.count(name) != 1 for name in ("time_s", "power_mw")):
        raise ValueError("CSV must have one time_s column and one power_mw column")

    samples = []
    for row in reader:
        try:
            samples.append((float(row["time_s"]), float(row["power_mw"])))
        except (TypeError, ValueError) as error:
            raise ValueError(f"invalid time or power in CSV record ending on line {reader.line_num}") from error
    return samples


def measure_window(
    samples: Iterable[tuple[float, float]], start_s: float, end_s: float
) -> dict[str, float]:
    points = list(samples)
    if len(points) < 2:
        raise ValueError("at least two samples are required")
    if not (isfinite(start_s) and isfinite(end_s) and start_s < end_s):
        raise ValueError("window start and end must be finite and start must precede end")
    duration = end_s - start_s
    if not isfinite(duration):
        raise ValueError("window duration is too large")
    for index, (time_s, power_mw) in enumerate(points):
        if not (isfinite(time_s) and isfinite(power_mw)):
            raise ValueError("sample times and powers must be finite")
        if index and time_s <= points[index - 1][0]:
            raise ValueError("sample times must be strictly increasing")
    if start_s < points[0][0] or end_s > points[-1][0]:
        raise ValueError("window must be covered by the CSV; extrapolation is not supported")

    areas_mj = []
    for (t0, p0), (t1, p1) in zip(points, points[1:]):
        left, right = max(t0, start_s), min(t1, end_s)
        if left >= right:
            continue
        # Clip the segment first and interpolate its power at both new endpoints.
        span = t1 - t0
        if not isfinite(span):
            raise ValueError("sample interval is too large")
        left_fraction, right_fraction = (left - t0) / span, (right - t0) / span
        p_left = (1 - left_fraction) * p0 + left_fraction * p1
        p_right = (1 - right_fraction) * p0 + right_fraction * p1
        areas_mj.append((right - left) * (0.5 * p_left + 0.5 * p_right))

    if not all(map(isfinite, areas_mj)):
        raise ValueError("energy calculation exceeded the finite float range")
    energy_mj = fsum(areas_mj)  # mW × s = mJ.
    average_power_mw = energy_mj / duration
    if not isfinite(average_power_mw):
        raise ValueError("average power calculation exceeded the finite float range")
    return {
        "start_s": start_s,
        "end_s": end_s,
        "duration_s": duration,
        "energy_mj": energy_mj,
        "average_power_mw": average_power_mw,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path, help="input CSV with time_s and power_mw columns")
    parser.add_argument("--start-s", type=float, required=True)
    parser.add_argument("--end-s", type=float, required=True)
    args = parser.parse_args()
    try:
        with args.csv_file.open(encoding="utf-8-sig", newline="") as stream:
            result = measure_window(read_samples(stream), args.start_s, args.end_s)
    except (OSError, ValueError, OverflowError, csv.Error) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
