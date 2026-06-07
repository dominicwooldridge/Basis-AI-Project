import numpy as np
import numpy_financial as npf


def run_dcf(
    capex_millions: float,
    annual_revenue_millions: float,
    discount_rate: float = 0.08,
    years: int = 25,
    itc_credit_millions: float = 0.0,
    opex_fraction: float = 0.02,
) -> dict:
    """
    Discounted cash flow model.

    ITC credit (if any) offsets capex in year 0 — it's a one-time tax credit
    taken in the year the project is placed in service.
    """
    opex = capex_millions * opex_fraction
    annual_cf = annual_revenue_millions - opex

    cashflows = np.array(
        [-capex_millions + itc_credit_millions] + [annual_cf] * years
    )

    npv = float(npf.npv(discount_rate, cashflows))
    try:
        irr = float(npf.irr(cashflows))
    except Exception:
        irr = float("nan")

    cumulative = np.cumsum(cashflows)
    crossover = np.where(cumulative >= 0)[0]
    payback = float(crossover[0]) if len(crossover) else float(years + 1)

    return {
        "npv": round(npv, 2),
        "irr": round(irr, 4) if not np.isnan(irr) else 0.0,
        "payback_years": round(payback, 1),
    }
