# ATLS Project Registry PRD

## 문서 목적

이 문서는 `ATLS Dashboard`에서 관리 대상 프로젝트를 추가, 조회, 수정, 보관/삭제할 수 있는 `Project Registry` 기능의 제품 요구사항을 정의한다.

이 기능의 목표는 다음과 같다.

- 대시보드에서 대상 프로젝트를 직접 등록하고 관리한다.
- 프로젝트별 `workspace`, `artifact root`, `auth`, `adapter`, `trusted docs`, `workflow scope`를 일관되게 관리한다.
- 프로젝트 onboarding을 수동 파일 편집이 아니라 구조화된 CRUD 흐름으로 바꾼다.
- 잘못 등록된 프로젝트나 미완성 프로젝트를 `draft`, `blocked`, `archived` 상태로 안전하게 관리한다.

## 배경

현재 `ATLS`는 프로젝트별 산출물과 adapter를 다룰 수 있지만, 관리 대상 프로젝트 목록은 구조화된 dashboard CRUD로 관리되지 않는다.

현재 문제:

- 새 프로젝트를 대시보드 대상에 넣으려면 경로와 산출물 구조를 직접 맞춰야 한다.
- dashboard의 project switcher는 실제 registry가 아니라 mock 데이터에 가깝다.
- 어떤 프로젝트가 활성 상태인지, 어떤 프로젝트가 초기 설정 중인지, 어떤 프로젝트가 더 이상 관리 대상이 아닌지 한 번에 파악하기 어렵다.
- auth 전략, artifact 경로, trusted docs 정책이 프로젝트마다 달라도 중앙 관리 포인트가 없다.

## 제품 비전

`Project Registry`는 `ATLS Dashboard`가 관리하는 모든 프로젝트의 진입점이다.

사용자는 여기서:

- 새 프로젝트를 등록하고
- 필요한 adapter/config를 설정하고
- 현재 상태를 확인하고
- 대시보드 대상에서 숨기거나 복원하고
- 잘못 등록된 설정을 수정하고
- 더 이상 쓰지 않는 프로젝트를 archive

할 수 있어야 한다.

## 대상 사용자

### 1. 개발 리드 / 도구 관리자

- 새 프로젝트 onboarding
- auth / artifact / workspace 설정
- trusted docs 정책 정의

### 2. 프로젝트 담당 개발자

- 자신의 프로젝트를 dashboard 대상으로 등록
- summary/task/test 흐름에 연결
- 경로 변경, base URL 변경 등 운영 설정 수정

### 3. QA / PM / 운영자

- 현재 어떤 프로젝트가 관리 대상인지 파악
- 프로젝트 상태와 blocker 확인

## 문제 정의

### 현재 상태

- 프로젝트 정보가 code/config/artifact 경로에 흩어져 있다.
- 프로젝트 추가 절차가 문서화되어 있어도 UI에서 수행할 수 없다.
- 잘못된 경로나 미완성 auth 설정이 있어도 대시보드에서 즉시 드러나지 않는다.

### 해결해야 하는 핵심 문제

1. 프로젝트 추가를 UI에서 할 수 있어야 한다.
2. 프로젝트 상태를 `draft`, `active`, `blocked`, `archived`로 관리할 수 있어야 한다.
3. 프로젝트별 adapter 정보를 읽고 수정할 수 있어야 한다.
4. 연동 가능 여부를 onboarding checklist로 검증할 수 있어야 한다.
5. 삭제는 hard delete보다 archive 중심으로 안전하게 처리해야 한다.

## 성공 기준

- 새 프로젝트를 5분 내에 draft 상태로 등록할 수 있다.
- 프로젝트 등록 후 adapter 검증 결과를 즉시 확인할 수 있다.
- 잘못된 경로나 auth 누락이 있으면 `blocked` 상태로 표시된다.
- 프로젝트 switcher는 registry의 active 프로젝트만 노출한다.
- archive된 프로젝트는 기본 뷰에서 숨겨지지만 복원 가능하다.

## 비목표

- Git repository 생성 자체를 자동화하지 않는다.
- Jira/Confluence 프로젝트 자체를 생성하지 않는다.
- 각 프로젝트의 모든 내부 설정을 완전히 UI에서 대체하지 않는다.
- 비밀값(secret) 자체를 평문으로 장기 저장하지 않는다.

## 핵심 원칙

1. `registry first`
2. `safe by default`
3. `archive over delete`
4. `validation before activation`
5. `source of truth 분리`

## 용어 정의

- `Project Registry`: dashboard가 관리하는 프로젝트 메타데이터 저장소
- `Project Adapter`: 프로젝트 종속 설정 묶음
- `Project Profile`: display name, key, 설명, owner 등 사람이 보는 정보
- `Activation`: dashboard 대상 프로젝트로 실제 노출되는 상태
- `Archive`: 삭제하지 않고 비활성 보관하는 상태

## 프로젝트 상태 모델

프로젝트는 아래 상태 중 하나를 가진다.

- `draft`
- `active`
- `blocked`
- `archived`

### 상태 의미

- `draft`: 생성됐지만 설정 검증 전
- `active`: dashboard 대상 프로젝트로 사용 가능
- `blocked`: 설정이 불완전해서 연동 불가
- `archived`: 기본 목록에서 숨김, 복원 가능

## 정보 구조

Project Registry는 아래 영역으로 구성한다.

1. `Project List`
2. `Project Create`
3. `Project Detail`
4. `Project Adapter Settings`
5. `Onboarding Validation`
6. `Archive & Restore`

## 주요 사용자 흐름

### Flow A. 프로젝트 추가

1. 사용자는 `Add Project` 버튼을 누른다.
2. 기본 정보 입력:
   - project key
   - display name
   - workspace root
   - artifact root
   - workflow type
3. auth / adapter 기본 정보 입력
4. 저장하면 프로젝트는 `draft` 상태로 생성된다.
5. onboarding validation이 자동 또는 수동으로 실행된다.

### Flow B. 프로젝트 활성화

1. validation 결과가 충분하면 `Activate` 버튼이 활성화된다.
2. 사용자가 승인하면 status가 `active`가 된다.
3. active 프로젝트는 sidebar switcher와 overview 대상에 포함된다.

### Flow C. 프로젝트 수정

1. 사용자는 project detail에서 설정을 편집한다.
2. 변경 후 validation을 다시 수행한다.
3. 문제가 없으면 active 유지
4. 문제가 생기면 `blocked`로 강등될 수 있다.

### Flow D. 프로젝트 archive / restore

1. 사용자는 archive를 실행할 수 있다.
2. archive된 프로젝트는 기본 목록에서 숨긴다.
3. restore 시 다시 `draft` 또는 `active`로 복원한다.

### Flow E. hard delete

기본 정책:

- hard delete는 기본 UX에서 노출하지 않는다.
- 필요하면 관리자 전용 위험 액션으로만 제공한다.

## 프로젝트 엔티티 정의

### 필수 필드

- `project_key`
- `display_name`
- `description`
- `status`
- `workspace_root`
- `artifact_root`
- `workflow_type`
- `owner`
- `created_at`
- `updated_at`

### adapter 관련 필드

- `base_url`
- `auth_strategy`
- `login_provider`
- `storage_state_path`
- `selector_policy`
- `trusted_docs_path`
- `ignored_docs_path`
- `runner_command_template`
- `tests_result_root`
- `raw_artifact_root`
- `html_report_root`

### 운영 관련 필드

- `last_validation_at`
- `last_validation_status`
- `last_run_at`
- `blocker_reason`
- `required_materials`

## 화면 요구사항

### 1. Project List

목적:

- 전체 프로젝트 상태를 한눈에 본다.

필수 컬럼:

- project key
- display name
- status
- owner
- workflow type
- last validation status
- last run at
- blocker 여부

필터:

- status
- owner
- workflow type
- blocked only
- archived 포함 여부

액션:

- add project
- open detail
- archive
- restore

### 2. Project Create

목적:

- 새 프로젝트를 dashboard 대상에 등록한다.

필수 입력:

- project key
- display name
- workspace root
- artifact root
- workflow type
- owner

선택 입력:

- description
- base URL
- auth strategy
- login provider
- trusted docs path
- ignored docs path

저장 정책:

- 생성 직후 기본 status는 `draft`
- validation 전까지 active 불가

### 3. Project Detail

목적:

- 프로젝트 메타데이터와 현재 상태를 확인한다.

필수 섹션:

- 기본 정보
- current status
- latest validation
- blockers
- required materials
- latest workflow run
- linked adapter config

### 4. Project Adapter Settings

목적:

- 프로젝트 종속 설정을 보고 수정한다.

필수 섹션:

- auth
- paths
- selectors
- runner
- docs policy

원칙:

- 민감 정보는 masked 표시
- secrets는 직접 저장보다 env/secret reference 방식 우선

### 5. Onboarding Validation

목적:

- 프로젝트가 dashboard 대상이 될 준비가 되었는지 검증한다.

검증 항목 예시:

- workspace root 존재 여부
- artifact root 존재 여부
- summary/task artifacts 존재 여부
- adapter json 유효 여부
- auth strategy 최소 필드 존재 여부
- trusted docs path 유효 여부

결과 상태:

- `pass`
- `fail`
- `partial`

### 6. Archive & Restore

목적:

- 운영 대상이 아닌 프로젝트를 안전하게 숨기고 복원한다.

원칙:

- archive는 reversible
- archive 시 기존 artifact/history는 삭제하지 않는다.
- restore 후 validation 재실행 가능

## CRUD 요구사항

### Create

필수:

- draft project 생성
- 기본 adapter 스켈레톤 생성 옵션
- onboarding validation 예약

### Read

필수:

- 전체 목록 조회
- 단건 상세 조회
- status/owner/workflow별 조회

### Update

필수:

- 기본 정보 수정
- adapter 설정 수정
- 상태 변경

주의:

- active -> blocked 전이는 validation failure 시 가능
- archived 프로젝트 수정 시 warning 필요

### Delete

기본 정책:

- soft delete 대신 archive

예외:

- hard delete는 관리자 전용
- hard delete 시 adapter/registry entry만 제거하고 artifact 삭제 여부는 별도 확인 단계 필요

## 프론트엔드 연동 포인트

### 라우트

- `/dashboard/projects`
- `/dashboard/projects/new`
- `/dashboard/projects/:projectKey`
- `/dashboard/projects/:projectKey/settings`
- `/dashboard/projects/:projectKey/validation`

### 상위 컴포넌트

- `ProjectRegistryPage`
- `ProjectTable`
- `ProjectCreateForm`
- `ProjectDetailHeader`
- `ProjectStatusBadge`
- `ProjectValidationPanel`
- `ProjectAdapterEditor`
- `ProjectArchiveDialog`

### 상태 모델

- `selectedProjectKey`
- `projectFilters`
- `validationRunState`
- `projectFormState`

## API 계약 요구사항

### Read API

- `GET /api/projects`
- `GET /api/projects/:projectKey`
- `GET /api/projects/:projectKey/settings/adapter`
- `GET /api/projects/:projectKey/validation`
- `GET /api/projects/:projectKey/environment/effective`

### Write API

- `POST /api/projects`
- `PATCH /api/projects/:projectKey`
- `POST /api/projects/:projectKey/validate`
- `POST /api/projects/:projectKey/activate`
- `POST /api/projects/:projectKey/archive`
- `POST /api/projects/:projectKey/restore`
- `DELETE /api/projects/:projectKey`

## 기본 경로 정책

프로젝트별 artifact 경로를 사용자가 따로 입력하지 않으면 `workspace_root` 기준으로 아래 기본 경로를 계산한다.

- `tests_result_root = <workspace_root>/tests/results/issues`
- `raw_artifact_root = <workspace_root>/tests/results/artifacts`
- `html_report_root = <workspace_root>/tests/results/html-report`
- `storage_state_path = <workspace_root>/tests/.auth/user.json`

예:

- `adcenter` 프로젝트 선택 시
  - `/Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/issues`
  - `/Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/artifacts`
  - `/Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/html-report`

원칙:

- 프로젝트 override가 있으면 override 우선
- 없으면 project adapter 값 사용
- 그것도 없으면 `workspace_root` 기반 derived default 사용

## 데이터 저장 전략

추천 방식:

- `registry.json` 또는 `registry.db` 같은 중앙 저장소
- 프로젝트별 adapter는 별도 json 유지 가능

권장 구조:

- registry는 "프로젝트 목록과 상태"
- adapter는 "프로젝트별 세부 설정"
- workflow artifacts는 기존 artifact root 유지

## 검증 규칙

- 필수 경로 없으면 `blocked`
- summary/task artifacts 없으면 `draft` 또는 `blocked`
- auth strategy가 incomplete면 `blocked`
- adapter parse 실패 시 `blocked`
- archive된 프로젝트는 switcher에서 기본 제외

## 권한 / 승인

### 승인 단계

1. `Project Draft Created`
2. `Validation Passed`
3. `Activation Approved`

### 원칙

- validation 없이 active 불가
- blocked project는 상태 이유를 반드시 남긴다.

## 오픈 이슈

- registry 저장소를 json으로 둘지 sqlite로 둘지
- hard delete를 정말 제공할지
- secrets reference를 어떤 방식으로 관리할지
- multi-user 동시 수정 충돌을 어디까지 지원할지

## MVP 범위

### 포함

- project list
- create draft project
- update basic metadata
- read-only adapter view
- validation result view
- archive / restore

### 제외

- hard delete UI
- secret manager 연동
- Jira/Confluence project provisioning
- multi-user conflict resolution

## 단계별 개발 제안

### Phase 1

- registry read model
- project list
- project detail
- project create draft

### Phase 2

- adapter edit
- onboarding validation
- activate / block / archive

### Phase 3

- hard delete admin flow
- secret reference UX
- onboarding wizard 개선

## 하네스 엔지니어링 관점의 결론

Project Registry는 단순한 설정 화면이 아니라, `ATLS`가 어떤 프로젝트를 source-backed workflow 대상으로 다룰 수 있는지 관리하는 첫 단계다.

따라서 이 기능은 아래를 보장해야 한다.

1. 프로젝트 추가가 구조화되어 있다.
2. 미완성 프로젝트는 active처럼 보이지 않는다.
3. blocker와 required materials가 명확하다.
4. archive가 delete보다 우선이다.
5. dashboard 대상 프로젝트의 lifecycle을 안전하게 관리할 수 있다.
