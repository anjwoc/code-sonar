# Code-Sonar

Code-Sonar는 여러 프로젝트의 소스코드, 설정, 위키, GitHub 변경 이력을 함께 읽어 아키텍처 문서와 운영 가능한 분석 문서를 생성하는 로컬 분석 플러그인이다. 결과물은 Markdown 파일 트리로 남기며, 필요하면 Confluence에 같은 구조로 발행한다.

Code-Sonar의 목표는 단순 요약이 아니다. 코드 근거가 있는 시스템 지도, 프로젝트별 상세 문서, 업무 판단 레이어, Evidence Audit를 함께 만들어 “이 시스템이 어떻게 생겼고, 왜 그렇게 동작하며, 문제가 생기면 어디부터 확인해야 하는지”를 문서화한다.

## 지원 환경

| 환경 | 사용 방식 | 주요 파일 |
| --- | --- | --- |
| Codex | Codex skill로 설치 후 `[$code-sonar]` 호출 | `.codex/skills/code-sonar/SKILL.md`, `scripts/install-codex.sh` |
| Claude Code | Claude plugin 설치 후 `/sonar:*` 명령 실행 | `.claude-plugin/plugin.json`, `.claude-plugin/commands/sonar/*.md`, `scripts/install-claude.sh` |
| Gemini/Qwen 호환 CLI | slash command 설정을 읽어 실행 | `commands/sonar/*.toml` |
| 공통 규칙 | 모든 환경이 같은 분석 계약을 공유 | `sonar/SONAR.md`, `sonar/config/sonar-config.md`, `sonar/skills/*`, `sonar/agents/*`, `sonar/templates/*` |

## 빠른 설치

### Codex

```bash
cd /path/to/code-sonar
./scripts/install-codex.sh
```

설치 후 새 Codex 세션을 열거나 skills를 다시 로드한다. 사용 예:

```text
[$code-sonar] 현재 .env 기준으로 프로젝트 분석을 실행하고 문서를 갱신해줘.
[$code-sonar] SONAR_OUTPUT_DIR 문서를 지정한 Wiki 상위 페이지에 업로드해줘.
[$code-sonar] Mermaid/Excalidraw 그래프 품질을 점검해줘.
```

설치 결과는 기본적으로 `$HOME/.codex/skills/code-sonar/SKILL.md`에 생성된다. `CODEX_HOME`을 사용 중이면 해당 경로 아래에 설치된다.

### Claude Code

```bash
cd /path/to/code-sonar
./scripts/install-claude.sh
```

설치 스크립트가 실패하면 아래 명령으로 수동 설치한다.

```bash
claude plugin install /path/to/code-sonar
```

대표 명령:

```text
/sonar:start
/sonar:multi-scan
/sonar:graph
/sonar:wiki
/sonar:wiki-batch
```

### Gemini/Qwen 호환 slash command

`commands/sonar/*.toml` 파일을 지원 CLI의 command/plugin 경로에 연결한다. 명령 이름은 다음과 같다.

```text
sonar:start
sonar:multi-scan
sonar:graph
sonar:wiki
sonar:wiki-batch
```

## 사전 조건

필수:

- Node.js: Excalidraw 렌더러와 검증 스크립트 실행
- Python 3: Wiki source scan 보조 스크립트 실행
- 로컬 분석 대상 소스코드

선택:

- `atls`: Confluence page 읽기/쓰기
- `gh`: GitHub MCP가 없을 때 GitHub 보조 근거 수집
- GitHub MCP: PR, commit, Actions, issue 근거 수집
- Obsidian Excalidraw plugin: `.excalidraw` 산출물 미리보기

## `.env` 설정

분석 대상과 출력 경로는 `.env`에 둔다.

```bash
SONAR_SYSTEM_ROOT=/Users/example/Documents/work
SONAR_TARGET_DIR=/Users/example/work/commerce-platform
SONAR_OUTPUT_DIR=/Users/example/Documents/work/commerce-analysis

# 선택: 설계/정책 Wiki를 분석 근거로 함께 수집
SONAR_WIKI_SOURCE_URLS=https://wiki.example.com/spaces/COM/pages/1000/Platform+Home
SONAR_WIKI_SOURCE_RECURSIVE=true
SONAR_WIKI_SOURCE_MAX_DEPTH=3
SONAR_WIKI_SOURCE_MAX_PAGES=100

# 선택: GitHub PR/commit/workflow 근거 수집
SONAR_GITHUB_ENABLED=false
SONAR_GITHUB_PROVIDER=auto
SONAR_GITHUB_HOST=github.example.com
SONAR_GITHUB_REPOS=https://github.example.com/org/commerce-api
SONAR_GITHUB_MAX_PULLS=50
SONAR_GITHUB_MAX_COMMITS=200
SONAR_GITHUB_TOKEN_ENV=GITHUB_TOKEN

# 선택: 다이어그램 렌더러
SONAR_DIAGRAM_RENDERER=mermaid
```

토큰과 비밀번호는 `.env`에 직접 쓰지 않는다. `SONAR_GITHUB_TOKEN_ENV`처럼 환경변수 이름만 넣고 실제 값은 쉘 환경에 둔다.

```bash
export GITHUB_TOKEN=redacted
```

## 실행 흐름

일반적인 실행 순서:

1. `.env`에서 `SONAR_TARGET_DIR`, `SONAR_OUTPUT_DIR`, `SONAR_SYSTEM_ROOT`를 읽는다.
2. `SONAR_WIKI_SOURCE_URLS`가 있으면 `_wiki-sources/`에 Wiki page와 child page를 수집한다.
3. `SONAR_GITHUB_ENABLED=true`이면 `_github/`에 PR, commit, workflow, CODEOWNERS 근거를 수집한다.
4. 프로젝트별 문서를 생성한다.
5. 전체 시스템 관점의 `System Index`를 생성한다.
6. `_business/`에 업무 판단/예외/추적 레이어를 생성한다.
7. `_evidence/`에 Evidence Ledger와 Evidence Audit를 생성한다.
8. QA reviewer가 Mermaid, Excalidraw, Wiki publish, Evidence 품질을 점검한다.
9. 요청이 있으면 `atls`로 Confluence에 발행한다.

## 생성되는 문서 구조

자세한 샘플은 [출력 트리 샘플](docs/samples/output-tree.md)을 참고한다.

```text
SONAR_OUTPUT_DIR/
├── Index.md
├── _business/
│   ├── Business Workflow.md
│   ├── Scenarios.md
│   └── Cross Project Traceability.md
├── _evidence/
│   ├── Evidence Ledger.md
│   └── Evidence Audit.md
├── _wiki-sources/
├── _github/
├── commerce-admin/
│   ├── Index.md
│   ├── Architecture & Dependencies.md
│   ├── Backend API.md
│   ├── Business Logic.md
│   └── Data Flow.md
└── commerce-api/
    ├── Index.md
    ├── Architecture & Dependencies.md
    ├── Backend API.md
    ├── Business Logic.md
    ├── Data Flow.md
    └── Database Schema.md
```

### 문서별 역할

| 문서 | 역할 |
| --- | --- |
| `Index.md` 또는 `_... System Index.md` | 전체 통합 구성도, 프로젝트 목록, 운영/서버 인벤토리 |
| `{project}/Index.md` | 프로젝트 요약, 주요 문서 링크, 핵심 책임 |
| `Architecture & Dependencies.md` | 모듈, 의존성, 외부 리소스, 런타임 관계 |
| `Backend API.md` | 엔드포인트, 요청/응답, 인증/권한, 호출자 |
| `Business Logic.md` | 핵심 정책, 알고리즘, 예외 처리 |
| `Data Flow.md` | sequenceDiagram, 업무 데이터플로우, 이벤트/저장소 흐름 |
| `Database Schema.md` | 테이블, 인덱스, 저장소 역할 |
| `_business/Business Workflow.md` | 업무 상태와 판정 조건 중심의 workflow |
| `_business/Scenarios.md` | 운영/예외 시나리오 |
| `_business/Cross Project Traceability.md` | 업무 질문별 추적 순서 |
| `_evidence/Evidence Ledger.md` | 주장과 근거 매핑 |
| `_evidence/Evidence Audit.md` | 근거 품질 감사 |

## 샘플 산출물

실제 산출물의 구조를 범용 도메인으로 치환한 샘플이다.

- [출력 트리](docs/samples/output-tree.md)
- [System Index](docs/samples/system-index.md)
- [프로젝트 Index](docs/samples/project-index.md)
- [Architecture & Dependencies](docs/samples/architecture.md)
- [Data Flow](docs/samples/data-flow.md)
- [Business Workflow](docs/samples/business-workflow.md)
- [Evidence Audit](docs/samples/evidence-audit.md)
- [Wiki 페이지 트리](docs/samples/wiki-tree.md)

## 다이어그램 정책

### Mermaid

- System Index에는 통합 `flowchart LR` 한 장을 둔다.
- 상세 시퀀스, 이벤트 처리, 저장소 의존성, 업무 데이터플로우는 프로젝트별 세부 문서에 둔다.
- Mermaid의 오래된 graph 선언과 fanout 축약 문법은 사용하지 않는다.
- API path, URL, 슬래시, 콜론이 들어간 노드 라벨은 quote 처리한다.
- 노드 라벨 안에서 Markdown list처럼 시작하는 문장을 쓰지 않는다.
- 라벨 줄바꿈은 `<br/>`를 사용한다.

### Excalidraw

Mermaid 기반 Excalidraw 재생성:

```bash
node scripts/render-excalidraw-from-mermaid.js --input "Index.md" --output "system-graph.excalidraw"
node scripts/render-excalidraw-from-mermaid.js --validate-only --output "system-graph.excalidraw"
```

품질 기준:

- 모든 arrow는 `elbowed: true`, `roundness: null`
- 대각선 segment 없음
- source/target 외 노드 bbox 관통 없음
- arrow label과 node bbox 겹침 없음
- Area 내부 padding과 node gap 유지
- node text는 rectangle에 binding되고 중앙 정렬
- 저장소 edge는 색상만이 아니라 rail, label 위치, label 배경으로 구분

기존 파일의 화살표만 교정:

```bash
node scripts/normalize-excalidraw-arrows.js path/to/file.excalidraw
```

## Wiki 업로드 정책

Confluence 업로드는 로컬 출력 트리를 그대로 반영한다. 샘플은 [Wiki 페이지 트리](docs/samples/wiki-tree.md)를 참고한다.

규칙:

- `SONAR_OUTPUT_DIR` 이름을 중간 Wiki page로 만들지 않는다.
- 출력 루트의 Markdown 파일과 프로젝트 디렉터리를 선택한 상위 page 바로 아래에 생성한다.
- `Index.md`, `_... Index.md`, `_... System Index.md`는 visible title을 `Index`로 올린다.
- 반복되는 상세 문서명은 `{project} - {document}` 형식으로 올린다.
- `_business`는 `Business Analysis`, `_evidence`는 `Evidence`로 올린다.
- `_wiki-sources`, `_github`는 발행하지 않는다.
- 디렉터리 page는 ToC-only로 작성한다.
- Markdown은 Confluence markdown macro로 올려 Mermaid fence를 보존한다.

`atls` 예:

```bash
atls wiki create "Index" --markdown-file "Index.md" --space "~user" --parent 1000
atls wiki update 1001 "commerce-api - Data Flow" --markdown-file "commerce-api/Data Flow.md"
```

## Wiki Source Scan

`SONAR_WIKI_SOURCE_URLS`를 설정하면 분석 전에 지정 Wiki page와 child page를 재귀 수집한다.

```bash
python3 scripts/scan-wiki-sources.py
```

수집 결과는 `_wiki-sources/`에 저장된다. Wiki는 설계 의도, 정책, 운영 맥락의 보조 근거로 사용하고, 구현 사실은 코드와 설정 파일을 우선한다.

## GitHub Source Scan

`SONAR_GITHUB_ENABLED=true`이면 GitHub 변경 이력과 운영 맥락을 함께 수집한다.

Provider 우선순위:

1. GitHub MCP
2. `gh` CLI
3. local git remote, commit, workflow 파일

GitHub MCP 예시:

```json
{
  "servers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e",
        "GITHUB_HOST",
        "-e",
        "GITHUB_TOOLSETS",
        "-e",
        "GITHUB_READ_ONLY",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}",
        "GITHUB_HOST": "https://github.example.com",
        "GITHUB_TOOLSETS": "repos,pull_requests,actions,issues",
        "GITHUB_READ_ONLY": "1"
      }
    }
  }
}
```

GitHub-only 근거는 구현 사실이 아니라 변경 이력/운영 맥락으로 표시한다.

## Business/Evidence 레이어

`_business`는 프로젝트 문서 요약이 아니다. 운영자와 기획자도 사용할 수 있는 업무 판단 레이어다.

- `Business Workflow.md`: 업무 질문, 판정 조건, 담당 프로젝트, 확인 근거, 운영 확인 위치
- `Scenarios.md`: Trigger, 증상, 확인 순서, 시스템 처리, 운영자 판단, 후속 조치
- `Cross Project Traceability.md`: 질문별 Wiki, 프로젝트 문서, 코드 근거, 테이블, 로그 확인 순서

`_evidence`는 문서의 주요 주장이 실제 근거를 갖는지 점검한다.

- code/config: 구현 사실
- wiki: 설계/정책/운영 맥락
- github: 변경 이력/운영 맥락
- inferred: 추론, 확정 표현 금지

## Troubleshooting

| 증상 | 확인할 것 | 조치 |
| --- | --- | --- |
| Mermaid가 코드 블록으로만 보임 | Confluence markdown macro 사용 여부 | `atls --markdown-file` 또는 markdown macro body 사용 |
| Mermaid parse error | 금지 문법, unquoted API path, fanout shorthand | `flowchart`와 quote label로 수정 |
| Excalidraw 선이 노드를 관통함 | 렌더러 QA 결과 | `render-excalidraw-from-mermaid.js --validate-only` 실행 |
| 디렉터리 page에 설명문이 들어감 | ToC-only 정책 위반 | directory page는 `# title`, `## Pages`, child links만 유지 |
| Wiki source가 발행됨 | 발행 제외 정책 위반 | `_wiki-sources`, `_github`는 publish 대상에서 제외 |
| Business layer가 기존 문서 요약처럼 보임 | Business independence QA | 업무 질문/판정/운영 확인 중심으로 재작성 |

## 개발자 검증 명령

```bash
bash -n scripts/install-codex.sh
bash -n scripts/install-claude.sh
node --check scripts/render-excalidraw-from-mermaid.js
node --check scripts/normalize-excalidraw-arrows.js
rg -n "docs/samples|install-codex|install-claude|SONAR_OUTPUT_DIR|SONAR_WIKI_SOURCE_URLS|SONAR_GITHUB_ENABLED" README.md docs
find docs/samples -type f | sort
```
