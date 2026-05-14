# ATLS Workflow Policy

## 목적

이 문서는 특정 이슈 하나를 임시로 해결하는 방법이 아니라, `ATLS`를 통해 반복 가능한 작업 방식을 어떻게 누적하고 재사용할지에 대한 정책을 정의한다.

핵심 원칙:

- 작업 방식은 항상 `ATLS` 내부 문서로 적립한다.
- 특정 케이스에만 맞춘 하드코딩보다, 다른 프로젝트와 이슈에도 재사용 가능한 규칙을 우선한다.
- Jira 본문, Jira 코멘트, 등록된 source 문서는 함께 판단한다.
- evidence는 최신 실행을 기본으로 보여주되, 이전 실행도 히스토리로 보존한다.
- issue 작업은 가능하면 `이슈 1개 = 커밋 1개`로 남긴다.

## 정책

### 1. Source Synthesis Policy

- Jira Description과 Recent Comments는 동등한 1급 source다.
- registered source document(`.md`)는 보조 source지만, requirement synthesis와 실행 계정 판단에 실제로 반영한다.
- source 간 차이가 있으면 자동으로 덮어쓰지 않고 `conflict`, `enrichment`, `review needed`로 드러낸다.
- 특정 QA 이슈의 comment 구조에만 의존하는 파서는 금지한다.
- 문맥 그룹화 규칙은 `배경 / AM / MM / 기타`처럼 일반화 가능한 패턴으로 구현한다.
- 코멘트에 번호 목록이나 bullet로 조건이 열거되어 있으면, **열거된 각 조건을 acceptance 조건 후보로 모두 보존**해야 한다.
- 번호 목록의 일부만 구현/검증하고 완료로 표시하는 것은 금지한다.
- `최초`, `클릭 후`, `이동 후`, `마지막`, `n번째` 같은 상태 전이 표현은 별도 단계 조건으로 유지한다.

### 2. Evidence Policy

- 이슈 재실행 시 기존 결과를 삭제하지 않는다.
- 최신 실행 결과는 `tests/results/issues/<ISSUE>`에 유지한다.
- 이전 실행 결과는 `tests/results/issues/<ISSUE>/history/<timestamp>`로 이동한다.
- dashboard는 최신 결과를 기본으로 보여주고, 이전 실행은 히스토리 아코디언으로 제공한다.
- video/screenshot 위에는 파일명만이 아니라 가능한 경우 테스트 케이스 설명을 먼저 노출한다.
- source review만으로 `이슈 아님`이 명확해진 경우에는 `source-reviewed resolved`로 분류하고, 억지 E2E를 만들지 않는다.
- 외부 URL, upstream API, 배포 일정 같은 의존성 때문에 실행이 불가능한 경우에는 `blocked by external dependency`로 분류하고, `Not Run`과 구분한다.

### 3. E2E Recording Policy

- issue 전용 E2E는 `tests/e2e/issues/<issue-key>.spec.ts`에 둔다.
- 녹화는 항상 `video: on`을 사용한다.
- 사용자 검토를 위한 영상은 각 동작 사이 `1초 pacing`을 기본으로 한다.
- screenshot 이름과 케이스 설명은 서로 매핑 가능해야 한다.

### 4. Issue Delivery Policy

- 실제 Jira 이슈 작업은 `fix: [ISSUE-KEY] 간단요약` 형식으로 커밋한다.
- dashboard/ATLS 플랫폼 기능 작업은 이슈 커밋과 분리한다.
- 하나의 커밋에 여러 Jira 이슈 구현을 섞지 않는다.
- 열거 조건이 있는 이슈는 `ATLS_REQUIREMENT_COMPLETENESS_CHECKLIST.md`를 통과하기 전까지 완료로 표시하지 않는다.
- E2E evidence가 일부 조건만 검증했다면 `부분 검증`으로 간주한다.

### 5. Dashboard Policy

- dashboard는 단순 결과 링크 모음이 아니라, source review, synthesis, evidence, 히스토리를 함께 보여줘야 한다.
- `Source Missing`, `Reanalysis Required`, `Synthesized Review` 같은 상태는 툴팁과 상세 설명으로 의미가 드러나야 한다.
- source 추가는 가능하면 프로젝트 설정 페이지 이동이 아니라 이슈 문맥 안에서 바로 수행할 수 있어야 한다.

### 6. Workflow / Worklog / Cloud Policy

- workflow run은 실행 시점의 `source rule snapshot`, `publish policy snapshot`, `jira post action snapshot`을 함께 보존해야 한다.
- rerun은 원래 run을 mutate 하지 않고 새 run attempt로 누적되어야 한다.
- worklog bulk preview는 deterministic 해야 하며, preview마다 signature를 남겨 stale 여부를 판정할 수 있어야 한다.
- preview와 execute 사이에 source issue 집합 또는 기존 worklog가 바뀌면 stale warning을 surfaced 해야 한다.
- cloud sync는 canonical local artifact를 대체하지 않고 delivery replica metadata로만 취급한다.
- cloud sync에는 `source path`, `target path`, `provider`, `syncedAt`, `result`, `retry count`가 남아야 한다.

## 구현 체크리스트

- source synthesis 결과가 특정 이슈 하드코딩이 아닌가
- 최신 실행과 이전 실행이 분리 저장되는가
- evidence UI에서 최신과 history가 모두 보이는가
- 테스트 케이스 설명이 media 위에 노출되는가
- 작업 방식 변화가 `ATLS` 문서로 남았는가
- 코멘트의 열거 조건이 acceptance case와 evidence에 전부 반영되었는가
- workflow run snapshot과 rerun lineage가 보존되는가
- worklog preview signature와 stale warning이 동작하는가
- cloud sync가 local-first replica metadata로 기록되는가

### 7. AI Step Session Policy

- `Codex OAuth connected`는 단순 UI 토글이 아니라 실제 local Codex CLI login 검증과 분리해서 다뤄야 한다.
- AI step session은 provider, model, prompt, workflow/step scope, realtime event log, final output을 session 단위로 남겨야 한다.
- local Codex CLI bridge가 준비된 경우 `codex exec --json` 로그를 realtime에 가깝게 surfaced 한다.
- bridge가 준비되지 않은 경우 blocked reason을 숨기지 않는다.

## 저장 규칙

- ATLS 산출물의 기본 저장 루트는 `ATLS package/.atls-data` 이다.
- 기본 구조는 아래를 따른다.
  - `projects/shared/jira/...`
  - `projects/shared/wiki/...`
  - `runtime/workflow-runs/...`
  - `runtime/worklogs/...`
  - `runtime/ai-sessions/...`
  - `replicas/cloud/...`
  - `system/locks/...`
- 예전 기본값인 `~/Documents/atls` 는 legacy 경로로 간주하고, 명시적 사용자 override가 없는 한 내부 루트로 정규화한다.
- local artifact가 canonical source 이고, cloud target은 delivery replica다.
