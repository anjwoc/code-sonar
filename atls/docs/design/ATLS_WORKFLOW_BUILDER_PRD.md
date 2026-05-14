# ATLS Workflow Builder PRD

Author: Harness Engineering  
Status: Draft  
Target Product: `ATLS Dashboard`

## 문서 목적

이 문서는 `ATLS Dashboard`에 "반복 가능한 Jira 기반 workflow를 화면에서 직접 구성, 수정, 실행, 저장하는 메뉴"를 추가하기 위한 제품 요구사항을 정의한다.

이 기능의 핵심은 고정된 `Daily Review` 한 가지 흐름만 제공하는 것이 아니라, 아래를 대시보드에서 규칙 기반으로 조립 가능하게 만드는 것이다.

- Jira에서 어떤 이슈를 수집할지 조건을 정의한다.
- 수집된 이슈를 어떤 문서 산출물로 변환할지 단계별로 설정한다.
- workflow 마지막에 Jira 상태를 변경할지 여부를 정한다.
- Wiki에 결과를 발행할지, 어디에 발행할지 경로 정책을 정한다.
- 실행 결과 리포트와 publish 이력을 날짜 기준으로 누적 보관한다.

## 배경

현재 `ATLS`는 CLI와 문서 중심으로 다음 workflow를 이미 수행할 수 있다.

- Jira 이슈 수집
- summary 생성
- task list / task plan 생성
- manifest 생성
- evidence report 생성
- Wiki publish
- Jira update

하지만 이 흐름은 코드와 CLI 옵션을 알아야 조정 가능하고, 아래 문제가 있다.

- 어떤 Jira 프로젝트/필터 기준으로 수집할지 화면에서 빠르게 바꾸기 어렵다.
- 특정 문구 포함 이슈만 모으거나, 기간 조건을 바꾸는 식의 실무 조정이 불편하다.
- workflow 단계별 on/off, 순서, 출력 위치를 CLI나 문서 규칙에 의존해 기억해야 한다.
- 같은 workflow라도 팀/프로젝트/날짜별로 publish 정책이 다를 수 있는데 이를 재사용 가능한 템플릿으로 관리하기 어렵다.
- 실행 후 Jira 상태 변경, Wiki 결과 저장, 날짜 디렉토리 하위 결과 리포트 축적을 일관되게 제어하기 어렵다.

사용자는 결국 "오늘 어떤 조건으로 어떤 산출물을 만들고, 어디까지 자동 후처리할지"를 `ATLS Dashboard`에서 손쉽게 바꾸고 싶어한다.

## 제품 비전

`ATLS Workflow Builder`는 Jira 기반 반복 작업을 위한 "규칙 편집 가능한 운영 콘솔"이다.

이 제품은 단순한 설정 페이지가 아니라 아래 질문에 즉시 답할 수 있어야 한다.

- 이번 실행에서 어떤 Jira 이슈를 대상으로 삼는가?
- 왜 이 이슈들이 수집되었는가?
- 어떤 workflow 단계를 실행하고 어떤 단계는 건너뛰는가?
- 어떤 문서는 로컬에만 만들고 어떤 문서는 Wiki에 발행하는가?
- 실행이 끝난 뒤 Jira 상태를 변경할지, 어떤 상태로 바꿀지?
- 결과 리포트는 날짜 하위 어느 위치에 남는가?

## 제품 목표

### 핵심 목표

1. 사용자는 workflow를 대시보드에서 템플릿 단위로 생성, 복제, 수정, 저장할 수 있어야 한다.
2. 사용자는 Jira 수집 조건을 UI로 구성할 수 있어야 한다.
3. 사용자는 workflow 단계별 활성화 여부와 상세 옵션을 조정할 수 있어야 한다.
4. 사용자는 Wiki publish 위치와 날짜 컨테이너 정책을 설정할 수 있어야 한다.
5. 사용자는 실행 후 Jira 상태 변경 여부를 선택할 수 있어야 한다.
6. 사용자는 실행 전 preview를 통해 수집 대상, 산출물, 후처리 계획을 검토할 수 있어야 한다.
7. 실행 결과 리포트는 날짜 기준으로 누적되어 추적 가능해야 한다.

### 성공 기준

- 사용자는 새로운 workflow 템플릿을 5분 내에 생성할 수 있다.
- 사용자는 Jira 프로젝트, assignee, 기간, text filter 조합을 코드 수정 없이 변경할 수 있다.
- 사용자는 workflow 단계별 enable/disable과 publish/update 정책을 한 화면에서 확인할 수 있다.
- 같은 workflow를 날짜별 실행했을 때 결과 리포트가 날짜 기준으로 누적 저장된다.
- 사용자는 preview 단계에서 "무엇이 실행되고 무엇이 생략되는지"를 즉시 이해할 수 있다.

## 비목표

- 범용 BPMN 툴이나 no-code 자동화 플랫폼을 만들지 않는다.
- 임의의 외부 SaaS를 무제한 연결하는 workflow engine을 만들지 않는다.
- 팀 전체 권한 관리와 approval workflow는 v1 범위에서 제외한다.
- AI가 workflow 단계를 임의로 생성하는 기능은 v1 비목표다.

## 대상 사용자

### 1. 개발자

- Daily Review, task plan, report 생성을 날짜/프로젝트 조건에 맞게 바꾸고 싶다.

### 2. QA / 운영 사용자

- 특정 프로젝트와 특정 문구를 가진 Jira 이슈만 모아 summary 또는 결과 리포트를 만들고 싶다.

### 3. 리드 / 매니저

- 팀에서 반복 사용하는 workflow를 템플릿으로 표준화하고 싶다.

## 핵심 사용자 시나리오

### 시나리오 A. Daily Review workflow를 날짜별로 실행

- 사용자는 `Daily Review` 템플릿을 연다.
- Jira 수집 조건으로 `assignee = currentUser()`, `resolution = unresolved`, `updated within 7d`를 유지한다.
- 단계는 `summary -> wiki publish`만 활성화한다.
- Wiki publish 경로는 `Daily Review > {date} > summary`로 둔다.
- 실행 결과 리포트는 `{artifact_root}/jira/workflow/daily_review/{date}/`에 저장된다.

### 시나리오 B. 특정 프로젝트의 UI 이슈만 수집해 별도 summary 작성

- 사용자는 workflow를 복제해 `UI Daily Review`를 만든다.
- Jira 조건에 `project in (ADCENTER, QA)`와 `summary contains "[UI]"`를 추가한다.
- 기간 조건은 `created between 2026-04-01 and 2026-04-06`
- 산출물은 `summary`, `task list`, `task plan`
- Jira 상태 변경은 비활성화
- Wiki 발행은 `업무 > 2026 > UI Review > {date}` 아래로 설정한다.

### 시나리오 C. workflow 마지막에 Jira 상태를 In Review로 일괄 변경

- 사용자는 `Issue Delivery` workflow를 연다.
- 이슈 수집 조건은 `assignee = currentUser() AND status in ("In Progress")`
- 단계는 `acceptance manifest`, `evidence report`, `jira transition`
- `jira transition` 단계에서 target status를 `In Review`로 설정한다.
- preview에서 변경 대상 이슈와 상태 전이를 확인한 뒤 실행한다.

### 시나리오 D. Wiki 결과 리포트를 날짜 디렉토리 하위에 별도 문서로 저장

- 사용자는 workflow의 publish 정책에서 `use date container = true`를 켠다.
- date page title은 `{date}`
- summary page title은 `summary`
- result page title은 `result-report`
- 실행 후 `Daily Review > 2026-04-06 > summary`, `Daily Review > 2026-04-06 > result-report` 구조로 저장된다.

## 정보 구조

### 신규 메뉴

`/dashboard/workflows`

하위 화면:

- `Workflow List`
- `Workflow Builder`
- `Run Preview`
- `Run History`
- `Workflow Settings`

### 사이드바 권장 순서

- Overview
- Issues
- Projects
- Workflows
- Settings

## 제품 개념

workflow는 아래 4개 계층으로 구성한다.

1. `Workflow Template`
2. `Source Rules`
3. `Execution Steps`
4. `Publish / Post Action Policies`

### 1. Workflow Template

workflow의 이름, 설명, 기본 실행 순서, 기본 저장 위치를 포함한다.

예시:

- `Daily Review`
- `Project Task Flow`
- `Issue Delivery`
- `QA Summary`

### 2. Source Rules

Jira에서 어떤 이슈를 가져올지 정의한다.

### 3. Execution Steps

수집된 이슈를 어떤 산출물로 가공할지 단계별로 정의한다.

### 4. Publish / Post Action Policies

실행 후 Wiki publish, Jira 상태 변경, 결과 리포트 저장을 어떻게 할지 정의한다.

## 기능 요구사항

## 1. Workflow List

사용자는 저장된 workflow 템플릿 목록을 볼 수 있어야 한다.

목록에는 최소 아래 정보가 보여야 한다.

- workflow name
- description
- last updated
- last run at
- owner
- enabled steps count
- publish target summary

목록 액션:

- create
- duplicate
- rename
- archive
- run
- view history

## 2. Workflow Builder

사용자는 workflow를 단계별로 편집할 수 있어야 한다.

Builder는 최소 아래 영역으로 구성한다.

- 기본 정보 패널
- Jira source rule 패널
- execution step 패널
- publish / post action 패널
- validation / preview 패널

## 3. Jira Source Rule Builder

### 기본 요구사항

사용자는 Jira 필터를 UI로 조합할 수 있어야 한다.

지원 대상:

- project
- assignee
- reporter
- status
- resolution
- priority
- issue type
- labels
- created date range
- updated date range
- text search
- summary contains
- description contains
- comment contains
- key includes
- JQL raw override

### 필터 조합 방식

v1 기본 정책:

- `AND` 조건 조합 지원
- text 조건은 여러 개 추가 가능
- 고급 사용자는 raw JQL 모드로 전환 가능

### text 조건 예시

- `summary contains "[UI]"`
- `description contains "워크로그"`
- `comment contains "재현 완료"`

### 기간 조건

지원 예시:

- today
- last 7 days
- custom start/end date
- updated within N days

### source rule explainability

화면에서 최종 쿼리를 사람이 읽을 수 있는 문장으로 보여줘야 한다.

예시:

`assignee가 currentUser이고, unresolved 상태이며, 최근 7일 내 업데이트된 ADCENTER/QA 프로젝트 이슈 중 summary에 [UI]가 포함된 항목을 수집합니다.`

## 4. Execution Step Builder

workflow 단계는 순서가 있고, 각 단계는 enable/disable 및 step-specific settings를 가진다.

### v1 권장 내장 단계

- `collect_issues`
- `generate_summary`
- `generate_task_list`
- `generate_task_plan`
- `generate_issue_manifest`
- `generate_acceptance_manifest`
- `run_tests`
- `generate_evidence_report`
- `publish_wiki`
- `update_jira_status`

### 공통 step 속성

- step id
- enabled
- execution order
- title override
- output artifact path
- depends_on
- continue_on_error
- required inputs

### step별 상세 설정 예시

#### `generate_summary`

- track grouping rule
- stale threshold rule
- max issues
- include issue analysis
- include next action

#### `generate_task_list`

- grouping 기준
- include blocked items
- include source coverage

#### `generate_task_plan`

- include recommendations
- include project adapter hints

#### `run_tests`

- project adapter 선택
- target issue subset
- evidence capture on/off

#### `generate_evidence_report`

- include video
- include screenshots
- include network log

## 5. Publish Policy Builder

사용자는 workflow 결과를 Wiki에 발행할지 여부와 위치를 설정할 수 있어야 한다.

### Wiki publish 설정

- publish enabled
- wiki space
- root parent page id or title
- use date container
- date title template
- child page title template
- overwrite existing page or update existing page
- create result report page separately

### 날짜 하위 문서 정책

v1 기본 정책:

- 날짜 기준 workflow는 결과를 날짜 하위에 저장 가능해야 한다.

예시:

- `Daily Review > 2026-04-06 > summary`
- `Daily Review > 2026-04-06 > result-report`
- `Project Task Flow > 2026-04-06 > task_plans`

### 발행 explainability

preview에서 아래를 반드시 보여줘야 한다.

- 어떤 페이지가 생성되는지
- 어떤 페이지가 업데이트되는지
- 날짜 컨테이너가 생성되는지
- 기존 페이지를 재사용하는지

## 6. Jira Post Action Builder

사용자는 workflow 완료 후 Jira 후처리를 설정할 수 있어야 한다.

### 지원 항목

- Jira update enabled
- target issues scope
- action type
- target status
- comment append
- skip if already in target status
- dry-run only

### v1 지원 액션

- transition status
- add comment
- add label

### 대표 시나리오

- evidence report 생성 후 `In Review` 전환
- summary 생성 후 Jira 변경 없음
- 실패 이슈에는 Jira update 미실행

## 7. Preview

실행 전 preview는 필수다.

### preview에서 보여줄 것

- 수집 대상 Jira 이슈 수
- 적용된 source rule 설명
- 실행될 단계 목록
- 비활성화된 단계 목록
- 생성 예정 artifact 목록
- Wiki 발행 예정 위치
- Jira 변경 예정 건수
- blocking validation errors
- warnings

### blocking validation 예시

- source rule 없음
- 모든 step 비활성화
- wiki publish enabled인데 target 미설정
- jira transition enabled인데 target status 미설정
- date container 사용인데 date variable template 없음

## 8. Run History / Result Report

workflow 실행 이력은 날짜 기준으로 누적되어야 한다.

### 로컬 저장 정책

실행 결과는 workflow/date 기준으로 저장한다.

예시:

- `{artifact_root}/jira/workflow/daily_review/2026-04-06/summary.md`
- `{artifact_root}/jira/workflow/daily_review/2026-04-06/result-report.md`
- `{artifact_root}/jira/workflow/project_task_flow/2026-04-06/task_plans.md`

### Run History 화면에서 보여줄 것

- run id
- workflow name
- started at
- finished at
- initiated by
- collected issue count
- success / partial / failed
- artifact links
- wiki publish links
- jira action result

## 9. Built-in Workflow Templates

v1에서는 몇 가지 기본 템플릿을 제공해야 한다.

- `Daily Review`
- `Project Task Flow`
- `Issue Delivery`
- `QA Summary`

정책:

- system template는 원본 보호
- 사용자는 복제 후 자기 버전을 수정

## 데이터 모델

### WorkflowTemplate

- id
- name
- description
- category
- sourceRules
- executionSteps[]
- publishPolicy
- jiraPostActions[]
- createdBy
- updatedAt

### JiraSourceRule

- projects[]
- assignees[]
- reporters[]
- statuses[]
- resolutions[]
- priorities[]
- issueTypes[]
- labels[]
- createdRange
- updatedRange
- textFilters[]
- rawJql

### TextFilter

- field (`summary`, `description`, `comment`, `all`)
- operator (`contains`, `not_contains`)
- value

### WorkflowStep

- id
- type
- enabled
- order
- titleOverride
- settings
- dependsOn[]

### PublishPolicy

- enabled
- wikiSpace
- parentPageId
- useDateContainer
- dateTitleTemplate
- childPageTitleTemplate
- separateResultReport
- resultPageTitleTemplate

### JiraPostAction

- enabled
- type
- targetStatus
- commentTemplate
- labels[]
- applyWhen

### WorkflowRun

- id
- workflowTemplateId
- executionDate
- status
- collectedIssues[]
- executedSteps[]
- generatedArtifacts[]
- wikiResults[]
- jiraResults[]

## API 요구사항

### 1. Workflow Template 목록

`GET /api/workflows`

response:

- templates[]
- lastRunSummary

### 2. Workflow Template 조회

`GET /api/workflows/[workflowId]`

response:

- template
- recentRuns[]

### 3. Workflow Template 저장

`PUT /api/workflows/[workflowId]`

body:

- workflow template payload

### 4. Workflow Template 생성

`POST /api/workflows`

body:

- name
- base template id optional

### 5. Preview 생성

`POST /api/workflows/[workflowId]/preview`

body:

- optional overrides

response:

- collected issue summary
- effective source rules
- step plan
- artifact plan
- wiki publish plan
- jira update plan
- blocking errors
- warnings

### 6. Workflow 실행

`POST /api/workflows/[workflowId]/execute`

body:

- preview id or preview hash
- optional overrides

response:

- run id
- status
- artifact results
- wiki publish results
- jira update results

### 7. Run History 조회

`GET /api/workflows/[workflowId]/runs`

### 8. Run Detail 조회

`GET /api/workflows/runs/[runId]`

## UX 요구사항

### 필수 UX 원칙

1. workflow 실행 전 preview 필수
2. source rule은 사람이 읽을 수 있게 설명 가능해야 함
3. step별 on/off와 side effect는 숨기지 않아야 함
4. Wiki publish와 Jira update는 위험 액션으로 분리 인지시켜야 함
5. 결과 리포트 위치는 날짜 하위 구조로 추적 가능해야 함

### Workflow Builder UX

- 왼쪽에 step list
- 오른쪽에 선택된 step 설정 패널
- 상단에 source rule summary
- 하단에 preview / save / run 버튼

### 위험 액션 UX

`publish_wiki` 또는 `update_jira_status`가 enabled면 상단에 배지 표시

예시:

- `Wiki Publish Enabled`
- `Jira Transition Enabled`

## 정책 / 제약사항

### Workflow 수

- v1 권장 상한: 사용자당 100개

### Step 수

- v1 권장 상한: workflow당 20개

### Jira source 조회

- 너무 큰 결과셋 방지를 위해 preview 기본 상한 필요
- v1 권장 상한: 500 issues

### Wiki publish 안전장치

- 기존 페이지 update/relocate는 preview에 명시
- title collision은 실행 전 경고

### Jira update 안전장치

- dry-run preview 필수
- target status transition 불가한 이슈는 사전 경고

## 수용 기준

### 기능 수용 기준

1. 사용자는 workflow 템플릿을 생성, 복제, 수정, 저장할 수 있다.
2. 사용자는 Jira project, assignee, 기간, text 조건을 UI에서 설정할 수 있다.
3. 사용자는 workflow 단계별 enable/disable과 세부 설정을 변경할 수 있다.
4. 사용자는 Wiki publish 위치를 날짜 하위 문서 정책으로 설정할 수 있다.
5. 사용자는 workflow 마지막에 Jira 상태 변경 여부를 선택할 수 있다.
6. 실행 전 preview에서 수집 대상, 산출물, 후처리 계획을 검토할 수 있다.
7. 실행 후 결과 리포트가 날짜 기준으로 저장되고 추적 가능하다.

### UX 수용 기준

1. 사용자는 raw CLI 옵션을 몰라도 workflow를 설정할 수 있다.
2. 사용자는 왜 특정 이슈가 수집되었는지 source rule 설명으로 이해할 수 있다.
3. 사용자는 publish 대상과 Jira 변경 대상을 실행 전에 확인할 수 있다.

## 향후 확장

- step drag-and-drop reorder
- OR 조건 그룹 지원
- reusable filter snippets
- project-scoped workflow sharing
- workflow version compare
- scheduled run
- approval gate before Jira transition
- run rollback helper
- AI-assisted workflow suggestion

## 오픈 질문

1. v1에서 raw JQL 수정과 UI 필터 빌더를 양방향 동기화할지, raw mode를 별도로 둘지?
2. system template의 직접 수정은 막고 clone만 허용할지?
3. Wiki publish 결과 문서 이름을 `summary`, `result-report` 같은 고정 규칙으로 강제할지, 자유 입력을 허용할지?
4. Jira post action은 workflow 전체 성공 시에만 수행할지, partial success일 때 일부 대상만 수행할지?
5. run history를 로컬 파일 기반으로 둘지, dashboard 저장소에 별도 인덱싱할지?
