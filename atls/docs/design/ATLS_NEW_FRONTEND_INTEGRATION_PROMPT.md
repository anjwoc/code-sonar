# ATLS New Frontend Integration Prompt

## 목적

이 프롬프트는 `/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls`를 `ATLS Platform`의 실제 dashboard frontend로 채택하고, `ATLS` 패키지 기능과 end-to-end로 연동하기 위한 하네스 엔지니어링 기반 실행 프롬프트다.

핵심 목표:

- 새 프론트가 현재 가지고 있는 화면 구조를 유지한다.
- `ATLS`의 artifact, workflow, connector, AI/provider, environment, project registry 기능과 실제로 연결한다.
- mock 기반 상태를 제거하고 source-backed read model과 controlled action model로 치환한다.
- 프론트 미구현 또는 연동 불가 지점은 추정하지 않고 명시적으로 보고한다.

## 입력 컨텍스트

- `ATLS` 루트: `/Users/jaecjeong/lab/memo/atsl`
- 새 프론트 루트: `/Users/jaecjeong/lab/memo/atsl/b_FHMb53khGls`
- 기존 연동 참고 구현:
  - `/Users/jaecjeong/lab/memo/atsl/dashboard/lib/atls/contracts.ts`
  - `/Users/jaecjeong/lab/memo/atsl/dashboard/lib/atls/artifact-loader.ts`
  - `/Users/jaecjeong/lab/memo/atsl/dashboard/app/api/projects/**/*`
- 기준 PRD:
  - `docs/design/ATLS_PLATFORM_MASTER_PRD.md`

## 하네스 엔지니어링 원칙

1. source of truth는 `ATLS` 산출물과 설정이다.
2. 프론트는 상태 계산기를 직접 구현하지 않고 `ATLS` read model과 action result를 읽는다.
3. mock 데이터를 실제 연동 완료처럼 간주하지 않는다.
4. 없는 API/contract는 `missing_api`로 표시한다.
5. source/evidence 부족 상태는 `blocked` 또는 `partial`로 드러낸다.
6. 무차별 fallback 금지

## 먼저 확인할 것

1. 새 프론트의 화면 목록
2. 각 화면이 현재 어떤 mock data에 의존하는지
3. 기존 `dashboard`에서 이미 만든 read API/loader를 그대로 재사용 가능한지
4. 새 프론트에서 추가된 페이지가 무엇인지
5. action 버튼이 실제로 연결 가능한지

## 현재 새 프론트에서 반드시 점검할 화면

- `/dashboard`
- `/dashboard/issues`
- `/dashboard/issues/:issueKey`
- `/dashboard/issues/:issueKey/requirements`
- `/dashboard/issues/:issueKey/cases`
- `/dashboard/issues/:issueKey/evidence`
- `/dashboard/projects`
- `/dashboard/projects/new`
- `/dashboard/projects/:projectKey`
- `/dashboard/projects/:projectKey/environment`
- `/dashboard/projects/:projectKey/settings`
- `/dashboard/settings/environment`
- `/dashboard/settings/ai`
- `/dashboard/settings/connectors`

## 기대 출력

### 1. Frontend Coverage Audit

- 화면별 현재 상태
- mock 의존 여부
- 대응하는 `ATLS` artifact / API
- missing API / missing action / missing contract 구분

### 2. Integration Mapping

- page -> read model
- page -> action API
- component -> source of truth

### 3. Migration Strategy

- 기존 `dashboard` API/loader를 재사용할지
- `b_FHMb53khGls`로 이식할지
- 공통 라이브러리로 분리할지

### 4. Delivery Plan

- Phase 1: read-only 연동
- Phase 2: project/environment/AI/connectors CRUD 연동
- Phase 3: issue actions / test run / evidence review 연동

### 5. Explicit Blockers

- 프론트 미구현
- API 미존재
- contract 미정
- 실제 asset serving 미지원

## 출력 형식

반드시 아래 구조를 따른다.

1. `Current Frontend Coverage`
2. `ATLS Feature Mapping`
3. `Missing Frontend / Missing API`
4. `Migration Decision`
5. `Phased Integration Plan`
6. `Blocked / Needs Follow-up`

## 금지 사항

- mock state를 real integration처럼 쓰지 않는다.
- source 없는 상태 계산을 프론트에서 하드코딩하지 않는다.
- 버튼이 있다고 해서 action이 구현된 것처럼 설명하지 않는다.
- evidence player UI가 있다고 해서 asset serving이 구현된 것처럼 설명하지 않는다.
