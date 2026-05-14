# ATLS E2E Harness Workflow

## 목적

이 문서는 `ATLS`를 이용해 Jira/Confluence 중심의 분석 결과를 재사용 가능한 E2E 검증 워크플로우로 연결하는 표준 흐름을 정의한다.

핵심 목표는 다음과 같다.

- Jira summary / task list / task plan을 테스트 가능한 명세로 변환한다.
- 프로젝트별 로그인 방식과 테스트 환경 차이를 `project adapter`로 분리한다.
- 수정 결과가 최초 요구조건과 부합하는지 케이스 단위로 자동 검증한다.
- 검증 결과를 markdown/json/html artifact로 남기고, 리뷰 및 배포 게이트와 연결한다.
- manifest 계열 산출물은 `json + md`를 함께 생성해 자동화 입력과 사람 검토를 동시에 지원한다.

## 범위

이 워크플로우는 다음 상황을 주 대상으로 한다.

- Alert message 문구 변경
- modal confirm / cancel / dim click 동작
- payload mapping 변경
- validation message / error handling 변경
- state persistence / restore 동작
- pagination / selection / list rendering 변경

## 기본 원칙

1. `요구조건 -> acceptance case -> runner -> report` 흐름을 유지한다.
2. 테스트 케이스는 구현 세부사항이 아니라 요구조건을 source of truth로 삼는다.
3. 프로젝트 의존 정보는 `project adapter`에 모으고, `ATLS core`에는 하드코딩하지 않는다.
4. unit test와 E2E test의 책임을 분리한다.
5. high-risk 변경은 케이스별 증거가 없으면 merge 하지 않는다.
6. source가 부족한 상태에서 AI가 임의로 요구사항을 채우지 않는다.
7. fallback 동작은 source가 있을 때만 테스트 기준으로 채택한다.

## Manifest 산출 규칙

`ATLS`는 아래 manifest를 생성할 때 `json`과 `md`를 함께 만든다.

- `issue requirement manifest`
- `acceptance manifest`

역할은 다음과 같이 나눈다.

- `json`: workflow 연결, generator 입력, 후속 자동화용
- `md`: 사람이 읽고 승인하거나 추가 자료 필요 여부를 판단하는 검토용

## Evidence Policy

이 워크플로우는 `문서가 부족한 프로젝트`를 전제로 동작해야 한다.

따라서 evidence는 아래 2개 축으로 분리한다.

1. `requirement source`
- PRD
- Jira 본문
- Jira 코멘트
- Jira 첨부
- OpenAPI / API 계약
- existing behavior
- code constraint

2. `execution evidence`
- video
- screenshot
- dom assertion
- network assertion
- state assertion

규칙:

- requirement source가 부족하면 실행 evidence가 많아도 `완전 검증`으로 판단하지 않는다.
- `existing behavior`와 `code constraint`는 보조 근거로만 쓴다.
- `exact text`, `payload exact shape`, `re-entry state`는 source가 없으면 `pending evidence`로 남긴다.

## 표준 산출물

### 1. Summary

- 목적: 어떤 이슈/태스크를 다룰지 선정
- 입력: Jira issues, comments, project context
- 산출물 예: `summary.md`

### 2. Task List

- 목적: track / category / priority / current status 기준으로 그룹화
- 입력: summary + project mapping
- 산출물 예: `project_task_list.md`

### 3. Task Plans

- 목적: 각 태스크별 작업 계획과 검증 방향 정의
- 입력: task list + project touchpoints
- 산출물 예: `task_plans.md`

### 4. Acceptance Manifest

- 목적: 태스크를 테스트 실행 단위로 변환
- 입력: task plans + issue requirement manifest
- 산출물 예: `acceptance-manifest.json`, `acceptance-manifest.md`

### 4-1. Issue Requirement Manifest

- 목적: 요구사항 근거와 부족한 증거를 구조화
- 입력: Jira / PRD / OpenAPI / trusted attachments
- 산출물 예: `issue-requirement-manifest.json`, `issue-requirement-manifest.md`

### 5. Project Adapter

- 목적: 로그인, baseURL, seed data, selector policy, environment strategy 정의
- 입력: 프로젝트 구조와 테스트 환경
- 산출물 예: `project-adapter.json`

### 6. Case Report

- 목적: 케이스별 pass/fail과 증거 저장
- 입력: runner execution result
- 산출물 예: `case-report.md`, `case-report.json`, screenshot, trace, video

## 워크플로우 단계

### Step 1. Collect

- Jira summary, description, comments 수집
- 관련 project root 지정
- 필요 시 PRD / OpenAPI / trusted docs 읽기

### Step 2. Analyze

- QA / GEMINI 등 track 분류
- category 분류
- priority 및 approval gate 분류
- touchpoints / blockers / validation plan 생성

### Step 3. Plan

- task list 생성
- task plans 생성
- 실행 전 승인 포인트 정의

### Step 4. Source Check

- requirement source hierarchy 확인
- exact text / payload / state 기준 확인
- 부족한 근거를 `needs_user_materials`로 표시
- `implementation_allowed` 여부 판단

### Step 5. Specify

- task plans를 acceptance manifest로 변환
- 각 케이스에 `precondition`, `action`, `expected`, `forbidden`, `evidence` 정의

### Step 6. Adapt

- 프로젝트 로그인 전략 확정
- storageState, API login, bootstrap route 등 환경 전략 선택
- 셀렉터 정책과 seed data 전략 명시

### Step 7. Execute

- contract E2E
- integrated E2E
- regression E2E

### Step 8. Report

- 케이스별 pass/fail
- failure reason
- screenshot / trace / video / network
- expected vs actual diff

### Step 9. Gate

- 리뷰어가 case report 기준으로 검증
- required suite 미통과 시 merge 금지
- Jira / Confluence에 실행 결과 링크 반영

## 자료 부족 시 멈춤 규칙

아래 중 하나라도 부족하면 `blocked` 또는 `pass_with_partial_evidence`로 남긴다.

- exact alert 문구
- payload key/value
- 상태 복원 기준
- 금지 동작(forbidden behavior)

이 경우 `ATLS`는 다음 항목을 사용자에게 요청해야 한다.

- Jira 코멘트 원문
- 첨부 이미지/영상
- Figma/시안 링크
- OpenAPI 예시 요청/응답
- 기존 운영 화면 녹화

## 테스트 계층 권장안

### Contract E2E

- 목적: UI 요구조건 검증
- 특징: API stub / mock 기반
- 대상: alert 문구, modal confirm, disabled state, exact message, conditional rendering
- 구현 팁: 프로젝트 내부에 로컬 전용 harness route를 두고, 고정된 mock props로 컴포넌트를 직접 띄우면 백엔드와 seed data 노이즈를 크게 줄일 수 있다.

### Integrated E2E

- 목적: 실제 API 연동 포함 검증
- 특징: staging 또는 dedicated env 사용
- 대상: payload mapping, state restore, navigation, persisted state

### Regression E2E

- 목적: 과거 이슈 재발 방지
- 특징: 핵심 시나리오만 모음
- 대상: high-risk 태스크

## 리뷰 / 배포 게이트 기준

1. 관련 이슈에 대응하는 acceptance case가 없으면 PR merge 금지
2. `validation`, `modal UX`, `payload mapping` 변경은 관련 E2E suite green 필수
3. 케이스별 artifact가 없으면 리뷰 승인 금지
4. flaky test는 production gate에서 제외하지 말고 원인 해결 전 quarantine으로 별도 관리
5. `Done` 또는 `In Review` 전환 시 case report 링크를 Jira에 반영

## 프로젝트 적용 예시

`adcenter`처럼 로그인 UI가 불안정한 프로젝트는 다음 우선순위를 따른다.

1. dedicated test account + CI secret
2. `auth.setup.ts`로 storageState 생성
3. 가능하면 API login 또는 bootstrap login route 도입
4. 개인 계정/개인 비밀번호 수동 입력은 금지
5. `adcenter` 기본 로그인 provider는 `GMKT / G마켓 로그인`으로 고정하고 `ESMPLUS`는 기본 인증 하네스 범위에서 제외한다.

또한 `adcenter`처럼 등록/수정 모달이 복잡한 프로젝트는 실제 운영 플로우 E2E만으로 회귀를 막기 어렵다.
이 경우 다음 2단 구조를 권장한다.

1. `contract harness route`
- 예: `/ad/registration/harness`
- 목적: alert, modal close confirm, exact message, dirty state 분기 검증
- 특징: mock props와 deterministic state만 사용

2. `integrated flow route`
- 예: 실제 `/ad/registration`
- 목적: 로그인 이후 실제 저장, payload, restore, navigation 검증
- 특징: storageState, 실제 session, 필요 시 trusted API만 연동

로컬 전용 자동화만 필요한 프로젝트라면 `CI gate`는 생략할 수 있다.
대신 case report와 Playwright artifact를 로컬에서 남기고, 최종 배포 전 수동 리뷰 체크포인트로 사용한다.

## 다음 단계

- `ATLS`에서 task plan -> acceptance manifest 생성 workflow 추가
- `ATLS`에서 issue requirement manifest 생성 workflow 추가
- `project adapter` 스키마 확정
- Playwright runner와 case report emitter 연결
- CI gate 규칙을 프로젝트별로 설정 가능하도록 분리

## 이슈 단위 실행 모델

여러 이슈를 한 번에 수정하더라도 검증은 이슈 단위로 독립 실행 가능해야 한다.

- 테스트 파일: `tests/e2e/issues/<jira-key>.spec.ts`
- 스크린샷: `tests/results/issues/<JIRA-KEY>/`
- video/trace: `tests/results/artifacts/`
- 결과 문서: `REPORT.md` 또는 프로젝트/ATLS 산출물 문서

권장 흐름은 다음과 같다.

1. Jira task plan에서 이슈 하나를 선택한다.
2. 이슈별 acceptance case를 확정한다.
3. 해당 이슈 전용 spec을 만든다.
4. 이슈 하나만 단독 실행한다.
5. 스크린샷, video, 수동 확인 포인트를 이슈 리포트에 묶는다.
6. 다음 이슈는 별도 spec과 별도 report로 반복한다.
