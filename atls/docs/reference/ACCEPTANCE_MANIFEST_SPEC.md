# Acceptance Manifest Spec

## 목적

`acceptance manifest`는 task plan을 E2E 실행 단위로 변환한 명세다.

이 포맷은 특정 프로젝트 구현과 분리되어야 하며, 같은 issue/task를 다른 프로젝트 adapter나 다른 runner에도 재사용할 수 있어야 한다.

## 산출물 형식

`ATLS`는 `acceptance manifest`를 만들 때 아래 두 형식을 함께 생성하는 것을 기본으로 한다.

- `json`: runner, generator, adapter가 읽는 구조화 데이터
- `md`: 리뷰어가 케이스를 빠르게 확인하는 문서

권장 출력 파일 예시는 다음과 같다.

- `acceptance-manifest.<issue-key>.json`
- `acceptance-manifest.<issue-key>.md`

## 필수 필드

- `manifest_version`: 포맷 버전
- `project_key`: 프로젝트 식별자
- `track`: `qa`, `gemini` 등
- `task_id`
- `issue_key`
- `category`
- `priority`
- `goal`
- `cases`

## case 필드

- `case_id`
- `title`
- `risk`
- `preconditions`
- `actions`
- `expected`
- `forbidden`
- `evidence`
- `tags`

## 권장 필드

- `source_summary`
- `source_task_plan`
- `source_requirement_manifest`
- `touchpoints`
- `requires_auth`
- `requires_seed_data`
- `contract_mode`
- `integrated_mode`
- `related_prd_refs`
- `related_api_refs`
- `evidence_sufficiency`
- `needs_user_materials`
- `missing_evidence`

## 예시

```json
{
  "manifest_version": "0.1",
  "project_key": "adcenter",
  "track": "gemini",
  "task_id": "D-4",
  "issue_key": "GEMINI-1792",
  "category": "modal UX",
  "priority": "P2",
  "goal": "제외상품 선택 팝업에서 취소/이탈 시 confirm alert가 정확히 노출되는지 검증한다.",
  "touchpoints": [
    "src/components/features/ad/registration/common/ProductSelectionLayer.tsx",
    "src/components/features/ad/edit/AdGroupModify.tsx"
  ],
  "cases": [
    {
      "case_id": "exclude-modal-cancel-dirty",
      "title": "변경사항이 있는 상태에서 취소 클릭 시 confirm alert 노출",
      "risk": "high",
      "preconditions": [
        "사용자가 상품 선택 팝업을 열어둔 상태다.",
        "선택 상태 또는 입력 상태가 변경되었다."
      ],
      "actions": [
        "취소 버튼을 클릭한다."
      ],
      "expected": [
        "confirm alert가 노출된다.",
        "문구가 기획 문구와 정확히 일치한다."
      ],
      "forbidden": [
        "alert 없이 팝업이 닫힌다.",
        "문구가 이전 문구이거나 오타가 있다."
      ],
      "evidence": [
        "screenshot",
        "trace",
        "dialog_text"
      ],
      "tags": [
        "modal",
        "alert",
        "dirty-state",
        "regression"
      ]
    }
  ]
}
```

## 생성 규칙

1. 한 task가 여러 동작을 가지면 case를 분리한다.
2. `expected`에는 positive result만 적지 말고 exact text, route change, state retention까지 포함한다.
3. `forbidden`에는 잘못 수정됐을 때 발생하는 대표 오동작을 명시한다.
4. `evidence`는 사람이 리뷰할 수 있는 결과여야 한다.
5. 프로젝트 고유 셀렉터나 로그인 정보는 manifest에 넣지 않는다. 그 정보는 adapter에 둔다.
6. source가 부족한 case는 `missing_evidence`와 `needs_user_materials`를 채우고, 자동 실행 우선순위를 낮춘다.
7. PRD가 없더라도 Jira / API 계약 / 첨부 자료로 source-backed case를 만들 수 있어야 한다.
8. `md` 출력에는 case별 `preconditions`, `actions`, `expected`, `forbidden`, `evidence`, `execution_status`를 읽기 쉽게 정리한다.

## Enumerated Requirement Completeness

Jira Comment 또는 source 문서 안에 열거된 조건이 있다면, `acceptance manifest`는 그 조건 집합을 빠짐없이 case 또는 case의 expected 단계로 확장해야 한다.

예를 들어 코멘트가 아래처럼 정리되어 있다면:

- 최초 노출시에는 화살표 없음
- 칩 5개 초과 시 우측 화살표 노출
- 우측 클릭 시 첫 칩이 맨 앞에 노출
- 중간 리스트에서는 좌우 화살표 노출
- 마지막 리스트에서는 왼쪽 화살표만 노출

최소 규칙은 다음과 같다.

1. 각 항목은 독립 acceptance 조건으로 보존한다.
2. 일부 항목만 구현/검증하고 `resolved` 또는 `done`으로 판단하면 안 된다.
3. evidence는 각 조건을 실제로 커버해야 한다.
4. `부분 구현`과 `부분 검증`은 명시적으로 표시해야 한다.

즉, source에 열거 조건이 있으면 `acceptance manifest`는 **조건 누락이 없는지** 먼저 확인해야 한다.
