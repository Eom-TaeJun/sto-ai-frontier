"""Produce a review checklist; no ledger, custody, or issuance is implemented."""


def design_token(asset, result, policy):
    institutional_private = asset.get("investor_type") == "institutional" and asset.get("offering") == "private"
    candidate = asset["asset_class"] in {"mmf_token", "corporate_bond"} and institutional_private
    return {
        "asset_id": asset["asset_id"], "stage": "CONCEPT_CHECKLIST",
        "screening_status": result["status"],
        "policy_snapshot_date": policy["as_of"],
        "scheduled_effective_date": policy["scheduled_effective_date"],
        "phase_one_policy_candidate": candidate,
        "policy_candidate_note": "정책상 후보와 개별 상품의 적법성·발행 승인은 별도" if candidate else "증권 유형·신탁 구조·공모 또는 사모 경로를 추가 검토",
        "policy_source": policy["source_url"],
        "rights_to_specify": ["현금흐름 배분", "양도·환매 조건", "불이행 시 권리", "권리기록과 원장 대조"],
        "unresolved_requirements": result["hold_reasons"] + result["review_reasons"],
        "institution_roles": {
            "issuer": "기초자산·권리와 공시자료 제공",
            "securities_firm": "해당 업무 인가 범위 및 책임 확인 필요",
            "account_management": "적용 제도·등록 요건에 따른 주체 별도 확인",
            "custody": "법적 수탁 관계·키 통제·복구 책임 별도 확인",
        },
        "capabilities": {
            "ledger_connected": False, "custody_implemented": False,
            "atomic_settlement_implemented": False, "trading_24_7_verified": False,
        },
        "issuance_authorized": False, "approval_owner": "별도 권한을 가진 담당자",
    }
