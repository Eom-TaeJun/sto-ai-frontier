# sto-ai-frontier

### 토큰증권 제도 시행 시나리오와 교보증권의 사업 선택

**증권업의 변화는 중개자의 소멸보다 업무와 책임의 재배분에 가깝다고 본다.** 토큰화는 권리 기록과 대조 방식을, AI는 정보 처리 방식을 바꿀 수 있다. 교보증권이 확보할 가치는 그 변화 속에서 고객이 맡길 업무를 정하고, 위험과 운영 비용을 감당하며 반복 가능한 서비스로 만드는 데 있다.

이 저장소는 그 견해를 **공개 공시로 확인한 현재 사업, 수익 방어·창출 가설, 제도 시나리오, 합성데이터 기반 운영 검토 예시**로 연결한 개인 프로젝트다. 사업 분석은 공개 실적 자료를 사용하며, 코드 POC 입력은 합성데이터다. 회사의 내부 시스템·내부 자료 또는 실제 상품 구현이 아니다.

## 먼저 볼 자료

| 읽을 내용 | 자료 |
|---|---|
| 금융환경·세계 규제·미국과 한국 기관 대응을 AI 에이전트와 증권업의 수익구조로 연결 | [통합 보고서 · 2026-10-05 개정 2.0](reports/digital-finance-agentic-securities.html) · [웹 미리보기](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Eom-TaeJun/sto-ai-frontier/main/reports/digital-finance-agentic-securities.html) |
| 제도 시행에 대비한 교보의 수익 방어·초기 진입·투자 확대 조건 검토 | [단일 HTML 보고서](reports/us-tokenization-kyobo.html) · [열기·출처·검증 안내](reports/README.md) |
| 지금 교보의 위치·메인 사업·수익·돈의 흐름은 어떠한가 | [현재 사업 기준선](docs/KYOBO_BUSINESS_BASELINE.md) |
| 경쟁사·파트너와 어떤 관계이며 자본과 조달 차이는 무엇인가 | [경쟁사 비교](docs/PEER_COMPARISON.md) |
| 수익은 어디서 지키고 누가 새 서비스에 돈을 내는가 | [수익 방어와 창출](docs/KYOBO_PROFIT_STRATEGY.md) |
| 제도 시행에 따라 무엇이 가능해지고 교보는 무엇부터 해야 하는가 | [시나리오와 대응안](docs/KYOBO_SCENARIOS.md) |
| 돈·자산·위험·정보·판단 권한은 누구 사이에서 이동하는가 | [업무와 책임 지도](docs/CHAIN_MAP.md) |
| 어떤 관측 결과가 나오면 사업 판단을 바꾸는가 | [지표와 수정 조건](docs/INDICATOR_CHARTER.md) |
| 사실·회사 발표·개인 해석의 근거는 무엇인가 | [근거 목록](docs/EVIDENCE_MAP.md) |
| 코드가 실제로 만들어 낸 결과는 무엇인가 | [실행 결과](outputs/reports/decision_brief.md) |

## 교보 관점의 선택

**가설:** 주식·해외선물의 중개 고객과 조달·운용 마진을 지키면서, 기존 IB 고객의 반복 사모사채 조달과 기관 MMF의 판매·관리 수요를 비교한다. 실제 추가 수수료·총원가·위험이 확인되는 한 업무부터 확장하고, 비상장주식·와인·공연IP 등은 권리·실사·회수 조건을 통과한 경우에 선택한다. 온체인 결제는 후속 선택지다.

2026년 상반기 수탁수수료 약 1,611억원 중 주식 약 787억원·해외선물 약 688억원이 91.57%를 차지한다. 토큰증권의 초기 매출은 미확인이므로 현재 수익을 곧바로 대체하는 사업으로 가정하지 않는다. 수탁고·총영업수익·순이자·영업이익은 서로 다른 값이다.

| 시나리오 | 사업 범위에 대한 가정 | 제안하는 교보의 행동 | 판단을 바꿀 신호 |
|---|---|---|---|
| S0, 일정·연계 지연 | 제도 또는 운영 인프라가 계획보다 늦어짐 | 기존 전자증권 방식의 문서·대조 업무 개선, 연결 투자 분할 | 승인·연계 일정과 실제 테스트 결과 |
| S1, 초기 인프라 가동 | 기관 전용 사모 MMF·사채 등의 경로 준비 | 기존 거래 대비 반복 발행·권리관리 비용과 고객 지불 의사 검증 | 재사용 가능한 거래, 비용 절감, 반복 계약 |
| S2, 조각투자 사업 확대 | 자산의 권리·가치평가·보관·유통 조건 충족 | 명품·콘텐츠 중 실사와 사후관리가 표준화되는 자산만 선택 | 순수수익, 환매·매각 지연, 민원·분쟁 |
| S3, 온체인 결제 연결 | 결제수단 제도·원장 연계·최종성 확인 | 지급결제 파트너와 좁은 DvP 실험, 자금 부담 비교 | 결제 실패·대기자금·상환·복구 성과 |

S1·S2는 병행 가능한 사업 가설이며 확정된 순서가 아니다. S3의 시기는 미정이다. 정책 내용과 제안의 구분은 [근거 목록](docs/EVIDENCE_MAP.md)에 남겼다.

## 구현한 범위

- 자산 8건: 권리·중복 담보·사후관리·유통 경로·원장 대조 조건을 점검한다. 채무성 자산에만 상환 현금흐름과 스트레스 계산을 적용한다.
- 문서 10건: 명시적 발행규모·DSCR을 구조화 근거와 대조하고, 한정된 보장 표현과 용어 혼동 패턴을 확인한다.
- 결과: 근거가 빠진 항목과 보류 이유를 기록하고, 별도 권한을 가진 담당자에게 넘긴다.

현재 단계는 **합성데이터로 동작을 확인한 POC**다. 문서 검사는 규칙 기반 기준선이며 LLM·RAG·일반 문맥 이해·DART 연계는 구현하지 않았다. 실제 토큰 발행·지갑·수탁·결제·24시간 거래도 구현하지 않았다. `READY_FOR_INTERNAL_REVIEW`는 내부 검토 후보이지 발행 승인이나 투자 적격 판정이 아니다.

## 실행

Python 3.10 이상, 표준 라이브러리만 사용한다. 네트워크·비밀키·외부 패키지가 필요 없다.

```bash
python run.py
python -m unittest discover -s tests -v
```

실행 위치와 관계없이 `outputs/reports/`에 JSON·CSV·요약을 생성한다. 기준일과 정책 출처는 `data/policy_snapshot.json`, POC 예제 입력은 `data/synthetic/`에 있다. `SYN-` 근거 ID는 시나리오상의 입력 근거 표시이며 실제 계약서가 아니다. [데이터 정의](data/README.md)를 참고한다.

공개 공시 분석은 POC와 별개다. `python analysis/business_baseline.py`로 `data/public/kyobo_2026h1.json`의 단위·합계와 가정 민감도를 재계산한다. [분석 노트북](analysis/kyobo_business_analysis.ipynb)은 같은 계산과 그림을 포함하며 그림 재생성에는 Matplotlib이 필요하다. 원문 전사값을 감사한 것이 아니라 산술·정의·범위를 점검한 결과다.

## 분석과 검증의 범위

토큰화와 AI가 새 상품과 자동화를 확대한다는 설명을, 기초자산 위험과 승인 책임까지 점검하는 기준으로 구체화했다. **누가 어떤 업무를 맡고, 어떤 비용을 줄이며, 어떤 조건에서 사업을 멈출지**를 시나리오와 코드의 판단 기준으로 삼았다.

공개 근거, 판단 조건, 실행 결과를 확인할 수 있도록 구성했다. 합성데이터 POC의 결과는 실제 현업 적용·상품 구현·사업 효과를 증명하지 않는다. 미국 사례 보고서도 교보의 확정 사업계획이나 국내 판매·담보·결제 허용을 뜻하지 않는다.

기준일: 2026-10-04. 작성 목적: 증권업의 현재 수익구조와 환경 변화, 교보증권의 조건부 대응 방식 분석.

## 기업·보험·연금의 수요와 금융기관의 수익 · 2026-10-11

[금융 전체 보고서 08C](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Eom-TaeJun/sto-ai-frontier/main/reports/financial-environment-response.html#demand-contract-economics)는 선정 고객 8곳의 자금관리·투자 접근 방식을 미국 금융기관의 공개 요율·위탁·운용·수탁·유통 경로 10개와 연결한다. 총비용의 조건, 기간별 공시 손익, 직접 접근에 따른 중개료 변화, 도입 속도에 따른 대응과 한국의 적용 조건을 함께 비교한다.

원장은 비공개 `Eom-TaeJun/finance`의 `finance_economics/collection/demand_contracts_2026-10-11.json`이며, 이 저장소에는 검토한 HTML 읽기본과 고정 버전의 가져오기·검증 기록을 둔다. 공개 보수·공시·고객 보고를 검토한 것으로, 비공개 서명계약이나 고객 전체 비용·인과효과를 확보한 조사는 아니다. 기존 증권업 보고서·예제 데이터·Pages·수집 일정은 이번 추가에서 변경하지 않았다.

## 경제 기능과 금융시장의 조정 · 2026-10-11

[일반 금융환경 보고서 08D장](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Eom-TaeJun/sto-ai-frontier/main/reports/financial-environment-response.html#economic-theory-functions)은 기존 08A–08C의 이론·기관 선택·실제 수요와 계약을 생산·노동·화폐·채권·안전자산·한국 자금 이동의 함수로 연결한다. AI의 과업 비용과 인간 노동시간, 지급·담보 편익과 은행 조달, 온체인 채권의 발행/유통, 플랫폼 접근성과 FX 수요·공급을 구분했다.

16개 선정 원문과 기존 기록 참조 9개를 연결하고 작성자의 설명식 10개·강한 조건부 시나리오 5개·판단 갱신 3개를 추가했다. 식의 계수는 추정하지 않았고 1년 원화 환산 수익 계산기의 초기 값은 설명용 가정이다. 현재 상품 조건·한국 접근 허용과 향후 거의 마찰 없는 글로벌 접근 가정은 별도로 읽는다. 원장 스냅샷은 finance `8d9d31ec74e30e0f87f5fb8c10bc89b4a1a8b6b4`, 공개 HTML SHA256은 `afbaf1d9abbeaf7862d75d0400d760cecfba82d6f7c3532620d368b477423f12`다. 원문 위치·버전·읽기 경계는 근거 H에 있으며 새 경제적 효과나 기존 G 대응 실험의 결과를 측정한 기록은 아니다.

## AI 생산성과 달러 접근의 동시 변화 · 2026-10-11

[일반 금융환경 보고서 08E장](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Eom-TaeJun/sto-ai-frontier/main/reports/financial-environment-response.html#joint-productivity-dollar)은 AI의 생산성 개선과 달러 안전자산 접근 확대를 함께 가정하고 미국·한국의 은행·증권·운용·중앙은행 여덟 역할을 비교한다. 수입·조달·위험의 변화, 강점의 조건과 지금 준비할 일·확대·방향 전환 기준을 세 고객 자금사슬에 연결한다.

공급 확산·투자 과열·플랫폼 집중과 동시 환매의 세 분기에서 대응이 어떻게 달라지는지 설명한다. 선정 공시·상품 조건·중앙은행 연구는 근거 I에 따로 두었으며 기관의 확정 계획·추정 계수·실측 인과효과로 표시하지 않는다. 원장은 finance의 `finance_economics/collection/joint_scenario_2026-10-11.json`이며 고정 내용 버전과 보고서 해시는 이 저장소의 `reports/financial-environment-response.verification.json`에서 확인한다. 기존 08A–08D·증권업 보고서와 예제 데이터는 보존했다.

## 2025년 하반기 온체인 전환의 이유 · 2026-10-11

[일반 금융환경 보고서 08F장](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Eom-TaeJun/sto-ai-frontier/main/reports/financial-environment-response.html#onchain-institutional-turn)은 미국 상반기의 회계·감독 절차 변화와 하반기의 법률·상품·인프라 연결을 한국의 예금토큰 실증·은행/플랫폼 협력·STO 입법 시간선과 비교한다. 기존 사건을 재검증한 종합이며, 거래비용·금융중개·네트워크 효과·불확실성 아래 투자로 기관의 유인을 설명한다.

20개 선정 URL은 기존 사실의 재열람과 비온체인 담보 계약 대조도 포함한다. 산업 전체의 태도나 도입 인과효과를 측정한 결과가 아니다. JPM 공식 색인의 제한된 확인, FDIC 공식 배포문, 사건/발표/효력/운영의 구별은 근거 J에 남겼다. 원장은 finance의 `finance_economics/collection/onchain_turn_2026-10-11.json`이며 고정 버전과 해시는 공개 검증 기록에서 확인한다.

## 미국 기관의 실제 온체인 업무 · 2026-10-11

[일반 금융환경 보고서 08G장](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Eom-TaeJun/sto-ai-frontier/main/reports/financial-environment-response.html#onchain-workflow-economics)은 Citi, JPM/OCBC, BNY·GS, IBKR, Broadridge DLR, BUIDL, BENJI의 7개 업무를 기존 계좌·API·펀드·수탁·repo와 비교한다. 공개 요율·회계 수입·고객 절감 추산과 작성자의 수익·고객관계 해석을 구별하고 한국 은행·증권·운용·수탁/공공 인프라의 선행 업무를 제안한다.

18개 선정 출처에는 기존 자료 재확인이 포함된다. IBKR 금액별 비용은 공개 누진요율의 산술이며 총비용 실측값이 아니다. Broadridge의 Canton 서비스 매출은 고객 DLR 이용료·현금·순이익과 다르다. 한국의 정책방향·입법예고는 확정 규칙이나 운영 완료가 아니다. 원장은 finance의 `finance_economics/collection/onchain_workflows_2026-10-11.json`이며 공개 검증 기록에 고정 버전과 해시를 남긴다.

## 주간 자금 변화와 기존 가설의 연결 · 2026-10-12

[일반 금융환경 보고서 08H](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Eom-TaeJun/sto-ai-frontier/main/reports/financial-environment-response.html#weekly-funding-hypotheses)에 미국 은행·국채와 한국 자금순환/국제수지의 선정 관측을 기존 전망·대응과 연결했다. 총예금에서 조달 고객·가격·집중으로, 거래량/AUM에서 순수익·보수 배분으로 판단 기준을 구체화한다. 미국·한국 은행·증권/딜러·운용·중앙은행 8개 유형의 대응과 4개 조건부 분기를 비교한다.

5개 공식 출처·15개 지표는 finance의 기존 주간 원장에서 재사용했으며 새 독립 관측으로 합산하지 않는다. 기간·단위가 다른 미국 주간/월말과 한국 분기/월간 자료를 구별하고 강한 AI·달러 접근 가정을 실제 도입이나 인과효과로 확정하지 않는다. 조달비·AI 절감의 수치 예시는 설명용 가정이다. 원장 canonical은 finance의 `finance_economics/collection/weekly_hypothesis_bridge_2026-10-12.json`이며 고정 내용 커밋·해시는 공개 검증 JSON에서 확인한다. 기존 본문·근거와 증권업 보고서는 보존한다.

## 미국 변화와 한국 은행의 수익 대응 · 2026-10-12

[일반 금융환경 보고서 08I](https://htmlpreview.github.io/?https://raw.githubusercontent.com/Eom-TaeJun/sto-ai-frontier/main/reports/financial-environment-response.html#us-korea-bank-response)는 미국 은행·코인 발행자·운용사·플랫폼의 역할과 한국 시중은행·인터넷은행의 실제 선택을 비교한다. KB·신한·카카오·토스·케이뱅크와 광주은행 협업을 예금 조달·신용·지급/FX·제휴 수입으로 연결했다. 고객 잔액이 투자상품으로 옮겨도 어떤 관계 수익을 남길지, 외부 AI가 선택할 때 어떤 은행 기능이 강점을 가질지를 조건부로 분석한다.

16개 선정 공식 출처·9개 절·5개 은행 카드는 전체 은행 조사나 신규 사건16건을 뜻하지 않는다. 잠정 IR·분기/반기·은행/그룹·총수수료/플랫폼 부분집합, MOU·실증·지정·실제 운영을 구분한다. 원장은 finance의 `finance_economics/collection/us_korea_bank_response_2026-10-12.json`이다. 고정 내용 커밋과 해시는 공개 검증 JSON에 있으며 상세 근거 M에서 확인 위치와 미완료를 읽을 수 있다. 기존08A–08H·다른 증권 보고서·예제 데이터는 보존한다.
