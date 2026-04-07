# Market Intelligence Workflow

이 디렉터리는 회사별 최신 정보 수집·검증·축적·주간 전략 해석을 위한 운영 문서 세트입니다.

## 구성
- `01_system_overview.md`: 전체 시스템 개요
- `02_operating_workflow.md`: 일간/주간 운영 흐름
- `03_agent_design.md`: 멀티 에이전트 역할 설계
- `04_scoring_and_validation.md`: 신뢰도·중요도·확실도 평가 체계
- `05_document_structure.md`: 문서 저장 구조와 파일 규칙
- `06_weekly_strategy_synthesis.md`: 주간 전략 브리프 작성 방식
- `07_kpi_and_cost_control.md`: 품질/비용 KPI와 운영 통제
- `08_execution_playbook.md`: 실제 실행 플레이북
- `templates/`: 바로 복사해서 쓸 수 있는 템플릿 모음

## 권장 운영 원칙
1. 일간 수집은 저비용 모델로 빠르게 수행한다.
2. 검증과 중복 제거는 별도 에이전트로 분리한다.
3. 원문 링크와 근거를 반드시 남긴다.
4. 주간 요약은 기사 요약이 아니라 전략 문서로 작성한다.
5. 회사별 문서와 테마 문서를 함께 운영한다.

## Physical AI 자동 파이프라인 (Obsidian 볼트)

- **Obsidian 볼트 루트**: `market-intel/` — 회사·테마·주간 리포트는 `[[위키링크]]`로 서로 연결된다.
- **설정**: `config/companies.yaml`, `config/keywords.yaml`, `config/sources.yaml`
- **실행 (로컬)**:
  - `cd pipeline`
  - `py -3 -m pip install -r requirements.txt`
  - `py -3 -m intel_pipeline collect` — RSS 수집, 중복 제거(SQLite), 소스 카드·일간 로그 갱신
  - `py -3 -m intel_pipeline weekly` — 최근 N일 DB 기준 주간 리포트 (`market-intel/reports/weekly_strategy/`)
- **LLM (선택)**: 환경 변수 `OPENAI_API_KEY`가 있으면 일간 이벤트 보강에 `gpt-4o-mini`, 주간에 `gpt-4o` 요약을 사용한다. 없으면 휴리스틱만 사용한다.
- **KPI 로그**: `pipeline/logs/kpi.jsonl`
- **GitHub Actions**: `.github/workflows/intel-collect.yml` (1일 3회), `intel-weekly.yml` (매주 월요일). 저장소 시크릿에 `OPENAI_API_KEY` 선택 설정. 멱등을 위해 `pipeline/state/intel.sqlite`를 커밋하는 것을 권장한다.
- **Windows 작업 스케줄러**: `scripts/intel_collect.ps1`을 참고해 동일 명령을 주기 실행하면 된다.
- **월간 리밸런싱**: `config/` 키워드·피드 목록과 `market-intel/dictionaries/`를 검토한다 (`02_operating_workflow.md` 주기).
