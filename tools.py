# tools.py — Complete tax logic with capital gains, rental income, what-if

# ── 1. Normal income tax (slabs) ─────────────────────────────────────────────

def calculate_slab_tax(taxable_income: float, regime: str) -> tuple:
    """Returns (tax, breakdown) for slab income only"""

    if regime == "new":
        slabs = [
            (400000, 0.00),
            (400000, 0.05),
            (400000, 0.10),
            (400000, 0.15),
            (400000, 0.20),
            (float('inf'), 0.30)
        ]
    else:
        slabs = [
            (250000, 0.00),
            (250000, 0.05),
            (500000, 0.20),
            (float('inf'), 0.30)
        ]

    tax = 0
    remaining = taxable_income
    breakdown = []

    for slab_limit, rate in slabs:
        if remaining <= 0:
            break
        taxable_in_slab = min(remaining, slab_limit)
        tax_in_slab = taxable_in_slab * rate
        tax += tax_in_slab
        if taxable_in_slab > 0 and rate > 0:
            breakdown.append({
                "slab": f"₹{taxable_income - remaining:,.0f} – ₹{taxable_income - remaining + taxable_in_slab:,.0f}",
                "rate": f"{int(rate * 100)}%",
                "tax": round(tax_in_slab, 2)
            })
        remaining -= taxable_in_slab

    return round(tax, 2), breakdown


# ── 2. Capital gains tax ──────────────────────────────────────────────────────

def calculate_capital_gains_tax(stcg: float, ltcg: float) -> dict:
    """
    STCG (Short Term Capital Gain) — held < 1 year → 20% flat
    LTCG (Long Term Capital Gain) — held > 1 year → 12.5% above ₹1.25L exempt
    These are taxed separately, never enter income slabs
    """

    # STCG — flat 20% no exemption
    stcg_tax = round(stcg * 0.20, 2) if stcg > 0 else 0

    # LTCG — first 1.25L exempt, rest at 12.5%
    ltcg_exemption = 125000
    ltcg_taxable = max(0, ltcg - ltcg_exemption)
    ltcg_tax = round(ltcg_taxable * 0.125, 2) if ltcg_taxable > 0 else 0

    total_cg_tax = round(stcg_tax + ltcg_tax, 2)

    return {
        "stcg": stcg,
        "stcg_tax": stcg_tax,
        "stcg_rate": "20% flat",
        "ltcg": ltcg,
        "ltcg_exemption_applied": min(ltcg, ltcg_exemption),
        "ltcg_taxable": ltcg_taxable,
        "ltcg_tax": ltcg_tax,
        "ltcg_rate": "12.5% above ₹1.25L",
        "total_capital_gains_tax": total_cg_tax
    }


# ── 3. Rental income ──────────────────────────────────────────────────────────

def calculate_rental_income(annual_rent: float, municipal_tax_paid: float = 0) -> dict:
    """
    Rental income goes into normal slabs but with 30% standard deduction
    Net rental income = (annual_rent - municipal_tax) * 0.70
    """
    income_after_municipal = annual_rent - municipal_tax_paid
    standard_deduction_30 = round(income_after_municipal * 0.30, 2)
    net_rental_income = round(income_after_municipal - standard_deduction_30, 2)

    return {
        "annual_rent": annual_rent,
        "municipal_tax_paid": municipal_tax_paid,
        "standard_deduction_30_percent": standard_deduction_30,
        "net_rental_income": net_rental_income,
        "note": "Net rental income added to normal income for slab taxation"
    }


# ── 4. Master tax calculator ──────────────────────────────────────────────────

def calculate_tax(
    normal_income: float,
    regime: str = "new",
    stcg: float = 0,
    ltcg: float = 0,
    rental_income_net: float = 0
) -> dict:
    """
    Master calculator — handles all income types correctly:
    - Normal income + rental goes through slabs
    - Capital gains taxed separately at flat rates
    - Surcharge calculated on TOTAL income (all sources combined)
    - Capital gains never counted twice
    """

    standard_deduction = 75000 if regime == "new" else 50000

    # Slab income = normal income + rental (both go through slabs)
    slab_income = normal_income + rental_income_net
    taxable_slab_income = max(0, slab_income - standard_deduction)

    # Slab tax
    slab_tax, breakdown = calculate_slab_tax(taxable_slab_income, regime)

    # Capital gains tax (separate, flat rates)
    cg_result = calculate_capital_gains_tax(stcg, ltcg)
    cg_tax = cg_result["total_capital_gains_tax"]

    # 87A rebate — only on slab tax, NOT on capital gains
    rebate = 0
    if regime == "new" and taxable_slab_income <= 1200000:
        rebate = min(slab_tax, 60000)
    elif regime == "old" and taxable_slab_income <= 500000:
        rebate = min(slab_tax, 12500)

    slab_tax_after_rebate = max(0, slab_tax - rebate)

    # Total income for surcharge threshold (ALL sources combined)
    total_income_for_surcharge = normal_income + rental_income_net + stcg + ltcg
    total_tax_before_surcharge = slab_tax_after_rebate + cg_tax

    # Surcharge on TOTAL tax
    surcharge = 0
    if total_income_for_surcharge > 50000000:
        surcharge = total_tax_before_surcharge * 0.37
    elif total_income_for_surcharge > 20000000:
        surcharge = total_tax_before_surcharge * 0.25
    elif total_income_for_surcharge > 10000000:
        surcharge = total_tax_before_surcharge * 0.15
    elif total_income_for_surcharge > 5000000:
        surcharge = total_tax_before_surcharge * 0.10

    # Cess 4% on (total tax + surcharge)
    cess = round((total_tax_before_surcharge + surcharge) * 0.04, 2)
    surcharge = round(surcharge, 2)

    total_tax = round(total_tax_before_surcharge + surcharge + cess, 2)

    return {
        "normal_income": normal_income,
        "rental_income_net": rental_income_net,
        "stcg": stcg,
        "ltcg": ltcg,
        "regime": regime,
        "standard_deduction": standard_deduction,
        "taxable_slab_income": taxable_slab_income,
        "slab_tax": round(slab_tax, 2),
        "rebate_87a": round(rebate, 2),
        "capital_gains_tax": cg_tax,
        "capital_gains_detail": cg_result,
        "surcharge": surcharge,
        "cess": cess,
        "total_tax": total_tax,
        "effective_rate": round((total_tax / total_income_for_surcharge) * 100, 2) if total_income_for_surcharge > 0 else 0,
        "slab_breakdown": breakdown
    }


# ── 5. Exemptions finder ──────────────────────────────────────────────────────

def find_exemptions(user_profile: dict) -> dict:
    exemptions = []
    total_savings = 0

    investments_80c = user_profile.get("investments_80c", 0)
    if investments_80c > 0:
        claimed = min(investments_80c, 150000)
        exemptions.append({
            "section": "80C",
            "description": "PPF, ELSS, LIC, EPF, NSC, home loan principal",
            "claimed": claimed,
            "max_limit": 150000
        })
        total_savings += claimed

    health_premium = user_profile.get("health_insurance_premium", 0)
    age = user_profile.get("age", 30)
    limit_80d = 50000 if age >= 60 else 25000
    if health_premium > 0:
        claimed = min(health_premium, limit_80d)
        exemptions.append({
            "section": "80D",
            "description": "Health insurance premium",
            "claimed": claimed,
            "max_limit": limit_80d
        })
        total_savings += claimed

    hra_received = user_profile.get("hra_received", 0)
    basic_salary = user_profile.get("basic_salary", 0)
    rent_paid = user_profile.get("rent_paid", 0)
    city_type = user_profile.get("city_type", "non-metro")

    if hra_received > 0 and rent_paid > 0:
        hra_percent = 0.50 if city_type == "metro" else 0.40
        hra_exemption = min(
            hra_received,
            basic_salary * hra_percent,
            rent_paid - (basic_salary * 0.10)
        )
        hra_exemption = max(0, hra_exemption)
        if hra_exemption > 0:
            exemptions.append({
                "section": "HRA",
                "description": f"House Rent Allowance ({'Metro' if city_type == 'metro' else 'Non-metro'})",
                "claimed": round(hra_exemption, 2),
                "max_limit": hra_received
            })
            total_savings += hra_exemption

    edu_loan = user_profile.get("education_loan_interest", 0)
    if edu_loan > 0:
        exemptions.append({
            "section": "80E",
            "description": "Education loan interest (no upper limit)",
            "claimed": edu_loan,
            "max_limit": -1
        })
        total_savings += edu_loan

    nps = user_profile.get("nps_contribution", 0)
    if nps > 0:
        claimed = min(nps, 50000)
        exemptions.append({
            "section": "80CCD(1B)",
            "description": "NPS contribution (over and above 80C)",
            "claimed": claimed,
            "max_limit": 50000
        })
        total_savings += claimed

    home_loan_interest = user_profile.get("home_loan_interest", 0)
    if home_loan_interest > 0:
        claimed = min(home_loan_interest, 200000)
        exemptions.append({
            "section": "24(b)",
            "description": "Home loan interest deduction",
            "claimed": claimed,
            "max_limit": 200000
        })
        total_savings += claimed

    return {
        "exemptions": exemptions,
        "total_deductions": round(total_savings, 2),
        "count": len(exemptions)
    }


# ── 6. Regime comparison ──────────────────────────────────────────────────────

def compare_regimes(
    normal_income: float,
    total_deductions: float,
    stcg: float = 0,
    ltcg: float = 0,
    rental_income_net: float = 0
) -> dict:

    # New regime — deductions don't apply (except built-in standard deduction)
    new_result = calculate_tax(normal_income, "new", stcg, ltcg, rental_income_net)

    # Old regime — apply all deductions to normal income only
    normal_income_after_deductions = max(0, normal_income - total_deductions)
    old_result = calculate_tax(normal_income_after_deductions, "old", stcg, ltcg, rental_income_net)

    savings = old_result["total_tax"] - new_result["total_tax"]
    recommended = "new" if new_result["total_tax"] <= old_result["total_tax"] else "old"

    return {
        "new_regime_tax": new_result["total_tax"],
        "old_regime_tax": old_result["total_tax"],
        "recommended_regime": recommended,
        "savings_with_recommended": abs(round(savings, 2)),
        "reason": (
            f"New regime saves ₹{abs(savings):,.0f} — deductions not enough to offset old regime rates"
            if recommended == "new"
            else f"Old regime saves ₹{abs(savings):,.0f} — your deductions of ₹{total_deductions:,.0f} make it worthwhile"
        ),
        "new_regime_details": new_result,
        "old_regime_details": old_result
    }


# ── 7. ITR form picker ────────────────────────────────────────────────────────

def get_itr_form(user_profile: dict) -> dict:
    income_sources = user_profile.get("income_sources", [])
    annual_income = user_profile.get("annual_income", 0)

    has_business = "business" in income_sources
    has_capital_gains = "capital_gains" in income_sources
    has_foreign = "foreign_income" in income_sources
    has_salary = "salary" in income_sources

    if has_business:
        form = "ITR-3"
        reason = "You have business or professional income"
    elif has_capital_gains or has_foreign:
        form = "ITR-2"
        reason = "You have capital gains or foreign income"
    elif has_salary:
        form = "ITR-1" if annual_income <= 5000000 else "ITR-2"
        reason = "Salaried individual" if annual_income <= 5000000 else "Income exceeds ₹50L"
    else:
        form = "ITR-1"
        reason = "Default for salaried individuals"

    return {
        "recommended_form": form,
        "reason": reason,
        "filing_deadline": "July 31, 2025 (AY 2025-26)",
        "late_fee": "₹5,000 if filed after deadline (₹1,000 if income < ₹5L)"
    }


# ── 8. What-if analyzer ───────────────────────────────────────────────────────

def whatif_analysis(
    normal_income: float,
    current_deductions: dict,
    proposed_changes: dict,
    stcg: float = 0,
    ltcg: float = 0,
    rental_income_net: float = 0
) -> dict:
    """
    Analyzes tax impact of a proposed change
    proposed_changes example:
    {"investments_80c": 50000, "home_loan_interest": 200000}
    """

    # Current tax
    current_exemptions = find_exemptions(current_deductions)
    current_comparison = compare_regimes(
        normal_income, current_exemptions["total_deductions"],
        stcg, ltcg, rental_income_net
    )
    current_rec = current_comparison["recommended_regime"]
    current_tax = current_comparison["new_regime_tax"] if current_rec == "new" else current_comparison["old_regime_tax"]

    # Proposed tax — merge current + proposed changes
    proposed_profile = {**current_deductions, **proposed_changes}
    proposed_exemptions = find_exemptions(proposed_profile)
    proposed_comparison = compare_regimes(
        normal_income, proposed_exemptions["total_deductions"],
        stcg, ltcg, rental_income_net
    )
    proposed_rec = proposed_comparison["recommended_regime"]
    proposed_tax = proposed_comparison["new_regime_tax"] if proposed_rec == "new" else proposed_comparison["old_regime_tax"]

    tax_saved = round(current_tax - proposed_tax, 2)

    return {
        "current_tax": current_tax,
        "proposed_tax": proposed_tax,
        "tax_saved": tax_saved,
        "current_deductions": current_exemptions["total_deductions"],
        "proposed_deductions": proposed_exemptions["total_deductions"],
        "additional_deductions": round(proposed_exemptions["total_deductions"] - current_exemptions["total_deductions"], 2),
        "verdict": f"This change saves you ₹{tax_saved:,.0f} in taxes" if tax_saved > 0 else f"This change increases tax by ₹{abs(tax_saved):,.0f}",
        "recommended_regime_after_change": proposed_rec
    }