# ATLS Daily Triage Design

## 목표

`atls`를 이용해 매일 다음 작업을 자동화한다.

1. 대상 Jira 이슈를 수집한다.
2. 각 이슈의 상세 내용을 가져온다.
3. 규칙 기반 + AI 기반으로 이슈를 라벨링하고 분석한다.
4. Markdown 리포트와 구조화 JSON을 남긴다.
5. 최종 요약을 Confluence 위키에 저장하거나 업데이트한다.

이 기능은 단순 조회가 아니라 "daily review pipeline"이다.

## 왜 별도 daily 기능이 필요한가

현재 `atls`는 아래까지는 이미 잘한다.

- `issue search`: 리스트 수집
- `issue get` / `issue mget`: 상세 수집
- `comment list`: 최근 코멘트 수집
- `wiki create` / `wiki update`: 위키 반영
- 모든 결과의 Markdown 아카이빙

하지만 아직 없는 것은 아래다.

- 여러 이슈를 한 번에 "오늘 리뷰 대상"으로 묶는 orchestration
- 규칙 기반 분류
- 이슈별 분석 요약
- daily 전체 리포트 생성
- 위키 페이지 upsert 전략

## 권장 명령 구조

고수준 명령은 아래 4단계로 나누는 것이 좋다.

### 1. 수집

```bash
atls daily collect assigned-unresolved
```

역할:
- 기본 JQL 실행
- 이슈 키 목록 추출
- 상세 조회용 raw snapshot 생성

기본 JQL 예시:

```text
assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC
```

옵션 예시:

```bash
atls daily collect assigned-unresolved --max 200
atls daily collect qa-gemini --jql "assignee = currentUser() AND resolution = Unresolved AND (key ~ 'GEMINI-' OR project = QA)"
```

### 2. 분석

```bash
atls daily analyze assigned-unresolved
```

역할:
- collect 결과를 읽는다
- 각 이슈에 대해 상세 필드와 코멘트를 조합한다
- 규칙 기반 분류를 수행한다
- 필요 시 AI 요약/분류를 추가한다

### 3. 리포트 생성

```bash
atls daily report assigned-unresolved
```

역할:
- 분석 결과를 Markdown 리포트로 렌더링
- 상태별, 트랙별, 우선순위별로 묶음
- 위키 반영용 HTML 또는 storage body 생성

### 4. 위키 반영

```bash
atls daily publish assigned-unresolved --page-id 123456789
```

역할:
- report 결과를 Confluence storage format으로 변환
- 기존 페이지 업데이트 또는 새 페이지 생성

### 최종 통합 실행

```bash
atls daily run assigned-unresolved --publish --page-id 123456789
```

즉, 최종적으로는 아래 흐름이 된다.

```text
collect -> analyze -> report -> publish
```

## 데이터 수집 범위

### 최소 수집 필드

search 단계:
- key
- summary
- status
- assignee
- priority
- issuetype
- updated
- labels

detail 단계:
- description
- comment
- labels
- issuetype
- priority
- assignee
- status
- updated

추가 권장 필드:
- parent
- components
- fixVersions
- reporter
- created
- resolution
- resolutiondate

현재 `atls issue get` / `mget`의 필드 집합만으로도 1차 분석은 가능하지만,
daily 분석에서는 field 확장이 필요하다.

## 분류 체계

분류는 2단계로 나눈다.

### 1. 규칙 기반 분류

규칙 기반 분류는 항상 재현 가능해야 한다.

예시 필드:

- `track`
  - `gemini`
  - `qa`
  - `adcenter_ui`
  - `legacy_adcenter`
  - `ops`
  - `infra`
  - `other`

- `workflow_bucket`
  - `todo`
  - `active`
  - `review`
  - `blocked`
  - `done_like`

- `qa_bucket`
  - `qa_execution`
  - `qa_followup`
  - `prd_sync`
  - `ux_sync`
  - `bugfix`
  - `inquiry`

- `risk_level`
  - `high`
  - `medium`
  - `low`

- `action_needed`
  - `needs_dev`
  - `needs_qa_retest`
  - `needs_prd_confirmation`
  - `needs_ux_confirmation`
  - `needs_comment_followup`
  - `needs_schedule_check`

### 2. AI 기반 분석

AI 기반 분석은 규칙 기반 결과 위에 붙인다.

생성 필드 예시:

- `one_line_summary`
- `why_it_matters`
- `next_recommended_action`
- `confidence`
- `suspected_duplicates`
- `blocking_points`

중요한 점:
- 규칙 기반 분류는 deterministic
- AI 분석은 explainable summary
- 둘을 섞지 말고 별도 필드로 저장

## 규칙 예시

### track 분류

- key가 `GEMINI-*` 이면 `track=gemini`
- key가 `QA-*` 이면 `track=qa`
- key가 `ADCENTER-*` 이고 summary에 `[UI]` 포함 시 `track=adcenter_ui`
- summary에 `Old Adcenter` 포함 시 `track=legacy_adcenter`
- key가 `SYSCHECK-*` 이면 `track=ops`
- 그 외 `other`

### workflow_bucket 분류

- status in `To Do`, `Open` -> `todo`
- status in `In Progress` -> `active`
- status in `In Review` -> `review`
- status in `Blocked`, `On Hold` -> `blocked`

### action_needed 분류

- labels에 `PRD_Sync`, `PD_sync` -> `needs_prd_confirmation`
- labels에 `UX` -> `needs_ux_confirmation`
- summary 또는 issue_type이 `Bug` -> `needs_dev`
- summary에 `문의` -> `needs_comment_followup`

### QA 우선 분류

당신의 현재 사용 패턴을 기준으로 우선순위는 다음과 같이 보는 것이 좋다.

1. `track=gemini`
2. `track=qa`
3. `track=adcenter_ui`
4. 나머지

즉 daily 리포트 첫 섹션은 GEMINI, 두 번째는 QA, 세 번째는 기타 unresolved가 된다.

## 저장 산출물

기본 루트는 이미 정해져 있다.

```text
/Users/jaecjeong/Documents/atls
```

### Jira 쪽 권장 산출물

```text
/Users/jaecjeong/Documents/atls/jira/2026_04_03_daily_collect_assigned_unresolved.md
/Users/jaecjeong/Documents/atls/jira/2026_04_03_daily_analyze_assigned_unresolved.md
/Users/jaecjeong/Documents/atls/jira/2026_04_03_daily_report_assigned_unresolved.md
/Users/jaecjeong/Documents/atls/jira/2026_04_03_daily_report_assigned_unresolved.json
```

### Wiki 쪽 권장 산출물

```text
/Users/jaecjeong/Documents/atls/wiki/2026_04_03_daily_publish_assigned_unresolved.md
```

## 분석 데이터 스키마

권장 JSON 스키마 예시:

```json
{
  "date": "2026-04-03",
  "scope": "assigned-unresolved",
  "total": 124,
  "groups": {
    "gemini": {
      "total": 15,
      "status_counts": {
        "To Do": 8,
        "In Progress": 4,
        "In Review": 3
      }
    }
  },
  "issues": [
    {
      "key": "GEMINI-1803",
      "summary": "...",
      "status": "To Do",
      "priority": "Medium",
      "issue_type": "Bug",
      "labels": ["DEV"],
      "track": "gemini",
      "workflow_bucket": "todo",
      "risk_level": "medium",
      "action_needed": ["needs_dev"],
      "one_line_summary": "...",
      "next_recommended_action": "...",
      "analysis_basis": {
        "description_excerpt": "...",
        "recent_comment_excerpt": "..."
      }
    }
  ]
}
```

## 위키 저장 전략

최종 목적지는 개인 스페이스 또는 팀 QA 페이지가 된다.

### 권장 페이지 전략

옵션 A: 하루 1개 페이지
- 제목 예시: `Daily Jira Review 2026-04-03`
- 장점: 날짜별 아카이브가 명확

옵션 B: 월간 페이지에 일자 섹션 append
- 제목 예시: `Daily Jira Review 2026-04`
- 장점: 페이지 수가 적음

현재 사용 패턴상 옵션 A가 더 안정적이다.

### 페이지 본문 구조

1. 요약
- 총 unresolved 수
- GEMINI / QA / 기타 개수
- In Progress / In Review 우선 확인 항목

2. GEMINI
- 상태별 그룹
- 티켓별 1줄 분석

3. QA
- 상태별 그룹
- 재테스트 필요 항목 강조

4. 기타
- UI / 운영 / 레거시 묶음

5. 액션 아이템
- 오늘 바로 볼 티켓
- PRD/UX 확인 필요 티켓
- 리뷰 대기 티켓

## 구현 순서

### 1차

- `daily collect`
- `daily analyze`
- `daily report`
- `daily publish`

### 2차

- AI 기반 요약 추가
- 위키 page upsert
- 중복 티켓 묶기
- comment 기반 blocker 감지

### 3차

- 스케줄러 연동
- 특정 시간 자동 실행
- daily diff: 어제 대비 신규/상태변경/종료 표시

## 가장 중요한 설계 포인트

이 기능은 단순히 "이슈를 읽어주는 기능"이 아니라 아래여야 한다.

1. collect는 raw snapshot을 남긴다
2. analyze는 재현 가능한 structured JSON을 만든다
3. report는 사람이 읽기 좋게 만든다
4. publish는 위키를 최신 상태로 유지한다

즉 source of truth는 항상 Jira raw snapshot과 analyzed JSON이고,
Markdown과 Wiki는 그 위에 올라가는 view 계층으로 보는 것이 맞다.

## 권장 다음 작업

다음 구현은 아래 순서가 가장 좋다.

1. `atls daily collect`
2. `atls daily analyze`
3. `atls daily report`
4. `atls daily publish`

지금 상태에서는 바로 1차 구현에 들어갈 수 있다.
