# 08. Execution Playbook

## 0. 준비
- 추적 회사 리스트 정의
- 회사별 핵심 키워드 정의
- 테마 문서 초기 생성
- 소스 우선순위 설정
- 점수 체계 합의

## 1. 일간 배치 실행
- 신규 자료 수집
- 메타데이터 정규화
- 태깅
- 중복 제거
- fact extraction
- source reliability 부여

## 2. 검증 실행
- 독립 출처 확인
- 공식 원문 확인
- 상충 정보 표시
- claim confidence 산정
- strategic importance 산정

## 3. 이벤트 생성 및 저장
- 이벤트 단위로 통합
- company daily log에 기록
- source card 저장
- 관련 theme doc 링크
- company profile 업데이트 후보 표기

## 4. 주간 전략 리포트 생성
- 주간 이벤트 묶기
- high-signal cluster 선정
- 변화 해석
- 전략 시사점 도출
- 리스크와 질문 정리

## 5. 리뷰 루프
- 잘못된 신호 기록
- 키워드 사전 수정
- 소스 가중치 조정
- 에이전트 프롬프트 개선
- 고비용 모델 투입 지점 재점검

## 추천 역할 분담
- Analyst 1: 회사/키워드 운영
- Analyst 2: 검증 및 예외 처리
- Strategist: 주간 synthesis 검토
- Librarian/Operator: 문서 구조와 품질 관리

## 최소 실행 버전(MVP)
- 대상 회사 5개
- 하루 2회 수집
- 소스 3종(뉴스/SNS/공식자료)
- 주 1회 전략 리포트
- 회사별 profile + daily log만 우선 운영

## 확장 버전
- 특허/채용/논문/GitHub까지 확장
- 테마 문서 활성화
- 경쟁사 비교 자동화
- 리스크 얼럿 도입
- 월간 deep dive 보고서 추가
