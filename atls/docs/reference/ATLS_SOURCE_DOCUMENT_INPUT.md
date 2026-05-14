# ATLS Source Document Input

## 목적

이 문서는 사용자가 `md` 문서를 source로 제공할 때 어떤 형태로 등록하면 되는지 정의한다.

## 권장 방식

가장 쉬운 방법은 대시보드에서 프로젝트별 `Source Documents`에 등록하는 것이다.

예:

- 프로젝트 설정 화면 이동
- `Source Documents` 섹션에서 `Add Source`
- 아래 항목 입력
  - `title`
  - `path`
  - `source_type`
  - `trust_level`
  - `notes`

## path 규칙

- 절대 경로를 권장한다.
- 예:
  - `/Users/jaecjeong/work/adcenter-workspace/adcenter/docs/prd/MMRegistration.md`
  - `/Users/jaecjeong/work/adcenter-workspace/adcenter/docs/qa/2026-04-02-manual-test-guide.md`

## source_type 권장값

- `prd`
  - 제품 요구사항의 기준 문서
- `qa_guide`
  - 테스트 가이드, 수동 검증 체크리스트
- `jira_note`
  - Jira 본문을 정리한 md, 코멘트 요약 md
- `openapi_note`
  - OpenAPI, request/response, payload 규칙 정리 md
- `figma_note`
  - Figma 화면/시안 설명 md
- `custom_md`
  - 위에 딱 맞지 않지만 source로 사용하려는 일반 md

## trust_level 가이드

- `1.0`
  - 최우선 기준. PRD 원문, 확정된 QA 체크리스트, 확정 API contract
- `0.8`
  - Jira 본문/코멘트 정리, 팀 합의 문서
- `0.6`
  - 실무 메모, 분석 문서, 임시 정리
- `0.3`
  - 참고용 메모. 단독 기준으로는 쓰지 않음

## notes 예시

- `exact alert 문구 기준`
- `payload field source of truth`
- `시안 캡처와 함께 확인 필요`
- `운영팀 확인 전까지 참고용`

## 사용 원칙

1. md 문서는 source가 될 수 있다.
2. 하지만 md 문서라고 해서 자동으로 신뢰되는 것은 아니다.
3. `source_type`과 `trust_level`을 함께 보고 requirement/source review에 반영한다.
4. exact 문구, payload, 상태 복원 규칙이 중요한 이슈는 notes에 기준을 명시한다.
5. 임시 메모 문서는 `custom_md` 또는 낮은 `trust_level`로 넣는 것이 안전하다.

## 현재 상태

- 대시보드에서 프로젝트별 source md 등록 가능
- 등록된 source 목록은 프로젝트 설정에 저장됨
- 이후 requirement/source review 단계에서 우선 참조 source로 활용 가능

주의:

- 현재는 "등록과 관리"까지 우선 지원한다.
- source md를 자동으로 재분류/재인덱싱하는 흐름은 다음 단계에서 연결한다.
