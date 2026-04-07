# 05. Document Structure

## 권장 폴더 구조
```text
market-intel/
  companies/
    company_a/
      profile.md
      daily/
        2026-04-07.md
      weekly/
        2026-W15.md
      sources/
        SRC-2026-0410-001.md
    company_b/
      ...
  themes/
    humanoid_robotics.md
    industrial_ai.md
    supply_chain.md
  reports/
    weekly_strategy/
      2026-W15.md
  dictionaries/
    company_keywords.md
    event_taxonomy.md
```

## 문서 유형
### 1) Company Profile
역할:
- 해당 회사의 장기 축적 요약본
- 사업 영역, 제품군, 기술 포지션, 공급망, 지역, 조직 변화
- 최근 4~8주 핵심 변화 요약

### 2) Daily Intel Log
역할:
- 당일 수집/검증 결과 누적
- 이벤트별 기록
- source link와 confidence 포함

### 3) Source Card
역할:
- 개별 소스에 대한 구조화 메모
- 원문 링크
- 핵심 주장
- 신뢰도
- 활용 여부

### 4) Weekly Strategy Report
역할:
- 회사별 또는 전체 시장 단위의 주간 전략 정리
- 단순 요약이 아닌 해석 중심 문서

### 5) Theme Document
역할:
- 여러 회사를 가로지르는 기술/시장 축 문서
- 예: 반도체, 로봇 SoC, 공급망, 인력 채용, 가격 전략

## 작성 원칙
- fact / evidence / interpretation / implication 구분
- 원문 URL 유지
- 날짜 표준화
- 루머는 별도 표시
- 추론은 추론이라고 명시
