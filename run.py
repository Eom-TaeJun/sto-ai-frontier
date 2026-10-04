"""Rebuild every output locally without dependencies, credentials, or network."""
import csv
import json
from collections import Counter
from pathlib import Path
from src.screening import screen_asset
from src.token_design import design_token
from src.disclosure_review import review_document

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs/reports"


def read(name):
    return json.loads((ROOT / "data/synthetic" / name).read_text(encoding="utf-8"))


def write_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    policy = json.loads((ROOT / "data/policy_snapshot.json").read_text(encoding="utf-8"))
    cases = read("rwa_samples.json")
    results = [screen_asset(a, policy["as_of"]) for a in cases]
    designs = [design_token(a, r, policy) for a, r in zip(cases, results)]
    documents = read("disclosure_samples.json")
    reviews = [review_document(d) for d in documents]
    OUT.mkdir(parents=True, exist_ok=True)
    write_json("asset_screening_result.json", results)
    write_json("token_review_checklists.json", designs)
    write_json("disclosure_review.json", reviews)
    fields = ["asset_id", "asset_class", "status", "coverage_ratio", "stressed_coverage_ratio", "issuance_authorized"]
    with (OUT / "asset_screening_result.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: r[k] for k in fields} for r in results)
    counts = dict(Counter(r["status"] for r in results))
    issues = sum(len(r["findings"]) for r in reviews)
    measured = {"scope": "SYNTHETIC_CASES_ONLY", "as_of": policy["as_of"],
                "assets": len(results), "status_counts": counts,
                "documents": len(reviews), "rule_findings": issues,
                "issuance_approvals": sum(r["issuance_authorized"] for r in results),
                "disclosure_approvals": sum(r["approved"] for r in reviews)}
    write_json("run_summary.json", measured)
    lines = ["# 실행 결과", "",
             "권리·근거가 빠진 자산을 자동 통과시키지 않고, 담당자에게 확인할 항목을 남겼다.", "",
             f"합성 자산 {len(results)}건, 합성 문서 {len(reviews)}건을 검사했다. 실증 성능·현업 채택 결과는 측정하지 않았다.", "",
             "| 자산 | 판단 | 기본/스트레스 상환배율 | 확인 또는 보류 이유 |",
             "|---|---|---|---|"]
    for r in results:
        ratio = "해당 없음" if r["coverage_applicability"] == "NOT_APPLICABLE" else f"{r['coverage_ratio']} / {r['stressed_coverage_ratio']}"
        reasons = ", ".join(r["hold_reasons"] + r["review_reasons"]) or "시나리오상 입력 조건 충족; 별도 승인 필요"
        lines.append(f"| {r['asset_id']} | {r['status']} | {ratio} | {reasons} |")
    lines += ["", f"문서에서 규칙 기반 확인 항목 {issues}건을 생성했다. 발행 승인 0건, 공시 승인 0건.", "",
              "READY_FOR_INTERNAL_REVIEW는 합성 시나리오의 내부 검토 후보라는 뜻이다.",
              "발행 가능성·투자 적합성·수익성·24시간 유통을 의미하지 않는다.", "",
              "기초자산 위험은 원장의 표현이 바뀌어도 남는다. 토큰화의 사업 가치는 권리관리·대조 업무가 얼마나 줄고, 고객이 그 서비스에 얼마를 지불하는지로 별도 검증해야 한다.", "",
              "다음 검증: 실제 권리 서류와 합법적으로 확보한 비식별 문서로 처리시간·오탐·누락·사람의 검토시간을 비교한다."]
    (OUT / "decision_brief.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(measured, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
