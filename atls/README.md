# atls

AI-friendly Atlassian CLI for Jira and Confluence.

`atls`는 Jira / Confluence 작업을 AI 세션과 터미널에서 안정적으로 호출할 수 있게 만든 CLI다. 현재 구조는 팀 배포를 염두에 두고 `src` 기반 패키지 형태로 정리되어 있다.

## 구조

```text
atsl/
├── README.md
├── pyproject.toml
├── atls.py                  # 기존 절대경로 실행 호환 shim
├── bin/
│   └── atls                 # 로컬 실행 wrapper
├── src/
│   └── atls/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py           # 실제 CLI 구현
│       └── analysis/
│           └── harness.py   # QA/GEMINI harness 분석기
├── docs/
│   ├── design/
│   ├── guides/
│   └── reference/
└── scripts/
    └── legacy/              # 이전 단독 스크립트 보관
```

## 실행

```bash
python3 atls.py meta
python3 -m atls meta
./bin/atls meta
```

## 설치

로컬 개발:

```bash
python3 -m pip install -e .
```

팀 배포 전 검증:

```bash
python3 -m build
pipx install dist/*.whl
```

## 주요 명령

```bash
atls meta
atls doctor
atls workflow daily-review
atls workflow daily-review-detail
atls workflow qa-gemini-harness --workspace-root /path/to/adcenter
atls workflow project-task-flow --workspace-root /path/to/project
atls workflow project-detail-v2 --workspace-root /path/to/project
```

## 재사용 워크플로우 문서

다음 문서는 일회성 산출물이 아니라, 이후 다른 프로젝트에도 재사용할 수 있는 `ATLS` 워크플로우 설계를 기록한다.

- `docs/design/ATLS_E2E_HARNESS_WORKFLOW.md`
- `docs/design/ATLS_ISSUE_E2E_PLAYBOOK.md`
- `docs/design/ATLS_WORKFLOW_POLICY.md`
- `docs/design/ATLS_DASHBOARD_PRD.md`
- `docs/design/ATLS_WORKFLOW_BUILDER_PRD.md`
- `docs/design/ATLS_BULK_WORKLOG_PRD.md`
- `docs/design/ATLS_WORKFLOW_WORKLOG_CLOUD_PRD.md`
- `docs/design/ATLS_PROJECT_REGISTRY_PRD.md`
- `docs/design/ATLS_DASHBOARD_INTEGRATION_PROMPT.md`
- `docs/design/ATLS_DASHBOARD_INTEGRATION_PLAN.md`
- `docs/design/ATLS_NEW_FRONTEND_INTEGRATION_PROMPT.md`
- `docs/design/ATLS_NEW_FRONTEND_INTEGRATION_PLAN.md`
- `docs/reference/ACCEPTANCE_MANIFEST_SPEC.md`
- `docs/reference/ATLS_REQUIREMENT_COMPLETENESS_CHECKLIST.md`
- `docs/reference/ATLS_DASHBOARD_READ_API_CONTRACT.md`
- `docs/reference/ISSUE_REQUIREMENT_MANIFEST_SPEC.md`
- `docs/reference/NETWORK_STATE_ASSERTION_TEMPLATE.md`
- `docs/reference/PASS_FAIL_EVIDENCE_REPORT_SPEC.md`
- `docs/reference/PROJECT_ADAPTER_SPEC.md`
- `docs/reference/acceptance-manifest.example.json`
- `docs/reference/project-adapter.example.json`

## 배포 준비 체크리스트

- `pyproject.toml` 기반 빌드 가능
- `project.scripts.atls` 엔트리포인트 제공
- 루트 shim으로 기존 절대경로 사용 유지
- 문서/레거시 스크립트 역할 분리
