# Acceptance Manifest Example

- Project: `adcenter`
- Track: `gemini`
- Task ID: `GEMINI-1803`
- Issue: `GEMINI-1803`
- Category: `validation_rule`
- Priority: `P0`
- Goal: 최상단 입찰가 레이어의 PRD 정합성을 source-backed requirement 범위 안에서 검증한다.

## Source

- Summary: `/Users/jaecjeong/Documents/atls/jira/workflow/project_task_flow/2026-04-04/summary.md`
- Task Plan: `/Users/jaecjeong/Documents/atls/jira/workflow/project_task_flow/2026-04-04/task_plans.md#GEMINI-1803`
- Requirement Manifest: `docs/reference/issue-requirement-manifest.gemini-1803.example.json`
- PRD: `docs/prd/registration/MMRegistration2.md#4.3.3`
- API: `docs/openapi/Registration.md#queryFirstSlotOverbid`

## Scope

- Requires Auth: `false`
- Requires Seed Data: `false`
- Contract Mode: `true`
- Integrated Mode: `false`
- Evidence Sufficiency: `partial`
- Needs User Materials: `true`

Missing Evidence:

- 왕관 아이콘 및 하이라이트의 exact visual spec
- 팝업 종료 후 바닥 영역의 exact interaction spec

## Touchpoints

- `src/components/features/ad/registration/common/TopExposureBidSettingLayer.tsx`
- `src/components/features/ad/registration/modules/GroupCreationModule.tsx`
- `tests/e2e/issues/gemini-1803.spec.ts`

## Cases

### Case 1

- Case ID: `top-bid-popup-opens`
- Title: 입찰가 올리기 버튼으로 최상단 입찰가 설정 팝업 진입
- Risk: `medium`

Preconditions:

- 수동 광고 등록 맥락 또는 하네스 화면이 열려 있다.
- 최상단 입찰가 레이어를 열 수 있는 버튼이 노출되어 있다.

Actions:

- 입찰가 올리기 또는 최상단 입찰가 레이어 다시 열기 버튼을 클릭한다.

Expected:

- 검색결과 최상단 입찰가 설정하기 팝업이 열린다.

Forbidden:

- 버튼 클릭 후 아무 반응이 없다.
- 다른 레이어가 열리거나 기존 화면에서만 상태가 바뀐다.

Evidence:

- `video`
- `screenshot`
- `dom_assert`

### Case 2

- Case ID: `top-bid-live-win-rate`
- Title: 입력 중 노출 확률 실시간 갱신
- Risk: `high`

Preconditions:

- 최상단 입찰가 설정 팝업이 열린 상태다.
- 입찰가 input이 기본 상태로 보인다.

Actions:

- 입찰가 input에 유효한 퍼센트 값을 입력한다.

Expected:

- 노출 확률이 `- %`에서 실제 퍼센트 값으로 갱신된다.

Forbidden:

- 입력 중에도 노출 확률이 계속 `- %`로 남는다.
- 입력과 무관한 고정값이 표시된다.

Evidence:

- `video`
- `screenshot`
- `dom_assert`
- `state_assert`

### Case 3

- Case ID: `top-bid-challenge-applies-recommendation`
- Title: 최상단 노출 도전하기 버튼으로 추천 비율 적용 및 비활성화
- Risk: `high`

Preconditions:

- 최상단 입찰가 설정 팝업이 열린 상태다.
- 추천 비율이 존재한다.

Actions:

- 최상단 노출 도전하기 버튼을 클릭한다.

Expected:

- 입찰가 input 값이 추천 비율로 채워진다.
- 최상단 노출 도전하기 버튼이 비활성화된다.

Forbidden:

- 버튼 클릭 후 input 값이 그대로 유지된다.
- 추천 비율 이상인데 버튼이 계속 활성 상태다.

Evidence:

- `video`
- `screenshot`
- `dom_assert`

### Case 4

- Case ID: `top-bid-visual-highlight`
- Title: 추천 비율 이상일 때 왕관과 하이라이트 시각 요소 노출
- Risk: `medium`
- Execution Status: `blocked_by_missing_evidence`

Required Materials:

- 시안 캡처 또는 Jira 첨부 이미지

Reason:

- 왕관/하이라이트의 exact visual oracle이 부족하다.

### Case 5

- Case ID: `top-bid-bottom-area-follow-up`
- Title: 팝업 종료 후 바닥 영역 상태 전이 검증
- Risk: `high`
- Execution Status: `blocked_by_missing_evidence`

Required Materials:

- 바닥 영역의 exact interaction spec
- 문구/숨김 조건이 보이는 시안 또는 Jira 코멘트

Reason:

- 바닥 영역 후속 상태는 텍스트 PRD만으로 exact rule을 고정하기 어렵다.

## Current Judgment

- 지금 바로 E2E 가능:
  - `top-bid-popup-opens`
  - `top-bid-live-win-rate`
  - `top-bid-challenge-applies-recommendation`
- 추가 자료 확보 후 진행:
  - `top-bid-visual-highlight`
  - `top-bid-bottom-area-follow-up`
