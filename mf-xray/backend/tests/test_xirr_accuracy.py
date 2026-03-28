from datetime import date
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from xirr_engine import xirr

def test_xirr_basic():
    # Example: 10% annual return
    # Jan 1: -100 (Investment)
    # Jan 1 (next year): +110 (Value)
    cashflows = [
        (date(2023, 1, 1), -100.0),
        (date(2024, 1, 1), 110.0)
    ]
    rate = xirr(cashflows)
    print(f"Basic 10% test: {rate:.4f}")
    assert abs(rate - 0.1) < 0.01

def test_xirr_complex():
    # Complex case
    cashflows = [
        (date(2020, 1, 1), -1000.0),
        (date(2021, 1, 1), -1000.0),
        (date(2022, 1, 1), 2500.0)
    ]
    rate = xirr(cashflows)
    print(f"Complex test: {rate:.4f}")
    # Expected is approx 15.8%
    assert 0.15 < rate < 0.16

if __name__ == "__main__":
    try:
        test_xirr_basic()
        test_xirr_complex()
        print("All tests passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)
