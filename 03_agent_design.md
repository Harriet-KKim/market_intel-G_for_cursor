# 03. Agent Design

## 권장 멀티 에이전트 구성

### 1) Collector Agent
역할:
- 지정된 소스에서 자료 수집
- 문서 메타데이터 확보
- 본문 추출
- URL 정규화

출력:
- raw document record

### 2) Tagging Agent
역할:
- 회사명
- 제품명
- 기술 키워드
- 시장/지역
- 인물
- 이벤트 타입
태깅 수행

출력:
- normalized metadata

### 3) Dedup Agent
역할:
- 중복 기사 제거
- 재인용 기사 식별
- 같은 사건의 반복 보도 묶기

판단 기준:
- 제목 유사도
- claim overlap
- 동일 출처 기반 여부
- 게시 시간 차이

### 4) Fact Extraction Agent
역할:
- 기사에서 사실 주장 단위 추출
- 의견과 사실 분리
- 숫자/날짜/조직명 구조화

출력 예시:
- 주장 A: 공장 증설
- 주장 B: 제품 출시 일정 연기
- 주장 C: 신규 채용 확대

### 5) Verification Agent
역할:
- 독립 근거 교차 검증
- 공식 발표 여부 확인
- 근거가 약한 정보 격리
- 상충하는 주장 표시

### 6) Source Critic Agent
역할:
- 소스 품질 평가
- 과장/홍보성/추정 표현 탐지
- 2차 인용 경고

### 7) Event Builder Agent
역할:
- 관련 주장들을 이벤트 단위로 통합
- 이벤트 importance/confidence 지정
- 관련 회사 문서에 연결

### 8) Company Context Agent
역할:
- 해당 회사의 기존 맥락과 연결
- 과거 이벤트와 비교
- “새로운 정보인지” 판별

### 9) Weekly Synthesis Agent
역할:
- 일주일 이상 축적된 이벤트 압축
- 방향성 변화 해석
- 시장 구조 변화 분석
- 전략적 인사이트 도출

## 운영 포인트
- 일간 레이어에서는 저비용 모델 사용
- 주간 레이어에서만 최고 성능 모델 사용
- 에이전트 간 출력 포맷을 표준화
- 각 에이전트는 reasoning보다 구조화 출력 중심으로 설계
