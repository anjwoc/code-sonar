# ATLS PDLC Jira Issue Collection Process

Author: Harness Engineering  
Status: Draft  
Target Product: `ATLS`  
Policy Source: `PDLC 플랫폼 - Tools`

## 문서 목적

이 문서는 ATLS가 회사 기준 PDLC 정책에 맞춰 Jira 이슈를 조회하고, 이후 Summary 작성, Acceptance Case 생성, 테스트 실행, 리소스 해석까지 이어질 수 있도록 표준 조회 프로세스를 정의한다.

핵심 목표는 아래와 같다.

- 사용자가 짧은 Jira/JQL 조건만 입력해도 PDLC 기준에 맞는 조회 집합을 만들 수 있어야 한다.
- 실제 실행 공수가 발생하는 표준 이슈와 상위 계층 이슈를 구분해서 다뤄야 한다.
- ATLS는 단순 이슈 나열이 아니라 Summary, 계획 수립, 테스트, 리포트 작성까지 이어지는 워크플로우를 위한 데이터 셋을 생성해야 한다.
- 리소스/배분 관점이 필요한 경우 PDLC의 Allocation 규칙과 동일한 해석을 따라야 한다.

## 배경

PDLC 문서 기준으로 회사 내 Jira 데이터는 단순 키 목록이 아니라 계층 구조와 공수 해석 규칙을 함께 고려해야 한다.

- Story, Task, Bug는 실제 실행 단위다.
- Epic, Initiative, Battle은 상위 맥락을 제공하는 참조 계층이다.
- 짧은 JQL만으로는 상위 컨텍스트가 빠질 수 있다.
- 반대로 상위 이슈를 직접 분석 대상으로 포함하면 공수 중복이나 노이즈가 발생할 수 있다.
- 필수 필드가 비어 있는 이슈나 상태 전환 정책 위반 이슈는 별도 추적 대상이 될 수 있다.

따라서 ATLS는 PDLC 정책을 반영한 별도 조회 프로세스를 가져야 한다.

## 적용 범위

이 문서는 아래 ATLS 기능에 공통 적용된다.

- Daily Review용 이슈 수집
- Summary 생성용 이슈 수집
- Harness Engineering 기반 테스트 대상 수집
- Acceptance Case 생성 대상 수집
- 프로젝트/팀 리소스 분석용 이슈 수집
- 필수 필드 누락 이슈 추적

## 핵심 원칙

### 1. 조회의 시작점은 표준 이슈다

ATLS의 기본 조회 기준은 실제 실행 단위인 표준 이슈다.

- 포함 기본 대상: `Story`, `Task`, `Bug`
- 제외 기본 대상: `Epic`, `Initiative`, `Battle`, `Sub-task`

상위 이슈는 조회 결과에 포함될 수 있지만, 시작 조건은 항상 표준 이슈를 기준으로 잡는다.

### 2. 상위 계층은 자동 확장한다

사용자가 상위 계층 추적용 JQL을 직접 작성하게 두지 않는다.

ATLS는 사용자가 입력한 기본 JQL을 바탕으로:

1. 표준 이슈만 남기도록 정제
2. Epic 자동 확장
3. Initiative / Battle 자동 확장

순서로 내부 변환한 뒤 Jira에 질의한다.

### 3. 조회와 공수 계산의 대상은 다를 수 있다

ATLS는 조회 결과에 상위 이슈를 포함할 수 있지만, 리소스/공수 계산은 표준 이슈 기준으로만 수행한다.

- 조회 데이터셋: 표준 이슈 + 상위 계층 컨텍스트
- 공수 계산 데이터셋: 표준 이슈만

### 4. 회사 정책 위반 이슈는 별도 프로세스로 분리한다

필수 필드 미입력, 완료 상태인데 worklog 없음 같은 이슈는 일반 업무 요약과 분리해서 추적한다.

## 데이터셋 종류

ATLS는 조회 목적에 따라 아래 세 가지 데이터셋을 구분해서 사용한다.

### A. Workflow Dataset

Summary, Task Plan, Acceptance Case, Test 후보를 만들기 위한 데이터셋이다.

- 기본 대상: 표준 이슈
- 상위 Epic / Initiative / Battle은 문맥 연결용으로 포함
- 가장 일반적인 ATLS 기본 모드

### B. Resource Dataset

월간/기간별 plan, actual, allocation 해석이 필요한 데이터셋이다.

- 표준 이슈 기준으로 계산
- 상위 계층 키는 grouping 용도로만 유지
- 배분 규칙은 PDLC Allocation 규칙을 따른다

### C. Policy Audit Dataset

필수 필드 누락, 상태 전환 정책 위반, 운영상 누락을 잡아내기 위한 데이터셋이다.

- Initiative 하위 이슈 여부
- Target start / Target end / Original estimate / Worklog 여부
- Assignee 존재 여부

## ATLS 입력 모델

ATLS는 PDLC 기준 조회 메뉴에서 아래 입력을 지원해야 한다.

- Jira project
- Jira assignee
- Jira group or membersOf
- issue key or key list
- created / updated / resolved 기간
- resolution 여부
- status
- priority
- label
- component
- text search
- raw JQL
- strict hierarchy 여부
- 필수 필드 감사 모드 여부
- resource mode 여부

## 조회 모드 정의

### 1. Standard Workflow Mode

일반적인 Summary / Harness / Daily Review용 기본 모드다.

입력 예:

- `assignee = currentUser()`
- `project = "PAYMENT"`
- `status != Done`

ATLS는 이 입력을 받아 표준 이슈 기반으로 계층 확장된 결과를 반환한다.

### 2. Team Resource Mode

팀/조직 단위 리소스 분석용 모드다.

입력 예:

- `assignee in membersOf("Payment Engineering") AND resolution is EMPTY`
- `created >= 2026-01-01`

ATLS는 이 데이터를 plan / actual 계산용으로 분기한다.

### 3. Initiative Strict Mode

Initiative 하위에 속한 이슈만 보고 싶은 경우 사용한다.

이 모드에서는 Initiative 미연결 이슈를 결과에서 제외한다.

### 4. Missing Fields Audit Mode

PDLC 필수 필드 누락 이슈를 추적하는 모드다.

이 모드에서는 일반 업무 조회가 아니라 정책 감시용 JQL을 우선 적용한다.

## JQL 처리 규칙

### 1단계. 사용자 입력 수집

ATLS는 아래 둘 중 하나를 입력으로 받는다.

- 구조화된 필터 입력
- raw JQL 입력

구조화된 필터와 raw JQL이 동시에 있으면, 구조화 필터를 JQL로 만든 뒤 raw JQL과 `AND` 결합한다.

### 2단계. 기본 필터 강제

Workflow Dataset / Resource Dataset에서는 아래 기본 필터를 자동 적용한다.

- `issuetype in standardIssueTypes()`
- `issuetype != Epic`

의도:

- 실행 공수가 없는 중간 계층을 시작점에서 제거
- Story, Task, Bug 중심의 안정적인 조회 집합 유지

### 3단계. 상위 계층 자동 확장

ATLS는 사용자의 JQL을 내부적으로 아래 개념으로 확장해야 한다.

- base issues
- epics of base issues
- portfolio parents of epics

정책:

- 사용자가 `epicsOf`, `portfolioParentsOf`, `bottomUpPortfolio`를 직접 작성하지 않게 한다
- ATLS가 자동으로 래핑한다

### 4단계. strict mode 처리

Initiative까지 연결된 이슈만 보고 싶다면 strict mode를 사용한다.

strict mode에서는:

- Initiative 없는 Epic 하위 이슈 제외
- 상위 계층 없는 단독 표준 이슈 제외

### 5단계. 정규화

JQL 문자열은 내부 변환 전에 정규화한다.

- 작은따옴표 / 큰따옴표 정리
- 함수 중첩 시 escape 정리
- 공백 정리

## 권장 조회 패턴

### 개인 기본 조회

- `assignee = currentUser()`

용도:

- 내 할당 이슈 Summary
- 내 Daily Review
- 내 Acceptance Case 후보

### 팀 조회

- `assignee in membersOf("Payment Engineering") AND resolution is EMPTY`

용도:

- 팀 단위 병목 확인
- 팀 요약 리포트
- 미완료 이슈 집합 분석

### 프로젝트 조회

- `project = "PAYMENT"`
- `"Epic Link" = SELLER-3365`

용도:

- 특정 프로젝트 진행 상황 요약
- 하위 이슈 기반 테스트/리뷰 대상 수집

### Initiative / Battle 조회

- Initiative 하위: strict portfolio mode
- Battle 하위: portfolio children 기반 조회 후 하위 실행 이슈 확장

용도:

- PM/PMO 관점의 상위 과제 분석

## 결과 데이터 모델

ATLS의 PDLC 조회 결과는 최소 아래 필드를 가져야 한다.

- key
- summary
- issueType
- status
- priority
- assignee
- reporter
- project
- created
- updated
- resolved
- originalEstimate
- timeSpent
- targetStart
- targetEnd
- epicKey
- initiativeKey
- battleKey
- parentKey
- labels
- components

## 결과 분류 규칙

### Execution Issues

실제 워크플로우 대상으로 쓰는 이슈다.

- Story
- Task
- Bug

### Context Issues

문맥 연결용 상위 이슈다.

- Epic
- Initiative
- Battle

### Policy Findings

필드 누락이나 상태 정책 위반으로 분류된 이슈다.

## 리소스 해석 규칙

ATLS가 PDLC 기준 리소스/배분 값을 해석할 때는 아래를 따른다.

### 핵심 기준

- `8시간 = 1일`을 기본값으로 사용
- 토요일/일요일은 제외
- 공휴일은 별도 휴일 파일 또는 기본 휴일 데이터 기준으로 제외
- 시간은 시작 시점부터 영업일 순차 배분

### Plan 해석

- 기준 필드: `Original Estimate`
- 시작일: `Target start`

### Actual 해석

- 기준 필드: 개별 `Worklog`
- 시작일: `Date started`

### 공수 계산 제외 대상

- Epic
- Initiative
- Battle

상위 이슈는 리소스 계산의 직접 대상이 아니라, grouping key로만 사용한다.

## 누락 필드 / 상태 정책

ATLS는 아래 정책을 조회 프로세스의 별도 audit 단계로 지원해야 한다.

### 누락 필드 대상

- `Target start` 없음
- `Target end` 없음
- `Original estimate` 없음
- 완료 또는 resolution 있음에도 `timespent` 없음
- `assignee` 없음인 경우는 별도 분류

### 상태 정책

- `To Do -> In Progress` 전환 전:
  - Target start
  - Target end
  - Original estimate
  가 채워져 있어야 한다
- `In Progress -> Done` 전환 전:
  - 최소 1분 이상의 worklog가 있어야 한다

### ATLS 활용 방식

ATLS는 이 정책을 직접 Jira 워크플로우에 강제하지 않더라도:

- 누락 이슈 보고서 생성
- 팀/프로젝트별 누락 현황 요약
- Summary에 정책 위험 항목 별도 표기

를 지원해야 한다.

## ATLS 워크플로우 단계별 적용 방식

### 1. Issue Collection

입력:

- 사용자 필터
- 프로젝트 필터
- 기간 필터
- raw JQL
- strict mode 여부

출력:

- execution issues
- context issues
- policy findings

### 2. Summary Inclusion

Summary에는 execution issues만 직접 요약 대상으로 사용한다.

상위 이슈는 아래 용도로만 사용한다.

- Initiative / Epic별 grouping
- 배경 설명
- 전략 과제 연결

### 3. Task Planning

Task Plan 생성 시 우선순위는 아래 순서를 따른다.

1. 표준 이슈 상태
2. assignee
3. priority
4. target date
5. 상위 Initiative / Battle 맥락

### 4. Acceptance Case Generation

Acceptance Case는 표준 이슈 단위로 생성한다.

단, Epic / Initiative에서 정책이나 요구사항 문맥이 중요하면 상위 이슈 summary를 참고 정보로 포함한다.

### 5. Test Candidate Selection

테스트 후보는 아래 조건을 우선 고려한다.

- Story / Task / Bug
- 최근 업데이트됨
- 상태가 완료 직전이거나 리뷰 직전임
- 정책상 필수 필드가 채워져 있음

### 6. Evidence / Report

결과 리포트에는 아래를 같이 담을 수 있어야 한다.

- 조회 JQL
- 자동 변환된 최종 JQL
- execution issue 수
- context issue 수
- policy finding 수
- assignee / project / initiative 기준 분포

## ATLS 메뉴 요구사항

ATLS에서 PDLC 기준 조회를 위한 메뉴는 최소 아래 옵션을 제공해야 한다.

### Query Builder

- project
- assignee
- membersOf group
- status
- resolution
- priority
- created range
- updated range
- label
- component
- key / key list
- text contains
- raw JQL

### Policy Options

- `표준 이슈만 시작점으로 강제`
- `상위 계층 자동 확장`
- `Initiative strict mode`
- `누락 필드 audit 포함`
- `리소스 계산 모드`

### Debug Options

- 사용자 입력 JQL 보기
- 정규화 후 JQL 보기
- 최종 전송 JQL 보기

## 기본값 제안

ATLS 기본 모드는 아래를 권장한다.

- mode: `Standard Workflow Mode`
- assignee: `currentUser()`
- resolution: `EMPTY`
- hierarchy expansion: `ON`
- strict mode: `OFF`
- policy audit: `OFF`

팀/조직 리포트는 템플릿으로 분리한다.

## 출력 아티팩트

ATLS는 PDLC 기준 조회 결과를 아래 형태로 저장할 수 있어야 한다.

- `summary.md`
- `summary.json`
- `issue_manifest.json`
- `policy_findings.md`
- `allocation_summary.md`
- `query_debug.json`

## 실패 처리 원칙

### 1. JQL 문법 오류

- 정규화 전/후 JQL을 같이 표시
- 어떤 단계에서 오류가 났는지 보여준다

### 2. 상위 계층 확장 실패

- base issues만으로 fallback 가능
- 단, context incomplete 경고를 남긴다

### 3. 리소스 필드 누락

- 조회는 유지
- allocation 계산은 해당 항목을 warning 처리

## 수용 기준

1. 사용자는 짧은 JQL만 입력해도 PDLC 기준의 계층 확장 결과를 얻을 수 있다.
2. ATLS는 표준 이슈와 상위 이슈를 구분해서 저장할 수 있다.
3. 리소스 계산 시 상위 이슈가 직접 공수 계산에 포함되지 않는다.
4. strict mode에서는 Initiative 미연결 이슈가 제외된다.
5. 필수 필드 누락 이슈를 별도 audit 결과로 분리할 수 있다.
6. Summary/Task Plan/Acceptance/Test 단계가 동일한 조회 결과를 기반으로 이어질 수 있다.
7. 사용자는 최종 전송된 JQL과 변환 과정을 확인할 수 있다.

## 향후 확장

- 조직/본부 단위 템플릿 프리셋
- 누락 필드 자동 알림 워크플로우
- status transition 정책 위반 예측
- Jira filter 저장 및 재사용
- PDLC 프로젝트군별 기본 JQL 템플릿
- allocation 결과를 ATLS Dashboard에서 직접 시각화

