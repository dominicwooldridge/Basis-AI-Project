def calculate_base_itc_rate(prevailing_wage: bool, apprenticeship: bool) -> dict:
    """
    IRA §48E base rate logic.
    Both PWA conditions must be met for the 5x multiplier.
    """
    pwa_compliant = prevailing_wage and apprenticeship

    if pwa_compliant:
        base_rate = 0.30   # 5x multiplier applied
        multiplier_applied = True
    else:
        base_rate = 0.06   # base rate only
        multiplier_applied = False

    return {
        "base_rate": base_rate,
        "multiplier_applied": multiplier_applied,
        "pwa_compliant": pwa_compliant
    }