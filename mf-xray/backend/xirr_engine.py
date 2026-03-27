from __future__ import annotations

from datetime import date
from typing import Iterable, Tuple


def xirr(
    cashflows: Iterable[Tuple[date, float]],
    guess: float = 0.1,
    tol: float = 1e-6,
    max_iter: int = 100,
) -> float:
    """
    Compute XIRR using Newton–Raphson, based on user-provided implementation.

    Inputs:
      cashflows: iterable of (datetime.date, amount), where contributions are negative
                and inflows/redemptions are positive.
    Returns:
      rate as a decimal (e.g. 0.1234 for 12.34%).
    """
    cashflows_list = list(cashflows)
    if not cashflows_list or len(cashflows_list) < 2:
        return 0.0

    # Ensure stable ordering by date
    cashflows_list.sort(key=lambda x: x[0])

    dates = [d for d, _ in cashflows_list]
    flows = [float(cf) for _, cf in cashflows_list]

    def npv(rate: float) -> float:
        base = dates[0]
        return sum(
            cf / (1.0 + rate) ** ((dt - base).days / 365.0)
            for cf, dt in zip(flows, dates)
        )

    def d_npv(rate: float) -> float:
        base = dates[0]
        return sum(
            -((dt - base).days / 365.0)
            * cf
            / (1.0 + rate) ** (((dt - base).days / 365.0) + 1.0)
            for cf, dt in zip(flows, dates)
        )

    rate = float(guess)
    for _ in range(int(max_iter)):
        value = npv(rate)
        derivative = d_npv(rate)

        if abs(derivative) < 1e-10:
            break

        new_rate = rate - value / derivative

        if abs(new_rate - rate) < tol:
            return new_rate

        rate = new_rate

    raise Exception("XIRR did not converge")
