# ATLS Issue E2E Playbook

## 목적

이 문서는 `task_plans.md`에서 선택한 Jira 이슈를 실제 구현, E2E 검증, 스크린샷/영상 리포트까지 연결하는 반복 가능한 실행 절차를 정리한다.

이 문서는 범용 규칙을 담고, 프로젝트별 실제 실행 경로와 명령은 각 프로젝트 문서에 둔다.

## 어디에 저장할지

- 범용 워크플로우: `ATLS`
  - 예: `/Users/jaecjeong/lab/memo/atsl/docs/design/ATLS_ISSUE_E2E_PLAYBOOK.md`
- 프로젝트별 실행 문서: 프로젝트 저장소
  - 예: `adcenter/tests/e2e/README.md`
  - 예: `adcenter/tests/e2e/issues/README.md`
  - 예: `adcenter/tests/results/issues/<JIRA-KEY>/REPORT.md`

정리하면:

- `ATLS`는 방법론과 표준 구조를 저장하는 곳
- 프로젝트 저장소는 실제 spec, artifact, 실행 명령을 저장하는 곳

## 표준 흐름

1. `task_plans.md`에서 이슈 1건을 고른다.
2. Jira 본문, 코멘트, 현재 상태를 확인해 acceptance case를 확정한다.
3. 관련 화면 코드를 수정한다.
4. 이슈 전용 E2E spec을 만든다.
5. 스크린샷과 video가 남도록 실행한다.
6. `REPORT.md`에 결과와 수동 확인 포인트를 남긴다.
7. 다음 이슈는 별도 spec과 별도 report로 반복한다.

## 파일 구조

- spec: `tests/e2e/issues/<jira-key>.spec.ts`
- 스크린샷: `tests/results/issues/<JIRA-KEY>/`
- 이슈 리포트: `tests/results/issues/<JIRA-KEY>/REPORT.md`
- video/trace: `tests/results/artifacts/`

## 실행 규칙

- 이슈는 반드시 개별 실행 가능해야 한다.
- 여러 이슈를 동시에 수정해도 검증은 개별 spec으로 분리한다.
- 리뷰용 영상은 너무 빨리 지나가지 않도록 주요 동작마다 기본 `1초` pause를 둔다.
- 커밋은 `태스크 1개 = 커밋 1개`를 기본 원칙으로 한다.
- 공통 인프라 변경이 필요해도, 가능하면 `공통 준비 커밋`과 `이슈 구현 커밋`을 분리한다.
- 이렇게 하면 특정 이슈만 되돌리거나 제외 커밋을 정리하기 쉬워진다.

## Source Missing vs Blocked

- `Source Missing`
  - 요구사항 source가 부족해서 pass/fail 기준을 확정할 수 없는 상태다.
  - 예: Jira 제목만 있고 exact 문구, PRD, 코멘트, 시안이 없음
- `Blocked`
  - 요구사항은 충분하지만 테스트 실행이 막힌 상태다.
  - 예: VPN, 세션, 외부 API 장애, 테스트 계정 문제

규칙:

- `Source Missing`이면 자료를 더 받기 전까지 테스트를 억지로 만들지 않는다.
- `Blocked`이면 실행 경로를 복구하거나, 이슈 본질과 무관한 upstream failure는 neutralize해서 검증한다.

## Upstream Failure 처리 원칙

- 등록 API 일부 장애처럼 이슈 본질과 무관한 상위 실패가 있으면, 성공 경로를 가정한 하네스/인터셉트 검증을 허용한다.
- 예:
  - payload 분리 이슈 → 실제 등록 성공까지 기다리지 않고 submit payload만 캡처
  - 실패 메시지 매핑 이슈 → backend duplicate 응답만 재현해서 UI 매핑 확인
- 단, 아래는 문서/리포트에 반드시 남긴다.
  - 어떤 upstream을 우회했는지
  - 왜 이슈 본질과 무관한지
  - 어떤 방식으로 neutralize했는지

## 권장 pause 구간

- 초기 화면 진입 직후
- 확인 팝업 노출 직후
- 분기 버튼 클릭 직전 또는 직후
- 최종 결과 화면 도달 직후

## 다음에 어떻게 쓰는지

1. `task_plans.md`를 열고 다음 이슈를 하나 고른다.
2. 현재 `REPORT.md`를 참고해 어떤 형식으로 남겼는지 확인한다.
3. 새 spec을 `tests/e2e/issues/<jira-key>.spec.ts`로 만든다.
4. 아래 형식으로 실행한다.

```bash
pnpm test -- tests/e2e/issues/<jira-key>.spec.ts --project="E2E Tests"
```

5. 실행 후 결과물을 아래 위치에서 확인한다.

- `tests/results/issues/<JIRA-KEY>/`
- `tests/results/artifacts/`

6. `REPORT.md`에 아래 항목을 채운다.

- 요구조건
- 자동 검증 결과
- 스크린샷 경로
- video 경로
- 수동 확인 체크포인트

7. 커밋은 이슈별로 따로 남긴다.

```bash
git commit -m "fix: [GEMINI-1787] 등록 취소 확인 팝업 추가"
```

권장 규칙:

- `fix: [티켓번호] 초간단 요약`
- 한 커밋에 여러 Jira 이슈를 섞지 않는다.
- 다음 태스크로 넘어가기 전에 현재 태스크를 먼저 커밋한다.

## adcenter 기준 현재 예시

- 이슈: `GEMINI-1787`
- spec: `/Users/jaecjeong/work/adcenter-workspace/adcenter/tests/e2e/issues/gemini-1787.spec.ts`
- report: `/Users/jaecjeong/work/adcenter-workspace/adcenter/tests/results/issues/GEMINI-1787/REPORT.md`
