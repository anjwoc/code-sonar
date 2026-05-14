# ATLS Bulk Worklog PRD

Author: Harness Engineering  
Status: Draft  
Target Product: `ATLS Dashboard`

## 문서 목적

이 문서는 `ATLS Dashboard`에 "현재 나에게 할당된 Jira 이슈를 기준으로 워크로그를 일괄 작성하는 메뉴"를 추가하기 위한 제품 요구사항을 정의한다.

이 기능의 핵심은 단순한 bulk submit이 아니라, 아래를 한 번에 처리하는 것이다.

- 현재 사용자에게 할당된 Jira 이슈를 대시보드에서 바로 선택한다.
- 날짜 범위와 근무시간을 입력한다.
- 점심시간 등 제외 시간대를 반영한다.
- 선택한 시간 단위(`30분`, `1시간`) 기준으로 전체 근무 가능 시간을 이슈들에 자동 분배한다.
- 실제 Jira worklog를 preview 후 일괄 생성한다.

## 배경

현재 Jira에서 워크로그를 작성하려면 이슈별로 진입해 시간을 직접 나눠 입력해야 한다. 이 방식은 아래 문제가 있다.

- 당일 처리한 이슈가 많을수록 입력 비용이 커진다.
- 하루 근무시간 전체를 기준으로 균등 분배하기 어렵다.
- 점심시간, 기존 등록된 worklog, 날짜 범위 분배를 사람이 직접 계산해야 한다.
- 여러 날짜에 걸친 worklog 분배를 반복 입력하는 과정에서 누락/중복/시간 초과가 발생하기 쉽다.

`ATLS Dashboard`는 이미 "오늘 내가 처리할 이슈를 Jira 기준으로 모아 보여주는" 역할을 하고 있으므로, worklog 작성도 같은 문맥 안에서 이어지는 것이 자연스럽다.

## 제품 목표

### 핵심 목표

1. 사용자는 `내게 할당된 Jira 이슈`를 한 화면에서 다중 선택할 수 있어야 한다.
2. 사용자는 날짜 범위와 근무시간 템플릿을 지정해 전체 시간을 자동 분배할 수 있어야 한다.
3. 점심시간 등 제외 시간대를 반영해 실제 기록 가능한 시간만 계산해야 한다.
4. 일괄 생성 전 `preview`에서 날짜별/이슈별 배치를 확인할 수 있어야 한다.
5. 실제 Jira worklog 생성 시 partial failure와 중복 위험을 명확히 보여줘야 한다.

### 성공 기준

- 사용자는 10개 이슈 기준 1분 내에 worklog preview를 생성할 수 있다.
- 사용자는 30개 이슈, 3일 범위 기준으로 수동 계산 없이 자동 분배 결과를 얻을 수 있다.
- 총 등록 worklog 시간이 사용자가 지정한 유효 근무시간 총합과 일치한다.
- 점심시간과 기존 등록 worklog 구간에 겹치는 배치가 기본값으로 발생하지 않는다.

## 비목표

- Jira 전체 time tracking 정책을 대체하는 범용 HR 시스템을 만들지 않는다.
- 이슈별 실제 작업량을 AI가 자동 추정하는 기능은 v1 범위에서 제외한다.
- drag-and-drop 캘린더 편집기는 v1 범위에서 제외한다.
- 팀원 간 공용 스케줄 동기화는 v1 범위에서 제외한다.

## 대상 사용자

### 1. 개발자

- 당일 처리한 여러 이슈에 대해 퇴근 전 worklog를 빠르게 정리한다.

### 2. QA / 운영 사용자

- 여러 이슈에 대해 날짜 범위를 지정해 반복 worklog를 배치한다.

### 3. 리드 / 매니저

- 팀원에게 일관된 worklog 작성 템플릿과 입력 규칙을 제공한다.

## 핵심 사용자 시나리오

### 시나리오 A. 오늘 할당 이슈 10개를 당일 근무시간에 자동 분배

- 사용자는 `Bulk Worklog` 메뉴에 진입한다.
- 기본 필터는 `assignee = currentUser()` 이다.
- 사용자는 오늘 처리한 Jira 10개를 체크한다.
- 날짜는 `오늘`, 근무시간은 `09:00~18:00`, 점심시간은 `12:00~13:00`, 시간 단위는 `30분`으로 둔다.
- 시스템은 총 8시간 = 16 슬롯을 계산한다.
- 10개 이슈에 대해 최소 1슬롯씩 배치하고, 남는 6슬롯을 선택 순서 기준으로 앞 이슈부터 추가 배치한다.
- 사용자는 preview를 확인하고 일괄 생성한다.

### 시나리오 B. Jira 30개를 4월 2일~4월 4일에 분산 입력

- 사용자는 Jira 30개를 선택한다.
- 날짜 범위는 `2026-04-02 ~ 2026-04-04`
- 근무시간은 `09:00~18:00`
- 점심시간은 `12:00~13:00`
- 시간 단위는 `30분`
- 시스템은 3일 x 8시간 = 24시간 = 48슬롯을 계산한다.
- 30개 이슈에 최소 1슬롯씩 우선 배치하고, 남는 18슬롯은 앞 이슈부터 추가 배치한다.
- 날짜별로 가능한 슬롯에 순차적으로 배치하고, 같은 이슈의 연속 슬롯은 1개 worklog entry로 합친다.

### 시나리오 C. 1시간 단위 설정 시 용량 부족

- 사용자는 Jira 10개를 선택한다.
- 날짜 범위는 1일, 근무시간은 8시간, 시간 단위는 `1시간`
- 총 슬롯은 8개인데 선택 이슈는 10개다.
- 시스템은 preview 생성 대신 `선택한 시간 단위 기준으로는 모든 이슈에 최소 1개 슬롯을 배정할 수 없습니다.` 오류를 보여준다.
- 사용자는 `30분`으로 바꾸거나 날짜 범위를 늘린다.

## 메뉴 / 정보 구조

### 신규 메뉴

`/dashboard/worklogs/bulk`

사이드바에 아래 순서로 노출한다.

- Overview
- Issues
- Projects
- `Bulk Worklog`
- Settings

### 왜 별도 메뉴인가

- 이 기능은 개별 이슈 상세의 부가 액션이 아니라, `여러 이슈를 한 번에 처리하는 작업 콘솔`이다.
- 이슈 선택, 일정 설정, preview, execution이 모두 필요하므로 전용 화면이 맞다.

## 기능 요구사항

## 1. 이슈 소스 패널

### 기본 동작

- 기본 JQL은 `assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC`
- 사용자는 현재 나에게 할당된 이슈를 리스트에서 확인한다.
- 이슈는 다중 선택 가능해야 한다.
- 이슈 리스트에는 최소 아래 정보가 보여야 한다.
  - issue key
  - summary
  - status
  - priority
  - updated
  - project

### 필터

- project
- status
- updated recency
- text search

### 선택 규칙

- 선택 순서는 유지되어야 한다.
- 분배 알고리즘의 기본 우선순위는 이 선택 순서를 따른다.
- 사용자는 정렬된 리스트와 별개로 `선택 순서 재정렬`을 할 수 있으면 좋지만, v1에서는 필수 아님.

## 2. 일정 설정 패널

사용자는 아래 항목을 입력하거나 템플릿으로 불러올 수 있어야 한다.

- 날짜 범위 시작일
- 날짜 범위 종료일
- 일 시작 시각
- 일 종료 시각
- 제외 시간대 목록
- 시간 단위
- 분배 방식

### 기본값

- 시작일: 오늘
- 종료일: 오늘
- 근무시간: `09:00~18:00`
- 제외 시간대: `12:00~13:00`
- 시간 단위: `30분`
- 분배 방식: `균등 분배`

### 시간 단위

v1 지원값:

- `30분`
- `1시간`

향후 확장 가능:

- `15분`
- `2시간`
- custom minute step

### 제외 시간대

v1에서는 하루 공통 반복 제외 구간을 지원한다.

예시:

- `12:00~13:00` 점심시간
- 필요 시 추가 break 등록 가능

## 3. 기존 worklog 반영

preview 계산 전에 시스템은 선택된 날짜 범위 내 현재 사용자 existing worklog를 조회해야 한다.

기본 정책:

- 이미 등록된 worklog 구간은 `occupied slot`으로 본다.
- 새 bulk worklog는 기존 구간과 겹치지 않게 계산한다.
- 겹침 때문에 총 용량이 부족하면 preview 단계에서 부족 시간을 알려준다.

표시 방식:

- `기존 등록 시간 3시간 30분`
- `신규 배치 가능 시간 20시간 30분`

## 4. 분배 알고리즘

### 4-1. 총 유효 근무시간 계산

각 날짜별 유효 근무시간은 아래로 계산한다.

`유효 근무시간 = (근무 종료 - 근무 시작) - 제외 시간대 합 - 기존 worklog 점유 시간`

예시:

- 근무시간: `09:00~18:00`
- 점심시간: `12:00~13:00`
- 기존 worklog: `15:00~16:00`
- 유효 근무시간: `9h - 1h - 1h = 7h`

### 4-2. 슬롯 생성

시간 단위에 따라 유효 근무시간을 슬롯으로 나눈다.

예시:

- 유효 근무시간 8시간
- 시간 단위 30분
- 총 슬롯 16개

### 4-3. 최소 배정 규칙

기본 분배 방식은 `균등 분배`다.

규칙:

1. 선택된 모든 이슈는 최소 1슬롯 이상 받아야 한다.
2. `총 슬롯 < 선택 이슈 수` 이면 preview를 만들지 않고 오류를 반환한다.
3. `총 슬롯 >= 선택 이슈 수` 이면 각 이슈에 1슬롯씩 우선 배정한다.
4. 남는 슬롯은 선택 순서 기준으로 앞에서부터 1슬롯씩 추가 배정한다.

### 4-4. 날짜 배치 규칙

배정된 슬롯 수를 기준으로 날짜 범위에 순서대로 채운다.

규칙:

1. 날짜는 오름차순으로 채운다.
2. 같은 날짜 안에서는 시간 오름차순으로 채운다.
3. 같은 이슈에 연속 배정된 슬롯은 하나의 worklog entry로 병합한다.
4. 같은 이슈가 하루를 넘겨 배정되면 날짜별로 별도 worklog entry를 만든다.

### 4-5. 예시 1

- 선택 이슈: 10개
- 날짜: 1일
- 근무시간: `09:00~18:00`
- 점심시간: `12:00~13:00`
- 단위: `30분`

계산:

- 총 슬롯 16개
- 최소 배정 10개
- 잔여 슬롯 6개
- 결과: 앞 6개 이슈는 1시간, 뒤 4개 이슈는 30분

### 4-6. 예시 2

- 선택 이슈: 30개
- 날짜: 3일
- 일 유효 근무시간: 8시간
- 단위: `30분`

계산:

- 총 슬롯 48개
- 최소 배정 30개
- 잔여 슬롯 18개
- 결과: 앞 18개 이슈는 1시간, 뒤 12개 이슈는 30분

### 4-7. 예시 3

- 선택 이슈: 10개
- 날짜: 1일
- 일 유효 근무시간: 8시간
- 단위: `1시간`

계산:

- 총 슬롯 8개
- 선택 이슈 10개
- 결과: preview 차단

오류 문구:

`선택한 시간 단위 기준으로는 모든 이슈에 최소 1개 슬롯을 배정할 수 없습니다. 시간 단위를 줄이거나 날짜 범위를 늘려 주세요.`

## 5. Preview 화면

실제 생성 전에 사용자는 아래 정보를 반드시 볼 수 있어야 한다.

- 총 선택 이슈 수
- 총 유효 근무시간
- 총 슬롯 수
- 이슈별 배정 시간
- 날짜별 시작/종료 시각
- 기존 worklog 충돌 여부
- 생성 예정 worklog entry 수

### Preview 레이아웃

상단 요약 카드:

- 선택 이슈 수
- 총 배정 시간
- 잔여 미배정 시간
- 기존 점유 시간

중앙 테이블:

- date
- start
- end
- issue key
- summary
- duration
- source rule (`equal_distribution`)

하단 검증:

- `총 배정 시간 = 총 유효 근무시간` 여부
- `모든 이슈 최소 1슬롯 충족` 여부
- `기존 worklog와 충돌 없음` 여부

## 6. 실행

사용자는 preview 이후에만 실제 생성할 수 있어야 한다.

실행 정책:

- 기본은 `draft preview -> confirm -> create`
- 일괄 생성 전 confirm dialog 필요
- 생성 단위는 Jira worklog API 호출이다
- partial failure가 나면 성공/실패 건을 분리해 보여준다

### Confirm 문구

`선택한 {N}개 이슈에 대해 총 {T}시간의 워크로그를 생성합니다. 계속하시겠습니까?`

## 7. 실행 결과

실행 후 아래 결과를 보여줘야 한다.

- 성공 건수
- 실패 건수
- 실패한 issue key 목록
- Jira 응답 메시지
- 생성된 worklog 링크

### 실패 정책

- 일부 이슈만 실패해도 성공 건은 유지한다.
- 결과 화면에서 실패 건만 다시 실행할 수 있어야 한다.
- 전체 rollback은 v1 비목표다.

## 8. 설정 저장

사용자는 근무시간 템플릿을 저장할 수 있어야 한다.

v1 저장 범위:

- 기본 근무 시작/종료 시각
- 기본 제외 시간대
- 기본 시간 단위

저장 위치:

- dashboard local config
- 향후 project-scoped or user-scoped storage로 확장 가능

## UX 요구사항

### 필수 UX 원칙

1. preview 없는 즉시 생성 금지
2. 날짜 범위/슬롯 부족은 실행 전에 차단
3. 기존 worklog 충돌은 기본적으로 자동 회피
4. 배정 규칙이 explainable 해야 함
5. 사용자는 "왜 이 이슈가 30분이고 왜 이 이슈가 1시간인지" 바로 이해할 수 있어야 함

### explainability

preview 각 row 또는 이슈 상세에는 아래 설명이 있어야 한다.

- `전체 16슬롯 중 균등 분배 규칙으로 1슬롯을 우선 배정했고, 잔여 6슬롯 분배 순서에 포함되어 추가 1슬롯이 배정되었습니다.`

## 정책 / 제약사항

### 날짜 범위

- 시작일은 종료일보다 늦을 수 없다.
- 날짜 범위가 너무 넓으면 성능 보호를 위해 상한이 필요하다.
- v1 권장 상한: 31일

### 슬롯 수

- 너무 많은 슬롯 생성 방지를 위해 preview 상한이 필요하다.
- v1 권장 상한: 500 worklog entries

### 이슈 선택 수

- v1 권장 상한: 200개

### 주말 / 휴일

v1 정책:

- 사용자가 날짜 범위에 포함시키면 주말도 계산 대상에 포함한다.
- 공휴일 자동 제외는 v1 비목표다.

향후 확장:

- 주말 제외 토글
- 국가별 공휴일 캘린더 연동

## API 요구사항

### 1. Assigned Issues 조회

`GET /api/worklogs/issues`

query:

- assignee=currentUser
- status
- project
- search

response:

- issue key
- summary
- status
- priority
- updated
- existing timeSpent summary

### 2. Existing Worklogs 조회

`POST /api/worklogs/existing`

body:

- date range
- user account id

response:

- date
- start
- end
- issue key
- duration minutes

### 3. Preview 생성

`POST /api/worklogs/bulk/preview`

body:

- selected issue keys
- date range
- daily schedule
- excluded windows
- slot size
- distribution mode

response:

- total available minutes
- total slots
- issue allocations
- worklog entries draft
- warnings
- blocking errors

### 4. 실제 생성

`POST /api/worklogs/bulk/execute`

body:

- preview id or preview payload hash
- worklog entries

response:

- success count
- failed count
- per issue result
- jira response payload

## 데이터 모델

### WorklogScheduleTemplate

- startTime
- endTime
- excludedWindows[]
- slotMinutes

### BulkWorklogPreview

- selectedIssueKeys[]
- dateRange
- totalAvailableMinutes
- totalSlots
- blockingErrors[]
- warnings[]
- issueAllocations[]
- draftEntries[]

### IssueAllocation

- issueKey
- allocatedMinutes
- allocatedSlots
- rationale

### DraftWorklogEntry

- issueKey
- workDate
- startAt
- endAt
- durationMinutes

## 권장 화면 구성

### 화면 1. Bulk Worklog Console

좌측:

- assignee issue list
- filter
- selection summary

우측:

- date range
- schedule template
- excluded windows
- slot size
- preview button

하단:

- preview result table
- create button

### 화면 2. Result Dialog or Result Page

- success/fail summary
- failed retry
- created links

## 보안 / 안전장치

- preview 결과와 execute 입력이 다르면 실행 차단
- 너무 오래된 preview는 실행 차단
- Jira 권한 부족 시 issue별 실패를 분리 표시
- 이미 동일 시간대에 동일 issue로 등록된 worklog가 있으면 duplicate warning 표시

## 분석 / 로그 요구사항

기능 사용성 개선을 위해 아래 이벤트를 수집한다.

- `bulk_worklog_issue_selected`
- `bulk_worklog_preview_requested`
- `bulk_worklog_preview_blocked`
- `bulk_worklog_execute_confirmed`
- `bulk_worklog_execute_succeeded`
- `bulk_worklog_execute_partial_failed`

## 수용 기준

### 기능 수용 기준

1. 사용자는 현재 assignee 기준 Jira 이슈를 다중 선택할 수 있다.
2. 사용자는 날짜 범위, 근무시간, 점심시간, 시간 단위를 설정할 수 있다.
3. 시스템은 전체 유효 근무시간을 계산해 균등 분배 preview를 생성한다.
4. 점심시간과 existing worklog는 자동 제외된다.
5. 슬롯 부족 시 실행 전에 차단된다.
6. preview 승인 후 Jira worklog가 일괄 생성된다.
7. partial failure 시 실패 목록과 이유가 보인다.

### UX 수용 기준

1. 사용자는 preview 없이 생성할 수 없다.
2. 사용자는 총 시간, 이슈별 시간, 날짜별 시간대를 동시에 볼 수 있다.
3. 사용자는 분배 규칙 설명을 화면에서 확인할 수 있다.

## 향후 확장

- `가중치 분배`: priority, status, manually assigned weight 기준 분배
- `issue당 최소 시간` 설정
- `주말 제외` 토글
- `공휴일 제외` 연동
- `팀 단위 일괄 작성`
- `CSV / markdown export`
- `undo helper` 또는 `delete created worklogs` 지원
- `일별 캘린더 drag edit`

## 오픈 질문

1. 기본 시간 단위는 `30분`으로 고정할지, 사용자별 마지막 선택을 기억할지?
2. 같은 이슈에 대해 하루 2개 이상의 분리 entry를 허용할지, 가능한 한 1개 contiguous entry로 강제할지?
3. Jira status가 `Done`이거나 `Resolved`인 이슈는 기본 리스트에서 제외만 할지, 선택 자체를 막을지?
4. existing worklog가 있는 경우 부족 시간만큼 자동으로 날짜 범위를 확장하는 옵션이 필요한지?
5. bulk worklog 결과를 dashboard 이력으로 남길지?
