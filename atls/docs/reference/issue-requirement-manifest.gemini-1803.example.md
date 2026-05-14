# Issue Requirement Manifest Example

- Project: `adcenter`
- Issue: `GEMINI-1803`
- Title: `"퍼스트 슬롯 비딩" 모듈 현재 프론트 구현과 PRD 불일치`
- Jira Status: `To Do`
- Workflow Bucket: `todo`
- Assignee: `정재철`

## Summary

- 이 이슈는 `최상단 입찰가 레이어`의 동작과 `팝업 이후 바닥 영역`의 상태 전이를 검증 대상으로 가진다.
- 현재 기준으로 팝업 진입, 실시간 노출 확률 갱신, 추천 비율 적용 버튼 동작은 source가 충분하다.
- 반면 왕관/하이라이트의 exact visual spec과 바닥 영역의 exact interaction spec은 아직 부족하다.
- 따라서 일부 requirement는 바로 구현/검증 가능하지만, 일부는 추가 자료가 필요하다.

## Requirements

### R1

- Title: 최상단 입찰가 설정 팝업 노출
- Statement: 입찰가 올리기 버튼을 클릭하면 최상단 입찰가 설정 팝업이 노출되어야 한다.
- Type: `modal_flow`
- Source Priority: `prd`
- Evidence Sufficiency: `sufficient`
- Implementation Allowed: `true`
- Needs User Materials: `false`

Source:

- `docs/prd/registration/MMRegistration2.md#4.3.3`
  - 입찰가 올리기 버튼 클릭 시 최상단 입찰가 설정 팝업 노출
- `https://jira.gmarket.com/browse/GEMINI-1803`
  - 퍼스트 슬롯 비딩 모듈의 프론트 구현이 PRD와 불일치

Notes:

- 팝업 진입 자체는 PRD 문장으로 확정 가능하다.

### R2

- Title: 입력 중 노출 확률 실시간 계산
- Statement: 입찰증액 퍼센트를 입력하면 노출 확률이 실시간으로 계산되어 표시되어야 한다.
- Type: `state_persistence`
- Source Priority: `prd`
- Evidence Sufficiency: `sufficient`
- Implementation Allowed: `true`
- Needs User Materials: `false`

Source:

- `docs/prd/registration/MMRegistration2.md#4.3.3`
  - 입력 입찰증액%에 따라 front-end에서 실시간 계산된 노출 확률%
- `docs/openapi/Registration.md#queryFirstSlotOverbid`
  - `sellerInputOverbidWinRate` 값을 반환하는 API 계약

Notes:

- 실시간 계산의 근거는 PRD, 계산값 source는 `queryFirstSlotOverbid` 응답으로 매핑할 수 있다.

### R3

- Title: 추천 비율 도전 버튼 동작
- Statement: 최상단 노출 도전하기 버튼을 클릭하면 추천 입찰증액 비율이 자동 적용되어야 하며, 추천 비율 이상인 상태에서는 버튼이 비활성화되어야 한다.
- Type: `validation_rule`
- Source Priority: `prd`
- Evidence Sufficiency: `sufficient`
- Implementation Allowed: `true`
- Needs User Materials: `false`

Source:

- `docs/prd/registration/MMRegistration2.md#4.3.3`
  - 최상단노출도전하기 버튼 클릭 시 추천 입찰증액% 자동 적용
  - 추천 증액비율% 이상인 경우 버튼 비활성화

Notes:

- 추천값의 exact 숫자는 서버 응답 기반이므로 하드코딩하지 않고 버튼 상태와 입력값 변경만 검증한다.

### R4

- Title: 노출 확률 하이라이트와 왕관 표시
- Statement: 추천 증액비율 이상인 경우 노출 확률에는 노란색 하이라이트와 왕관 표시가 노출되어야 한다.
- Type: `visual_spec`
- Source Priority: `prd`
- Evidence Sufficiency: `partial`
- Implementation Allowed: `false`
- Needs User Materials: `true`

Source:

- `docs/prd/registration/MMRegistration2.md#4.3.3`
  - 추천 증액비율 이상이면 노출확률 앞에 왕관 표기, 노란색 하이라이트 처리

Missing Evidence:

- Gap Type: `visual_exactness`
- Description: 왕관 아이콘의 형태, 위치, 하이라이트 색상 기준이 PRD 텍스트만으로는 불충분하다.
- Required Material: 시안 캡처 또는 Jira 첨부 이미지
- Blocking: `true`

Notes:

- 텍스트 PRD는 존재하지만 exact visual oracle이 부족하므로 자동 구현 기준으로는 확정하지 않는다.

### R5

- Title: 팝업 종료 후 바닥 영역의 후속 상태
- Statement: 팝업에서 설정한 최상단 입찰가가 바닥 영역 input과 안내 문구, 상품별 최상단 입찰가 영역에 어떻게 반영되는지 명확히 정의되어야 한다.
- Type: `state_persistence`
- Source Priority: `prd`
- Evidence Sufficiency: `partial`
- Implementation Allowed: `false`
- Needs User Materials: `true`

Source:

- `docs/prd/registration/MMRegistration2.md#4.3.3`
  - 팝업 종료 후 input 노출, 안내 문구, 추천입찰가 적용 버튼, 상품별 최상단 입찰가 노출

Missing Evidence:

- Gap Type: `interaction_detail`
- Description: 바닥 영역의 상태 전이 순서와 exact 문구/숨김 조건이 텍스트만으로는 완전히 고정되지 않는다.
- Required Material: 바닥 영역 시안 또는 Jira 코멘트의 상세 동작 설명
- Blocking: `true`

Notes:

- 현재 구현 검증은 팝업 레이어까지만 확정하는 것이 안전하다.

## Additional Materials Needed

- 왕관/하이라이트의 exact visual spec
  - 추천 비율 이상일 때 왕관 아이콘 형태, 위치, 색상 기준
- 바닥 영역의 exact interaction spec
  - 팝업 종료 후 어떤 안내 문구가 어떤 조건에서 보여야 하는지
  - 추천입찰가 적용하기 버튼, bubble, input, 성공 배너의 노출/숨김 조건

## Current Judgment

- 구현/검증 바로 가능:
  - `R1`, `R2`, `R3`
- 추가 자료 없이는 확정 불가:
  - `R4`, `R5`
