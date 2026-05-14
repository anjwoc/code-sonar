# ATLS Dashboard Integration Prompt

## 목적

이 프롬프트는 `ATLS`와 `/Users/jaecjeong/lab/memo/atsl/dashboard`를 연동할 때, 하네스 엔지니어링 원칙에 따라 작업 범위를 분석하고 구현 계획을 생성하기 위한 실행 프롬프트다.

핵심 목표는 다음과 같다.

- 현재 dashboard의 mock 기반 화면을 실제 `ATLS` 산출물과 연결한다.
- `summary -> task list -> task plan -> issue requirement manifest -> acceptance manifest -> test run -> evidence report` 흐름을 대시보드에서 조회 가능하게 한다.
- source-backed requirement와 execution evidence를 분리해 시각화한다.
- 프론트 미구현으로 연동이 불가능한 지점은 숨기지 않고 명시적으로 보고한다.

## 하네스 엔지니어링 원칙

1. source와 evidence를 분리한다.
2. mock 데이터와 실제 산출물 매핑을 명확히 한다.
3. 없는 API나 화면을 추정으로 메우지 않는다.
4. 프론트가 미구현이면 `blocked_frontend`로 표시한다.
5. exact contract가 없으면 `needs_contract_definition`로 남긴다.
6. 대시보드 상태 판단은 프론트가 임의 계산하지 않고 `ATLS` 산출물을 source of truth로 삼는다.

## 입력 컨텍스트

- `ATLS` 프로젝트 루트: `/Users/jaecjeong/lab/memo/atsl`
- 대시보드 프로젝트 루트: `/Users/jaecjeong/lab/memo/atsl/dashboard`
- 핵심 문서:
  - `docs/design/ATLS_DASHBOARD_PRD.md`
  - `docs/design/ATLS_E2E_HARNESS_WORKFLOW.md`
  - `docs/reference/ISSUE_REQUIREMENT_MANIFEST_SPEC.md`
  - `docs/reference/ACCEPTANCE_MANIFEST_SPEC.md`
  - `docs/reference/PASS_FAIL_EVIDENCE_REPORT_SPEC.md`
- 핵심 코드:
  - `src/atls/cli.py`
  - `src/atls/analysis/harness.py`
  - `dashboard/lib/mock-data.ts`
  - `dashboard/app/dashboard/**/*`
  - `dashboard/components/dashboard/**/*`

## 반드시 확인할 것

1. 현재 dashboard가 어떤 화면까지 구현되어 있는지
2. 어떤 화면이 `mock-data.ts`에 의존하는지
3. 어떤 `ATLS` 산출물이 이미 존재하는지
4. 어떤 API / local server / file adapter가 아직 없는지
5. 어떤 버튼이나 액션이 아직 시각 요소만 있고 실제 연동이 없는지

## 기대 출력

### 1. Integration Inventory

- dashboard 화면별 현재 상태
- 현재 mock 의존 여부
- 연결할 `ATLS` 산출물
- 필요한 API 또는 adapter

### 2. Contract Map

- `ATLS artifact -> dashboard view` 매핑
- `summary.md -> Overview / Issue Queue`
- `task_plans.md -> Issue Detail`
- `issue requirement manifest -> Requirements`
- `acceptance manifest -> Acceptance Cases`
- `case report / video / screenshot -> Evidence`

### 3. Frontend Gap Report

아래 상태값 중 하나로 표시한다.

- `implemented`
- `mock_only`
- `missing_api`
- `missing_action`
- `needs_contract_definition`
- `blocked_frontend`

### 4. Delivery Plan

- Phase 1: read-only real data integration
- Phase 2: execution trigger wiring
- Phase 3: Jira/Confluence action preparation

### 5. Immediate Blockers

- 내가 추가로 구현해야 하는 backend/API
- 프론트에서 아직 없는 route/component/action
- 사용자에게 받아야 할 자료나 정책

## 출력 형식

반드시 아래 구조를 유지한다.

1. `Current Dashboard Coverage`
2. `ATLS Artifact Mapping`
3. `Frontend Gaps`
4. `Integration Phases`
5. `Immediate Next Tasks`
6. `Blocked / Needs User Input`

## 금지 사항

- 프론트가 없는 기능을 있는 것처럼 쓰지 않는다.
- mock 데이터를 실제 연동 완료처럼 설명하지 않는다.
- 대시보드가 계산해야 할 판단 로직을 프론트에 하드코딩하는 계획을 세우지 않는다.
- source가 없는 상태값을 green badge로 승격하지 않는다.
