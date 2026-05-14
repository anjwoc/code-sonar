# ATLS New Frontend Integration Plan

## 목적

이 문서는 `/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls`를 `ATLS Platform`의 실제 frontend 후보로 보고, 현재 `ATLS` 패키지 기능과 어떤 순서로 연동할지 정리한 실행 계획서다.

기준 원칙:

- 새 프론트는 화면 구조와 UX를 제공한다.
- `ATLS`는 artifact 생성, 상태 계산, workflow 판단, connector/setting source of truth를 제공한다.
- 연동이 안 된 부분은 숨기지 않고 `mock_only`, `missing_api`, `missing_action`, `needs_contract_definition`으로 분류한다.

## 현재 점검 결과 요약

### 새 프론트에서 이미 있는 것

화면 범위:

- Overview
- Issue Queue
- Issue Detail
- Requirements
- Acceptance Cases
- Evidence
- Projects
- Project Create
- Project Detail
- Project Environment
- Project Settings
- Settings / Environment
- Settings / AI
- Settings / Connectors

근거:

- [projects/page.tsx](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/app/dashboard/projects/page.tsx)
- [projects/new/page.tsx](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/app/dashboard/projects/new/page.tsx)
- [projects/[projectKey]/page.tsx](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/app/dashboard/projects/[projectKey]/page.tsx)
- [projects/[projectKey]/environment/page.tsx](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/app/dashboard/projects/[projectKey]/environment/page.tsx)
- [projects/[projectKey]/settings/page.tsx](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/app/dashboard/projects/[projectKey]/settings/page.tsx)
- [settings/environment/page.tsx](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/app/dashboard/settings/environment/page.tsx)
- [settings/ai/page.tsx](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/app/dashboard/settings/ai/page.tsx)
- [settings/connectors/page.tsx](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/app/dashboard/settings/connectors/page.tsx)

### 현재 가장 큰 사실

새 프론트도 현재는 전부 [mock-data.ts](/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls/lib/mock-data.ts) 기반이다.

또한:

- `app/api` route가 없다.
- `fetch`, `useSWR`, `react-query`, server action 기반 데이터 연결이 없다.
- Create/Save/Add 버튼들은 UI만 있고 실제 저장/실행 액션은 없다.

즉 이 프론트는 범위는 넓지만 현재 상태는 `high-fidelity mock frontend`다.

## 기존 자산 재사용 판단

기존 `/Users/jaecjeong/lab/memo/atsl/dashboard` 쪽에는 이미 아래 자산이 있다.

- read contract
- artifact loader
- read-only API routes

근거:

- [contracts.ts](/Users/jaecjeong/lab/memo/atsl/dashboard/lib/atls/contracts.ts)
- [artifact-loader.ts](/Users/jaecjeong/lab/memo/atsl/dashboard/lib/atls/artifact-loader.ts)
- [/Users/jaecjeong/lab/memo/atsl/dashboard/app/api/projects](/Users/jaecjeong/lab/memo/atsl/dashboard/app/api/projects)

### 결론

가장 좋은 방향은 아래다.

1. 기존 `dashboard/lib/atls/*` loader/contract를 공통 모듈로 승격
2. 새 프론트 `b_FHMb53khGls`에 read API를 붙임
3. 새 프론트 화면을 mock에서 real loader/API 기반으로 교체

즉 `API/loader를 새로 다시 짜기`보다 `기존 read model 재사용 + 새 화면 연동`이 낫다.

## 화면별 연동 상태

| 화면 | 현재 상태 | 연동 대상 | 판정 | 메모 |
| --- | --- | --- | --- | --- |
| Overview | mock | summary aggregate / overview API | `mock_only` | 기존 overview API 재사용 가능 |
| Issue Queue | mock | issues API | `mock_only` | 기존 issues API 재사용 가능 |
| Issue Detail | mock | issue detail / workflow API | `mock_only` | 기존 detail/workflow API 재사용 가능 |
| Requirements | mock | issue requirement manifest API | `mock_only` | requirement manifest 실데이터 부족 시 blocked 표시 필요 |
| Acceptance Cases | mock | acceptance API | `mock_only` | 기존 acceptance API 재사용 가능 |
| Evidence | mock | evidence API + asset serving | `mock_only` | inventory는 가능, asset serving은 미구현 |
| Projects List | mock | project registry API | `missing_api` | 새로 구현 필요 |
| Project Create | form only | project create action | `missing_action` | 저장 backend 없음 |
| Project Detail | mock | project detail API | `missing_api` | 새로 구현 필요 |
| Project Environment | mock | project environment read/write API | `missing_api` | 새로 구현 필요 |
| Project Settings | mock | project adapter/settings read/write API | `missing_api` | 새로 구현 필요 |
| Settings / Environment | mock | global environment read/write API | `missing_api` | 새로 구현 필요 |
| Settings / AI | mock | AI provider read/write + OAuth API | `missing_api` | 새로 구현 필요 |
| Settings / Connectors | mock | connector registry read/write API | `missing_api` | 새로 구현 필요 |

## 필요한 연동 축

### 1. Issue Read Model 연동

대상:

- Overview
- Issue Queue
- Issue Detail
- Requirements
- Acceptance Cases
- Evidence

재사용 자산:

- 기존 `artifact-loader.ts`
- 기존 `app/api/projects/**/*`

작업:

- 새 프론트에 API route 이식 또는 공통 backend화
- page가 mock 대신 API를 읽도록 치환

### 2. Project Registry 연동

대상:

- Projects List
- Project Create
- Project Detail
- Project Environment
- Project Settings

현재 상태:

- UI만 존재
- project registry backend 없음

작업:

- registry 저장소 설계
- read/write API 구현
- validation 상태 계산기 구현

### 3. Environment Settings 연동

대상:

- Settings / Environment
- Project Environment

현재 상태:

- global / project path preview UI는 있음
- 실제 저장/불러오기 없음

작업:

- global env config 저장소
- effective settings 계산기
- derived default path calculator

### 4. AI Provider 연동

대상:

- Settings / AI

현재 상태:

- `API Key`, `Codex OAuth` UI 존재
- 실제 provider registry / OAuth flow 없음

작업:

- provider registry API
- validate API
- OAuth start/callback/disconnect flow

### 5. Source Connector 연동

대상:

- Settings / Connectors

현재 상태:

- connector card UI 있음
- 실제 connector registry/validation 없음

작업:

- connector registry 저장소
- connector validation API
- source explorer용 metadata API

## 추천 마이그레이션 결정

### 권장 방향

`b_FHMb53khGls`를 새 UI 기준으로 보고, 아래 순서로 진행한다.

1. 기존 `dashboard`의 read contract / artifact loader를 공통화
2. 새 프론트에 read API부터 붙임
3. issue 영역 mock 제거
4. project/environment/ai/connectors 영역 write model 추가

### 권장하지 않는 방향

- 기존 `dashboard`와 새 프론트를 둘 다 각각 유지하며 기능을 중복 구현
- 새 프론트 화면을 보면서 다시 loader/API를 새로 설계

## 단계별 실행 계획

### Phase 1. Read-only Foundation

목표:

- issue/summary/evidence 영역을 실데이터로 읽게 한다.

작업:

1. 공통 `atls/contracts` 추출
2. 공통 `artifact-loader` 추출
3. 새 프론트에 `app/api/projects/**/*` 이식
4. Overview, Issue Queue, Issue Detail 연동
5. Requirements, Cases, Evidence 연동

완료 기준:

- issue 관련 화면이 `mock-data.ts` 없이 동작

### Phase 2. Project Registry Backend

목표:

- projects 관련 화면을 실제 CRUD와 연결한다.

작업:

1. registry 저장소 설계
2. list/detail/create/update/archive/restore API
3. project validation 계산기
4. Projects List / New / Detail / Settings / Environment 연결

완료 기준:

- 새 프로젝트 생성과 조회가 실동작

### Phase 3. Environment + AI + Connector Settings

목표:

- settings 화면들을 실제 설정 저장소와 연결한다.

작업:

1. global environment API
2. project environment API
3. AI provider API
4. Codex OAuth flow
5. connector registry API

완료 기준:

- environment/ai/connectors 페이지가 실설정과 연결

### Phase 4. Controlled Actions

목표:

- 프론트 버튼들을 실제 동작에 연결한다.

대상 버튼:

- `Create Project`
- `Save Changes`
- `Add Provider`
- `Add Connector`
- `Open in Jira`
- `Approve Evidence`
- `Request Re-run`
- case run 버튼

완료 기준:

- 최소 로컬 저장/실행 액션이 동작

## 프론트 미구현 또는 연동 불가 지점

아래는 현재 기준으로 바로 보고해야 하는 항목이다.

### 1. API layer 없음

- `app/api` route 부재
- 상태: `missing_api`

### 2. 모든 화면이 mock-only

- `lib/mock-data.ts` 중심
- 상태: `mock_only`

### 3. write actions 없음

- create/save/add/archive/reset 버튼 미연동
- 상태: `missing_action`

### 4. evidence asset serving 없음

- 영상/이미지 inventory는 향후 가능
- 브라우저 재생 URL 정책 미정
- 상태: `needs_contract_definition`

### 5. AI OAuth 실제 플로우 없음

- `Codex OAuth` UI는 있으나 backend flow 없음
- 상태: `missing_api`

### 6. connector validation 없음

- connector card UI만 있음
- 상태: `missing_api`

## 사용자에게 계속 보고해야 하는 항목

연동 중 아래 상황이 나오면 바로 보고해야 한다.

1. 프론트 화면은 있는데 backend contract가 없는 경우
2. path preview는 있는데 실제 저장 정책이 결정되지 않은 경우
3. OAuth UI는 있는데 redirect/callback 정책이 미정인 경우
4. video player는 있는데 asset serving이 없는 경우
5. connector는 있는데 실제 MCP/API 접근 정책이 미정인 경우

## 권장 다음 작업

1. `b_FHMb53khGls`를 정식 dashboard 후보로 결정
2. 기존 `dashboard/lib/atls/*` 공통화
3. 새 프론트에 read API 이식
4. issue 영역 mock 제거부터 시작

## 하네스 엔지니어링 관점의 결론

새 프론트는 이미 제품 범위를 잘 담고 있다.  
하지만 지금 상태는 `실행 가능한 운영 화면`이 아니라 `정교한 mock UX`다.

따라서 진짜 연동의 핵심은:

1. 기존 `ATLS` loader/API 자산 재사용
2. mock 제거 순서 명확화
3. source-backed read model 유지
4. write action은 controlled하게 추가

이 원칙으로 가야 새 프론트를 살리면서도 `ATLS Platform`의 하네스 엔지니어링 철학을 깨지 않을 수 있다.
