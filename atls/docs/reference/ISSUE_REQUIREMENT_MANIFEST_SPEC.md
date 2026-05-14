# Issue Requirement Manifest Spec

## 목적

`issue requirement manifest`는 Jira 이슈 하나를 "무엇을 근거로", "어디까지 확정되었는지", "무엇이 아직 부족한지"까지 포함해 구조화하는 포맷이다.

이 문서는 `acceptance manifest`보다 한 단계 앞선 문서다.

- `issue requirement manifest`: 요구사항과 근거를 정리하는 문서
- `acceptance manifest`: 실행 가능한 테스트 케이스로 변환한 문서

## 산출물 형식

`ATLS`는 `issue requirement manifest`를 만들 때 아래 두 형식을 함께 생성하는 것을 기본으로 한다.

- `json`: 자동 처리와 후속 workflow 연결용 원본 데이터
- `md`: 사람이 바로 읽고 검토하기 위한 포맷팅 문서

권장 출력 파일 예시는 다음과 같다.

- `issue-requirement-manifest.<issue-key>.json`
- `issue-requirement-manifest.<issue-key>.md`

핵심 원칙은 다음과 같다.

1. 요구사항 source와 실행 evidence를 분리한다.
2. 증거가 부족한 요구사항은 억지로 확정하지 않는다.
3. AI의 해석이 들어간 문장은 반드시 source-backed fact와 분리한다.
4. fallback으로 "그럴듯한 기대 동작"을 만들지 않는다.

## Source Hierarchy

요구사항 source는 아래 우선순위를 따른다.

1. `prd`
2. `jira_body`
3. `jira_comment`
4. `jira_attachment`
5. `api_contract`
6. `existing_behavior`
7. `code_constraint`

규칙:

- 상위 source가 있으면 하위 source는 보조 근거로만 사용한다.
- `existing_behavior`는 요구사항 source가 아니라 회귀 기준으로만 사용하는 것이 안전하다.
- `code_constraint`는 구현 규칙의 근거일 수는 있지만, 제품 요구사항의 대체물이 되지 않는다.

## Evidence Sufficiency 등급

각 requirement는 아래 상태 중 하나를 가져야 한다.

- `sufficient`: 구현/검증에 필요한 근거가 충분하다.
- `partial`: 핵심 방향은 있으나 exact text, edge case, payload shape 중 일부가 부족하다.
- `missing`: 요구사항을 확정할 만한 근거가 없다.

`partial` 또는 `missing`이면 구현보다 먼저 추가 자료 요청이 나가야 한다.

해석 기준:

- `Source Missing`은 여기서 말하는 `evidence_sufficiency = missing`과 같은 뜻이다.
- 즉 실행 환경 문제가 아니라, **요구사항을 확정할 source 자체가 부족한 상태**를 의미한다.
- 예:
  - Jira 제목만 있고 본문/코멘트/시안/PRD가 전혀 없음
  - exact alert 문구가 없어 pass/fail 기준을 확정할 수 없음
  - payload shape를 확인해야 하는데 API contract나 Jira 설명이 없음

## 필수 필드

- `manifest_version`
- `project_key`
- `issue_key`
- `issue_title`
- `jira_status`
- `requirements`

## requirement 필드

- `requirement_id`
- `title`
- `statement`
- `requirement_type`
- `source_priority`
- `sources`
- `evidence_sufficiency`
- `implementation_allowed`
- `needs_user_materials`
- `missing_evidence`
- `notes`

## requirement_type 권장 값

- `ui_text`
- `modal_flow`
- `payload_contract`
- `state_persistence`
- `navigation`
- `validation_rule`
- `list_rendering`
- `access_control`
- `visual_spec`

## source 항목 필드

- `source_type`
- `source_ref`
- `excerpt_summary`
- `confidence`
- `is_primary`

`source_ref` 예시:

- Jira URL
- PRD 파일 경로
- OpenAPI 문서 경로
- 첨부 이미지 파일명
- 기존 배포 경로 또는 화면 식별자

## missing_evidence 항목 필드

- `gap_type`
- `description`
- `required_material`
- `blocking`

`required_material` 예시:

- Jira 코멘트 원문
- PRD 캡처
- Figma 링크
- API example response
- 실제 운영 화면 녹화
- 정확한 alert 문구

## 생성 규칙

1. requirement는 가능한 한 한 문장으로 쪼갠다.
2. 하나의 requirement에는 하나의 중심 동작만 둔다.
3. `statement`는 source를 바탕으로 작성하고, AI의 추측 문장을 넣지 않는다.
4. `implementation_allowed`는 `evidence_sufficiency = sufficient`일 때만 `true`로 둔다.
5. exact 문구, payload 필드, 상태 복원 규칙이 부족하면 `needs_user_materials = true`로 둔다.

## Enumerated Comment Expansion

Jira Comment 안에 번호 목록이나 bullet 형태로 조건이 정리되어 있으면, `ATLS`는 이를 단순 요약으로 뭉개지 않고 **열거된 조건 집합**으로 취급해야 한다.

예:

- 최초 노출시에는 화살표 없음
- 리스트 당 칩 5개 초과 시 우측 화살표 노출
- 우측 화살표 클릭 시 첫 칩이 맨 앞에 노출
- 마지막 리스트에서는 왼쪽 화살표만 노출

규칙:

1. 각 항목은 requirement 후보로 독립 보존한다.
2. `최초`, `중간`, `마지막`, `이동 후`, `n번째` 같은 단계 표현은 상태 전이 정보이므로 삭제하지 않는다.
3. 코멘트의 일부만 requirement로 뽑고 나머지를 버리면 안 된다.
4. 인사말, 감사 문구, 확인 요청, 단순 링크는 requirement에서 제외한다.
5. `사전 조건`, `재현 경로`, `계정 정보`는 실행 정보이지 제품 요구사항 자체가 아님을 구분한다.

즉, 코멘트가 사실상 구현 규칙을 정리해준 경우에는 그 코멘트 전체가 requirement source의 핵심이 된다.

## Upstream Failure 분리 원칙

이슈 본질과 무관한 상위 실패가 있으면 source가 충분해도 실행이 막힐 수 있다.

예:

- 등록 API 자체 장애
- 테스트 환경 계정 이상
- 외부 세션 만료
- unrelated backend 500

이 경우 규칙은 다음과 같다.

1. 이슈가 검증하려는 본질이 `실패 메시지 처리`, `payload shape`, `validation`, `state persistence`라면
   upstream 성공/실패를 분리해서 하네스 또는 request interception으로 검증한다.
2. 즉, **실제 운영 API가 실패하더라도 이슈 본질이 그 실패 자체가 아니면 성공 경로를 가정한 검증**을 허용한다.
3. 다만 이때는 `notes`에 반드시 다음을 남긴다.
   - 어떤 upstream failure를 우회했는지
   - 왜 이 우회가 이슈 본질과 무관한지
   - 어떤 방식으로 neutralize했는지
4. upstream failure가 이슈 본질 그 자체이면 우회하지 않고 그대로 검증한다.

## 예시

```json
{
  "manifest_version": "0.1",
  "project_key": "adcenter",
  "issue_key": "GEMINI-1787",
  "issue_title": "등록 화면 취소 시 2차 확인 팝업 필요",
  "jira_status": "To Do",
  "requirements": [
    {
      "requirement_id": "R1",
      "title": "dirty state 취소 확인 팝업",
      "statement": "등록 화면에서 변경사항이 있는 상태로 취소를 누르면 확인 팝업이 노출되어야 한다.",
      "requirement_type": "modal_flow",
      "source_priority": "jira_body",
      "sources": [
        {
          "source_type": "jira_body",
          "source_ref": "https://jira.gmarket.com/browse/GEMINI-1787",
          "excerpt_summary": "취소 버튼 클릭 시 2차 확인 팝업 필요",
          "confidence": "high",
          "is_primary": true
        }
      ],
      "evidence_sufficiency": "partial",
      "implementation_allowed": false,
      "needs_user_materials": true,
      "missing_evidence": [
        {
          "gap_type": "exact_text",
          "description": "확인 팝업의 정확한 문구가 없다.",
          "required_material": "Jira 코멘트 또는 시안의 alert 문구",
          "blocking": true
        }
      ],
      "notes": "alert 노출 자체는 확정 가능하지만 exact text는 추가 근거가 필요하다."
    }
  ]
}
```

## ATLS 사용 규칙

`ATLS`는 `issue requirement manifest`를 만들 때 아래 규칙을 따른다.

1. 근거가 부족한 requirement는 `pending_evidence`로 남긴다.
2. `needs_user_materials = true`이면 사용자에게 필요한 자료 목록을 출력한다.
3. source가 약한 requirement는 자동으로 `acceptance manifest`로 넘기지 않는다.
4. `partial` requirement는 실행 케이스를 만들더라도 "확정 검증"이 아니라 "탐색 검증"으로 표시한다.
5. `md` 출력에는 requirement별 `충분한 근거`, `부족한 근거`, `추가 필요 자료`를 표나 섹션으로 명확히 드러낸다.
6. 코멘트의 열거 조건이 있으면, 모든 항목이 requirement 후보로 반영되었는지 completeness 체크를 수행한다.
7. completeness 체크를 통과하지 못한 requirement set은 `완료`로 간주하지 않는다.
