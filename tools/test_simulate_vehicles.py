
import random

from tools.simulate_vehicles import build_report


def test_build_report_has_expected_fields_and_values(monkeypatch):
    """Check the report structure and deterministic values."""
    monkeypatch.setattr(random, "uniform", lambda low, high: (low + high) / 2)
    monkeypatch.setattr(random, "randint", lambda low, high: low)

    report = build_report(
        lat=11.7493,
        lon=79.7452,
        severity=3,
        jitter_deg=0.00001,
    )

    assert set(report) == {
        "latitude",
        "longitude",
        "deltaG",
        "severity",
        "satellites",
        "timestamp",
        "source",
    }

    assert report["latitude"] == 11.7493
    assert report["longitude"] == 79.7452
    assert report["deltaG"] == 0.65
    assert report["severity"] == 3
    assert report["satellites"] == 5
    assert isinstance(report["timestamp"], int)
    assert report["source"] == "simulator"


def test_build_report_values_are_in_valid_ranges(monkeypatch):
    """Check the expected ranges and data types."""
    monkeypatch.setattr(random, "uniform", lambda low, high: high)
    monkeypatch.setattr(random, "randint", lambda low, high: high)

    report = build_report(
        lat=11.7493,
        lon=79.7452,
        severity=4,
        jitter_deg=0.00001,
    )

    assert 0.35 <= report["deltaG"] <= 0.95
    assert 5 <= report["satellites"] <= 8
    assert report["severity"] == 4
    assert isinstance(report["latitude"], float)
    assert isinstance(report["longitude"], float)
    assert isinstance(report["timestamp"], int)
    assert report["source"] == "simulator"



def test_report_coordinates_stay_in_same_rounded_grid_cell(monkeypatch):
    """
    Check that different jitter values stay in the same rounded grid cell.

    The dashboard groups coordinates using round(coordinate, 4).
    The selected coordinates are away from rounding boundaries, and the
    jitter is small enough to keep both reports in the same cell.
    """
    values = iter([
        -0.00001, -0.00001, 0.50,  # First report: lat, lon, deltaG
         0.00001,  0.00001, 0.70,  # Second report: lat, lon, deltaG
    ])

    monkeypatch.setattr(
        random,
        "uniform",
        lambda low, high: next(values),
    )
    monkeypatch.setattr(random, "randint", lambda low, high: low)

    lat, lon = 11.7493, 79.7452

    first = build_report(lat, lon, 3, 0.00001)
    second = build_report(lat, lon, 4, 0.00001)

    # The coordinates must differ before checking their rounded cells.
    assert first["latitude"] != second["latitude"]
    assert first["longitude"] != second["longitude"]

    # Both reports must belong to the same dashboard grid cell.
    assert round(first["latitude"], 4) == round(second["latitude"], 4)
    assert round(first["longitude"], 4) == round(second["longitude"], 4)



def test_build_report_does_not_need_network_or_hardware(monkeypatch):
    """Check that report generation returns data without hardware setup."""
    monkeypatch.setattr(random, "uniform", lambda low, high: low)
    monkeypatch.setattr(random, "randint", lambda low, high: low)

    report = build_report(
        lat=11.7493,
        lon=79.7452,
        severity=2,
        jitter_deg=0.00001,
    )

    # build_report constructs a report dictionary; it doesn't upload it.
    assert isinstance(report, dict)
    assert report["source"] == "simulator"
