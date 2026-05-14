# ATLS Dashboard Read API Contract

## 목적

이 문서는 `/Users/jaecjeong/lab/memo/atsl/dashboard`가 `ATLS` 산출물을 읽기 위해 사용하는 read-only API 계약을 정의한다.

이 계약은 현재 mock 기반 dashboard를 real artifact 기반으로 치환하기 위한 1차 계약이다.

## 원칙

1. 이 API는 read-only다.
2. 상태 판단은 프론트가 아니라 `ATLS` 산출물과 loader가 수행한다.
3. 데이터가 없으면 추정값 대신 `missing`, `not_available`, `404`로 응답한다.
4. requirement source가 없으면 `missing_issue_requirement_manifest`를 그대로 드러낸다.

## 기본 엔드포인트

### `GET /api/projects`

프로젝트 목록과 최신 workflow run 정보를 반환한다.

응답 개요:

- `projects[]`
  - `key`
  - `name`
  - `latestRunDate`
  - `workflow`
  - `issueCount`
  - `blockedCount`
  - `testedCount`
  - `artifactRoot`
  - `workspaceRoot`

### `GET /api/projects/:projectKey/overview`

overview 카드와 차트에 필요한 집계 데이터를 반환한다.

응답 개요:

- `total`
- `blocked`
- `inProgress`
- `needsReview`
- `tested`
- `ready`
- `sufficiency`
- `testStatus`

### `GET /api/projects/:projectKey/issues`

issue queue용 목록을 반환한다.

응답 개요:

- `issues[]`
  - `key`
  - `title`
  - `track`
  - `jiraStatus`
  - `priority`
  - `assignee`
  - `requirementSufficiency`
  - `requirementSufficiencySource`
  - `acceptanceCoverage`
  - `latestTestStatus`
  - `latestTestStatusSource`
  - `readyForJiraUpdate`
  - `readyStatus`
  - `updatedAt`
  - `workflowBucket`

### `GET /api/projects/:projectKey/issues/:issueKey`

issue detail용 데이터를 반환한다.

응답 개요:

- issue queue 필드 전체
- `description`
- `recentComments`
- `issueUrl`
- `problem`
- `approach`
- `solution`
- `result`
- `validationPlan`
- `blockers`
- `touchpoints`
- `evidence`
- `workflowSteps`
- `currentStageIndex`
- `sourceRefs`

### `GET /api/projects/:projectKey/issues/:issueKey/workflow`

timeline 전용 workflow 단계 배열을 반환한다.

응답 개요:

- `issueKey`
- `workflow[]`
  - `stage`
  - `label`
  - `status`
  - `owner`
  - `blockerReason`
  - `requiredMaterials`
  - `latestComment`
  - `outputRefs`

### `GET /api/projects/:projectKey/issues/:issueKey/requirements`

issue requirement manifest 기반 requirement 목록을 반환한다.

응답 개요:

- `issueKey`
- `projectKey`
- `status`
  - `available`
  - `missing_issue_requirement_manifest`
- `source`
- `requirements[]`
- `gaps[]`

주의:

- 현재 issue별 requirement manifest가 없으면 빈 배열과 `missing_issue_requirement_manifest`가 내려간다.
- 이 상태는 오류가 아니라 "프론트에 표시되어야 하는 실제 부족 상태"다.

### `GET /api/projects/:projectKey/issues/:issueKey/acceptance`

acceptance manifest 기반 case 목록을 반환한다.

응답 개요:

- `issueKey`
- `projectKey`
- `status`
  - `available`
  - `missing`
- `manifestPath`
- `goal`
- `cases[]`

### `GET /api/projects/:projectKey/issues/:issueKey/evidence`

workspace 내 로컬 결과물 기반 evidence inventory를 반환한다.

응답 개요:

- `issueKey`
- `projectKey`
- `status`
  - `available`
  - `not_available`
- `resultDirectory`
- `reportPath`
- `videoCount`
- `screenshotCount`
- `videos[]`
- `screenshots[]`
- `reports[]`
- `notes[]`

주의:

- 현재는 file serving URL이 아니라 절대 경로 inventory를 반환한다.
- 실제 브라우저 재생용 URL serving은 다음 단계 계약이 필요하다.

### `GET /api/projects/:projectKey/settings/adapter`

project adapter 정보를 반환한다.

응답 개요:

- `projectKey`
- `sourcePath`
- `adapter`

## 현재 알려진 제한 사항

1. dashboard 프론트는 아직 이 read API를 사용하지 않는다.
2. issue requirement manifest 실데이터가 없어 requirements 화면은 아직 완전 연동 불가다.
3. evidence API는 inventory만 제공하며 정적 파일 serving은 아직 없다.
4. action API는 이번 계약 범위에 포함되지 않는다.
