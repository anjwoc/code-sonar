# ATLS Dashboard Integration Plan

## 목적

이 문서는 `/Users/jaecjeong/lab/memo/atsl`의 현재 기능을 `/Users/jaecjeong/lab/memo/atsl/dashboard`와 연동하기 위한 실제 작업 계획서다.

기준 원칙:

- `ATLS`는 산출물 생성과 상태 판단의 source of truth다.
- `dashboard`는 시각화와 제어 UI다.
- mock 기반 화면은 우선 real artifact read-only 연동부터 치환한다.
- 프론트가 없는 기능은 `미구현`으로 보고하고, 억지 fallback은 만들지 않는다.

## 현재 상태 요약

### `ATLS`에서 이미 가능한 것

- Jira/Confluence 기반 summary 생성
- task list / task plans 생성
- detail v2 문서 생성
- issue requirement manifest / acceptance manifest 포맷 정의
- Playwright spec skeleton 생성
- E2E 결과 기반 evidence report 운용
- project adapter 개념과 문서화

근거:

- [cli.py](/Users/jaecjeong/lab/memo/atsl/src/atls/cli.py)
- [harness.py](/Users/jaecjeong/lab/memo/atsl/src/atls/analysis/harness.py)

### `dashboard`에서 이미 구현된 것

- Overview 화면
- Issue Queue 화면
- Issue Detail 화면
- Requirements 화면
- Acceptance Cases 화면
- Evidence 화면
- Settings / Project Adapter 화면
- Workflow timeline 컴포넌트

근거:

- [page.tsx](/Users/jaecjeong/lab/memo/atsl/dashboard/app/dashboard/page.tsx)
- [page.tsx](/Users/jaecjeong/lab/memo/atsl/dashboard/app/dashboard/issues/page.tsx)
- [page.tsx](/Users/jaecjeong/lab/memo/atsl/dashboard/app/dashboard/issues/[issueKey]/page.tsx)
- [page.tsx](/Users/jaecjeong/lab/memo/atsl/dashboard/app/dashboard/issues/[issueKey]/requirements/page.tsx)
- [page.tsx](/Users/jaecjeong/lab/memo/atsl/dashboard/app/dashboard/issues/[issueKey]/cases/page.tsx)
- [page.tsx](/Users/jaecjeong/lab/memo/atsl/dashboard/app/dashboard/issues/[issueKey]/evidence/page.tsx)
- [page.tsx](/Users/jaecjeong/lab/memo/atsl/dashboard/app/dashboard/settings/page.tsx)
- [workflow-timeline.tsx](/Users/jaecjeong/lab/memo/atsl/dashboard/components/dashboard/workflow-timeline.tsx)

### 현재 가장 큰 사실

dashboard는 현재 거의 전부 [mock-data.ts](/Users/jaecjeong/lab/memo/atsl/dashboard/lib/mock-data.ts) 기반이다.  
즉 화면 구조는 있으나, 실제 `ATLS` 산출물과 연결된 상태는 아니다.

## 연동 원칙

1. `mock-data.ts` 치환을 최우선으로 한다.
2. 파일 직접 읽기와 local API server 중 하나를 source layer로 고정한다.
3. PRD/Jira/source sufficiency 계산은 프론트에서 하지 않는다.
4. 버튼 액션은 실제 backend adapter가 생기기 전까지 `disabled` 또는 `not wired`로 표기한다.
5. timeline은 실제 artifact/output_ref를 받아 그린다.

## 연동 대상 매핑

| Dashboard 영역 | 현재 데이터 소스 | 연결할 ATLS source | 상태 | 비고 |
| --- | --- | --- | --- | --- |
| Overview | `mockProjects`, `mockIssues`, `getOverviewStats` | summary/workflow artifact aggregate | `mock_only` | 통계 집계 adapter 필요 |
| Issue Queue | `mockIssues` | summary + task list | `mock_only` | assignee/status/filter real 연결 필요 |
| Issue Detail | `getIssueByKey` | issue context + task plan + workflow state | `mock_only` | Jira 원문 요약/코멘트 요약 연결 필요 |
| Requirements | `mockRequirements` | issue requirement manifest | `mock_only` | md/json parser 또는 API 필요 |
| Acceptance Cases | `mockAcceptanceCases` | acceptance manifest | `mock_only` | case 실행 상태와 latest run 연결 필요 |
| Evidence | `mockTestRun` | pass/fail evidence report + artifact inventory | `mock_only` | video/image URL serving 필요 |
| Settings | `mockAdapter` | project adapter | `mock_only` | read-only부터 연동 가능 |
| Workflow Timeline | issue.workflowSteps | workflow state projection | `mock_only` | 단계 계산기 필요 |

## 프론트 미구현 / 연동 불가 지점

아래 항목은 현재 기준으로 실제 연동이 안 되는 상태다.

### 1. Dashboard API layer 없음

현재 상태:

- `dashboard/app` 아래에 `api` route가 없다.
- `fetch`, `useSWR`, `react-query`, server action 기반 데이터 로딩이 없다.

판단:

- 상태: `missing_api`
- 영향: 모든 페이지가 real artifact를 읽지 못함

### 2. mock-data.ts가 단일 source로 하드코딩

현재 상태:

- overview, issue queue, detail, requirements, cases, evidence, settings 전부 `mock-data.ts` 의존

판단:

- 상태: `mock_only`
- 영향: 현재 UI는 데모 상태

### 3. Jira / test action 버튼 미연동

현재 상태:

- `Open in Jira`
- `Approve Evidence`
- `Request Re-run`
- case row의 run 버튼

이 버튼들은 실제 action으로 연결되지 않았다.

판단:

- 상태: `missing_action`
- 영향: 대시보드에서 작업 실행/반영 불가

### 4. Artifact serving layer 없음

현재 상태:

- evidence 화면은 video/screenshot 구조는 있으나 실제 파일 전달 레이어가 없다.

판단:

- 상태: `missing_api`
- 영향: 영상/이미지/trace를 실제 재생할 수 없음

### 5. Workflow recompute contract 없음

현재 상태:

- timeline UI는 있지만, real workflow state를 만드는 contract가 없다.

판단:

- 상태: `needs_contract_definition`
- 영향: 진행 상태와 blocker가 실제 산출물과 연결되지 않음

## 작업 단계

### Phase 1. Read-Only Real Data Integration

목표:

- mock 화면을 실제 `ATLS` 산출물 기반 조회 화면으로 치환한다.

세부 작업:

1. `ATLS dashboard adapter` 읽기 레이어 정의
2. project root / artifact root 기준 경로 규약 정의
3. summary, task list, task plan, requirement manifest, acceptance manifest, evidence report의 read contract 정의
4. dashboard에 read API 추가
5. settings, overview, issue queue부터 real data 연결

완료 기준:

- `mock-data.ts` 없이 실제 artifact에서 목록/상세가 보인다.

### Phase 2. Requirement / Acceptance / Evidence Integration

목표:

- requirement, case, evidence 화면을 실데이터로 연결한다.

세부 작업:

1. issue requirement manifest parser/API 구현
2. acceptance manifest parser/API 구현
3. evidence report parser/API 구현
4. video/screenshot artifact inventory API 구현
5. requirement-result-evidence 매핑 구조 구현

완료 기준:

- 이슈별 requirement/case/evidence를 대시보드에서 실제 파일 기반으로 조회 가능

### Phase 3. Workflow State Projection

목표:

- timeline을 실제 작업 상태와 연결한다.

세부 작업:

1. workflow state projection 규칙 정의
2. stage별 source/output/blocker 계산기 구현
3. latest run과 final judgment를 timeline에 연결
4. `ready_for_jira_update` 계산 결과 연결

완료 기준:

- timeline이 단순 mock이 아니라 현재 artifact 상태를 반영

### Phase 4. Controlled Actions

목표:

- 대시보드에서 안전한 액션만 실행할 수 있게 한다.

세부 작업:

1. `generate-requirements`
2. `generate-acceptance`
3. `run-tests`
4. `sync-summary`
5. `prepare-jira-update`

원칙:

- 실제 Jira/Confluence write는 최종 승인 전 preview만 제공 가능
- source 부족이면 액션은 blocked 처리

완료 기준:

- 최소한 로컬 artifact 생성/갱신 액션은 대시보드에서 트리거 가능

## 구현 단위별 작업 목록

### A. ATLS 쪽 작업

1. dashboard가 읽을 수 있는 stable output schema 정리
2. 산출물별 index 파일 또는 project manifest 추가
3. workflow state projection 함수 구현
4. artifact inventory 생성기 구현
5. local read API 또는 JSON export pack 설계

### B. Dashboard 쪽 작업

1. `mock-data.ts` 의존 제거
2. overview data loader 추가
3. issue queue data loader 추가
4. issue detail data loader 추가
5. requirements data loader 추가
6. cases data loader 추가
7. evidence data loader 추가
8. settings data loader 추가
9. timeline detail drawer 실제 output_ref 연결

### C. 공통 계약 작업

1. project selector contract
2. issue workflow contract
3. requirement manifest response contract
4. acceptance manifest response contract
5. evidence asset response contract
6. run action response contract

## 화면별 연동 포인트

### Overview

필요 데이터:

- total issue count
- blocked count
- ready count
- sufficiency 분포
- test status 분포

연동 source:

- summary
- issue/workflow aggregate

### Issue Queue

필요 데이터:

- issue list
- jira status
- assignee
- sufficiency
- latest test status
- ready status

연동 source:

- summary
- task list
- workflow projection

### Issue Detail

필요 데이터:

- issue meta
- Jira 요약
- 최근 코멘트 요약
- touchpoints
- workflow timeline

연동 source:

- task plan
- detail v2
- workflow projection

### Requirements

필요 데이터:

- requirement list
- source refs
- missing evidence
- implementation_allowed

연동 source:

- issue requirement manifest

### Acceptance Cases

필요 데이터:

- case list
- risk
- execution_status
- evidence type
- blocked reason

연동 source:

- acceptance manifest
- latest run result projection

### Evidence

필요 데이터:

- run summary
- requirement results
- video/screenshot assets
- network/state assertions
- final judgment

연동 source:

- pass/fail evidence report
- result artifact inventory

### Settings

필요 데이터:

- project adapter

연동 source:

- adapter json/md

## 추천 API / adapter 계약

최소 read API:

- `GET /api/projects`
- `GET /api/projects/:projectKey/overview`
- `GET /api/projects/:projectKey/issues`
- `GET /api/projects/:projectKey/issues/:issueKey`
- `GET /api/projects/:projectKey/issues/:issueKey/workflow`
- `GET /api/projects/:projectKey/issues/:issueKey/requirements`
- `GET /api/projects/:projectKey/issues/:issueKey/acceptance`
- `GET /api/projects/:projectKey/issues/:issueKey/evidence`
- `GET /api/projects/:projectKey/settings/adapter`

최소 action API:

- `POST /api/projects/:projectKey/issues/:issueKey/generate-requirements`
- `POST /api/projects/:projectKey/issues/:issueKey/generate-acceptance`
- `POST /api/projects/:projectKey/issues/:issueKey/run-tests`
- `POST /api/projects/:projectKey/issues/:issueKey/sync-summary`
- `POST /api/projects/:projectKey/issues/:issueKey/prepare-jira-update`

## 바로 착수 가능한 순서

1. dashboard read API 레이어 생성
2. settings page를 real project adapter로 연결
3. issue queue를 real summary/task list로 연결
4. issue detail + workflow timeline 연결
5. requirements / acceptance / evidence 순서로 연결

## 사용자 보고가 필요한 항목

현재 기준으로 아래는 내가 진행하다가 바로 보고해야 하는 항목이다.

1. 프론트 페이지는 있지만 data contract가 없는 경우
2. action 버튼 UX는 있는데 실행 endpoint가 아직 없는 경우
3. evidence player UI는 있는데 실제 asset serving 방식이 정해지지 않은 경우
4. workflow 단계 상태 계산 규칙이 PRD/문서상 확정되지 않은 경우

## 이번 점검 기준 프론트 미구현 보고

현재 즉시 보고할 항목:

- `dashboard`에 real data API layer가 없다.
- 모든 주요 페이지가 `mock-data.ts` 기반이다.
- evidence 영상/이미지 파일을 실제 서빙하는 방식이 없다.
- `Open in Jira`, `Approve Evidence`, `Request Re-run`, case run 버튼이 연동되지 않았다.
- workflow timeline은 UI는 있으나 real workflow projection contract가 없다.

이 항목들은 연동 작업 중 숨기지 않고 계속 `미구현`으로 보고해야 한다.
