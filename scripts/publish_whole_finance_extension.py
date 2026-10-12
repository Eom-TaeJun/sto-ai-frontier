#!/usr/bin/env python3
"""Import the reviewed finance extension without duplicating its canonical data.

Requires a local, committed finance checkout. No network, Git write or publication.
The older public report must match the source after removing extension markers.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

FINANCE_COMMIT = "46033518fa4f16132a605649c563650d810d0930"
REVIEWED_PREVIOUS_PUBLIC_SHA256 = "b4a94682f7193cbcbc96d1bd8fb31af9e52a14aa858052ff2ef2d1c919147361"
ROOT = Path(__file__).resolve().parents[1]
REPORT = "finance_economics/reports/financial_environment_response.html"
BUILDER = "finance_economics/reports/build_financial_system_extension.py"
SOURCE = "finance_economics/updates/2026-10-08/financial_system_hypotheses_source.json"
FINANCE_MANIFEST = "finance_economics/updates/2026-10-08/financial_system_extension_verification.json"
MARKDOWN = "finance_economics/updates/2026-10-08/global_finance_system_hypotheses_2026-10-08.md"
PERSPECTIVE_SOURCE = "finance_economics/collection/us_finance_perspectives_2026-10-11.json"
PERSPECTIVE_BUILDER = "finance_economics/collection/render_perspectives.py"
PERSPECTIVE_MARKDOWN = "finance_economics/collection/us_finance_perspectives_2026-10-11.md"
DISCOVERY_SUMMARY = "finance_economics/collection/runs/2026-10-11-summary.json"
DEMAND_SOURCE = "finance_economics/collection/demand_contracts_2026-10-11.json"
DEMAND_BUILDER = "finance_economics/collection/render_demand.py"
DEMAND_MARKDOWN = "finance_economics/collection/demand_contracts_2026-10-11.md"
ECONOMIC_SOURCE = "finance_economics/collection/economic_functions_2026-10-11.json"
ECONOMIC_BUILDER = "finance_economics/collection/render_economic.py"
ECONOMIC_MARKDOWN = "finance_economics/collection/economic_functions_2026-10-11.md"
JOINT_SOURCE = "finance_economics/collection/joint_scenario_2026-10-11.json"
JOINT_BUILDER = "finance_economics/collection/render_joint.py"
JOINT_MARKDOWN = "finance_economics/collection/joint_scenario_2026-10-11.md"
ONCHAIN_SOURCE = "finance_economics/collection/onchain_turn_2026-10-11.json"
ONCHAIN_BUILDER = "finance_economics/collection/render_onchain.py"
ONCHAIN_MARKDOWN = "finance_economics/collection/onchain_turn_2026-10-11.md"
WORKFLOWS_SOURCE = "finance_economics/collection/onchain_workflows_2026-10-11.json"
WORKFLOWS_BUILDER = "finance_economics/collection/render_workflows.py"
WORKFLOWS_MARKDOWN = "finance_economics/collection/onchain_workflows_2026-10-11.md"
WEEKLY_SOURCE = "finance_economics/collection/weekly_hypothesis_bridge_2026-10-12.json"
WEEKLY_BUILDER = "finance_economics/collection/render_weekly_bridge.py"
WEEKLY_MARKDOWN = "finance_economics/collection/weekly_hypothesis_bridge_2026-10-12.md"
WEEKLY_LEDGER = "finance_economics/updates/2026-10-03/monitoring_run_2026-10-12.json"
BANK_SOURCE = "finance_economics/collection/us_korea_bank_response_2026-10-12.json"
BANK_BUILDER = "finance_economics/collection/render_bank_response.py"
BANK_MARKDOWN = "finance_economics/collection/us_korea_bank_response_2026-10-12.md"
SECURITIES_SOURCE = "finance_economics/collection/korea_securities_asset_managers_2026-10-12.json"
SECURITIES_BUILDER = "finance_economics/collection/render_securities_response.py"
SECURITIES_MARKDOWN = "finance_economics/collection/korea_securities_asset_managers_2026-10-12.md"
INSURANCE_SOURCE = "finance_economics/collection/insurance_pensions_2026-10-12.json"
INSURANCE_BUILDER = "finance_economics/collection/render_insurance_pensions.py"
INSURANCE_MARKDOWN = "finance_economics/collection/insurance_pensions_2026-10-12.md"
REVIEWED_INPUTS = (REPORT, BUILDER, SOURCE, FINANCE_MANIFEST, MARKDOWN,
                   PERSPECTIVE_SOURCE, PERSPECTIVE_BUILDER, PERSPECTIVE_MARKDOWN, DISCOVERY_SUMMARY,
                   DEMAND_SOURCE, DEMAND_BUILDER, DEMAND_MARKDOWN,
                   ECONOMIC_SOURCE, ECONOMIC_BUILDER, ECONOMIC_MARKDOWN,
                   JOINT_SOURCE, JOINT_BUILDER, JOINT_MARKDOWN,
                   ONCHAIN_SOURCE, ONCHAIN_BUILDER, ONCHAIN_MARKDOWN,
                   WORKFLOWS_SOURCE, WORKFLOWS_BUILDER, WORKFLOWS_MARKDOWN,
                   WEEKLY_SOURCE, WEEKLY_BUILDER, WEEKLY_MARKDOWN, WEEKLY_LEDGER,
                   BANK_SOURCE, BANK_BUILDER, BANK_MARKDOWN,
                   SECURITIES_SOURCE, SECURITIES_BUILDER, SECURITIES_MARKDOWN,
                   INSURANCE_SOURCE, INSURANCE_BUILDER, INSURANCE_MARKDOWN)
PUBLIC_REPORT = ROOT / "reports/financial-environment-response.html"
PUBLIC_MANIFEST = ROOT / "reports/financial-environment-response.verification.json"


def digest(value):
    return hashlib.sha256(value).hexdigest()


def normalise(value):
    return value.replace(b"\r\n", b"\n")


def git(checkout, *args):
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={checkout.as_posix()}", "-C", str(checkout), *args]
    )


def verify_committed(checkout, commit, path):
    expected = git(checkout, "show", f"{commit}:{path}")
    actual = (checkout / path).read_bytes()
    if normalise(expected) != normalise(actual):
        raise ValueError(f"Uncommitted finance input: {path}; preserve and review those edits")


def compatible_report(module, public, finance, expected_hash):
    public_base = module.strip_extension(public)
    finance_base = module.strip_extension(finance)
    if public_base != finance_base or digest(public_base.encode("utf-8")) != expected_hash:
        raise ValueError("Public report has unrelated edits; preserve and merge them before import")
    if public != public_base and public != finance and digest(public.encode("utf-8")) != REVIEWED_PREVIOUS_PUBLIC_SHA256:
        raise ValueError("Existing public extension differs; preserve and review those edits before import")
    if module.strip_extension(finance) != public_base:
        raise ValueError("Import would alter earlier content")
    ids = re.findall(r'\bid="([^"]+)"', finance)
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate HTML identity")
    links = re.findall(r'\bhref="#([^"]+)"', finance)
    if not set(links).issubset(ids):
        raise ValueError("Broken HTML fragment link")
    for i in range(1, 8):
        if ids.count(f"system-G{i}") != 1:
            raise ValueError("Missing reviewed G hypothesis")
    if ids.count("us-finance-perspectives") != 1:
        raise ValueError("Missing reviewed perspectives extension")
    if ids.count("demand-contract-economics") != 1:
        raise ValueError("Missing reviewed demand and contract extension")
    if ids.count("economic-theory-functions") != 1:
        raise ValueError("Missing reviewed economic-function extension")
    if ids.count("joint-productivity-dollar") != 1:
        raise ValueError("Missing reviewed joint-shock extension")
    if ids.count("onchain-institutional-turn") != 1:
        raise ValueError("Missing historical institutional transition review")
    if ids.count("onchain-workflow-economics") != 1:
        raise ValueError("Missing operational workflow comparison")
    if ids.count("weekly-funding-hypotheses") != 1:
        raise ValueError("Missing weekly funding and hypothesis analysis")
    if ids.count("us-korea-bank-response") != 1:
        raise ValueError("Missing US-to-Korea bank response comparison")
    if ids.count("korea-securities-asset-managers") != 1:
        raise ValueError("Missing Korean securities and asset-manager response comparison")
    if ids.count("insurance-pension-alm") != 1:
        raise ValueError("Missing insurance and pension ALM comparison")
    return public_base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finance-checkout", required=True, type=Path)
    args = parser.parse_args()
    checkout = args.finance_checkout.resolve()
    commit = git(checkout, "rev-parse", "HEAD").decode().strip()
    if commit != FINANCE_COMMIT:
        raise ValueError("Finance HEAD is not the fixed reviewed snapshot; review a new version before updating this script")
    for path in REVIEWED_INPUTS:
        verify_committed(checkout, commit, path)

    specification = importlib.util.spec_from_file_location("reviewed_finance_builder", checkout / BUILDER)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    data = json.loads((checkout / SOURCE).read_text(encoding="utf-8"))
    module.validate(data)
    original = (checkout / REPORT).read_text(encoding="utf-8")
    public = PUBLIC_REPORT.read_text(encoding="utf-8")
    base = compatible_report(module, public, original, data["base_report_sha256_normalized_lf"])
    before = digest(original.encode("utf-8"))
    subprocess.run([sys.executable, "-X", "utf8", "-B", str(checkout / BUILDER)], check=True)
    regenerated = (checkout / REPORT).read_text(encoding="utf-8")
    if digest(regenerated.encode("utf-8")) != before:
        raise ValueError("Finance builder does not reproduce its reviewed HTML")
    compatible_report(module, public, regenerated, data["base_report_sha256_normalized_lf"])
    verified = json.loads((checkout / FINANCE_MANIFEST).read_text(encoding="utf-8"))
    if verified["result_sha256"] != before or verified["source_sha256"] != digest((checkout / SOURCE).read_bytes()):
        raise ValueError("Finance verification hashes do not match")
    if verified["new_measured_followup_results"] != 0:
        raise ValueError("The preserved G designs have no measured response experiment outcomes")
    demand = json.loads((checkout / DEMAND_SOURCE).read_text(encoding="utf-8"))
    if verified["demand_extension"]["source_sha256"] != digest((checkout / DEMAND_SOURCE).read_bytes()):
        raise ValueError("Demand canonical hash does not match")
    if demand["boundaries"]["causal_effect_measured"] or demand["boundaries"]["private_customer_contracts_obtained"]:
        raise ValueError("Unsupported causal outcome or private signed-contract claim")
    economic = json.loads((checkout / ECONOMIC_SOURCE).read_text(encoding="utf-8"))
    if verified["economic_extension"]["source_sha256"] != digest((checkout / ECONOMIC_SOURCE).read_bytes()):
        raise ValueError("Economic canonical hash does not match")
    if economic["boundaries"]["parameters_estimated"] or economic["boundaries"]["causal_outcomes_measured"]:
        raise ValueError("Explanatory functions have no estimated coefficients or causal response outcomes")
    joint = json.loads((checkout / JOINT_SOURCE).read_text(encoding="utf-8"))
    if verified["joint_extension"]["source_sha256_normalized_lf"] != digest(normalise((checkout / JOINT_SOURCE).read_bytes())):
        raise ValueError("Joint canonical hash does not match")
    if any(joint["boundaries"].values()):
        raise ValueError("Joint scenario has no estimated outcomes, confirmed plans or external Page/schedule changes")

    onchain = json.loads((checkout / ONCHAIN_SOURCE).read_text(encoding="utf-8"))
    if verified["onchain_extension"]["source_sha256_normalized_lf"] != digest(normalise((checkout / ONCHAIN_SOURCE).read_bytes())) or any(onchain["boundaries"].values()):
        raise ValueError("Onchain source hash or scope mismatch")

    workflows = json.loads((checkout / WORKFLOWS_SOURCE).read_text(encoding="utf-8"))
    if verified["workflows_extension"]["source_sha256_normalized_lf"] != digest(normalise((checkout / WORKFLOWS_SOURCE).read_bytes())) or any(workflows["boundaries"].values()):
        raise ValueError("Workflow source hash or scope mismatch")

    weekly = json.loads((checkout / WEEKLY_SOURCE).read_text(encoding="utf-8"))
    if verified["weekly_bridge_extension"]["source_sha256_normalized_lf"] != digest(normalise((checkout / WEEKLY_SOURCE).read_bytes())) or any(weekly["boundaries"].values()):
        raise ValueError("Weekly analysis source hash or scope mismatch")
    if weekly["actual_response_outcomes"] is not None:
        raise ValueError("Macro observations do not identify institution response outcomes")
    if weekly["evidence_ledger"]["path"] != WEEKLY_LEDGER or weekly["evidence_ledger"]["lf_sha256"] != digest(normalise((checkout / WEEKLY_LEDGER).read_bytes())):
        raise ValueError("Referenced weekly evidence ledger differs from its reviewed snapshot")
    if not verified["weekly_bridge_extension"]["prior_08A_to_08G_content_and_evidence_preserved"]:
        raise ValueError("Earlier extensions must remain intact")

    bank = json.loads((checkout / BANK_SOURCE).read_text(encoding="utf-8"))
    if verified["bank_response_extension"]["source_sha256_normalized_lf"] != digest(normalise((checkout / BANK_SOURCE).read_bytes())) or any(bank["boundaries"].values()):
        raise ValueError("Bank response source hash or scope mismatch")
    if bank["actual_response_outcomes"] is not None or not verified["bank_response_extension"]["prior_08A_to_08H_content_and_evidence_preserved"]:
        raise ValueError("Bank response must preserve prior sections and unobserved outcomes")

    securities = json.loads((checkout / SECURITIES_SOURCE).read_text(encoding="utf-8"))
    if verified["securities_response_extension"]["source_sha256_normalized_lf"] != digest(normalise((checkout / SECURITIES_SOURCE).read_bytes())) or any(securities["boundaries"].values()):
        raise ValueError("Securities response source hash or scope mismatch")
    if securities["actual_response_outcomes"] is not None or not verified["securities_response_extension"]["prior_08A_to_08I_content_and_evidence_preserved"]:
        raise ValueError("Securities response must preserve prior sections and unobserved outcomes")

    insurance = json.loads((checkout / INSURANCE_SOURCE).read_text(encoding="utf-8"))
    if verified["insurance_pension_extension"]["source_sha256_normalized_lf"] != digest(normalise((checkout / INSURANCE_SOURCE).read_bytes())) or any(insurance["boundaries"].values()):
        raise ValueError("Insurance/pension source hash or scope mismatch")
    if insurance["actual_response_outcomes"] is not None or not verified["insurance_pension_extension"]["prior_08A_to_08J_content_and_evidence_preserved"]:
        raise ValueError("Insurance/pension analysis must preserve prior sections and unobserved outcomes")

    protected = ROOT / "reports/digital-finance-agentic-securities.html"
    protected_hash = digest(protected.read_bytes())
    manifest = {
        "schema_version": "1.0",
        "original_report_record_date": data["original_report_record_date"],
        "extension_record_date": data["record_date"],
        "canonical_repository": "Eom-TaeJun/finance",
        "canonical_repository_visibility": "private_at_publication_check",
        "canonical_commit": commit,
        "canonical_files": {
            path: {"sha256_normalized_lf": digest(normalise((checkout / path).read_bytes()))}
            for path in REVIEWED_INPUTS
        },
        "public_report": PUBLIC_REPORT.relative_to(ROOT).as_posix(),
        "public_report_sha256": before,
        "base_report_sha256_normalized_lf": digest(base.encode("utf-8")),
        "existing_report_preserved_exactly_after_removing_extension": True,
        "prior_date_preserved": "2026-10-05",
        "prior_ids_and_source_links_preserved": True,
        "hypothesis_ids": [h["id"] for h in data["hypotheses"]],
        "source_records": len(data["sources"]),
        "observation_designs": len(data["observations"]),
        "new_measured_followup_results": 0,
        "content_boundaries": {
            "facts": "Selected primary-source statements, customer choices, public prices/contracts and reported period financial values; company statements remain attributed.",
            "hypotheses": "Author's strong conditional financial-system scenarios and explanatory economic functions, not confirmed adoption, estimated parameters or probabilities.",
            "unobserved": "No causal response experiment, customer total-cost measurement, private signed customer agreement, isolated digital-product net profit, global-law census or institution readiness claim. Reported company financial values are separately scoped."
        },
        "preservation_scope": "Only WF-marked extension, its navigation, metadata, footer and evidence are imported. Earlier general-finance report and October 5 date remain unchanged; Kyobo HTML is not rewritten.",
        "verification_scope": "Pinned finance inputs, canonical validation and deterministic regeneration, hashes, unchanged base, unique IDs and local fragment links. Browser/source/economic review are recorded separately; these are not product outcome tests.",
        "protected_kyobo_report_sha256": protected_hash
    }
    manifest["schema_version"] = "1.10"
    manifest["perspectives_extension"] = verified["perspectives_extension"]
    manifest["demand_extension"] = verified["demand_extension"]
    manifest["economic_extension"] = verified["economic_extension"]
    manifest["joint_extension"] = verified["joint_extension"]
    manifest["onchain_extension"] = verified["onchain_extension"]
    manifest["workflows_extension"] = verified["workflows_extension"]
    manifest["weekly_bridge_extension"] = verified["weekly_bridge_extension"]
    manifest["bank_response_extension"] = verified["bank_response_extension"]
    manifest["securities_response_extension"] = verified["securities_response_extension"]
    manifest["insurance_pension_extension"] = verified["insurance_pension_extension"]
    manifest["reviewed_previous_public_sha256"] = REVIEWED_PREVIOUS_PUBLIC_SHA256
    manifest["perspective_source_repository"] = "finance; public HTML is the reviewed reading copy, not another fact ledger"
    PUBLIC_REPORT.write_text(regenerated, encoding="utf-8", newline="\n")
    PUBLIC_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if digest(protected.read_bytes()) != protected_hash:
        raise ValueError("Protected Kyobo report changed")
    print(json.dumps({"public_report_bytes": len(regenerated.encode("utf-8")), "canonical_commit": commit, "earlier_report_preserved": True, "kyobo_report_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
