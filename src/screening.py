"""Separate rights/operations gates from class-specific financial checks.

All thresholds are illustrative project assumptions, not regulatory criteria.
"""
from datetime import date
from math import isfinite

COMMON_GATES = (
    "rights_verified", "unencumbered", "servicing_defined",
    "investor_route_defined", "custody_reconciliation_defined",
)
CLASS_GATES = {
    "renewable_receivables": ("debtor_confirmation",),
    "corporate_bond": ("debt_terms_verified",),
    "content_ip": ("ip_chain_verified", "revenue_waterfall_defined"),
    "luxury": ("authenticity_verified", "valuation_verified", "physical_custody_verified"),
    "fractional_art": ("authenticity_verified", "valuation_verified", "physical_custody_verified"),
    "mmf_token": ("nav_reconciled", "redemption_terms_verified", "liquidity_plan_verified"),
}
DEBT_CLASSES = {"renewable_receivables", "corporate_bond"}


def number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (ValueError, TypeError):
        return None
    return result if isfinite(result) else None


def screen_asset(asset, as_of, *, stress_haircut=0.20, max_age_days=90):
    if asset.get("synthetic") is not True:
        raise ValueError("This prototype accepts explicitly synthetic cases only")
    if not 0 <= stress_haircut <= 1:
        raise ValueError("stress_haircut must be between 0 and 1")
    if max_age_days < 0:
        raise ValueError("max_age_days must be non-negative")
    asset_class = asset.get("asset_class")
    if asset_class not in CLASS_GATES:
        raise ValueError(f"Unsupported asset class: {asset_class}")
    today = date.fromisoformat(as_of)
    hold, review, checks = [], [], []
    for gate in COMMON_GATES + CLASS_GATES[asset_class]:
        value = asset.get("gates", {}).get(gate)
        evidence = asset.get("evidence", {}).get(gate)
        status = "CONFIRMED_IN_SCENARIO" if value is True and evidence else "UNKNOWN"
        if value is False:
            status = "FAILED_IN_SCENARIO"
            hold.append(gate)
        elif value is not True or not evidence:
            review.append(gate)
        checks.append({"check": gate, "status": status, "evidence_ref": evidence})
    try:
        observed = date.fromisoformat(asset["data_as_of"])
        age = (today - observed).days
        if age < 0 or age > max_age_days:
            review.append("data_freshness")
    except (KeyError, TypeError, ValueError):
        age = None
        review.append("data_freshness")

    coverage = stressed = None
    if asset_class in DEBT_CLASSES:
        cash = number(asset.get("cash_available_won"))
        service = number(asset.get("debt_service_won"))
        if cash is None or service is None or cash < 0 or service <= 0:
            review.append("debt_cashflow_missing_or_invalid")
        elif not asset.get("financial_source_ref"):
            review.append("financial_evidence_missing")
        else:
            coverage = cash / service
            stressed = cash * (1 - stress_haircut) / service
            if coverage < 1 or stressed < 1:
                hold.append("stress_cashflow_shortfall")
            elif coverage < 1.2:
                review.append("illustrative_coverage_threshold")
    status = "HOLD" if hold else "NEEDS_REVIEW" if review else "READY_FOR_INTERNAL_REVIEW"
    return {
        "asset_id": asset["asset_id"], "asset_class": asset_class,
        "synthetic": True, "status": status,
        "hold_reasons": hold, "review_reasons": review,
        "coverage_ratio": round(coverage, 4) if coverage is not None else None,
        "stressed_coverage_ratio": round(stressed, 4) if stressed is not None else None,
        "coverage_applicability": "DEBT_CASHFLOW_ONLY" if asset_class in DEBT_CLASSES else "NOT_APPLICABLE",
        "data_age_days": age, "checks": checks,
        "financial_source_ref": asset.get("financial_source_ref"),
        "issuance_authorized": False, "next_owner": "상품·법무·준법·운영 담당자",
    }
