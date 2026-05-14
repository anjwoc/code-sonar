# ATLS Workflow, Worklog, and Cloud Sync PRD

Author: Harness Engineering  
Status: Draft  
Target Product: `ATLS Dashboard`

## 문서 목적

이 문서는 새 dashboard 프론트에 추가된 아래 영역을 `ATLS` 제품 기능으로 정식 정의한다.

- Workflow 관리
- Workflow 실행 / 실행 이력 관리
- Worklog 관리
- Bulk Worklog 자동 분배
- Cloud Storage 연동
  - Google Drive
  - iCloud Drive

이 문서는 단순 UI 추가가 아니라, `ATLS`의 기존 source-backed workflow와 evidence lifecycle 위에 새 기능을 어떻게 얹을지 `Harness Engineering` 관점에서 정의한다.

## 배경

현재 `ATLS`는 아래 흐름을 이미 수행하고 있다.

- Jira / Confluence source 수집
- summary / task plan / requirement manifest / acceptance manifest 생성
- 테스트 실행
- evidence 수집
- Jira / Wiki 반영 준비

하지만 실제 운영에서는 아래 공백이 있다.

- 반복적인 Jira 기반 workflow를 dashboard에서 템플릿 단위로 운영하기 어렵다.
- 테스트/문서/evidence 작업과 별도로, 실제 worklog 입력 흐름이 분리되어 있다.
- evidence, report, run history를 로컬에서만 보존하거나 수동으로 백업해야 한다.
- 결과물을 Google Drive / iCloud Drive 같은 사용자 친화적인 스토리지로 내보내는 운영 흐름이 없다.

새 프론트는 이 간극을 메우기 위한 UI를 제공한다.  
이 PRD는 그 UI를 `ATLS`의 실제 runtime, artifact, source policy와 연결하기 위한 제품 기준을 정의한다.

## 제품 비전

`ATLS Dashboard`는 단순히 이슈를 보는 화면이 아니라, 아래를 하나의 연속된 작업 시스템으로 제공해야 한다.

1. source를 바탕으로 요구사항을 정리한다.
2. workflow template로 반복 작업을 정의한다.
3. 해당 workflow를 실행해 산출물과 evidence를 축적한다.
4. 실행 결과를 run history로 관리한다.
5. 실제 worklog까지 연결해 일 단위 업무 기록을 정리한다.
6. 필요한 결과물을 cloud storage로 동기화한다.

즉 이 기능들은 개별 메뉴가 아니라, 하나의 `work orchestration + proof retention + reporting` 체계로 동작해야 한다.

## Harness Engineering 원칙

1. source-backed fact와 operator action을 분리한다.
2. workflow는 템플릿이 아니라 “검증 가능한 실행 규약”이어야 한다.
3. 실행 결과는 항상 `latest pointer + immutable history`로 남겨야 한다.
4. worklog는 테스트/evidence 흐름과 분리된 부가 기능이 아니라, 작업 마감 단계의 일부로 본다.
5. cloud sync는 원본 evidence를 대체하지 않고, 복제/배포 경로로 취급한다.
6. AI가 생성한 요약과 실제 source/evidence는 혼합하지 않는다.
7. blocked / missing / reanalysis_required 상태를 숨기지 않는다.
8. 기본 artifact root는 `ATLS package/.atls-data` 이고, 외부 경로는 override가 없는 한 canonical root로 쓰지 않는다.

## 범위

이 문서는 아래 3개 모듈을 다룬다.

1. `Workflow Orchestration`
2. `Worklog Management`
3. `Cloud Sync & Archive Delivery`

## 1. Workflow Orchestration

### 목표

- 반복적인 Jira 기반 작업 흐름을 대시보드에서 생성, 수정, 실행, 재실행, 추적할 수 있어야 한다.

### 핵심 화면

- `/dashboard/workflows`
- `/dashboard/workflows/[workflowId]`
- `/dashboard/workflows/run`
- `/dashboard/workflows/[workflowId]/history`
- workflow run 화면 안의 `Codex Step Prompt` 패널

### 핵심 사용자 질문

- 어떤 Jira 이슈를 대상으로 이 workflow가 동작하는가?
- 어떤 단계가 켜져 있고 어떤 단계가 생략되는가?
- Wiki publish / Jira transition / evidence report 생성 여부는 무엇인가?
- 최근 실행 결과는 성공/부분성공/실패 중 무엇인가?
- 특정 단계만 재실행할 수 있는가?

### 핵심 요구사항

1. 사용자는 workflow template을 생성, 복제, 수정, archive 할 수 있어야 한다.
2. source rule은 JQL raw mode와 structured mode를 둘 다 지원해야 한다.
3. execution step은 enable/disable 상태와 순서를 보존해야 한다.
4. publish policy와 Jira post-action은 템플릿 일부로 저장되어야 한다.
5. 실행 결과는 run 단위로 기록되고 history에서 재검토 가능해야 한다.
6. run은 step-level 상태와 duration, error, generated artifacts, publish result, Jira result를 남겨야 한다.
7. failed step 또는 selected step 단위 재실행이 가능해야 한다.
8. selected step에 prompt를 붙여 Codex session을 실행할 수 있어야 한다.
9. Codex session은 realtime event log와 final output을 남겨야 한다.

### Harness 관점 세부 요구사항

- workflow template은 “자동화 규약”이므로, 실행 시점의 source rule snapshot을 함께 보존해야 한다.
- run history는 단순 로그가 아니라 `what rule produced what artifacts`를 증명해야 한다.
- rerun은 원래 run을 mutate 하지 않고 새로운 rerun attempt 메타를 남겨야 한다.
- AI-assisted step run은 prompt, provider, model, realtime event log, final output을 session 단위로 보존해야 한다.
- `Codex OAuth connected` 표시는 실제 bridge readiness와 분리해서 검증해야 한다.

## 2. Worklog Management

### 목표

- 사용자가 이슈 처리 흐름을 끝낸 뒤, worklog까지 `ATLS` 안에서 정리할 수 있어야 한다.

### 핵심 화면

- `/dashboard/worklogs/calendar`
- `/dashboard/worklogs/bulk`

### 두 가지 사용 방식

1. `Calendar / Manual`
   - 날짜 중심으로 worklog를 조회/수정/삭제
2. `Bulk Worklog`
   - 여러 Jira 이슈를 선택하고 날짜 범위와 시간 규칙에 따라 자동 분배 preview를 만든 뒤 일괄 생성

### 핵심 사용자 질문

- 오늘 어떤 이슈에 얼마만큼 시간을 기록했는가?
- 남은 근무시간을 어떤 이슈들에 나눌 수 있는가?
- 기존 worklog와 충돌하지 않게 preview를 만들 수 있는가?
- bulk submit 전 rationale을 볼 수 있는가?

### 핵심 요구사항

1. 사용자는 currentUser 기준 unresolved / active issue를 source로 worklog 후보를 볼 수 있어야 한다.
2. 사용자는 날짜 범위, 근무시간, 제외 시간, slot 분 단위를 지정할 수 있어야 한다.
3. bulk preview는 기존 worklog와 제외 시간대를 뺀 실제 가용 슬롯만 계산해야 한다.
4. preview는 날짜별, 이슈별, rationale을 함께 보여줘야 한다.
5. bulk execution은 partial failure를 허용하되 성공/실패 항목을 분리해 보여줘야 한다.
6. calendar view는 수동 추가/수정/삭제를 지원해야 한다.
7. worklog는 Jira publish 이전에 local draft로도 유지 가능해야 한다.

### Harness 관점 세부 요구사항

- worklog bulk preview는 deterministic 해야 한다.
- 동일 입력이면 동일 allocation이 나와야 한다.
- preview와 실제 submit 사이의 source issue 집합과 schedule config가 바뀌면 stale warning이 떠야 한다.
- worklog는 evidence와 직접 같지 않지만, issue 처리 증적의 운영 레이어이므로 run/evidence 링크를 붙일 수 있어야 한다.

## 3. Cloud Sync & Archive Delivery

### 목표

- evidence, report, worklog export, workflow run artifacts를 로컬 파일 시스템 밖으로 안전하게 복제/동기화할 수 있어야 한다.

### 핵심 화면

- `/dashboard/settings/cloud`

### 초기 지원 대상

- Google Drive
- iCloud Drive

### 지원 정책

- v1은 local-first
- cloud는 “원본 저장소”가 아니라 “배포/백업 대상”
- future backend:
  - internal artifact root
  - optional Cloudflare R2 as canonical object store
  - Drive / iCloud는 downstream sync target

### 핵심 사용자 질문

- 어떤 산출물을 Drive/iCloud에 저장할 것인가?
- 저장 루트 경로는 어디인가?
- workflow 실행 후 자동 동기화할 것인가?
- evidence만 보낼 것인지, worklog와 settings backup도 같이 보낼 것인지?

### 핵심 요구사항

1. provider 연결 상태를 명확히 표시해야 한다.
2. provider별 root path를 수정 가능해야 한다.
3. 저장 대상을 세분화할 수 있어야 한다.
   - artifacts
   - evidence reports
   - worklogs
   - settings backup
4. 실행 시 자동 저장 여부를 설정할 수 있어야 한다.
5. sync failure는 silent fail 금지, run/evidence 화면에 surfaced 되어야 한다.
6. local path와 cloud path의 매핑 규칙을 보존해야 한다.

### Harness 관점 세부 요구사항

- cloud sync는 원본 evidence 판단에 사용되는 canonical path를 덮어쓰면 안 된다.
- local artifact가 primary source이고, cloud artifact는 delivery replica다.
- sync metadata에는 source path, target path, syncedAt, provider, result, retry count가 남아야 한다.

## 4. AI Step Session Bridge

### 목표

- workflow 각 단계에서 prompt 기반 AI 실행을 시도하고, 그 출력과 상태를 실시간에 가깝게 관찰할 수 있어야 한다.

### 초기 브리지 정책

- v1 canonical bridge: local Codex CLI JSONL session
- `Codex OAuth connected`는 단순 토글이 아니라 아래를 구분한다.
  - local configured
  - validated
  - bridge ready
- 실제 realtime 표시 대상은 `codex exec --json` event stream 이다.

### 저장 규칙

- session metadata: `.atls-data/runtime/ai-sessions`
- canonical artifact root: `.atls-data/projects/shared/{jira|wiki}`
- cloud replica root: `.atls-data/replicas/cloud`
- session에는 최소 아래가 남아야 한다.
  - provider
  - model
  - prompt
  - workflow/step scope
  - startedAt/finishedAt
  - realtime event list
  - final output
  - error or blocked reason

## Frontend Integration Points

### 이번에 dashboard에 반영된 UI 경로

- `/dashboard/workflows`
- `/dashboard/workflows/run`
- `/dashboard/workflows/[workflowId]`
- `/dashboard/workflows/[workflowId]/history`
- `/dashboard/worklogs/calendar`
- `/dashboard/worklogs/bulk`
- `/dashboard/settings/cloud`

### 현재 상태

- UI는 dashboard에 흡수됨
- 현재는 mock/domain-driven interaction 중심
- `ATLS`의 실데이터 레이어와 완전 연결된 것은 아님

### 바로 연결 가능한 재사용 계층

- project registry
- environment settings
- AI / connector settings
- issue queue / source synthesis / evidence APIs

### 추가로 필요한 backend/API

- `GET /api/workflows`
- `POST /api/workflows`
- `GET /api/workflows/:workflowId`
- `PATCH /api/workflows/:workflowId`
- `POST /api/workflows/:workflowId/run`
- `POST /api/workflows/:workflowId/steps/:stepId/rerun`
- `GET /api/workflows/:workflowId/history`
- `GET /api/worklogs`
- `POST /api/worklogs`
- `PATCH /api/worklogs/:worklogId`
- `DELETE /api/worklogs/:worklogId`
- `POST /api/worklogs/bulk/preview`
- `POST /api/worklogs/bulk/execute`
- `GET /api/settings/cloud`
- `PATCH /api/settings/cloud`
- `POST /api/settings/cloud/providers/:providerId/connect`
- `POST /api/settings/cloud/providers/:providerId/validate`
- `POST /api/settings/cloud/providers/:providerId/sync`

## Data Model

### Workflow Template

- workflow id
- name
- description
- category
- source rule
- execution steps
- publish policy
- Jira post actions
- owner
- last run metadata

### Workflow Run

- run id
- workflow template id
- startedAt / finishedAt
- initiatedBy
- status
- collected issue count
- step results
- generated artifacts
- wiki results
- jira results
- rerun attempts

### Worklog Entry

- worklog id
- issue key
- issue summary
- work date
- start / end
- duration
- comment
- author
- source (`manual` | `bulk`)

### Bulk Worklog Preview

- selected issue keys
- date range
- total available minutes
- total slots
- existing occupied minutes
- blocking errors
- warnings
- issue allocations
- draft entries

### Cloud Sync Provider Record

- provider id
- provider type
- status
- root path
- save targets
- autosync flags
- last sync
- last validation
- error message

## 상태 모델

### Workflow Run Status

- `success`
- `partial`
- `failed`
- `running`
- `cancelled`

### Cloud Provider Status

- `disconnected`
- `connecting`
- `connected`
- `error`

### Worklog Execution Result

- `success`
- `partial`
- `failed`
- `dry_run_only`

## 제품화 단계

### Phase 1

- UI 흡수
- mock/domain model 정리
- sidebar / routes / local engine 연결
- PRD와 정책 적립

### Phase 2

- workflow template persistence
- workflow run history persistence
- worklog preview/execute API
- cloud settings persistence
- workflow run source rule snapshot persistence
- immutable rerun attempt history
- deterministic worklog preview signature + stale warning
- cloud sync metadata/audit trail for local-first replica delivery

### Phase 3

- Jira worklog submit 연동
- workflow step rerun 실제 backend 실행
- evidence artifact sync metadata 저장

### Phase 4

- Google Drive / iCloud 실연동
- canonical object storage abstraction
- optional Cloudflare R2 backend
- cloud delivery retry / audit trail

## 비목표

- v1에서 Google Drive / iCloud를 canonical evidence store로 사용하지 않는다.
- v1에서 workflow editor를 범용 low-code tool로 확장하지 않는다.
- v1에서 팀 단위 권한/approval 체계를 만들지 않는다.
- v1에서 AI가 workflow를 임의 생성/수정하는 기능은 범위 밖이다.

## 수용 기준

1. dashboard에서 workflows / worklogs / cloud storage 메뉴가 자연스럽게 접근 가능해야 한다.
2. workflow/worklog/cloud 기능은 `ATLS` 문서 정책 안에 정식 적립되어야 한다.
3. latest run과 history run이 분리되어야 한다.
4. local artifact와 cloud replica의 역할이 구분되어야 한다.
5. worklog preview는 deterministic allocation과 rationale을 제공해야 한다.
6. workflow run은 step-level rerun과 result tracking을 지원해야 한다.
7. 이후 backend 연결 시 현재 UI를 버리지 않고 단계적으로 실데이터화할 수 있어야 한다.
