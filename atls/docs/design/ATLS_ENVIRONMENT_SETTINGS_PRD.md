# ATLS Environment Settings PRD

## 문서 목적

이 문서는 `ATLS Dashboard`에서 Jira / Confluence / AI provider API key, OAuth, base URL, profile, 기본 artifact 경로, 테스트 결과 저장 경로 등을 관리하는 `Environment Settings` 기능의 제품 요구사항을 정의한다.

이 기능의 목표는 다음과 같다.

- 대시보드에서 전역 환경설정을 관리한다.
- Jira / Confluence / AI provider 연동 정보와 프로젝트별 기본 경로 정책을 중앙에서 설정한다.
- 테스트 실행 후 영상/스크린샷/report 저장 경로를 명확히 제어한다.
- 프로젝트별 경로를 입력하지 않아도 `workspace_root` 기준 기본값이 자동 적용되게 한다.

## 배경

현재 `ATLS`는 로컬 config와 project adapter를 통해 환경설정을 처리할 수 있지만, dashboard에서 이를 직접 관리하는 전용 화면은 없다.

현재 문제:

- Jira / Confluence token, AI provider 연결 방식, base URL, default profile을 UI에서 관리할 수 없다.
- 프로젝트를 선택해도 artifact 저장 경로가 UI에서 일관되게 보이지 않는다.
- 테스트 실행 결과가 어디에 저장되는지 매번 코드/설정 파일을 확인해야 한다.
- 프로젝트별 경로를 지정하지 않은 경우 어떤 기본값이 적용되는지 명확하지 않다.

## 제품 비전

`Environment Settings`는 `ATLS Dashboard`의 운영 제어판이다.

사용자는 여기서:

- Jira / Confluence 연동 프로필을 등록하고
- AI provider 연결 방식을 선택하고
- 어떤 profile이 기본인지 정하고
- 프로젝트별 artifact 저장 경로 정책을 보고
- 경로가 비어 있을 때 적용되는 기본 경로를 확인하고
- 테스트 실행 시 어떤 경로에 무엇이 저장되는지 즉시 이해할 수 있어야 한다.

## 핵심 원칙

1. `global setting`과 `project setting`을 분리한다.
2. 비밀값은 가능한 한 reference 기반으로 다루고, 평문 저장은 최소화한다.
3. artifact 경로는 비어 있을 때 deterministic default를 사용한다.
4. 기본 경로는 프로젝트 선택만으로 예측 가능해야 한다.
5. 잘못된 경로나 미존재 경로는 validation으로 즉시 보여준다.

## 설정 범위

### 1. Global Integration Settings

- Jira base URL
- Jira token
- Confluence base URL
- Confluence token
- AI provider
- AI auth mode
- AI API key
- Codex OAuth connection status
- default profile
- default artifact root
- default wiki space
- default assignee

### 2. Project Execution Settings

- workspace root
- project artifact root
- tests result root
- screenshot root
- video root
- html report root
- storage state path
- env file path
- runner command template
- project AI provider override
- project AI auth mode override

### 3. Path Policy Settings

- 프로젝트별 명시 경로
- 프로젝트별 default path policy
- 전역 fallback path policy

## Global / Project 분리 원칙

### Global에 두는 것

- Jira / Confluence profile
- AI provider profile
- default artifact root
- 공통 profile 이름
- 공통 wiki 관련 기본값

### Project에 두는 것

- workspace root
- base URL
- auth strategy
- login provider
- project AI provider override
- project-specific artifact path
- tests result path
- runner command

## 기본 경로 정책

프로젝트에서 artifact 경로를 명시하지 않으면 아래 기본 규칙을 적용한다.

### 기본 규칙

- `workspace_root`가 있으면 우선 그것을 기준으로 계산한다.
- 프로젝트별 명시 경로가 있으면 그것이 최우선이다.
- 둘 다 없으면 global artifact root를 사용한다.

### 테스트 결과 기본값

프로젝트 선택 시 기본 경로는 아래와 같다.

- `tests result root`: `<workspace_root>/tests/results/issues`
- `raw artifact root`: `<workspace_root>/tests/results/artifacts`
- `html report root`: `<workspace_root>/tests/results/html-report`
- `storage state path`: `<workspace_root>/tests/.auth/user.json`
- `env file path`: `<workspace_root>/.env.e2e`

예: `adcenter`

- `workspace_root = /Users/jaecjeong/work/adcenter-workspace/adcenter`
- 기본 `tests result root = /Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/issues`
- 기본 `video/artifact root = /Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/artifacts`
- 기본 `html report root = /Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/html-report`

## 상태 모델

환경설정 레코드는 아래 상태를 가질 수 있다.

- `valid`
- `partial`
- `invalid`

### 판단 기준

- `valid`: 필수값과 경로 검증이 모두 통과
- `partial`: 일부 선택값 누락, 실행은 가능
- `invalid`: 필수값 누락 또는 경로 오류

## 화면 요구사항

### 1. Global Settings Page

목적:

- Jira / Confluence / AI provider / default profile을 관리한다.

필수 섹션:

- Jira profile settings
- Confluence profile settings
- AI provider settings
- default profile selector
- default artifact root
- validation result

표시 규칙:

- token은 masked로 표시
- 저장 시 `updated_at`과 `last_validated_at` 기록

### 2. Project Environment Page

목적:

- 선택한 프로젝트의 실행 환경과 경로 정책을 관리한다.

필수 섹션:

- workspace root
- artifact path settings
- auth settings
- AI execution settings
- runner settings
- derived default paths preview

핵심 UX:

- 프로젝트 선택 시 현재 설정값과 derived defaults를 동시에 보여준다.
- 사용자가 path를 비워두면 “기본 경로 사용” 배지가 보여야 한다.

### 3. Path Preview Panel

목적:

- 현재 입력값 기준으로 실제 저장 경로를 미리 보여준다.

예시 항목:

- screenshots -> `/.../tests/results/issues`
- videos -> `/.../tests/results/artifacts`
- html report -> `/.../tests/results/html-report`

### 4. Validation Panel

목적:

- 잘못된 base URL, 없는 경로, 누락된 token/reference를 즉시 보여준다.

검증 항목:

- URL 유효성
- token presence 또는 secret reference 존재 여부
- workspace root 존재 여부
- derived path 계산 가능 여부
- writable directory 여부

## CRUD 요구사항

### Global Settings

- create profile
- read profile list
- update profile
- archive profile

### AI Provider Settings

- create provider config
- read provider list
- update provider config
- connect/disconnect OAuth
- validate connection

### Project Settings

- create per-project override
- read effective settings
- update override
- reset to default

## 프론트엔드 연동 포인트

### 라우트

- `/dashboard/settings/environment`
- `/dashboard/settings/environment/profiles`
- `/dashboard/projects/:projectKey/environment`

### 컴포넌트

- `IntegrationProfileForm`
- `ProfileList`
- `EnvironmentSettingsForm`
- `AIProviderSettingsForm`
- `AIConnectionModeSelector`
- `CodexOAuthConnectButton`
- `AIProviderStatusBadge`
- `PathPreviewPanel`
- `SettingsValidationBadge`
- `SecretField`
- `DerivedDefaultsCard`

## API 계약 요구사항

### Global Settings Read

- `GET /api/settings/environment`
- `GET /api/settings/environment/profiles`
- `GET /api/settings/ai/providers`

### Global Settings Write

- `POST /api/settings/environment/profiles`
- `PATCH /api/settings/environment/profiles/:profileId`
- `POST /api/settings/environment/profiles/:profileId/archive`
- `POST /api/settings/ai/providers`
- `PATCH /api/settings/ai/providers/:providerId`
- `POST /api/settings/ai/providers/:providerId/validate`
- `POST /api/settings/ai/providers/:providerId/oauth/start`
- `GET /api/settings/ai/providers/:providerId/oauth/callback`
- `POST /api/settings/ai/providers/:providerId/disconnect`

### Project Settings Read

- `GET /api/projects/:projectKey/environment`
- `GET /api/projects/:projectKey/environment/effective`

### Project Settings Write

- `PATCH /api/projects/:projectKey/environment`
- `POST /api/projects/:projectKey/environment/reset`
- `POST /api/projects/:projectKey/environment/validate`

## 보안 요구사항

### 권장 정책

- token은 raw value 대신 secret reference 저장 우선
- UI에는 masked 표시
- 복호화 가능한 평문 재표시는 금지
- OAuth token/session은 secure storage 또는 server session에 저장

### 로컬 우선 정책

현재 `ATLS`가 로컬 도구 성격이 강하면, 초기 버전에서는 아래를 허용할 수 있다.

- local-only config 저장
- profile export/import
- API Key 또는 Codex OAuth를 모두 지원

단, 이 경우에도 UI 표시 원칙은 다음을 따른다.

- 저장 후 token 전체 재노출 금지
- 마지막 4자리만 표시 가능

## 기본값 계산 규칙

### Effective Settings 계산 우선순위

1. project override
2. project adapter 값
3. global environment default
4. derived path from workspace root

### derived path 계산 예시

- screenshot root: `join(workspace_root, "tests/results/issues")`
- video root: `join(workspace_root, "tests/results/artifacts")`
- html report root: `join(workspace_root, "tests/results/html-report")`

## 사용자 흐름

### Flow A. 전역 Jira/Confluence 설정

1. 사용자는 Global Settings에서 profile을 추가한다.
2. base URL과 token 또는 secret reference를 입력한다.
3. validation을 실행한다.
4. 통과하면 default profile로 지정할 수 있다.

### Flow A-2. AI Provider 연결

1. 사용자는 AI provider를 선택한다.
2. 인증 방식으로 `API Key` 또는 `Codex OAuth`를 고른다.
3. `API Key`면 key를 입력하고 검증한다.
4. `Codex OAuth`면 브라우저 인증 플로우를 시작한다.
5. 연결이 완료되면 상태가 `connected`로 표시된다.

### Flow B. 프로젝트 선택 시 기본 경로 확인

1. 사용자는 프로젝트를 선택한다.
2. 프로젝트 전용 경로가 없으면 dashboard는 derived default path를 계산한다.
3. path preview panel에 실제 저장 경로가 표시된다.
4. 사용자는 필요 시 override를 입력한다.

### Flow C. 테스트 실행 전 경로 검토

1. 사용자는 run-tests 전 project environment를 확인한다.
2. 영상/스크린샷/html report 저장 위치를 본다.
3. 필요 시 경로를 수정한다.
4. 테스트 실행 후 해당 경로에 artifact가 저장된다.

## 오픈 이슈

- token 저장소를 local json으로 둘지 OS keychain으로 둘지
- Codex OAuth token/session을 어디에 저장할지
- secret reference 형식을 어떤 식으로 통일할지
- writable directory 검증 범위를 어디까지 할지
- 프로젝트별 경로 override를 adapter에 저장할지 registry에 저장할지

## MVP 범위

### 포함

- global Jira/Confluence settings read/write
- global AI provider settings read/write
- project environment read/write
- derived default path preview
- validation badge
- reset to default

### 제외

- secret manager 연동
- multi-profile sharing
- OS keychain 통합

## 하네스 엔지니어링 관점의 결론

환경설정 화면은 단순한 옵션 페이지가 아니라, 어떤 source와 어떤 artifact 경로를 기준으로 `ATLS`가 검증과 산출을 수행하는지 명확하게 드러내는 운영 제어판이다.

따라서 이 기능은 아래를 보장해야 한다.

1. Jira/Confluence 연동 정보가 명확하다.
2. AI provider와 인증 방식이 명확하다.
3. 프로젝트별 실행 경로가 예측 가능하다.
4. 경로를 지정하지 않아도 안전한 기본값이 계산된다.
5. 잘못된 경로나 누락된 token은 즉시 `invalid`로 드러난다.
6. 테스트 결과 영상/이미지 저장 위치를 사용자가 항상 확인할 수 있다.
