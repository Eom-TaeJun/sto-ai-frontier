"""Rule baseline for tagged statements, not an LLM or semantic validator.

Only explicit patterns are recognized. A clean result never grants approval.
"""
import re
from decimal import Decimal, InvalidOperation

AMOUNT = re.compile(r"발행규모\s*[:：]?\s*([\d,]+(?:\.\d+)?)\s*(억원|백만원|만원|원)")
UNITS = {"억원": Decimal(100000000), "백만원": Decimal(1000000), "만원": Decimal(10000), "원": Decimal(1)}
GUARANTEE = re.compile(r"(?:원금|수익)(?:과\s*수익)?(?:을|를)?\s*(?:보장합니다|보장한다|보장됩니다)")
EQUIVALENCE = re.compile(r"토큰증권(?:과|은)\s*가상자산(?:은|과)?\s*동일(?:합니다|하다)")
DSCR = re.compile(r"DSCR\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)


def review_document(document):
    if document.get("synthetic") is not True:
        raise ValueError("This prototype accepts explicitly synthetic documents only")
    text = document["text"]
    findings = []

    def flag(code, match, message, evidence_ref=None):
        findings.append({"code": code, "message": message,
                         "quote": match.group(0), "span": [match.start(), match.end()],
                         "evidence_ref": evidence_ref, "owner": "공시·준법 담당자"})

    for match in GUARANTEE.finditer(text):
        flag("GUARANTEE_REVIEW", match, "보장 표현의 근거·조건·적합성 검토 필요")
    for match in EQUIVALENCE.finditer(text):
        flag("TERM_EQUIVALENCE_REVIEW", match, "증권 여부와 토큰 형태를 동일 개념으로 처리했는지 검토")
    for match in AMOUNT.finditer(text):
        ref = document.get("amount_source_ref")
        expected = document.get("expected_amount_won")
        if expected is None or not ref:
            flag("AMOUNT_EVIDENCE_MISSING", match, "대조할 발행금액 근거가 없음", ref)
        else:
            try:
                baseline = Decimal(str(expected))
                valid = not isinstance(expected, bool) and baseline.is_finite() and baseline >= 0
            except (InvalidOperation, ValueError, TypeError):
                valid = False
            if not valid:
                flag("AMOUNT_EVIDENCE_INVALID", match, "금액 근거 값이 유효하지 않음", ref)
            elif Decimal(match.group(1).replace(",", "")) * UNITS[match.group(2)] != baseline:
                flag("AMOUNT_MISMATCH", match, "같은 의미의 발행규모가 근거 값과 다름", ref)
    for match in DSCR.finditer(text):
        value = Decimal(match.group(1))
        if value < 1:
            flag("COVERAGE_SHORTFALL", match, "정의·기간을 확인하고 상환 현금흐름 부족 검토")
        expected = document.get("expected_dscr")
        ref = document.get("dscr_source_ref")
        if expected is None or not ref:
            flag("DSCR_EVIDENCE_MISSING", match, "DSCR 산식·기간·근거 확인 필요", ref)
        else:
            try:
                baseline = Decimal(str(expected))
                valid = not isinstance(expected, bool) and baseline.is_finite() and baseline >= 0
            except (InvalidOperation, ValueError, TypeError):
                valid = False
            if not valid:
                flag("DSCR_EVIDENCE_INVALID", match, "DSCR 근거 값이 유효하지 않음", ref)
            elif value != baseline:
                flag("DSCR_MISMATCH", match, "DSCR이 제공된 구조화 근거와 다름", ref)
    return {"document_id": document["document_id"], "synthetic": True,
            "engine": "DETERMINISTIC_RULE_BASELINE", "findings": findings,
            "review_status": "FLAGS_REQUIRE_REVIEW" if findings else "NO_RULE_FLAGS",
            "approval_required": True, "approved": False,
            "scope": "명시적 표현·태그가 있는 수치만 검사; 오탈자·일반 문맥 전체 검증 미구현"}
