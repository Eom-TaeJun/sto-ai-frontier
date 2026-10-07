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

FINANCE_COMMIT = "2d5132971e4b6f8449df98e33a62f92d5b153634"
ROOT = Path(__file__).resolve().parents[1]
REPORT = "finance_economics/reports/financial_environment_response.html"
BUILDER = "finance_economics/reports/build_financial_system_extension.py"
SOURCE = "finance_economics/updates/2026-10-08/financial_system_hypotheses_source.json"
FINANCE_MANIFEST = "finance_economics/updates/2026-10-08/financial_system_extension_verification.json"
MARKDOWN = "finance_economics/updates/2026-10-08/global_finance_system_hypotheses_2026-10-08.md"
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
    if public != public_base and public != finance:
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
    return public_base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finance-checkout", required=True, type=Path)
    args = parser.parse_args()
    checkout = args.finance_checkout.resolve()
    commit = git(checkout, "rev-parse", "HEAD").decode().strip()
    if commit != FINANCE_COMMIT:
        raise ValueError("Finance HEAD is not the fixed reviewed snapshot; review a new version before updating this script")
    for path in (REPORT, BUILDER, SOURCE, FINANCE_MANIFEST, MARKDOWN):
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
    subprocess.run([sys.executable, str(checkout / BUILDER)], check=True)
    regenerated = (checkout / REPORT).read_text(encoding="utf-8")
    if digest(regenerated.encode("utf-8")) != before:
        raise ValueError("Finance builder does not reproduce its reviewed HTML")
    compatible_report(module, public, regenerated, data["base_report_sha256_normalized_lf"])
    verified = json.loads((checkout / FINANCE_MANIFEST).read_text(encoding="utf-8"))
    if verified["result_sha256"] != before or verified["source_sha256"] != digest((checkout / SOURCE).read_bytes()):
        raise ValueError("Finance verification hashes do not match")
    if verified["new_measured_followup_results"] != 0:
        raise ValueError("This extension has no measured followup outcomes")

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
            for path in (REPORT, BUILDER, SOURCE, FINANCE_MANIFEST, MARKDOWN)
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
            "facts": "Selected primary-source statements and historical stages; company statements remain attributed.",
            "hypotheses": "Author's strong conditional financial-system scenarios, not confirmed adoption or probabilities.",
            "unobserved": "No actual followup business experiment, measured profit, current global-law census or institution readiness claim."
        },
        "preservation_scope": "Only WF-marked extension, its navigation, metadata, footer and evidence are imported. Earlier general-finance report and October 5 date remain unchanged; Kyobo HTML is not rewritten.",
        "verification_scope": "Pinned finance inputs, canonical validation and deterministic regeneration, hashes, unchanged base, unique IDs and local fragment links. Browser/source/economic review are recorded separately; these are not product outcome tests.",
        "protected_kyobo_report_sha256": protected_hash
    }
    PUBLIC_REPORT.write_text(regenerated, encoding="utf-8", newline="\n")
    PUBLIC_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if digest(protected.read_bytes()) != protected_hash:
        raise ValueError("Protected Kyobo report changed")
    print(json.dumps({"public_report_bytes": len(regenerated.encode("utf-8")), "canonical_commit": commit, "earlier_report_preserved": True, "kyobo_report_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
