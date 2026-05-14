# ATLS Generic CLI Design

## 목표

`atls`를 AI가 장기적으로 재사용할 수 있는 범용 Atlassian CLI로 확장한다.

요구사항은 다음과 같다.

1. Jira / Confluence의 자주 쓰는 작업은 짧은 명령으로 제공한다.
2. 미구현 기능도 raw REST 계층으로 처리 가능해야 한다.
3. 출력은 항상 AI가 읽기 쉬운 JSON 중심으로 유지한다.
4. 삭제만 interactive 확인을 요구한다.
5. Jira / Confluence 작업 결과는 일관된 Markdown 규칙으로 저장한다.

## 설계 원칙

### 1. 두 계층 구조

고수준 명령:
- 사람이 읽고 AI가 쓰기 쉬운 안정된 인터페이스
- 자주 쓰는 업무 흐름을 짧게 감싼다
- 예: `issue search`, `worklog add`, `wiki append`

Raw API 계층:
- 고수준 명령이 아직 없는 API를 즉시 호출하는 탈출구
- 예: `jira-api GET /rest/agile/1.0/board`
- 범용성을 이 계층이 보장한다

### 2. 삭제 안전장치

삭제는 다음 규칙을 따른다.

- 전용 delete 명령은 삭제 전에 대상을 조회해서 요약을 보여준다
- raw DELETE도 가능한 경우 대상 정보를 조회하고, 아니면 경로/쿼리/페이로드를 보여준다
- TTY가 아니면 삭제는 차단한다

### 3. AI 친화 출력

출력 규칙:
- 성공 결과는 JSON
- 오류는 stderr
- URL, key, id, 상태, 담당자처럼 후속 작업에 필요한 식별자를 남긴다

### 4. 결과물 아카이빙

- 기본 루트는 `/Users/jaecjeong/Documents/atls`
- 서비스별 하위 폴더는 `jira/`, `wiki/`
- 파일명은 `{YYYY}_{MM}_{DD}_{task_name}.md`
- 예: `2026_04_03_issue_search_unresolved.md`
- 같은 이름이 이미 있으면 뒤에 `_2`, `_3`를 붙여 보존한다

## 명령 영역

### Jira

- `issue`
  - `get`
  - `mget`
  - `search`
  - `create`
  - `update`
  - `transitions`
  - `transition`
  - `delete`
- `worklog`
  - `list`
  - `get`
  - `add`
  - `update`
  - `delete`
- `comment`
  - `list`
  - `get`
  - `add`
  - `update`
  - `delete`
- `project`
  - `list`
  - `get`
- `user`
  - `me`
  - `search`
- `jira-api`
  - 모든 Jira REST / Agile REST endpoint 호출

### Confluence

- `wiki`
  - `search`
  - `get`
  - `create`
  - `update`
  - `append`
  - `children`
  - `delete`
- `wiki-api`
  - 모든 Confluence REST endpoint 호출

## 왜 Python 유지인가

이 도구의 실질 병목은 네트워크 I/O다.

- CLI startup 비용은 Atlassian API 왕복보다 훨씬 작다
- 현재 저장소 자산이 Python 기반이다
- JSON 처리와 shell 호출 안정성이 충분하다

즉, 지금 단계에서 Node로 갈아타는 이득은 크지 않다.
정말 더 낮은 startup latency가 중요해지는 시점이면 Node보다 Go/Rust가 더 강한 후보가 된다.

## 향후 확장 포인트

다음은 raw 계층 위에 차례로 올리기 좋은 고수준 명령들이다.

- Jira attachment add/download
- Jira issue link add/remove
- Jira watcher add/remove
- Jira board / sprint 명령
- Confluence comment 고수준 명령
- Confluence label / attachment 고수준 명령
- 배치 실행 명령
- 템플릿 기반 wiki 생성 명령

## 권장 사용 전략

1. AI는 먼저 고수준 명령으로 시도한다.
2. 기능이 없으면 `jira-api`, `wiki-api`로 바로 내려간다.
3. 반복 호출이 잦아지면 그때 raw 패턴을 고수준 명령으로 승격한다.

이 방식이면 CLI를 처음부터 과도하게 비대하게 만들지 않으면서도, 실제 가능 범위는 거의 전체 API로 넓힐 수 있다.
