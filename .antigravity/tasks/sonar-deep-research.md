# Code-Sonar Deep Research — Task

## Input

<!-- 아래에 분석할 프로젝트 경로를 입력하세요 -->

**분석 대상 프로젝트:** `<!-- 예: /path/to/project 또는 프로젝트명 -->`

<!-- 아래에 집중 질문을 작성하세요 (선택) -->

## 집중 질문

## Q1.
<!-- 질문 내용 -->

## Q2.
<!-- 질문 내용 -->

## Output

- Output directory: `{output_dir}/{project}/deep-research/`

## Task 1: 초기화 및 탐색

`.env`와 `sonar/config/sonar-config.md`를 읽고 타겟 프로젝트와 설정을 확인한다.
질문이 있으면 파싱하여 `SEARCH_KEYWORDS`와 `FOCUS_AREAS`를 추출한다.
`SONAR_CROSS_REPO_SEARCH=true`이면 `cross-repo-tracer`로 GitHub MCP 탐색을 실행한다.
탐색 결과를 `progress.txt`에 기록한다.

## Task 2: 병렬 심층 분석

다음 에이전트를 동시 스폰한다:
- `env-matrix-analyst` → `ENV-MATRIX.md`
- `integration-flow-analyst` → `INTEGRATION-FLOW.md`
- `business-workflow-analyst` (deep mode) → `BUSINESS-STATE-MACHINE.md`
- `analyst-backend` (deep mode) → `USER-JOURNEY.md`

분석 완료 후 `progress.txt`에 기록한다.

## Task 3: 질문 답변 및 통합 출력

각 질문에 대해 코드 근거 기반 답변을 `QUESTION-ANSWER.md`에 작성한다.
`evidence-auditor`와 `qa-reviewer`로 품질 검증 후 `DEEP-RESEARCH.md`를 최종 생성한다.
완료 마커를 `progress.txt`에 기록한다.
