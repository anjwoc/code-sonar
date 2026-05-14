# ATLS Platform Feature Audit

## 목적

이 문서는 `Project Registry` 외에 `ATLS Dashboard`가 실제 운영 도구가 되기 위해 추가로 필요한 기능을 점검한 결과를 정리한다.

핵심 질문:

- 프로젝트 관리 외에 무엇이 더 있어야 하는가?
- 어떤 기능이 없으면 실제 운영이 막히는가?
- 어떤 기능은 후순위로 미뤄도 되는가?

## 결론 요약

`Project Registry`는 시작점이지만, 그것만으로는 `ATLS Dashboard`가 완성되지 않는다.

실제 운영을 위해 최소한 아래 6개 축이 더 필요하다.

1. `Artifact & Data Source Management`
2. `Workflow Orchestration`
3. `Requirement / Evidence Governance`
4. `Test Execution Control`
5. `Evidence Review & Approval`
6. `Jira / Confluence Sync Center`

이 중 1~4는 사실상 필수에 가깝고, 5~6은 운영 효율과 품질 보증을 위해 강하게 권장된다.

## 기능 점검 결과

### 1. Project Registry

설명:

- 관리 대상 프로젝트 CRUD
- onboarding
- adapter/settings 관리

상태:

- PRD 있음
- 구현 없음

문서:

- [ATLS_PROJECT_REGISTRY_PRD.md](/Users/jaecjeong/lab/memo/atsl/docs/design/ATLS_PROJECT_REGISTRY_PRD.md)

판정:

- `필수`

### 2. Artifact & Data Source Management

설명:

- 프로젝트별 summary/task plan/detail/manifest/report/artifact를 어디서 읽는지 관리
- 현재 어떤 산출물이 존재하는지 inventory 제공
- md/json/report/video/screenshot를 대시보드에서 조회 가능한 형식으로 정리

왜 필요한가:

- 프로젝트가 등록돼 있어도 실제 artifact 위치를 안정적으로 못 읽으면 dashboard는 빈 화면이 된다.
- 현재 evidence는 inventory까지만 있고, asset serving과 source index가 약하다.

필수 하위 기능:

- artifact inventory
- latest run selector
- artifact existence check
- md/json pairing
- evidence asset serving policy

현재 상태:

- 일부 loader/API 초안 있음
- 완전한 asset serving 없음

판정:

- `필수`

### 3. Workflow Orchestration

설명:

- `summary -> task list -> task plan -> requirement manifest -> acceptance manifest -> test -> evidence -> jira update`
  흐름의 현재 단계를 계산하고 제어하는 기능

왜 필요한가:

- timeline UI만 있고 실제 진행 상태 계산이 없으면 운영자가 다음 액션을 판단하기 어렵다.
- blocked와 next action이 자동으로 드러나야 한다.

필수 하위 기능:

- workflow state projection
- current stage
- blocker calculation
- next action suggestion
- run history

현재 상태:

- timeline PRD 있음
- UI 있음
- real projection contract은 아직 약함

판정:

- `필수`

### 4. Requirement / Evidence Governance

설명:

- source-backed requirement와 execution evidence를 구분 관리
- 부족한 자료를 explicit하게 드러내고 blocked 상태를 유지

왜 필요한가:

- 이 제품의 핵심 차별점이 하네스 엔지니어링 기반의 증거 중심 운영이기 때문
- 이 레이어가 약하면 일반 이슈 보드와 다를 바 없다.

필수 하위 기능:

- issue requirement manifest viewer
- source hierarchy viewer
- missing evidence tracker
- required materials request
- pass_with_partial_evidence 표시

현재 상태:

- 포맷/문서는 있음
- 이슈별 실데이터는 아직 부분적

판정:

- `필수`

### 5. Test Execution Control

설명:

- 대시보드에서 unit / E2E / contract / integrated 테스트를 실행하거나 재실행하는 제어 기능

왜 필요한가:

- 지금은 CLI와 로컬 스크립트가 중심이라 운영 화면에서 loop가 끊긴다.
- 적어도 "실행 요청 -> 결과 조회"는 이어져야 한다.

필수 하위 기능:

- issue 단위 run
- case 단위 run
- run queue
- latest run status
- re-run with reason

현재 상태:

- action API 없음
- run 버튼은 UI만 있음

판정:

- `필수`

### 6. Evidence Review & Approval

설명:

- 영상, 스크린샷, network/state assertion을 requirement 결과와 함께 리뷰하고 승인하는 기능

왜 필요한가:

- green test만으로 완료를 판단하면 다시 유령버그가 생긴다.
- 사람이 evidence를 보고 승인하는 단계가 필요하다.

필수 하위 기능:

- requirement result matrix
- approve / request re-run
- review note
- final judgment

현재 상태:

- evidence 화면 mock 존재
- 실제 승인 플로우 없음

판정:

- `강권장`

### 7. Jira / Confluence Sync Center

설명:

- summary, 준비된 코멘트, 상태 업데이트 draft, 위키 반영 preview를 한 곳에서 관리

왜 필요한가:

- 지금은 local summary와 실제 Jira/Confluence 반영이 분리되어 있다.
- 마지막 반영 단계가 수동이면 운영 누락이 생긴다.

필수 하위 기능:

- jira update preview
- comment draft
- status transition prep
- confluence publish preview
- sync history

현재 상태:

- 계획과 문서만 있음
- 실제 write flow 없음

판정:

- `강권장`

### 8. Search / Saved Views / Filters

설명:

- 이슈, 프로젝트, blocked 상태, source 부족 상태, 영상 없는 run 등을 빠르게 찾는 기능

왜 필요한가:

- 프로젝트 수와 이슈 수가 늘어나면 기본 테이블만으로 운영이 어려워진다.

현재 상태:

- 일부 필터 UI 있음
- real saved view 없음

판정:

- `중요`

### 9. Audit Log / History

설명:

- 누가 언제 manifest를 갱신했고, 언제 테스트가 실행됐고, 언제 Jira update 준비가 바뀌었는지 추적

왜 필요한가:

- review 책임과 상태 변경 추적이 필요하다.

현재 상태:

- timeline history 요구사항은 있음
- 별도 audit 설계는 없음

판정:

- `중요`

### 10. Notifications / Follow-up Queue

설명:

- blocked 자료 요청, 재실행 요청, review 대기 상태를 알려주는 기능

왜 필요한가:

- 제품 성숙도가 올라가면 유용하지만, MVP에 꼭 필요하진 않다.

현재 상태:

- 없음

판정:

- `후순위`

## 꼭 필요한 추가 PRD 후보

아래는 `Project Registry` 외에 별도 PRD로 분리하는 것이 좋은 기능들이다.

1. `ATLS Artifact Management PRD`
2. `ATLS Workflow Orchestration PRD`
3. `ATLS Test Execution Control PRD`
4. `ATLS Evidence Review PRD`
5. `ATLS Jira/Confluence Sync Center PRD`

## MVP 기준 최소 기능 세트

프로젝트 관리 외에 MVP에 꼭 포함해야 하는 것은 아래다.

1. artifact inventory / read model
2. workflow timeline real projection
3. requirement / evidence governance view
4. test run control 최소 버전
5. evidence review 최소 버전

## 지금 당장 가장 먼저 보강할 기능

우선순위:

1. `Artifact & Data Source Management`
2. `Workflow Orchestration`
3. `Test Execution Control`
4. `Evidence Review & Approval`
5. `Jira / Confluence Sync Center`

이 순서가 좋은 이유:

- 1, 2가 없으면 대시보드는 mock을 벗어나지 못한다.
- 3이 없으면 대시보드 안에서 작업 루프가 완성되지 않는다.
- 4가 없으면 evidence 중심 운영이 약해진다.
- 5는 마지막 publish 단계지만 실무 효율에 중요하다.

## 하네스 엔지니어링 관점의 최종 판단

`ATLS Dashboard`는 단순히 프로젝트와 이슈를 관리하는 제품이 아니다.

이 제품이 완성되려면 최소한 다음이 함께 있어야 한다.

- 어떤 source가 근거인지 관리하는 기능
- 어떤 단계에서 막혔는지 계산하는 기능
- 어떤 테스트를 실행할지 제어하는 기능
- 어떤 evidence로 승인할지 검토하는 기능
- 어떤 결과를 Jira/Confluence에 반영할지 준비하는 기능

즉 `Project Registry`는 필요하지만 충분조건은 아니다.
