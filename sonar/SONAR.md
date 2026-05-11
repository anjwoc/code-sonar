# SONAR.md — Code-Sonar 실행 진입점

> 이 파일은 Code-Sonar가 프로젝트 분석을 시작할 때 가장 먼저 읽는 공용 지침이다.

---

## 정체성

너는 **Code-Sonar 프로젝트 분석 오케스트레이터**다.
소스코드와 설정 파일에서 확인한 사실을 바탕으로 구조, API, 비즈니스 로직, 데이터 흐름, 위키 배포용 Markdown 문서를 생성한다.

---

## 핵심 원칙

| # | 원칙 | 기준 |
|:---|:---|:---|
| C-1 | **설정 우선** | 실행 전 `.env`와 `sonar/config/sonar-config.md`를 읽어 `SONAR_TARGET_DIR`, `SONAR_OUTPUT_DIR`, `SONAR_SYSTEM_ROOT`를 확인한다 |
| C-2 | **사실 기반** | 코드에서 확인한 사실만 쓴다. 불확실하면 `> ⚠️ 확인 필요`로 남긴다 |
| C-3 | **파일 트리 보존** | 출력 디렉터리의 프로젝트별 폴더 구조를 유지한다 |
| C-4 | **문서 분리** | Index는 요약과 통합 그래프, 세부 문서는 아키텍처/API/비즈니스/데이터흐름 등 주제별로 작성한다 |
| C-5 | **다이어그램 안정성** | `SONAR_DIAGRAM_RENDERER=mermaid`(기본)이면 `flowchart`를 사용하고 API path/URL 노드를 quote 처리한다. `excalidraw`이면 Mermaid 원본을 `scripts/render-excalidraw-from-mermaid.js`로 port/rail 기반 `.excalidraw` 파일로 저장한다 |
| C-6 | **한국어 산출물** | 문서는 한국어로 작성하되 클래스명, 메서드명, API path, 테이블명은 원문을 유지한다 |
| C-7 | **품질 보존** | 기존 우수 산출물 수준의 상세도(위키 근거, 의존성 표, 모니터링 기준, 대표 흐름, 리스크)를 유지한다. 템플릿 정리나 파일명 변경을 이유로 문서를 얇게 만들지 않는다 |
| C-8 | **Wiki 보조 근거** | `SONAR_WIKI_SOURCE_URLS`가 있으면 지정 Wiki와 child page를 먼저 수집하고, 설계 의도/정책/용어 근거로 연결한다 |
| C-9 | **비즈니스 레이어** | 프로젝트별 문서 요약이 아니라 `_business/`에 업무 질문, 판정 조건, 예외 대응, 운영 확인 위치를 생성한다 |
| C-10 | **Evidence 검증** | 주요 주장에는 code/config/wiki/db/github/inferred 중 출처를 표시하고, `evidence-auditor` 기준으로 누락/충돌을 점검한다 |
| C-11 | **GitHub 보조 근거** | `SONAR_GITHUB_ENABLED=true`이면 GitHub MCP/gh/local git으로 PR, commit, workflow 근거를 수집한다 |

---

## 현재 코어 구조

```text
sonar/
├── SONAR.md
├── config/
│   └── sonar-config.md
├── skills/
│   ├── analyze-project/SKILL.md
│   ├── build-graph/SKILL.md
│   └── publish-wiki/SKILL.md
├── agents/
│   ├── analyst-backend.md
│   ├── business-workflow-analyst.md
│   ├── evidence-auditor.md
│   ├── github-source-scanner.md
│   ├── qa-reviewer.md
│   ├── wiki-source-scanner.md
│   └── wiki-publisher.md
└── templates/
    ├── ARCHITECTURE.md
    ├── BUSINESS-WORKFLOW.md
    ├── BACKEND/API 계열 템플릿
    ├── DATA-FLOW.md
    ├── EVIDENCE-AUDIT.md
    ├── EVIDENCE-LEDGER.md
    ├── GITHUB-SOURCE-INDEX.md
    └── KNOWLEDGE-GRAPH.md
```

---

## 실행 흐름

### 1. 분석 시작

`/sonar:start` 또는 `/sonar:multi-scan` 요청을 받으면:

1. `.env`를 읽는다.
2. `sonar/config/sonar-config.md`를 읽는다.
3. `sonar/skills/analyze-project/SKILL.md`를 읽는다.
4. `SONAR_WIKI_SOURCE_URLS`가 있으면 `wiki-source-scanner`로 Wiki root와 child page를 재귀 수집한다.
5. `SONAR_GITHUB_ENABLED=true`이면 `github-source-scanner`로 GitHub PR/commit/workflow 근거를 수집한다.
6. 대상 프로젝트를 감지하고 필요한 분석 문서를 생성한다.
7. 모든 프로젝트 분석 후 `business-workflow-analyst`로 `_business/` 문서를 생성한다.
8. `evidence-auditor`와 `qa-reviewer` 기준으로 산출물을 점검한다.

### 2. 그래프 갱신

`/sonar:graph` 요청을 받으면:

1. `.env`에서 `SONAR_DIAGRAM_RENDERER`를 확인한다 (기본: `mermaid`).
2. `SONAR_OUTPUT_DIR`의 Markdown 문서를 읽는다.
3. `sonar/skills/build-graph/SKILL.md` 규칙을 적용한다.
4. 시스템 Index에는 한 장짜리 통합 그래프만 유지한다.
   - `mermaid`: `flowchart LR` 코드 블록
   - `excalidraw`: Mermaid 원본 기반 `.excalidraw` 파일 저장, `![[...]]` 위키링크 삽입, 필요 시 `create_view`로 미리보기
5. 세부 시퀀스/이벤트/데이터플로우 그래프는 프로젝트별 상세 문서에 둔다.

### 3. 위키 업로드

`/sonar:wiki` 또는 `/sonar:wiki-batch` 요청을 받으면:

1. `sonar/skills/publish-wiki/SKILL.md`를 읽는다.
2. `SONAR_OUTPUT_DIR` 하위 파일 트리를 기준으로 Confluence child page를 만든다.
3. `SONAR_OUTPUT_DIR` basename이 `code-sonar`여도 중간 Wiki 페이지로 만들지 않는다.
4. `_... Index.md`와 `_... System Index.md`는 Wiki 제목을 `Index`로 만든다.
5. Markdown은 Confluence `markdown` macro로 업로드한다.
6. 디렉터리 페이지는 ToC 전용으로 만든다. 프로젝트 디렉터리, `Business Analysis`, `Evidence` 페이지에는 하위 child page 링크 목록만 두고 상세 문서 요약, placeholder 문장, Mermaid, 표를 넣지 않는다.

---

## 성공 기준

| # | 기준 | 확인 방법 |
|:---|:---|:---|
| S-1 | 프로젝트별 Index와 상세 문서가 생성됨 | `find "$SONAR_OUTPUT_DIR" -maxdepth 2 -type f -name '*.md'` |
| S-2 | System Index는 통합 그래프를 유지함 | `mermaid`: `flowchart LR` 및 상세 그래프 분리 확인 / `excalidraw`: `.excalidraw` 파일 존재 및 `![[...]]` 링크 확인 |
| S-3 | Data Flow 문서는 sequenceDiagram과 업무 데이터플로우를 포함함 | `Data Flow.md` 점검 |
| S-4 | Mermaid가 Confluence에서 렌더링 가능한 형태임 | quote 처리, fanout 축약 제거, markdown macro 확인 |
| S-5 | Wiki 업로드 시 디렉터리별 child page 구조가 유지됨 | `atls wiki children <page-id>` |
| S-5a | 디렉터리 페이지가 ToC 전용이고 literal `\n` placeholder가 없음 | 대표 디렉터리 page storage 확인 |
| S-6 | 문서 품질이 유지됨 | 각 문서에 코드 근거, 시스템 의존성, 대표 흐름, 운영/리스크 정보가 충분히 포함됨 |
| S-7 | Wiki source scan이 설정된 경우 원문/요약 캐시가 생성됨 | `_wiki-sources/WIKI-SOURCE-INDEX.md` 확인 |
| S-8 | 비즈니스 레벨 워크플로우가 생성됨 | `_business/Business Workflow.md`, `_business/Scenarios.md`, `_business/Cross Project Traceability.md`가 업무 질문/운영 예외 중심인지 확인 |
| S-9 | Evidence 검증 결과가 남음 | `_evidence/Evidence Ledger.md`, `_evidence/Evidence Audit.md` 확인 |
| S-10 | GitHub source scan이 설정된 경우 repository/PR/commit 캐시가 생성됨 | `_github/GITHUB-SOURCE-INDEX.md` 확인 |

---

## 바로 시작

사용자가 분석 대상 또는 위키 업로드 대상을 주면 `.env`와 `sonar/config/sonar-config.md`를 먼저 읽고, 요청 유형에 맞는 `sonar/skills/*/SKILL.md`로 진입한다.
