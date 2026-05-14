# Pass / Fail Evidence Report Spec

## 목적

이 문서는 이슈 단위 검증 결과를 `요구사항별 pass/fail`로 정리하는 리포트 포맷을 정의한다.

핵심 목표:

- 영상/스크린샷/네트워크/상태 증거를 한 문서에서 추적 가능하게 한다.
- 무엇이 통과했고 무엇이 근거 부족인지 분리한다.
- "테스트는 통과했지만 요구사항 확정은 아님" 상태를 숨기지 않는다.

## 리포트 섹션

### 1. Header

- `issue_key`
- `issue_title`
- `execution_date`
- `executor`
- `project`
- `spec_path`

### 2. Evidence Summary

- `video_count`
- `screenshot_count`
- `network_assertion_count`
- `state_assertion_count`
- `missing_evidence_count`

### 3. Requirement Results

각 requirement를 아래 형식으로 적는다.

- `requirement_id`
- `statement`
- `source_ref`
- `result`
- `result_reason`
- `evidence_links`
- `open_gaps`

`result`는 아래 중 하나를 쓴다.

- `pass`
- `fail`
- `blocked`
- `not_executed`
- `pass_with_partial_evidence`

### 4. Final Judgment

- `ready_for_jira_update: true/false`
- `ready_for_release_confidence: high/medium/low`
- `manual_follow_up_required`

## 판단 규칙

### pass

- source가 충분하다.
- 실행 결과가 source와 일치한다.
- forbidden behavior도 검증되었다.

### fail

- source가 충분하다.
- 실행 결과가 source와 불일치한다.

### blocked

- 구현 전 또는 검증 전 필요한 source/evidence가 없다.
- 또는 source는 충분하지만, 테스트 환경/외부 API/세션 문제로 실행 자체가 막혔다.
- 이 경우 `blocked_reason`에 `source_missing`인지 `execution_blocked`인지 분리해서 적는다.

### pass_with_partial_evidence

- 핵심 동작은 맞지만 exact text / payload / state 중 일부 근거가 부족하다.
- Jira 완료 처리 전 추가 자료가 필요하다.

## Markdown 템플릿

```md
# Evidence Report

- Issue: GEMINI-1803
- Spec: tests/e2e/issues/gemini-1803.spec.ts
- Execution Date: 2026-04-04

## Evidence Summary

- Video: 1
- Screenshot: 3
- Network Assertions: 0
- State Assertions: 0
- Missing Evidence: 1

## Requirement Results

### R1

- Statement: 입찰가 입력 중에도 노출 확률이 실시간으로 계산되어야 한다.
- Source: docs/prd/registration/MMRegistration2.md
- Result: pass
- Result Reason: 입력 직후 `- %`에서 실제 확률 값으로 갱신됨을 확인했다.
- Evidence:
  - video: `tests/results/issues/GEMINI-1803/artifacts/.../video.webm`
  - screenshot: `tests/results/issues/GEMINI-1803/02-top-bid-live-rate-updated.png`
- Open Gaps: 없음

### R2

- Statement: 추천 비율 이상이면 최상단 노출 도전하기 버튼이 비활성화되어야 한다.
- Source: docs/prd/registration/MMRegistration2.md
- Result: pass
- Result Reason: 도전하기 버튼으로 추천값 적용 후 disabled 상태를 확인했다.
- Evidence:
  - video: `tests/results/issues/GEMINI-1803/artifacts/.../video.webm`
  - screenshot: `tests/results/issues/GEMINI-1803/03-top-bid-challenge-applied.png`
- Open Gaps: exact recommended percent 노출값은 서버 응답 기반이라 별도 고정값 검증은 하지 않음

## Final Judgment

- Ready for Jira Update: true
- Ready for Release Confidence: medium
- Manual Follow-up Required: false
```

## 사용자 추가 자료 요청 섹션

리포트에 아래 섹션을 넣을 수 있다.

```md
## Additional Materials Needed

- exact alert 문구 캡처
- Jira 코멘트 원문
- OpenAPI response example
```

이 섹션이 비어 있지 않으면 `ready_for_jira_update`는 기본적으로 `false` 또는 `conditional`이어야 한다.

## ATLS 사용 규칙

1. 리포트는 `테스트 결과`와 `요구사항 충족 판단`을 섞지 않는다.
2. 영상이 있어도 source가 없으면 `pass` 대신 `pass_with_partial_evidence` 또는 `blocked`를 쓴다.
3. "대충 맞아 보임"은 결과값으로 허용하지 않는다.
4. 필요한 자료가 있으면 리포트 하단에 명시적으로 요청한다.
5. 이슈 본질과 무관한 upstream failure는 neutralize한 뒤 본질 요구사항을 따로 검증할 수 있다.
6. 이때는 `execution_notes`에 아래를 명시한다.
   - neutralized upstream
   - neutralization method
   - why it is irrelevant to the issue under test
