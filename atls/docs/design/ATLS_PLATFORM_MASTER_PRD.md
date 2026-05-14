# ATLS Platform Master PRD

## 문서 목적

이 문서는 `ATLS`의 dashboard, project registry, environment settings, AI provider settings, workflow orchestration, evidence review, Jira/Confluence sync까지 포함한 전체 플랫폼 요구사항을 하나로 통합한 마스터 PRD다.

이 문서는 아래 분리 PRD의 내용을 통합한 단일 기준 문서다.

- `ATLS_PROJECT_REGISTRY_PRD.md`
- `ATLS_ENVIRONMENT_SETTINGS_PRD.md`
- `ATLS_SOURCE_CONNECTOR_MASTER_PRD.md`

앞으로 제품 기준 문서는 이 문서를 우선한다.

이 문서는 아래를 하나의 제품으로 본다.

- Jira / Confluence 기반 작업 수집
- AI provider 연결 및 실행
- summary / task plan / manifest 생성
- 프로젝트 등록 및 설정 관리
- 테스트 실행과 evidence 검토
- Jira / Confluence 반영 준비

즉 `ATLS Platform`은 단순 CLI도 아니고 단순 대시보드도 아니며,  
`source-backed engineering workflow operating system`을 지향한다.

## 제품 비전

`ATLS Platform`은 다음 질문에 한 곳에서 답할 수 있어야 한다.

- 지금 내가 처리해야 할 이슈는 무엇인가?
- 이 이슈는 어떤 source를 근거로 요구사항이 확정되었는가?
- 부족한 자료는 무엇인가?
- 어떤 프로젝트를 dashboard 대상으로 관리하고 있는가?
- Jira / Confluence / AI / 테스트 환경 설정은 어떻게 되어 있는가?
- 어떤 테스트가 실행됐고, 어떤 evidence가 남았는가?
- 지금 Jira 상태를 업데이트해도 되는가?

## 하네스 엔지니어링 원칙

1. `source-backed requirement first`
2. `summary -> task list -> task plan -> requirement manifest -> acceptance manifest -> test -> evidence -> jira update`
   흐름 고정
3. source와 execution evidence를 분리
4. evidence 부족 상태를 숨기지 않음
5. AI 추론과 source-backed fact를 분리
6. fallback으로 그럴듯한 기대 동작을 만들지 않음
7. blocked 상태를 first-class로 다룸

## 제품 범위

이 플랫폼은 아래 10개 모듈로 구성된다.

1. `Dashboard`
2. `Issue Workflow`
3. `Project Registry`
4. `Environment Settings`
5. `AI Provider Settings`
6. `Source Connector Management`
7. `Artifact & Data Source Management`
8. `Test Execution Control`
9. `Evidence Review & Approval`
10. `Jira / Confluence Sync Center`

## 1. Dashboard

### 목적

- 전체 이슈, 프로젝트, workflow 상태, test/evidence 상태를 한 곳에서 시각화한다.

### 핵심 화면

- Overview
- Issue Queue
- Issue Detail
- Requirement Review
- Acceptance Cases
- Execution & Evidence
- Settings

### 핵심 질문

- 지금 어떤 이슈가 active인가?
- 어떤 이슈가 blocked인가?
- 어떤 이슈가 ready_for_jira_update 상태인가?

## 2. Issue Workflow

### 목적

- 이슈 하나가 어떤 단계까지 왔는지 timeline으로 관리한다.

### 단계

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

### 단계 상태

- `not_started`
- `in_progress`
- `done`
- `blocked`
- `skipped`

### timeline에서 꼭 보여야 하는 것

- 현재 단계
- 다음 단계
- blocker reason
- required materials
- output refs
- latest run / latest evidence

## 3. Project Registry

### 목적

- dashboard가 관리할 프로젝트를 추가/수정/archive/restore 한다.

### 프로젝트 상태

- `draft`
- `active`
- `blocked`
- `archived`

### 필수 기능

- 프로젝트 생성
- 프로젝트 조회
- 기본 메타데이터 수정
- archive / restore
- onboarding validation

### 프로젝트 필수 필드

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

## 4. Environment Settings

### 목적

- Jira / Confluence API key, base URL, default profile, artifact 경로 정책을 관리한다.

### 전역 설정

- Jira base URL
- Jira token
- Confluence base URL
- Confluence token
- default AI provider
- default AI auth mode
- default profile
- default artifact root
- default wiki space
- default assignee

### 프로젝트별 환경 설정

- workspace root
- base URL
- auth strategy
- login provider
- storage state path
- env file path
- tests result root
- raw artifact root
- html report root

### 경로 기본값 정책

프로젝트에서 명시하지 않으면 `workspace_root` 기준으로 계산한다.

- `tests_result_root = <workspace_root>/tests/results/issues`
- `raw_artifact_root = <workspace_root>/tests/results/artifacts`
- `html_report_root = <workspace_root>/tests/results/html-report`
- `storage_state_path = <workspace_root>/tests/.auth/user.json`
- `env_file_path = <workspace_root>/.env.e2e`

예: `adcenter`

- `/Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/issues`
- `/Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/artifacts`
- `/Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/html-report`

### 보안 원칙

- token은 masked 표시
- 가능하면 secret reference 우선
- 저장 후 전체 token 재노출 금지

## 5. AI Provider Settings

### 목적

- `ATLS`가 어떤 AI provider를 어떤 인증 방식으로 사용할지 관리한다.

### 지원 대상

- `API Key`
- `Codex OAuth`

### 왜 필요한가

- 현재는 사용자가 `ATLS` 패키지를 직접 실행하는 방식에 가깝다.
- 제품으로 확장하려면 구독 기반 사용자도 dashboard에서 바로 AI 연결을 설정할 수 있어야 한다.
- OpenClaw와 유사하게 `Codex OAuth` 기반 연결을 지원하면, API key가 없는 사용자도 사용할 수 있다.

### 지원 시나리오

#### 1. API Key 방식

- 가장 단순한 연결 방식
- provider 선택 후 API key 입력
- key는 masked 저장
- project 또는 global default로 지정 가능

#### 2. Codex OAuth 방식

- OpenClaw 스타일의 OAuth 연결
- 사용자는 브라우저에서 인증하고 access token/session을 획득
- dashboard는 연결 상태와 scope를 표시
- subscription 기반 사용자도 쓸 수 있어야 한다

### 필수 설정 필드

- `provider_id`
- `provider_name`
- `auth_mode`
  - `api_key`
  - `codex_oauth`
- `status`
  - `connected`
  - `disconnected`
  - `expired`
  - `invalid`
- `model_preferences`
- `reasoning_mode`
- `rate_limit_profile`
- `last_validated_at`

### 프론트 요구사항

- AI provider 설정 화면 필요
- 연결 방식 selector 필요
- `API Key` 입력 폼 필요
- `Connect with Codex` OAuth 버튼 필요
- 현재 연결 상태 badge 필요
- 기본 provider 선택 UI 필요

### API 요구사항

- `GET /api/settings/ai/providers`
- `POST /api/settings/ai/providers`
- `PATCH /api/settings/ai/providers/:providerId`
- `POST /api/settings/ai/providers/:providerId/validate`
- `POST /api/settings/ai/providers/:providerId/oauth/start`
- `GET /api/settings/ai/providers/:providerId/oauth/callback`
- `POST /api/settings/ai/providers/:providerId/disconnect`

### 보안 원칙

- API key 평문 재노출 금지
- OAuth token은 session/secret store에 저장
- provider별 scope와 만료 시간 표시
- 연결이 끊기거나 만료되면 즉시 `expired` 또는 `invalid`

### 프로젝트별 적용

- global default AI provider 가능
- project override 가능
- issue 실행 시 effective AI provider를 표시해야 함

## 6. Source Connector Management

### 목적

- Jira / Confluence / Notion / Obsidian / Figma 같은 다양한 source를 같은 플랫폼 안에서 연결하고 관리한다.

### 지원 대상 connector

- `jira`
- `confluence`
- `notion`
- `obsidian`
- `figma`

### connector 역할

- `operational_source`
- `document_source`
- `local_document_source`
- `visual_source`
- `visual_evidence_source`

### connector 공통 필드

- `connector_id`
- `connector_type`
- `display_name`
- `source_kind`
- `access_mode`
- `trust_level`
- `default_priority`
- `enabled`
- `scope`
- `last_sync_at`
- `validation_status`

### access mode

- `api`
- `mcp`
- `local_filesystem`
- `hybrid`

### source 신뢰도 / 우선순위

기본 source priority 예시는 다음과 같다.

1. `prd`
2. `jira_body`
3. `jira_comment`
4. `jira_attachment`
5. `confluence_page`
6. `notion_page`
7. `figma_node`
8. `obsidian_note`
9. `existing_behavior`
10. `code_constraint`

### Figma 특별 규칙

- Figma는 단순 참고 이미지가 아니라 `visual requirement source`와 `visual evidence oracle` 둘 다 될 수 있다.
- MCP를 통해 node metadata를 가져오면 exact visual spec 판단에 활용할 수 있다.

### AI와 connector의 관계

- AI는 connector raw data를 normalize / summarize / map 하는 보조 레이어다.
- AI가 source 없는 requirement를 만들면 안 된다.
- AI 결과에는 항상 `source_refs`, `model`, `confidence`가 따라야 한다.

### 프론트 요구사항

- connector registry 화면
- connector enable/disable
- connector validation 상태
- source explorer
- trust policy 표시

### API 요구사항

- `GET /api/connectors`
- `POST /api/connectors`
- `PATCH /api/connectors/:connectorId`
- `POST /api/connectors/:connectorId/validate`
- `POST /api/connectors/:connectorId/archive`
- `GET /api/sources`
- `GET /api/issues/:issueKey/sources`

## 7. Artifact & Data Source Management

### 목적

- dashboard가 읽는 모든 산출물과 evidence의 위치를 관리한다.

### 관리 대상

- summary
- task list
- task plan
- detail v2
- issue requirement manifest
- acceptance manifest
- pass/fail evidence report
- screenshots
- videos
- html report

### 필수 기능

- artifact inventory
- latest run selector
- md/json pair recognition
- result directory validation
- evidence existence check

### 중요한 점

- 프로젝트가 등록돼 있어도 artifact layer가 없으면 dashboard는 제대로 동작하지 않는다.

## 8. Requirement / Evidence Governance

### 목적

- requirement의 근거와 evidence의 충분성을 명확히 관리한다.

### requirement source hierarchy

1. `prd`
2. `jira_body`
3. `jira_comment`
4. `jira_attachment`
5. `api_contract`
6. `existing_behavior`
7. `code_constraint`

### 필수 상태

- `sufficient`
- `partial`
- `missing`

### requirement 결과 상태

- `pass`
- `fail`
- `blocked`
- `not_executed`
- `pass_with_partial_evidence`

### 반드시 보여야 하는 것

- primary source ref
- missing evidence
- required materials
- implementation_allowed

## 9. Test Execution Control

### 목적

- dashboard에서 테스트 실행을 제어한다.

### 테스트 타입

- unit
- E2E
- contract
- integrated

### 필수 기능

- issue 단위 run
- case 단위 run
- re-run
- latest run status
- run history

### 저장 경로 규칙

- 프로젝트별 override 우선
- 없으면 project adapter 사용
- 그것도 없으면 workspace-derived default 사용

## 10. Evidence Review & Approval

### 목적

- 실행된 테스트의 영상, 스크린샷, network/state assertion을 검토하고 승인한다.

### 필수 기능

- requirement result matrix
- screenshot timeline
- video player
- network assertion panel
- state assertion panel
- approve evidence
- request re-run
- final judgment

### 원칙

- green test만으로 완료 판정 금지
- source 부족이면 `pass_with_partial_evidence` 또는 `blocked`

## 11. Jira / Confluence Sync Center

### 목적

- 마지막 반영 단계를 준비하고 제어한다.

### 필수 기능

- Jira update preview
- Jira comment draft
- status transition prep
- summary sync preview
- Confluence publish preview
- sync history

### 원칙

- 자동 반영보다 preview와 승인 우선
- source/evidence가 부족하면 sync blocked

## 핵심 사용자 흐름

### Flow A. 프로젝트 등록

1. 사용자는 프로젝트를 등록한다.
2. workspace root, artifact root, auth를 입력한다.
3. validation이 통과하면 active로 전환한다.

### Flow B. 이슈 선택

1. Overview / Issue Queue에서 작업 대상을 선택한다.
2. Issue Detail과 timeline으로 현재 상태를 본다.

### Flow C. 요구사항 검토

1. requirement manifest를 본다.
2. source sufficiency와 missing evidence를 확인한다.
3. 부족한 자료가 있으면 blocked로 유지한다.

### Flow D. 테스트 실행

1. acceptance cases를 확인한다.
2. issue 또는 case 단위로 테스트를 실행한다.
3. 결과 artifact가 프로젝트 경로 정책에 따라 저장된다.

### Flow E. evidence 리뷰

1. 영상/스크린샷/network/state evidence를 requirement 기준으로 본다.
2. approve 또는 re-run 요청을 선택한다.

### Flow F. Jira/Confluence 반영

1. ready_for_jira_update 여부를 확인한다.
2. preview를 본다.
3. 승인 후 Jira/Confluence 반영을 수행한다.

## 프론트엔드 정보 구조

### 주요 라우트

- `/dashboard`
- `/dashboard/issues`
- `/dashboard/issues/:issueKey`
- `/dashboard/issues/:issueKey/requirements`
- `/dashboard/issues/:issueKey/cases`
- `/dashboard/issues/:issueKey/evidence`
- `/dashboard/projects`
- `/dashboard/projects/new`
- `/dashboard/projects/:projectKey`
- `/dashboard/projects/:projectKey/settings`
- `/dashboard/projects/:projectKey/environment`
- `/dashboard/settings/environment`
- `/dashboard/settings/ai`
- `/dashboard/settings/connectors`

### 주요 컴포넌트

- `DashboardShell`
- `IssueWorkflowTimeline`
- `ProjectRegistryPage`
- `ProjectCreateForm`
- `ProjectAdapterEditor`
- `EnvironmentSettingsForm`
- `AIProviderSettingsForm`
- `AIConnectionCard`
- `CodexOAuthConnectButton`
- `ConnectorRegistryPage`
- `ConnectorCard`
- `SourceExplorer`
- `PathPreviewPanel`
- `RequirementCard`
- `AcceptanceCaseCard`
- `VideoEvidencePlayer`
- `ScreenshotTimeline`
- `FinalJudgmentCard`

## API 요구사항

### Read API

- `GET /api/projects`
- `GET /api/projects/:projectKey`
- `GET /api/projects/:projectKey/overview`
- `GET /api/projects/:projectKey/issues`
- `GET /api/projects/:projectKey/issues/:issueKey`
- `GET /api/projects/:projectKey/issues/:issueKey/workflow`
- `GET /api/projects/:projectKey/issues/:issueKey/requirements`
- `GET /api/projects/:projectKey/issues/:issueKey/acceptance`
- `GET /api/projects/:projectKey/issues/:issueKey/evidence`
- `GET /api/projects/:projectKey/settings/adapter`
- `GET /api/projects/:projectKey/environment`
- `GET /api/projects/:projectKey/environment/effective`
- `GET /api/settings/environment`
- `GET /api/settings/environment/profiles`
- `GET /api/settings/ai/providers`
- `GET /api/connectors`
- `GET /api/sources`
- `GET /api/issues/:issueKey/sources`

### Write API

- `POST /api/projects`
- `PATCH /api/projects/:projectKey`
- `POST /api/projects/:projectKey/validate`
- `POST /api/projects/:projectKey/activate`
- `POST /api/projects/:projectKey/archive`
- `POST /api/projects/:projectKey/restore`
- `DELETE /api/projects/:projectKey`
- `PATCH /api/projects/:projectKey/environment`
- `POST /api/projects/:projectKey/environment/reset`
- `POST /api/projects/:projectKey/environment/validate`
- `POST /api/settings/ai/providers`
- `PATCH /api/settings/ai/providers/:providerId`
- `POST /api/settings/ai/providers/:providerId/validate`
- `POST /api/settings/ai/providers/:providerId/oauth/start`
- `GET /api/settings/ai/providers/:providerId/oauth/callback`
- `POST /api/settings/ai/providers/:providerId/disconnect`
- `POST /api/connectors`
- `PATCH /api/connectors/:connectorId`
- `POST /api/connectors/:connectorId/validate`
- `POST /api/connectors/:connectorId/archive`
- `POST /api/projects/:projectKey/issues/:issueKey/generate-requirements`
- `POST /api/projects/:projectKey/issues/:issueKey/generate-acceptance`
- `POST /api/projects/:projectKey/issues/:issueKey/run-tests`
- `POST /api/projects/:projectKey/issues/:issueKey/sync-summary`
- `POST /api/projects/:projectKey/issues/:issueKey/prepare-jira-update`

## 프로젝트 관리 외에 추가로 꼭 필요한 기능 점검 결과

프로젝트 관리 외에도 아래 기능이 사실상 필요하다.

### 필수

1. `Source Connector Management`
2. `Artifact & Data Source Management`
3. `Workflow Orchestration`
4. `Requirement / Evidence Governance`
5. `Test Execution Control`

### 강권장

6. `Evidence Review & Approval`
7. `Jira / Confluence Sync Center`

### 중요하지만 후순위 가능

7. `Search / Saved Views`
8. `Audit Log / History`
9. `Notifications / Follow-up Queue`

즉, 지금 요청한 것 외에도 실제 운영 완성도를 위해선 최소 `artifact`, `workflow`, `test control`, `evidence review` 축이 더 필요하다.

## MVP 범위

### 포함

- dashboard read model
- project registry CRUD
- environment settings
- ai provider settings
- source connector management
- workflow timeline
- requirement/acceptance/evidence 조회
- issue 단위 테스트 실행
- evidence 최소 리뷰

### 제외

- hard delete 기본 UX
- secret manager 연동
- multi-user conflict resolution
- flaky quarantine 자동화

## 단계별 개발 제안

### Phase 1

- project registry
- environment settings
- read-only artifact integration
- overview / queue / detail / timeline

### Phase 2

- requirements / cases / evidence 실데이터 연결
- artifact serving
- issue 단위 run action

### Phase 3

- evidence approval
- jira/confluence sync preview
- audit/history

### Phase 4

- saved views
- notifications
- admin hard delete

## 하네스 엔지니어링 관점의 최종 결론

`ATLS Platform`이 완성되려면 프로젝트 등록만 잘 되는 것으로는 부족하다.

이 플랫폼은 아래를 함께 보장해야 한다.

1. 어떤 프로젝트를 관리할지 명확하다.
2. 어떤 AI provider와 인증 방식으로 실행하는지 명확하다.
3. 어떤 connector를 통해 어떤 source를 읽는지 명확하다.
4. 어떤 source를 근거로 요구사항이 확정됐는지 명확하다.
5. 어떤 경로에 어떤 artifact가 저장되는지 예측 가능하다.
6. 어떤 테스트를 실행했고 어떤 evidence가 남았는지 추적 가능하다.
7. source/evidence 부족 상태가 숨겨지지 않는다.
8. 마지막 Jira/Confluence 반영까지 일관된 흐름으로 이어진다.

따라서 앞으로는 이 문서를 `ATLS` 플랫폼 전체의 단일 기준 PRD로 삼고, 세부 문서는 보조 참고 문서로 사용하는 것이 적절하다.
