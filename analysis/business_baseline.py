"""공개 공시의 단위·합계와 명시적 민감도 가정을 재계산한다."""
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/public/kyobo_2026h1.json"


def calculate():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    connected, separate = data["connected"], data["separate"]
    assert data["data_type"] == "PUBLIC_REPORTED_FINANCIAL_FACTS"
    assert data["synthetic"] is False
    for period in ("2026h1", "2025h1"):
        assert sum(connected[f"segment_operating_profit_{period}"].values()) == connected[f"operating_profit_{period}"]
    assert sum(connected["fees_2026h1"].values()) == connected["gross_fee_income_2026h1"]
    assert connected["gross_fee_income_2026h1"] - connected["fee_expense_2026h1"] == connected["net_fee_income_2026h1"]
    assert connected["interest_income_2026h1"] - connected["interest_expense_2026h1"] == connected["net_interest_income_2026h1"]
    assert sum(connected["borrowings"].values()) == connected["borrowings_total"]
    for scope in (connected, separate):
        assert scope["assets"] - scope["liabilities"] == scope["equity"]
    mix = separate["brokerage_fee_breakdown_krw_million"]
    total = separate["brokerage_fee_total_krw_million"]
    assert sum(mix.values()) == total
    assert abs(total * 1000 - connected["fees_2026h1"]["수탁"]) < 1000

    def eok_from_krw_thousand(value):
        return round(value / 100000, 2)  # 억원, 1억원 = 100000천원

    result = {
        "source": data["report_url"], "as_of": data["as_of"],
        "flow_period": data["flow_period"], "unit": "KRW_100_MILLION",
        "brokerage_fee_mix": [
            {"category": name, "fee": round(value / 100, 2), "share_pct": round(value / total * 100, 2)}
            for name, value in mix.items()
        ],
        "stock_and_overseas_futures_share_pct": round((mix["주식"] + mix["해외선물"]) / total * 100, 2),
        "net_fee_growth_pct": round((connected["net_fee_income_2026h1"] / connected["net_fee_income_2025h1"] - 1) * 100, 2),
        "net_interest_growth_pct": round((connected["net_interest_income_2026h1"] / connected["net_interest_income_2025h1"] - 1) * 100, 2),
        "ib_operating_profit_growth_pct": round((connected["segment_operating_profit_2026h1"]["투자은행"] / connected["segment_operating_profit_2025h1"]["투자은행"] - 1) * 100, 2),
        "self_and_derivative_operating_profit_sum": eok_from_krw_thousand(connected["segment_operating_profit_2026h1"]["자기매매"] + connected["segment_operating_profit_2026h1"]["장내외파생"]),
        "separate_equity": eok_from_krw_thousand(separate["equity"]),
        "illustrative_brokerage_fee_pressure": [
            {"effective_fee_reduction_pct": rate, "revenue_reduction_same_h1_volume": round(total / 100 * rate / 100, 2)}
            for rate in (5, 10, 20)
        ],
        "illustrative_new_fee_scale": [
            {"issued_amount_trillion_won": 1, "incremental_fee_after_variable_cost_bp": bp, "contribution_before_fixed_cost_and_risk": float(Decimal("10000") * Decimal(bp) / Decimal("10000"))}
            for bp in (10, 20, 50)
        ],
        "scenario_caveats": [
            "수수료 압력은 거래량·고객 구성 고정 가정의 반기 매출 민감도다. 이익 감소 전망이 아니다.",
            "신규 수수료율은 변동비 차감 후 가정. 실제 가격·수요·과금 적법성은 미확인이고 고정비·조달·자본·손실은 추가 차감한다.",
            "신규 사업 수수료를 기존 고객 수수료로부터 이전한 경우 증분으로 계산하지 않는다."
        ],
        "validation": "공시 전사값의 부문·수수료·이자·차입·대차 합계 및 백만원 반올림 대조 통과"
    }
    return result


def main():
    result = calculate()
    destination = ROOT / "outputs/reports/business_baseline_metrics.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
