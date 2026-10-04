# 토큰화 이후의 증권업: 미국 사례와 교보증권의 선택

[us-tokenization-kyobo.html](us-tokenization-kyobo.html)을 다운로드해 브라우저에서 연다. 데이터·코드·스타일을 포함한 단일 파일이며, 보고서를 읽는 데 별도 설치나 네트워크가 필요하지 않다. 원문 출처를 방문할 때는 인터넷이 필요하다. GitHub 파일 화면은 웹페이지 호스팅 화면이 아니므로 파일을 내려받아 연다.

기준일은 2026-10-04다. 개인 경험·지원동기 대신 회사의 현재 수익, 금융 기능의 이동, 미국 사례의 실제 권리와 사용 단계, 한국 적용 조건을 다룬다.

## 담은 내용

- 교보 2026년 상반기 공시: 수탁수수료 구성, 연결 부문 손익, 자본·조달·고객 신탁자산의 구분.
- BlackRock BUIDL·BSTBL·BRSRV, BNY·Goldman Sachs, JPMorgan, DTCC/DTC, Robinhood, Apollo·KKR·Hamilton Lane의 12개 비교 사례.
- 상품·판매·명의개서·보관·현금·담보의 역할, 보수와 책임.
- 한국의 시행 예정·추진방향·입법예고를 나눠 본 3개 조건부 환경 시나리오.
- 기존 수익 방어, 신규 유료 역할, 투자 확대·수정·보류 신호.
- 설명용 가정의 증분 공헌 계산기와 AI 업무 지원의 적용·검증 조건.

사례 제목을 선택하면 해당 세부 근거가 열린다. 출처 버튼은 영역에 사용한 검토 데이터와 provenance를 보여준다. 계산기에 입력한 값은 회사 전망이나 실제 사업 가격이 아니다. FACT·THEORY·INTERPRETATION·HYPOTHESIS·UNKNOWN과 사용 단계를 구분한다.

## 근거와 소스

[reviewed_snapshot.json](source/reviewed_snapshot.json)에 공시 전사값·사례·출처 URL·자료 기준일·해석·미확인 범위가 들어 있다. 원문은 교보 DART, 한국 금융위, 미국 발행자·인프라 공식 문서와 SEC 공시를 중심으로 사용했다. 교보 AI 구축은 공급사 발표 보도로 구분했다. 일부 JPM TCN 자료는 직접 접근 403으로 공식 검색색인을 검토한 한계를 표시했다.

[ReportContent.jsx](source/ReportContent.jsx), [report.css](source/report.css)는 보고서의 작성 영역이다. canonical Data report runtime의 `src/content/report/`에 대응하며, snapshot은 `src/data.json`에 대응한다. 보호된 공통 UI·차트·출처·편집·내보내기 기능을 유지해 컴파일하고, 검증된 split build에서 offline HTML로 내보냈다. 이 소스 묶음 자체가 독립 npm 프로젝트는 아니다.

## 검증 범위

[verification.json](verification.json)에 검증과 미실시 항목을 구분해 남겼다. canonical build·offline export, 데이터 구조·단위·합계, 가정 산식과 경계값을 확인했다. 저장소의 기존 합성데이터 실행과 22개 테스트도 통과했다. 해당 테스트는 미국 사례의 법률 효과나 교보의 사업 수익성을 검증하는 테스트가 아니다.

현재 실행 환경에서 브라우저 바이너리 설치가 실패해 실제 브라우저의 화면·클릭·모바일 동작 검증은 실시하지 못했다. 빌드 성공을 해당 검증의 통과로 표시하지 않았다.
