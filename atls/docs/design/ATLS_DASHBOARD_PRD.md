# ATLS Dashboard PRD

## 문서 목적

이 문서는 `ATLS`가 수집하는 Jira / Confluence / project analysis / manifest / test evidence를 한 곳에서 제어하고 시각화하는 통합 대시보드의 제품 요구사항을 정의한다.

핵심 목표는 다음과 같다.

- Jira 중심의 작업 대상을 빠르게 선정하고 상태를 추적한다.
- 이슈별 요구사항 근거와 부족한 자료를 명확히 보여준다.
- `summary -> task list -> task plan -> issue requirement manifest -> acceptance manifest -> test -> evidence report` 흐름을 한 화면 체계 안에서 연결한다.
- 테스트 실행 결과를 영상, 스크린샷, assertion 결과와 함께 검토 가능하게 한다.
- AI의 주관적 해석이나 무차별 fallback 없이, source-backed requirement와 execution evidence를 분리해 관리한다.

## 배경

현재 `ATLS`는 CLI와 문서 산출물 중심으로 다음 흐름을 이미 만들고 있다.

- Jira / Confluence 수집
- summary 생성
- project task list / task plan 생성
- issue requirement manifest / acceptance manifest 생성
- E2E 기반 검증
- pass / fail evidence report 생성

하지만 이 흐름은 파일과 CLI 중심이라 전체 현황을 한 번에 보기 어렵고, 다음 문제가 있다.

- 어떤 이슈가 실제 작업 대상인지 빠르게 파악하기 어렵다.
- 어떤 요구사항이 source-backed인지, 어떤 것은 자료 부족인지 분산되어 있다.
- 테스트 증거가 파일 단위로 흩어져 있어 비교와 검토가 번거롭다.
- 프론트 구현자는 어떤 화면이 필요한지, 어떤 데이터가 필요한지 별도 재해석을 해야 한다.

이 대시보드는 위 문제를 해결하기 위한 통합 운영 화면이다.

## 제품 비전

`ATLS Dashboard`는 "Jira 기반 작업 관리 + requirement source 검토 + 테스트 실행/검토 + evidence 중심 승인"을 하나의 운영 화면에서 다루는 AI-assisted engineering console이다.

이 제품은 문서를 예쁘게 모아 보여주는 위키가 아니라, 아래 질문에 즉시 답할 수 있어야 한다.

- 지금 내가 처리해야 할 이슈는 무엇인가?
- 이 이슈는 어떤 근거로 확정되었는가?
- 부족한 자료는 무엇이며 내가 무엇을 더 가져와야 하는가?
- 현재 구현은 어떤 테스트로 검증되었는가?
- 영상 / 스크린샷 / network / state evidence까지 보면 정말 요구사항과 부합하는가?

## 대상 사용자

### 1. 작업 개발자

- assignee 기준으로 오늘 처리할 이슈를 확인한다.
- 이슈별 task plan과 requirement manifest를 본다.
- 테스트를 실행하고 evidence를 검토한다.

### 2. 리뷰어 / 리드

- source-backed requirement와 blocked case를 검토한다.
- pass / fail / partial evidence 상태를 확인한다.
- Jira 업데이트 가능 여부를 판단한다.

### 3. QA / PM / 기획

- 요구사항 근거가 충분한지 확인한다.
- 부족한 자료 요청 항목을 확인하고 보완한다.
- PRD와 Jira 코멘트 기준으로 동작을 다시 맞춘다.

## 문제 정의

### 현재 상태

- Jira, Confluence, project docs, local result files, test artifacts가 분산되어 있다.
- 실행 결과는 있지만 그 결과가 어떤 requirement를 검증하는지 연결이 약하다.
- 문서가 약한 프로젝트에서는 AI가 fallback으로 그럴듯한 기대 동작을 만들어낼 위험이 있다.

### 해결해야 하는 핵심 문제

1. 작업 우선순위와 상태를 대시보드에서 바로 볼 수 있어야 한다.
2. requirement source와 execution evidence를 섞지 않아야 한다.
3. 자료가 부족한 경우 "지금 확정 불가"가 명확히 보여야 한다.
4. 테스트 실행 결과가 이슈, requirement, case, evidence 단위로 추적 가능해야 한다.
5. 프론트엔드가 구현 가능한 명확한 정보 구조와 API 계약이 필요하다.

## 성공 기준

### 제품 성공 기준

- 사용자는 하루 작업 시작 시 5분 내에 오늘 처리할 이슈를 선정할 수 있다.
- 각 이슈에 대해 `ready`, `blocked_by_missing_evidence`, `tested`, `needs_review` 상태를 즉시 확인할 수 있다.
- 이슈별 테스트 증거를 영상 포함으로 한 화면에서 검토할 수 있다.
- `ready_for_jira_update` 여부를 리포트 없이도 대시보드에서 바로 판단할 수 있다.

### 품질 성공 기준

- source가 부족한 requirement는 자동으로 `blocked` 또는 `partial`로 표시된다.
- exact text / exact visual / exact interaction spec이 없으면 pass 판정을 제한한다.
- evidence 없는 green test가 "완료"처럼 보이지 않는다.

## 비목표

- Jira / Confluence 전체 기능을 대체하는 범용 업무 툴을 만들지 않는다.
- IDE나 Git client를 대체하지 않는다.
- 테스트 runner 자체를 새로 만들지 않는다.
- AI가 근거 없이 requirement를 생성하는 기능을 제공하지 않는다.

## 핵심 설계 원칙

1. `source-backed requirement first`
2. `manifest-driven workflow`
3. `case-by-case evidence review`
4. `blocked state is first-class`
5. `project adapter 분리`
6. `frontend는 시각화와 제어, ATLS는 수집과 생성`

## 용어 정의

- `Summary`: 작업 대상 이슈를 track / status / stale 기준으로 묶은 상위 뷰
- `Task List`: 프로젝트 맥락으로 분류된 실행 대상 목록
- `Task Plan`: 이슈별 접근 방식과 해결 방향
- `Issue Requirement Manifest`: requirement source와 부족한 증거를 구조화한 문서
- `Acceptance Manifest`: 실행 가능한 test case 목록
- `Case Report`: test execution 결과와 evidence를 정리한 문서
- `Project Adapter`: 로그인, selector, seed data, base URL 등 프로젝트 종속 설정

## 정보 구조

대시보드는 아래 7개 영역으로 구성한다.

1. `Overview`
2. `Issue Queue`
3. `Issue Detail`
4. `Requirement Review`
5. `Acceptance Cases`
6. `Execution & Evidence`
7. `Settings / Project Adapter`

## Workflow Visualization 요구사항

이 대시보드는 단순 리스트 화면이 아니라, 이슈가 현재 어떤 단계에 있고 다음에 무엇을 해야 하는지를 흐름으로 보여줘야 한다.

### 목표

- 이슈가 전체 workflow의 어디에 있는지 즉시 보이게 한다.
- 각 단계의 입력/출력/승인 상태를 한 번에 확인하게 한다.
- 막힌 단계와 이유를 timeline에서 바로 드러낸다.
- 사람이 "지금 구현 단계인지", "자료 요청 단계인지", "테스트 검토 단계인지"를 헷갈리지 않게 한다.

### 기본 workflow 단계

1. `Issue Collected`
2. `Summary Included`
3. `Task Planned`
4. `Requirement Sources Reviewed`
5. `Acceptance Cases Generated`
6. `Implementation In Progress`
7. `Tests Executed`
8. `Evidence Reviewed`
9. `Ready for Jira Update`
10. `Jira Updated`

### 단계별 상태값

각 단계는 아래 상태 중 하나를 가진다.

- `not_started`
- `in_progress`
- `done`
- `blocked`
- `skipped`

### 단계별 메타데이터

timeline에 각 단계별로 아래 정보를 함께 보여준다.

- started_at
- finished_at
- owner
- source_ref
- output_ref
- blocker_reason
- required_materials
- latest_comment

### 시각화 규칙

- 완료 단계는 초록
- 진행 중 단계는 파랑
- blocked 단계는 빨강
- partial evidence 단계는 노랑
- hover 또는 expand 시 해당 단계의 산출물 링크를 보여준다.

### 대표 컴포넌트

- `IssueWorkflowTimeline`
- `WorkflowStageBadge`
- `WorkflowStageDetailDrawer`
- `WorkflowBlockerNotice`
- `WorkflowOutputLinkList`

### Timeline에서 보여줘야 하는 핵심 질문

- 지금 이슈는 어느 단계까지 왔는가?
- 다음 단계는 무엇인가?
- 왜 멈췄는가?
- 누구의 자료/승인이 필요한가?
- 이 단계에서 생성된 산출물은 무엇인가?

### Timeline에서 연결해야 하는 산출물

- summary
- task plan
- issue requirement manifest
- acceptance manifest
- latest run report
- latest video
- latest screenshots
- Jira update draft

### Timeline의 인터랙션 요구사항

- 단계 클릭 시 우측 패널에서 상세 설명을 연다.
- blocked 단계 클릭 시 `required_materials`와 `blocking source gap`을 먼저 보여준다.
- done 단계 클릭 시 생성된 md/json 산출물과 evidence 링크를 보여준다.
- `latest` 토글 시 최신 run 기준으로 timeline을 갱신한다.
- `history` 토글 시 이전 run 이력과 상태 변경 이력을 볼 수 있다.

## 주요 사용자 흐름

### Flow A. 오늘 처리할 이슈 선정

1. 사용자는 `Overview`에서 assignee / project / track / status 필터를 건다.
2. `Issue Queue`에서 `To Do`, `In Progress`, `In Review` 이슈를 본다.
3. 각 이슈는 `source sufficiency`, `test coverage`, `ready_for_jira_update` 상태를 함께 보여준다.
4. 사용자는 이슈 하나를 선택해 `Issue Detail`로 진입한다.

### Flow B. 구현 전에 근거 확인

1. 사용자는 `Issue Detail`에서 Jira 본문, 코멘트, PRD, 첨부, API contract 링크를 본다.
2. `Requirement Review`에서 requirement별 `sufficient / partial / missing` 상태를 확인한다.
3. `needs_user_materials`가 있으면 필요한 자료를 바로 확인한다.
4. 부족한 자료가 있으면 구현/테스트 실행 버튼은 `blocked` 또는 `conditional`로 표시된다.

### Flow C. 테스트 실행과 증거 검토

1. 사용자는 `Acceptance Cases`에서 case 목록을 확인한다.
2. 케이스별 `preconditions / actions / expected / forbidden / evidence`를 본다.
3. `Execution & Evidence`에서 unit / E2E 실행을 트리거하거나 최근 결과를 본다.
4. 실행 후 각 case에 대해 pass / fail / blocked / pass_with_partial_evidence를 확인한다.
5. 영상, 스크린샷, network/state assertion 결과를 requirement 기준으로 검토한다.

### Flow D. Jira 업데이트 준비

1. 사용자는 `Case Report` 요약을 확인한다.
2. `ready_for_jira_update`와 `manual_follow_up_required` 상태를 확인한다.
3. 대시보드는 Jira에 남길 추천 상태 문안과 evidence 링크를 생성한다.
4. 사용자가 승인하면 Jira 상태 업데이트 또는 코멘트 반영을 수행한다.

### Flow E. Timeline 기반 진행 추적

1. 사용자는 `Issue Detail` 상단의 workflow timeline에서 현재 단계를 확인한다.
2. blocked 단계가 있으면 필요한 자료와 담당 액션을 바로 본다.
3. 구현 완료 후 `Tests Executed` 단계로 이동하면서 최신 run과 evidence가 자동 연결된다.
4. evidence 검토가 끝나면 `Ready for Jira Update` 단계가 활성화된다.

## 화면 요구사항

### 1. Overview

목적:

- 전체 작업량과 현재 병목을 한눈에 보여준다.

필수 요소:

- assignee 기준 total issue count
- project / track / status별 count
- source sufficiency 분포
- testing status 분포
- blocked by missing evidence count
- 최근 실행 실패 case 수

위젯 예시:

- `Today Queue`
- `Track Summary`
- `Evidence Gaps`
- `Recent Test Runs`
- `Ready for Jira Update`

### 2. Issue Queue

목적:

- 작업 대상 이슈를 테이블/보드 형태로 관리한다.

필수 컬럼:

- issue key
- title
- track
- jira status
- priority
- assignee
- requirement sufficiency
- acceptance coverage
- latest test status
- ready_for_jira_update
- updated at

필터:

- assignee
- project
- track
- jira status
- category
- source sufficiency
- test status

정렬:

- updated desc
- priority desc
- blocked first
- ready first

### 3. Issue Detail

목적:

- 이슈의 원문과 프로젝트 맥락을 한 곳에서 본다.

필수 섹션:

- Jira 본문 요약
- 최근 코멘트 요약
- 현재 상태 판단
- 관련 summary / task plan 링크
- 관련 PRD / API / attachment 링크
- touchpoints
- 구현 상태
- 최근 test run 요약
- workflow timeline
- 현재 단계의 blocker / next action

### 4. Requirement Review

목적:

- source-backed requirement를 검토한다.

필수 요소:

- requirement list
- source priority
- primary source ref
- evidence sufficiency
- implementation_allowed
- missing_evidence
- needs_user_materials

강조 규칙:

- `missing`은 빨간 상태
- `partial`은 노란 상태
- `sufficient`는 초록 상태

### 5. Acceptance Cases

목적:

- 실행 가능한 케이스를 리뷰하고 선택 실행한다.

필수 요소:

- case_id
- title
- risk
- execution_status
- preconditions
- actions
- expected
- forbidden
- evidence type
- required materials

추가 기능:

- case 단건 실행
- issue 전체 실행
- blocked case 숨기기 / 보기

### 6. Execution & Evidence

목적:

- 실제 검증 결과를 requirement와 연결해 본다.

필수 요소:

- latest run id
- run date
- executor
- test type: unit / e2e / contract / integrated
- requirement result matrix
- screenshot gallery
- video player
- network assertion panel
- state assertion panel
- final judgment

핵심 요구:

- 영상은 case별로 바로 재생 가능해야 한다.
- 스크린샷은 step별 타임라인으로 보여야 한다.
- requirement 기준으로 어떤 evidence가 연결되는지 보여야 한다.

### 7. Settings / Project Adapter

목적:

- 프로젝트별 설정을 관리한다.

필수 요소:

- project key
- workspace root
- auth strategy
- login provider
- storage state path
- selector policy
- base URL
- runner command template
- result path
- trusted docs path
- ignored docs path

## 프론트엔드 연동 포인트

프론트엔드는 아래 단위로 구현하면 된다.

### A. 페이지 라우트

- `/dashboard`
- `/dashboard/issues`
- `/dashboard/issues/:issueKey`
- `/dashboard/issues/:issueKey/requirements`
- `/dashboard/issues/:issueKey/cases`
- `/dashboard/issues/:issueKey/evidence`
- `/dashboard/settings/projects/:projectKey`

### B. 상위 레이아웃 컴포넌트

- `DashboardShell`
- `ProjectSwitcher`
- `FilterBar`
- `StatusSummaryCards`
- `IssueTable`
- `IssueBoard`
- `IssueDetailHeader`
- `IssueWorkflowTimeline`
- `EvidenceLayout`

### C. 데이터 카드 / 패널 컴포넌트

- `RequirementCard`
- `SourceBadgeList`
- `MissingEvidencePanel`
- `AcceptanceCaseCard`
- `ExecutionRunSummary`
- `RequirementResultTable`
- `VideoEvidencePlayer`
- `ScreenshotTimeline`
- `NetworkAssertionPanel`
- `StateAssertionPanel`
- `FinalJudgmentCard`
- `WorkflowStageDetailDrawer`
- `NextActionPanel`
- `BlockerMaterialsPanel`

### D. 프론트 상태 모델

핵심 query state:

- `selectedProject`
- `selectedIssueKey`
- `filters`
- `selectedRunId`
- `selectedRequirementId`
- `selectedCaseId`

캐시/비동기 전략:

- overview, issue queue는 polling 또는 수동 refresh
- issue detail은 issue key 기준 fetch
- evidence는 run id 기준 fetch
- 영상/이미지는 lazy load

### E. 프론트 API 연동 포인트

권장 방식은 frontend가 직접 파일 시스템을 읽지 않고, `ATLS dashboard server` 또는 local adapter API를 통해 읽는 구조다.

필수 read API:

- `GET /api/projects`
- `GET /api/projects/:projectKey/overview`
- `GET /api/projects/:projectKey/issues`
- `GET /api/projects/:projectKey/issues/:issueKey`
- `GET /api/projects/:projectKey/issues/:issueKey/workflow`
- `GET /api/projects/:projectKey/issues/:issueKey/requirements`
- `GET /api/projects/:projectKey/issues/:issueKey/acceptance`
- `GET /api/projects/:projectKey/issues/:issueKey/runs`
- `GET /api/projects/:projectKey/issues/:issueKey/runs/:runId`
- `GET /api/projects/:projectKey/issues/:issueKey/evidence`
- `GET /api/projects/:projectKey/settings/adapter`

필수 action API:

- `POST /api/projects/:projectKey/issues/:issueKey/generate-requirements`
- `POST /api/projects/:projectKey/issues/:issueKey/generate-acceptance`
- `POST /api/projects/:projectKey/issues/:issueKey/run-tests`
- `POST /api/projects/:projectKey/issues/:issueKey/sync-summary`
- `POST /api/projects/:projectKey/issues/:issueKey/prepare-jira-update`
- `POST /api/projects/:projectKey/issues/:issueKey/workflow/recompute`

주의사항:

- 프론트는 requirement를 생성하지 않는다.
- 프론트는 source sufficiency를 임의 계산하지 않는다.
- 프론트는 `ready_for_jira_update`를 임의 판정하지 않는다.
- 위 판단은 `ATLS`가 생성한 산출물을 읽어와 그대로 표현한다.

### F. 프론트에서 꼭 시각화해야 하는 상태

- `sufficient`
- `partial`
- `missing`
- `pass`
- `fail`
- `blocked`
- `pass_with_partial_evidence`
- `ready_for_jira_update`
- `manual_follow_up_required`

### G. 프론트에서 피해야 하는 것

- 근거가 없는 green badge
- PRD / Jira source가 없는데 "정상 동작"처럼 보이는 표시
- 영상만 보고 pass로 판정하는 UI
- blocked case를 숨겨서 없는 것처럼 보이게 하는 UI
- timeline을 단순 장식으로만 두고 blocker, output, next action을 숨기는 UI

## 데이터 모델

### Core Entities

- `Project`
- `Issue`
- `TaskPlan`
- `IssueRequirementManifest`
- `Requirement`
- `AcceptanceManifest`
- `AcceptanceCase`
- `TestRun`
- `RequirementResult`
- `EvidenceAsset`
- `ProjectAdapter`

### 관계

- Project 1:N Issue
- Issue 1:1 TaskPlan
- Issue 1:1 IssueRequirementManifest
- Issue 1:1 AcceptanceManifest
- AcceptanceManifest 1:N AcceptanceCase
- Issue 1:N TestRun
- TestRun 1:N RequirementResult
- RequirementResult 1:N EvidenceAsset

## 단위테스트 / E2E 통합 요구사항

### 단위테스트

현재 `ATLS` 핵심 검증은 E2E 중심이지만, 대시보드는 unit test도 수용해야 한다.

예상 사용처:

- formatter
- summary parser
- source hierarchy resolver
- manifest renderer
- result aggregation

표시 방식:

- unit test pass/fail은 issue 단위 aggregate로 노출
- requirement 직접 증거로는 사용하지 않고 보조 confidence로만 사용

### E2E

핵심 요구:

- case 단위 실행 결과를 requirement에 매핑해야 한다.
- 영상/스크린샷/trace/network/state evidence를 함께 보여야 한다.
- contract mode와 integrated mode를 구분해야 한다.

## 권한 / 승인 단계

### 승인 단계

1. `Issue Selection Approved`
2. `Requirement Source Approved`
3. `Acceptance Cases Approved`
4. `Execution Reviewed`
5. `Ready for Jira Update`

### 원칙

- source가 부족하면 다음 단계로 자동 승격하지 않는다.
- blocked case가 있으면 전체 완료 badge를 제한한다.

## 로그 / 이력

대시보드는 다음 이력을 보존해야 한다.

- manifest 생성 시각
- source 변경 이력
- test run 이력
- final judgment 변경 이력
- Jira 업데이트 준비 이력

## 검색 / 필터 요구사항

- issue key 검색
- title keyword 검색
- source 부족 이슈만 보기
- blocked case 있는 이슈만 보기
- 영상 없는 최근 run 보기
- 특정 assignee만 보기
- 특정 track만 보기

## 알림 / 배지 규칙

- `Blocked by Missing Evidence`
- `Ready to Implement`
- `Ready to Test`
- `Needs Manual Review`
- `Ready for Jira Update`
- `Evidence Partial`

## MVP 범위

### MVP에 포함

- overview
- issue queue
- issue detail
- requirement review
- acceptance cases
- latest evidence run view
- project adapter read-only view

### MVP에서 제외

- 자동 Jira 상태 변경
- Confluence 자동 편집
- 복수 프로젝트 동시 실행 orchestration
- flaky test quarantine 운영 자동화

## 단계별 개발 제안

### Phase 1

- summary / task list / task plan 시각화
- issue detail과 requirement review

### Phase 2

- acceptance manifest 시각화
- test run 이력과 evidence viewer

### Phase 3

- unit test 집계
- Jira update prep flow
- Confluence sync preview

## 오픈 이슈

- local file 기반 접근과 local API server 중 어느 구조가 더 적합한가
- 영상/이미지 artifact 용량 증가를 어떻게 관리할 것인가
- Jira / Confluence 쓰기 권한은 어떤 approval UX와 연결할 것인가
- 다중 사용자 동시 편집 상태를 어디까지 지원할 것인가

## 하네스 엔지니어링 관점의 결론

이 대시보드는 단순한 status board가 아니라 다음을 보장해야 한다.

1. requirement의 근거가 명확하다.
2. 부족한 자료가 숨지 않는다.
3. 테스트 결과가 requirement 단위로 해석된다.
4. evidence가 없는 낙관적 완료 상태를 만들지 않는다.
5. 사람이 영상과 케이스를 보고도 납득할 수 있고, 기계가 manifest와 result를 보고도 추적할 수 있다.

즉 `ATLS Dashboard`의 본질은 "작업 관리 UI"가 아니라 "source-backed engineering verification cockpit"이다.
