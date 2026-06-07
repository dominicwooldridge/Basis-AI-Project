def generate_pwa_risk_flags(prevailing_wage: bool, apprenticeship: bool) -> list:
    flags = []

    if not prevailing_wage and not apprenticeship:
        flags.append({
            "severity": "high",
            "flag": "No PWA compliance — base rate 6% only",
            "impact": f"Credit rate is 6% vs 30% with compliance. "
                      f"On a $100M project that's $6M vs $30M.",
            "action": "Consult a labor compliance firm before breaking ground. "
                      "PWA must be established in construction contracts upfront "
                      "— it cannot be applied retroactively."
        })

    elif not prevailing_wage:
        flags.append({
            "severity": "high",
            "flag": "Prevailing wage not confirmed",
            "impact": "Davis-Bacon rates must be written into all construction "
                      "contracts and documented via certified payroll records.",
            "action": "Look up applicable wage determination on SAM.gov by "
                      "county and construction type before hiring contractors."
        })

    elif not apprenticeship:
        flags.append({
            "severity": "medium",
            "flag": "Apprenticeship requirement not confirmed",
            "impact": "10-15% of labor hours must be performed by apprentices "
                      "from a DOL-registered program. Often overlooked.",
            "action": "Contact local registered apprenticeship programs early — "
                      "availability varies significantly by region."
        })

    if prevailing_wage and apprenticeship:
        flags.append({
            "severity": "info",
            "flag": "PWA compliance claimed — documentation required",
            "impact": "IRS may request certified payroll records on audit. "
                      "Recapture risk if compliance cannot be demonstrated.",
            "action": "Retain certified payroll records for all contractors "
                      "and subcontractors for the life of the project."
        })

    return flags