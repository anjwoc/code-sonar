# sonar-config.md — Code-Sonar 실행 설정

> 정적 기본값만 둔다. 실행 여부와 범위는 매 실행 시 사용자 확인 또는 `.env` 값으로 결정한다.

## 1. 경로

| 설정 | 값 | 설명 |
|:---|:---|:---|
| `system_root` | `${SONAR_SYSTEM_ROOT}` | 산출물이 놓일 상위 작업 루트 |
| `target_dir` | `${SONAR_TARGET_DIR}` | 분석할 소스 루트 |
| `output_dir` | `${SONAR_OUTPUT_DIR}` | Markdown 산출물 루트 |

## 2. 분석 기본값

| 설정 | 값 | 설명 |
|:---|:---|:---|
| `language` | `ko` | 산출물 기본 언어 |
| `parallel` | `false` | 다중 프로젝트 순차 분석 권장 |
| `overwrite` | `confirm` | 기존 문서 덮어쓰기 전 확인 |
| `mcp_deep_scan` | `ask` | DB/GitHub MCP 심층 분석 여부는 실행 시 확인 |

## 3. Wiki Source Scan

| 설정 | 값 | 설명 |
|:---|:---|:---|
| `wiki_source_urls` | `${SONAR_WIKI_SOURCE_URLS}` | 분석 근거로 함께 읽을 Confluence page URL/ID 목록. 쉼표 구분 |
| `wiki_source_recursive` | `${SONAR_WIKI_SOURCE_RECURSIVE}` 또는 `true` | 지정 페이지의 child page를 재귀적으로 수집 |
| `wiki_source_max_depth` | `${SONAR_WIKI_SOURCE_MAX_DEPTH}` 또는 `3` | 재귀 수집 최대 깊이 |
| `wiki_source_output_dir` | `${SONAR_WIKI_SOURCE_OUTPUT_DIR}` 또는 `${SONAR_OUTPUT_DIR}/_wiki-sources` | 수집한 Wiki 원문/요약 캐시 위치 |
| `wiki_source_tool` | `atls` 우선, Confluence MCP fallback | 내부 Wiki는 `atls`로 접근 가능하면 우선 사용 |

Wiki source scan 규칙:

- Wiki 원문은 코드 분석의 보조 근거다. 현재 동작/구현 사실은 코드와 설정 파일 근거를 우선한다.
- 각 페이지는 title, page id, URL, version, parent, breadcrumb, 수집 시간을 함께 기록한다.
- 재귀 수집은 지정한 root page 밖으로 확장하지 않는다.
- 첨부파일/이미지는 사용자가 요청했거나 페이지 본문 이해에 필수일 때만 별도 근거로 기록한다.
- Wiki에서 확인한 비즈니스 용어, 정책, 설계 의도는 프로젝트 문서와 `_business/` 문서에 연결한다.
- Wiki와 코드가 충돌하면 확정 표현을 피하고 `> ⚠️ 확인 필요`와 양쪽 근거를 함께 남긴다.

## 4. 비즈니스 레벨 분석

| 설정 | 값 | 설명 |
|:---|:---|:---|
| `business_layer_output_dir` | `${SONAR_OUTPUT_DIR}/_business` | 업무 의사결정/예외 대응/운영 질문 문서 위치 |
| `business_workflow_doc` | `Business Workflow.md` | 업무 상태별 질문, 판정 조건, 책임, 운영 확인 위치 |
| `business_scenario_doc` | `Scenarios.md` | 운영/예외 중심 시나리오와 확인 순서 |
| `cross_project_trace_doc` | `Cross Project Traceability.md` | 업무 질문별 프로젝트/Wiki/코드/테이블/로그 추적 가이드 |

## 5. Evidence 검증

| 설정 | 값 | 설명 |
|:---|:---|:---|
| `evidence_output_dir` | `${SONAR_OUTPUT_DIR}/_evidence` | 근거 원장과 감사 리포트 위치 |
| `evidence_ledger_doc` | `Evidence Ledger.md` | 코드/Wiki/설정/DB/GitHub 근거 목록 |
| `evidence_audit_doc` | `Evidence Audit.md` | 근거 누락, 충돌, 추정 표현 점검 결과 |
| `min_evidence_level` | `source-or-wiki` | 주요 주장에는 code/config/wiki 중 하나 이상의 출처 필요 |

## 6. GitHub Source Scan

| 설정 | 값 | 설명 |
|:---|:---|:---|
| `github_enabled` | `${SONAR_GITHUB_ENABLED}` 또는 `false` | GitHub 근거 수집 여부 |
| `github_provider` | `${SONAR_GITHUB_PROVIDER}` 또는 `auto` | `mcp`, `gh`, `local-git`, `auto` |
| `github_host` | `${SONAR_GITHUB_HOST}` | GitHub Enterprise host. 예: `github.gmarket.com` |
| `github_repos` | `${SONAR_GITHUB_REPOS}` | 명시 repository URL 목록. 없으면 git remote에서 추론 |
| `github_max_pulls` | `${SONAR_GITHUB_MAX_PULLS}` 또는 `50` | 최근 PR 수집 상한 |
| `github_max_commits` | `${SONAR_GITHUB_MAX_COMMITS}` 또는 `200` | 최근 commit 수집 상한 |
| `github_output_dir` | `${SONAR_GITHUB_OUTPUT_DIR}` 또는 `${SONAR_OUTPUT_DIR}/_github` | GitHub 근거 캐시 위치 |
| `github_token_env` | `${SONAR_GITHUB_TOKEN_ENV}` 또는 `GITHUB_TOKEN` | token이 들어 있는 환경변수명. token 값은 문서화 금지 |

GitHub source scan 규칙:

- Provider는 `auto`일 때 GitHub MCP → `gh` CLI → local git 순서로 사용한다.
- private host/token 값은 산출물에 기록하지 않는다.
- GitHub 근거는 PR/commit/workflow/운영 이력의 보조 근거다. 현재 구현 동작은 코드와 설정 파일을 우선한다.
- GitHub와 코드가 충돌하면 코드 기준으로 쓰고 GitHub 항목은 변경 이력 또는 확인 필요로 표시한다.
- GitHub 근거는 `_github/`와 `_evidence/Evidence Ledger.md`에 `github:{repo}:{kind}:{id}` 형식으로 연결한다.

## 7. 그래프 규칙

| 항목 | 규칙 |
|:---|:---|
| System Index | 전체 통합 그래프 한 장 |
| 세부 문서 | sequence, event, storage, 업무 데이터플로우 그래프 분리 |
| 렌더러 | `SONAR_DIAGRAM_RENDERER` 값에 따라 Mermaid(기본) 또는 Excalidraw |
| Mermaid theme | `theme: "base"` + 밝은 파스텔 계층 색상 |
| Mermaid safety | API path/URL/슬래시/콜론 포함 노드 라벨 quote 처리 |
| Mermaid 금지 문법 | `graph TD/LR`, `A --> B & C`, `A & B --> C` |
| Excalidraw 출력 | `.excalidraw` 파일을 `SONAR_OUTPUT_DIR`에 저장, Markdown에서 `![[파일명.excalidraw]]`로 참조 |
| Excalidraw 라우팅 | `scripts/render-excalidraw-from-mermaid.js` 우선 사용, Arrow Type `직각`, port/rail routing, bbox 관통/라벨 겹침 0건, 저장소 edge 프로토콜별 색상 구분 |

### 7.5. Excalidraw 렌더러 설정

`SONAR_DIAGRAM_RENDERER=excalidraw`로 설정된 경우 아래 규칙을 따른다.

| 항목 | 값 | 설명 |
|:---|:---|:---|
| `diagram_renderer` | `${SONAR_DIAGRAM_RENDERER}` 또는 `mermaid` | `mermaid` 또는 `excalidraw` |
| MCP 도구 | `read_me`, `create_view` | excalidraw-mcp 서버 제공 |
| 출력 파일 | `{diagram-name}.excalidraw` | `SONAR_OUTPUT_DIR` 하위 해당 프로젝트 디렉터리에 저장 |
| Markdown 참조 | `![[{diagram-name}.excalidraw]]` | Obsidian Excalidraw 플러그인에서 렌더링 |

Excalidraw 렌더러 실행 순서:
1. System Index Mermaid 또는 아키텍처 모델(YAML)에서 컨테이너와 관계를 Excalidraw elements JSON으로 변환한다.
   - `rectangle` 노드: 시스템/서비스 컨테이너
   - `arrow` 엣지: 프로토콜/목적 레이블 포함
   - 레이어는 `frame` 요소로 그룹화
2. `scripts/render-excalidraw-from-mermaid.js`를 우선 사용해 port/rail routing과 QA를 적용한다.
3. 필요하면 `create_view` 도구를 호출해 elements JSON을 전달하고 인터랙티브 다이어그램을 렌더링한다.
4. 생성된 elements JSON을 `.excalidraw` 파일(Excalidraw JSON 포맷)로 `SONAR_OUTPUT_DIR` 내 해당 경로에 저장한다.
5. Markdown 문서의 Mermaid 블록 자리에 `![[{diagram-name}.excalidraw]]` 위키링크를 삽입한다.

> Excalidraw MCP 서버가 없을 경우 `mermaid` 렌더러로 자동 폴백한다.

## 8. 위키 발행

| 설정 | 값 | 설명 |
|:---|:---|:---|
| `wiki_space` | `ask` | Space Key는 args 또는 사용자 입력 |
| `wiki_parent_page_id` | `ask` | parent page id는 args 또는 사용자 입력 |
| `wiki_upload_format` | `markdown_macro` | Confluence markdown macro 사용 |
| `create_output_root_page` | `false` | `SONAR_OUTPUT_DIR` basename은 중간 페이지로 만들지 않음 |

## 9. 위키 페이지 제목

| 로컬 파일 | 위키 제목 |
|:---|:---|
| `_... Index.md` | `Index` |
| `_... System Index.md` | `Index` |
| `Index.md` | `Index` |
| 반복되는 세부 문서 | `{프로젝트명} - {파일명}` |
| `_business` 디렉터리 | `Business Analysis` |
| `_evidence` 디렉터리 | `Evidence` |

발행 제외:

| 로컬 디렉터리 | 이유 |
|:---|:---|
| `_wiki-sources` | 분석 근거 캐시. Wiki 발행 대상이 아님 |
| `_github` | 분석 근거 캐시. Wiki 발행 대상이 아님 |

## 10. 환경변수

| 환경변수 | 용도 |
|:---|:---|
| `SONAR_SYSTEM_ROOT` | 산출물 상위 루트 |
| `SONAR_TARGET_DIR` | 분석 대상 소스 루트 |
| `SONAR_OUTPUT_DIR` | Markdown 산출물 루트 |
| `SONAR_WIKI_SOURCE_URLS` | 분석에 함께 반영할 Confluence 원본 페이지 URL/ID 목록 |
| `SONAR_WIKI_SOURCE_RECURSIVE` | Wiki child page 재귀 수집 여부 |
| `SONAR_WIKI_SOURCE_MAX_DEPTH` | Wiki 재귀 수집 최대 깊이 |
| `SONAR_WIKI_SOURCE_OUTPUT_DIR` | Wiki 원문/요약 캐시 출력 위치 |
| `SONAR_GITHUB_ENABLED` | GitHub source scan 활성화 여부 |
| `SONAR_GITHUB_PROVIDER` | GitHub provider 선택: `auto`, `mcp`, `gh`, `local-git` |
| `SONAR_GITHUB_HOST` | GitHub Enterprise host |
| `SONAR_GITHUB_REPOS` | 명시 repository URL 목록 |
| `SONAR_GITHUB_MAX_PULLS` | PR 수집 상한 |
| `SONAR_GITHUB_MAX_COMMITS` | commit 수집 상한 |
| `SONAR_GITHUB_OUTPUT_DIR` | GitHub 근거 캐시 출력 위치 |
| `SONAR_GITHUB_TOKEN_ENV` | token이 들어 있는 환경변수명 |
| `SONAR_DIAGRAM_RENDERER` | 다이어그램 렌더러: `mermaid`(기본) 또는 `excalidraw` |
| `SONAR_TEAMS_WEBHOOK` | 선택적 Teams 알림 |
| `WIKI_URL` | REST fallback용 Confluence URL |
| `WIKI_TOKEN` | REST fallback용 Confluence token |

## 11. MCP

| MCP | 사용 목적 | 기본 |
|:---|:---|:---|
| GitHub | PR/commit/workflow/issue 근거 수집 | `SONAR_GITHUB_ENABLED`가 true면 사용 |
| DB/devdb | 테이블, SP, 의존성 확인 | 실행 시 확인 |
| Confluence/atls | Wiki source scan 및 위키 발행 | 가능하면 사용 |
| excalidraw-mcp | 아키텍처 다이어그램 렌더링 및 `.excalidraw` 파일 생성 | `SONAR_DIAGRAM_RENDERER=excalidraw`일 때 사용 |

## 12. 산출물 구조

```text
SONAR_OUTPUT_DIR/
├── _{시스템명} System Index.md
├── _wiki-sources/
│   ├── WIKI-SOURCE-INDEX.md
│   └── pages/
├── _github/
│   ├── GITHUB-SOURCE-INDEX.md
│   └── {repo}/
├── _business/
│   ├── Business Workflow.md
│   ├── Scenarios.md
│   └── Cross Project Traceability.md
├── _evidence/
│   ├── Evidence Ledger.md
│   └── Evidence Audit.md
├── {project-a}/
│   ├── _{project-a} Index.md
│   ├── Architecture & Dependencies.md
│   ├── Data Flow.md
│   └── ...
└── {project-b}/
    └── ...
```

## 13. 품질 기준

- 인덱스 문서와 세부 문서의 그래프 역할을 섞지 않는다.
- 코드에서 확인되지 않은 시스템, 테이블, 토픽은 확정 표현으로 쓰지 않는다.
- 주요 업무 흐름, API, 이벤트, 저장소, 정책 설명에는 Evidence Ledger의 근거 ID를 연결한다.
- Wiki 근거만 있고 코드 근거가 없는 구현 설명은 `설계/정책 근거`로 표기하고 구현 사실처럼 쓰지 않는다.
- GitHub 근거만 있고 코드 근거가 없는 구현 설명은 변경 이력/운영 맥락으로 표기하고 구현 사실처럼 쓰지 않는다.
- 위키 발행 후 대표 페이지에서 `ac:name=\"markdown\"`과 Mermaid fenced block을 확인한다.
