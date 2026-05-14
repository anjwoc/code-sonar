# atls - Atlassian CLI (Jira & Confluence)

## 개념

`atls`는 AI 채팅 세션(Claude Code, ChatGPT 등)이 터미널에서 안정적으로 호출할 수 있도록 만든 범용 Atlassian CLI입니다.

핵심 목표는 세 가지입니다.

1. 자주 쓰는 Jira / Confluence 작업은 짧은 고수준 명령으로 바로 실행
2. 고수준 명령이 없더라도 `jira-api`, `wiki-api` raw 계층으로 전체 REST API 접근
3. 삭제는 반드시 interactive 확인을 거치고, AI 자동 삭제는 차단

```text
유저 → AI → atls → Jira/Confluence REST API
```

출력은 JSON, 오류는 stderr로 분리됩니다.

## 왜 Python인가

이 도구의 병목은 런타임보다 Atlassian API 네트워크 왕복 시간입니다.
그래서 현재 단계에서는 Node보다 Python이 충분하고, 기존 자산을 그대로 살리면서 빠르게 확장하기 좋습니다.

## 설치

```bash
python3 -m pip install -e /Users/jaecjeong/lab/memo/atsl
# 또는
alias atls='/Users/jaecjeong/lab/memo/atsl/bin/atls'
```

## 에이전트 첫 진입

컨텍스트가 없는 에이전트라면 먼저 아래 둘 중 하나를 실행하면 됩니다.

```bash
atls meta
atls doctor
atls ping all
atls workflow daily-review
atls workflow daily-review-detail
```

- `meta`: 기능 범위, 안전 규칙, 예시를 JSON으로 출력
- `doctor`: 현재 환경에서 실제 실행 가능한지 점검
- `ping`: DNS, TCP, HTTP, API 단계로 Jira/Confluence 연결 상태를 점검

## 결과 저장 규칙

`atls`의 Jira / Confluence 작업 결과는 자동으로 Markdown 파일로 저장됩니다.

- 기본 루트: `<ATLS_PACKAGE_ROOT>/.atls-data`
- Jira 결과: `<ATLS_PACKAGE_ROOT>/.atls-data/projects/shared/jira`
- Wiki 결과: `<ATLS_PACKAGE_ROOT>/.atls-data/projects/shared/wiki`
- 자동 결과: `<ATLS_PACKAGE_ROOT>/.atls-data/projects/shared/{jira|wiki}/auto_results/{YYYY-MM-DD}`
- 파일명 규칙: `{YYYY}_{MM}_{DD}_{task_name}.md`
- 예시: `2026_04_03_issue_search_unresolved.md`

같은 날 같은 태스크명이 이미 있으면 `_2`, `_3` 식으로 뒤에 번호가 붙습니다.

Markdown 내용은 같은 템플릿을 따릅니다.

- 실행 시각
- 프로파일
- 서비스 구분
- 실제 실행한 명령
- JSON 결과 원문

### 저장 루트 바꾸는 방법

우선순위는 아래 순서입니다.

1. 일회성: `atls --artifact-root /path ...`
2. 환경변수: `ATLS_ARTIFACT_ROOT=/path`
3. 워크스페이스별: `.atls.json` 에 `"artifact_root": "/path"`
4. 전역 프로파일: `~/.atls_config.json` 의 프로파일에 `"artifact_root": "/path"`

현재 이 저장소의 기본값은 아래처럼 맞춰져 있습니다.

```json
{
  "profile": "gmarket",
  "artifact_root": "/Users/jaecjeong/lab/memo/atls/.atls-data"
}
```

## 명령 구조

### Jira 고수준 명령

```bash
# 이슈
atls issue get GEMINI-1234
atls issue search "assignee=jaecjeong AND status='In Progress'" --max 50
atls issue create --project GEMINI --summary "로그인 오류" --description "..." --type Bug
atls issue update GEMINI-1234 --summary "제목 수정" --add-label qa
atls issue transitions GEMINI-1234
atls issue transition GEMINI-1234 --name "In Review"

# 워크로그
atls worklog list GEMINI-1234
atls worklog get GEMINI-1234 123456
atls worklog add GEMINI-1234 "QA 검토" 2h --started 2026-04-01T09:00:00.000+0900
atls worklog update GEMINI-1234 123456 --time 1h --comment "수정"

# 댓글
atls comment list GEMINI-1234
atls comment get GEMINI-1234 10001
atls comment add GEMINI-1234 "수정 완료했습니다"
atls comment update GEMINI-1234 10001 "내용 수정"

# 프로젝트 / 사용자
atls project list
atls project get GEMINI
atls user me
atls user search jaecjeong

# 연결 점검
atls ping jira
atls ping wiki
atls ping all --timeout 3

# daily workflow
atls workflow daily-review
atls workflow daily-review-detail
atls workflow qa-gemini-harness --no-jira --workspace-root /path/to/adcenter
atls workflow daily-review --max 200
atls workflow daily-review-detail --max 200
atls workflow daily-review --publish --page-id 543080607
atls workflow daily-review --publish
ATLS_DAILY_REVIEW_WIKI_PARENT_PAGE_ID=543086649 atls workflow daily-review --publish
```

## Daily Review 워크플로우 설정

`daily-review`는 위키 publish 기본값을 설정 파일이나 환경변수로 받을 수 있습니다.
`daily-review-detail`도 같은 구조로 별도 설정이 가능합니다.

현재 기본 예시는 아래처럼 저장할 수 있습니다.

```json
{
  "default_profile": "gmarket",
  "profiles": {
    "gmarket": {
      "workflows": {
        "daily_review": {
          "wiki_space": "~jaecjeong",
          "wiki_parent_page_id": "543086649",
          "wiki_title_template": "{date} Daily Review",
          "wiki_auto_publish": false,
          "wiki_parent_title": "Daily Review",
          "wiki_path_hint": "업무 > 2026 > Daily Review"
        },
        "daily_review_detail": {
          "wiki_space": "~jaecjeong",
          "wiki_parent_page_id": "543086649",
          "wiki_title_template": "{date} Daily Review Detail",
          "wiki_auto_publish": false,
          "wiki_parent_title": "Daily Review",
          "wiki_path_hint": "업무 > 2026 > Daily Review"
        }
      }
    }
  }
}
```

워크스페이스별로는 `.atls.json`에서도 같은 구조로 override할 수 있습니다.

```json
{
  "profile": "gmarket",
  "artifact_root": "/Users/jaecjeong/lab/memo/atls/.atls-data",
  "workflows": {
    "daily_review": {
      "wiki_parent_page_id": "543086649"
    },
    "daily_review_detail": {
      "wiki_parent_page_id": "543086649"
    }
  }
}
```

환경변수 override도 지원합니다.

```bash
export ATLS_DAILY_REVIEW_WIKI_SPACE="~jaecjeong"
export ATLS_DAILY_REVIEW_WIKI_PARENT_PAGE_ID="543086649"
export ATLS_DAILY_REVIEW_WIKI_TITLE_TEMPLATE="{date} Daily Review"
export ATLS_DAILY_REVIEW_WIKI_AUTO_PUBLISH="true"
export ATLS_DAILY_REVIEW_DETAIL_WIKI_TITLE_TEMPLATE="{date} Daily Review Detail"
```

이제 `atls workflow daily-review --publish`를 실행하면:

1. 설정된 parent page 아래에서 오늘 제목과 같은 문서를 먼저 찾습니다.
2. 있으면 update 합니다.
3. 없으면 child page로 create 합니다.

리포트 포맷도 강화되어, 영어 제목은 아래 형식으로 정리됩니다.

```text
[해석한 제목]
(원문)
```

각 이슈 아래에는 1~3줄 분석 문구와 다음 확인 포인트가 같이 들어갑니다.

추가로 `atls workflow daily-review-detail`은 생성일과 최근 업데이트 시각을 읽어:

1. `open_days`, `idle_days`, `stale_status`를 계산합니다.
2. `긴급 QA 진행`, `긴급 QA 착수 필요`, `장기 방치 백로그` 같은 attention 카테고리로 다시 묶습니다.
3. 이슈별로 문제 상황, 영향 범위, 진행 판단, 다음 액션을 정리한 디테일 리포트를 생성합니다.
4. 요약과 상세 결과물은 모두 `<ATLS_PACKAGE_ROOT>/.atls-data/projects/shared/jira/workflow/daily_review/{YYYY-MM-DD}` 아래에 저장합니다.
5. 날짜 폴더 안에는 기본적으로 `summary.md`, `summary.json`, `detailed_analysis.md`, `detailed_analysis.json` 네 파일이 갱신됩니다.

### Confluence 고수준 명령

```bash
atls wiki search --title "QA Status"
atls wiki search --text "신규광고센터"
atls wiki get 543080607
atls wiki children 543080607
atls wiki create "제목" "<h1>내용</h1>" --space ~jaecjeong --parent 123456
atls wiki update 543080607 "새 제목" "<h1>수정된 내용</h1>"
atls wiki append 543080607 "<p>추가 문단</p>"
```

### Raw API 계층

고수준 명령이 없는 기능도 raw 계층으로 처리할 수 있습니다.

```bash
# Jira Agile API 예시
atls jira-api GET /rest/agile/1.0/board

# Jira issue link 생성 예시
atls jira-api POST /issueLink --json '{"type":{"name":"Blocks"},"inwardIssue":{"key":"GEMINI-1"},"outwardIssue":{"key":"GEMINI-2"}}'

# Confluence raw 조회 예시
atls wiki-api GET /content/543080607/child/comment
```

### 에이전트용 규칙

```text
1. 먼저 atls meta 를 읽는다
2. 가능하면 high-level command 를 쓴다
3. 없으면 jira-api / wiki-api 로 내려간다
4. delete 는 비대화형에서 막히므로 사용자가 직접 확인해야 한다
```

## 삭제 정책

- `issue delete`
- `worklog delete`
- `comment delete`
- `wiki delete`
- `jira-api DELETE ...`
- `wiki-api DELETE ...`

위 삭제 명령은 모두 interactive 확인을 거칩니다.
TTY가 아닌 환경에서는 AI가 자동 삭제하지 못하도록 차단됩니다.

## 설정 우선순위

1. 환경변수: `ATLS_PROFILE`, `ATLS_JIRA_TOKEN`, `ATLS_CONFLUENCE_TOKEN` 등
2. `.atls.json` 현재 또는 상위 디렉토리
3. `~/.atls_config.json`

## 설정 관리

```bash
atls config show
atls config profiles
atls config add-profile antigravity
atls config set-default antigravity
atls config init-local antigravity
```

프로젝트 루트에 아래처럼 `.atls.json`을 두면 해당 워크스페이스에서 자동으로 프로파일이 선택됩니다.

```json
{
  "profile": "gmarket"
}
```

## AI 사용 원칙

AI는 다음 순서로 사용하면 가장 자연스럽습니다.

1. 가능한 한 고수준 명령부터 사용
2. 고수준 명령이 없으면 raw API 계층으로 이동
3. 삭제는 AI가 안내만 하고, 실제 확인은 사용자가 터미널에서 수행
