# Analyze Project Skill

이 스킬은 타겟 레거시 프로젝트의 코드를 스캔하고, 환경/MCP 설정에 따라 도메인별 서브에이전트를 스폰하여 **구조 분석 문서**와 **데이터플로우·비즈니스플로우 문서**를 자동 생성하는 메인 파이프라인입니다.

## 1. 사전 조건 (Prerequisites)
- `sonar/config/sonar-config.md` 로드 완료 및 설정값 확인
  - **`system_root`**, **`output_dir`**, **`target_dir`** 경로 변수를 파싱합니다.
  - `output_dir` 내부의 `{system_root}`는 실제 경로로 치환합니다.

## 2. 작업 흐름 (Workflow)

### STEP 0: 대상 프로젝트 자동 감지 및 매핑
`target_dir` 하위의 폴더 구조를 분석합니다.
- **다중 프로젝트:** 내부에 여러 디렉토리가 있다면, 각각을 독립적인 프로젝트로 간주하고 순차적으로 스캔을 예약합니다.
- **단일 프로젝트:** 해당 경로 자체가 단일 프로젝트의 루트(`package.json` 또는 `build.gradle` 존재)라면 1개만 분석합니다.
- 각 프로젝트별로 `output_dir`의 `{프로젝트명}` 변수를 치환하여 최종 출력 대상 디렉토리를 확정합니다.

### STEP 0.5: Wiki Source Scan 레이어
`.env`에 `SONAR_WIKI_SOURCE_URLS`가 설정되어 있으면 코드 분석 전에 Wiki 원문을 근거로 수집합니다.

**담당 에이전트:** `sonar/agents/wiki-source-scanner.md`

**입력:**
- `SONAR_WIKI_SOURCE_URLS`: 쉼표로 구분된 Confluence page URL 또는 page id
- `SONAR_WIKI_SOURCE_RECURSIVE`: 기본 `true`
- `SONAR_WIKI_SOURCE_MAX_DEPTH`: 기본 `3`
- `SONAR_WIKI_SOURCE_OUTPUT_DIR`: 기본 `${SONAR_OUTPUT_DIR}/_wiki-sources`

**처리 규칙:**
- `atls`로 접근 가능하면 우선 사용하고, 실패 시 Confluence MCP 또는 REST fallback을 사용합니다.
- root page와 child page를 재귀 수집하되 지정 root 밖으로 확장하지 않습니다.
- 페이지별 title, page id, URL, version, parent, breadcrumb, 수집 시각을 저장합니다.
- Wiki 내용은 구현 사실의 최종 근거가 아니라 설계 의도, 정책, 용어, 운영 맥락의 보조 근거로 사용합니다.
- 코드와 Wiki가 충돌하면 확정 표현을 피하고 양쪽 근거를 함께 남깁니다.

**출력:**
- `_wiki-sources/WIKI-SOURCE-INDEX.md`
- `_wiki-sources/pages/{page-id}-{slug}.md`
- `_evidence/Evidence Ledger.md`에 `wiki:{page-id}` 근거 항목 추가

### STEP 0.6: GitHub Source Scan 레이어
`.env`에 `SONAR_GITHUB_ENABLED=true`가 설정되어 있으면 GitHub 근거를 수집합니다.

**담당 에이전트:** `sonar/agents/github-source-scanner.md`

**입력:**
- `SONAR_GITHUB_PROVIDER`: `auto`, `mcp`, `gh`, `local-git`
- `SONAR_GITHUB_HOST`: GitHub Enterprise host
- `SONAR_GITHUB_REPOS`: 명시 repository URL 목록. 없으면 `target_dir` 하위 git remote에서 추론
- `SONAR_GITHUB_MAX_PULLS`, `SONAR_GITHUB_MAX_COMMITS`
- `SONAR_GITHUB_OUTPUT_DIR`: 기본 `${SONAR_OUTPUT_DIR}/_github`
- `SONAR_GITHUB_TOKEN_ENV`: token 환경변수명

**처리 규칙:**
- `auto` provider는 GitHub MCP → `gh` CLI → local git 순서로 시도합니다.
- token 값, private credential, session 정보는 문서에 남기지 않습니다.
- GitHub 내용은 PR/commit/workflow/운영 이력의 보조 근거입니다. 현재 구현 사실은 코드와 설정 파일을 우선합니다.
- PR/commit이 Jira/Wiki/릴리즈 맥락을 제공하면 `_business/`와 `_evidence/`에 연결합니다.

**출력:**
- `_github/GITHUB-SOURCE-INDEX.md`
- `_github/{repo}/Repository.md`
- `_evidence/Evidence Ledger.md`에 `github:{repo}:{kind}:{id}` 근거 항목 추가

### STEP 1: 아키텍처 및 프레임워크 스니핑
타겟 프로젝트의 구조를 분석하여 백엔드(Spring, .NET)와 프론트엔드(Next.js, Vue 등)의 존재 여부를 파악합니다.

### STEP 2: 에이전트 팀 생성
파악된 프레임워크에 맞게 두 종류의 분석 에이전트를 스폰합니다.

**구조 분석 에이전트** — `sonar/templates/ANALYZE.md` 기반:
- 백엔드 로직 발견 시: `Agent(prompt, subagent_type: "analyst-backend")`
- 프론트엔드 발견 시: `Agent(prompt, subagent_type: "analyst-frontend")`

**데이터플로우 분석 에이전트** — `sonar/templates/DATA-FLOW.md` 기반:
- 모든 프로젝트에 대해 `Agent(prompt, subagent_type: "analyst-dataflow")`를 함께 스폰합니다.
- 이 에이전트는 구조 분석과 **병렬**로 실행됩니다.

> **Note:** 에이전트를 생성할 때 해당 템플릿과 타겟 경로, 엔트리포인트를 주입합니다.

### STEP 3: 병렬 분석 및 데이터 수집
스폰된 에이전트들이 각자의 도메인에서 코드 분석을 수행합니다.
- `analyst-backend`는 내부적으로 `{MCP사용여부}` 옵션에 따라 DB/GitHub 추적 도구를 활용합니다.
- `analyst-dataflow`는 Service 클래스의 메서드 호출 체인, 상태 전이, 트랜잭션 경계를 추적합니다.

**데이터플로우 분석 시 필수 탐색 대상:**
1. `@Service` 어노테이션이 붙은 클래스의 public 메서드
2. `@Transactional` 어노테이션 적용 범위
3. `if`/`switch` 분기에서 상태값(status, yn, type 등)을 변경하는 코드
4. `@KafkaListener`, `@Async`, `WebClient`, `Feign` 등 외부/비동기 호출 지점
5. `@Cacheable`, `@CacheEvict` 등 캐시 관련 어노테이션
6. Custom Exception 클래스 계층 구조
7. Entity 또는 DTO의 상태 필드(status, state, procYn 등)와 그 변이 지점

### STEP 4: Obsidian 친화적 파일 분할 및 링크 (Knowledge Graph 최적화)
단일 거대 파일 대신, 옵시디언에서 지식그래프가 잘 형성되도록 문서를 계층화하여 저장합니다.
System Index는 전체 통합 그래프만 담당하고, 상세 그래프는 아래 프로젝트별 세부 문서에 주제별로 배치합니다.

> **품질 보존 원칙:** 기존 산출물이 제공하던 상세도는 유지합니다. 템플릿 정리나 파일명 변경을 이유로 문서가 얇아지면 안 됩니다. 각 문서는 코드 근거, 확인한 설정/위키 출처, 주요 API/이벤트/저장소, 운영상 주의점, 대표 흐름을 충분히 포함해야 합니다.
> **운영 인수인계 보존:** Wiki source에 인수인계/운영/서버/Fusion/RMS/Swagger/DB 세팅/모니터링 정보가 있으면 프로젝트 세부 문서뿐 아니라 System Index의 운영/서버 인벤토리에도 반드시 요약합니다. 상세 서버 정보가 그래프에 들어가면 복잡해지므로 표로 내리고, 그래프 품질은 유지합니다.
> **민감정보 보호:** Wiki나 설정 파일에 password/token/secret/Vault 값이 있더라도 문서에는 원문을 남기지 않고 host/port/접속 방식까지만 남깁니다.
> **핵심 알고리즘 보존:** Rate Limiter, 인증/인가, 라우팅, 배치 재처리, 정산 판정, 캐시/락/분산 key, 재시도/보상 트랜잭션처럼 시스템 품질을 좌우하는 설계·알고리즘은 `상세 문서`에 Deep Dive 섹션으로 반드시 작성합니다. “Redis 사용”, “Kafka 처리” 같은 자원명 요약만으로 끝내면 안 됩니다.

**프로젝트당 생성되는 파일 목록:**

| 파일명 | 기반 템플릿 | 설명 |
|:---|:---|:---|
| `_{프로젝트명} Index.md` | — | MOC (Map of Content) 허브 노트 |
| `Architecture & Dependencies.md` | ARCHITECTURE.md | 멀티모듈 구조, 기술 스택, 의존성 |
| `Backend API.md` | ANALYZE.md §6 | API 엔드포인트 목록 |
| `Database Schema.md` | ANALYZE.md §7 | DB 스키마, 주요 인덱스 |
| `Business Logic.md` | ANALYZE.md §4-5 | 핵심 비즈니스 도메인 개념 및 플로우 |
| **`Data Flow.md`** | **DATA-FLOW.md** | **서비스 계층 데이터플로우, 상태 전이, 트랜잭션 경계** |

- 모든 분할된 문서는 `[[문서명]]` 형태의 위키링크로 서로 양방향 연결합니다.
- `_{프로젝트명} Index.md`에서 `[[Data Flow]]` 링크를 반드시 포함합니다.
- `Architecture & Dependencies.md`에는 프로젝트 내부 모듈/컨테이너/저장소/외부 연동 상세 그래프, 의존성 표, 확인한 설정 파일 근거를 작성합니다.
- `Architecture & Dependencies.md` 또는 프로젝트 특화 문서(`Routing & Security.md`, `Batch Jobs.md`, `Event Consumers.md`)에는 핵심 알고리즘/설계 의사결정 Deep Dive를 포함합니다. 최소 항목은 `문제`, `알고리즘`, `키/상태 모델`, `설정값`, `코드 진입점`, `운영/성능 근거`, `장애/한계`입니다.
- 멀티모듈 구조 그래프는 시스템 구성도와 같은 밝은 파스텔 스타일로 작성합니다. 실행 모듈, 공유 라이브러리, 저장소/외부 리소스를 좌우 컬럼으로 분리하고, 빌드 의존성은 점선, 런타임 호출은 실선으로 구분합니다.
- `Backend API.md`에는 엔드포인트, Controller/Handler, Request/Response DTO, 호출 대상, 인증/권한, 오류 코드를 요약합니다.
- `Business Logic.md`에는 도메인 용어, 핵심 유스케이스, 분기/상태 변경, 재처리/예외 처리 흐름을 작성합니다.
- `Data Flow.md`에는 대표 시나리오마다 `sequenceDiagram`과 첨부 예시 같은 업무 데이터플로우 `flowchart LR`를 함께 작성합니다.
- 배치/이벤트/프론트/게이트웨이 프로젝트는 각각 Batch Jobs, Event Consumers, Pages & Components, Routing & Security처럼 사용자가 기대하는 세부 문서를 유지합니다.
- `_{프로젝트명} Index.md`에는 해당 프로젝트 요약과 문서 링크를 두고, 상세 그래프를 중복 삽입하지 않습니다.

### STEP 4.5: 비즈니스 레벨 워크플로우 레이어
모든 프로젝트 문서가 생성된 뒤, 프로젝트 단위 설명을 넘어서 전체 시스템이 어떤 업무 흐름으로 연결되는지 별도 문서로 정리합니다.

**담당 에이전트:** `sonar/agents/business-workflow-analyst.md`

**입력 근거:**
- 각 프로젝트의 `Index`, `Architecture & Dependencies.md`, `Backend API.md`, `Business Logic.md`, `Data Flow.md`
- `_wiki-sources/`에 수집된 설계/정책/운영 Wiki
- `_github/`에 수집된 PR/commit/workflow 근거
- `_evidence/Evidence Ledger.md`

**생성 문서:**

| 파일명 | 설명 |
|:---|:---|
| `_business/Business Workflow.md` | 업무 상태별 질문, 판정 조건, 책임 프로젝트, 운영 확인 위치 |
| `_business/Scenarios.md` | 운영/예외 중심 시나리오와 확인 순서, 운영자 판단, 후속 조치 |
| `_business/Cross Project Traceability.md` | 업무 질문별 Wiki/프로젝트 문서/코드/테이블/로그 확인 순서 |

**작성 규칙:**
- 프로젝트별 세부 문서 내용을 얇게 요약하지 말고, 업무 질문/판정 조건/운영 확인 위치를 새로 종합합니다.
- 업무 흐름마다 “근거 ID”를 연결합니다. 코드 근거가 없고 Wiki 근거만 있으면 설계/정책 근거로 표시합니다.
- System Index에는 통합 시스템 구성도 한 장만 유지하고, 비즈니스 시나리오 상세 그래프는 `_business/` 문서에 둡니다.
- `_business/Business Workflow.md`의 End-to-End Workflow는 System Index의 계층형 시스템 구성도와 달라야 합니다. 컴포넌트 계층(subgraph: 외부/프론트/게이트웨이/백엔드/이벤트/저장소)을 반복하지 말고, 번호가 붙은 업무 단계와 분기만 왼쪽에서 오른쪽으로 배치합니다.
- 저장소/모니터링/재처리는 주 흐름의 보조 근거로 점선 또는 하위 분기로만 표현합니다. 주 흐름을 되돌리는 선이나 계층 간 장거리 교차선을 만들지 않습니다.
- `_business/Business Workflow.md`에는 `업무 질문`, `판정 조건`, `담당 프로젝트`, `확인 근거`, `운영 확인 위치`가 반드시 있어야 합니다.
- `_business/Scenarios.md`는 정상 흐름보다 운영/예외 중심으로 작성하고 정상 흐름은 1개 이하로 제한합니다.
- `_business/Scenarios.md`에는 주문 이벤트 누락, LAST_TARGET_URL 미등록, 주문-유입 매핑 실패, 배송완료/환불 누락 보정, 월지급 전 정합성 실패, Open API token 검증 실패를 반드시 포함합니다.
- 각 시나리오는 `Trigger → 증상 → 확인 순서 → 시스템 처리 → 운영자 판단 → 후속 조치` 형식을 따릅니다.
- `_business/Cross Project Traceability.md`는 프로젝트 나열표가 아니라 업무 질문별 추적 가이드로 작성하고, `Question`, `When to use`, `Check order`, `Evidence`, `Decision`, `Next action` 컬럼을 포함합니다.

### STEP 5: Evidence 및 품질 검수(QA)로 위임
각 서브에이전트가 산출물 작성을 완료하면, 즉시 `qa-reviewer` 에이전트를 스폰하여 다음을 점검합니다:
- 마크다운 문법 무결성
- 템플릿 섹션 준수 여부 (`> 해당 없음` 표기 포함)
- 위키링크 유효성
- 주요 주장에 Evidence Ledger 근거가 연결되었는지
- Wiki 근거와 코드 근거가 충돌하는 설명이 확정 표현으로 작성되지 않았는지
- GitHub PR/commit 근거가 현재 구현 사실처럼 과장되지 않았는지
- **`Data Flow.md`의 서비스 계층 호출 흐름(섹션 2)에 실제 클래스명/메서드명이 포함되었는지**
- **`Data Flow.md`의 대표 런타임 시퀀스(섹션 3)가 실제 호출/이벤트/DB 흐름을 기반으로 작성되었는지**
- **`Data Flow.md`의 업무 데이터플로우(섹션 4)가 처리 단계, 이벤트, 저장소, 배치, 참조 관계를 한 장의 가로 흐름으로 표현하는지**
- **상태 전이 다이어그램(섹션 7)이 코드에서 확인된 상태값을 기반으로 작성되었는지**
- **기존 문서 품질 기준(위키 출처, 의존성 매트릭스, 모니터링/운영 기준, 대표 흐름 요약)이 불필요하게 빠지지 않았는지**
- **`_business/Business Workflow.md`의 End-to-End Workflow가 System Index 구성도와 중복되지 않고, 번호가 붙은 업무 단계 선후관계로 정렬되어 있는지**
- **`_business` 문서가 기존 프로젝트 문서를 70% 이상 반복하지 않고 업무 질문/판정/운영 확인/예외 대응을 독립적으로 제공하는지**
- **`_business/Scenarios.md`에 운영/예외 시나리오 6개 이상과 필수 시나리오 6종이 모두 포함되어 있는지**
- **`_business/Cross Project Traceability.md`가 업무 질문별 확인 순서 표인지**

동시에 `evidence-auditor` 에이전트가 다음을 점검합니다:
- `_evidence/Evidence Ledger.md`에 code/config/wiki/db/github/inferred 근거가 구조화되어 있는지
- `inferred` 근거가 확정 사실처럼 쓰이지 않았는지
- 파일 경로, 클래스명, 메서드명, API path, 테이블명, topic명이 실제 근거와 일치하는지
- 검증 실패 항목이 `_evidence/Evidence Audit.md`에 보완 요청으로 남았는지

### STEP 6: 완료 보고
검수가 완료된 모든 문서를 정리하고 성공/실패 여부를 리포트합니다.

---

## 3. Data Flow 분석 에이전트 프롬프트 템플릿

`analyst-dataflow` 에이전트를 스폰할 때 아래 프롬프트를 기반으로 주입합니다:

```
당신은 레거시 Spring Boot 코드의 서비스 계층 데이터플로우 분석 전문가입니다.
타겟 프로젝트 경로: {target_path}
출력 경로: {output_path}/Data Flow.md

sonar/templates/DATA-FLOW.md 템플릿을 기반으로 Data Flow.md를 작성하세요.

분석 우선순위:
1. @Service 클래스에서 핵심 비즈니스 메서드 (3개 이상의 의존성을 가진 메서드) 식별
2. 식별된 메서드의 호출 체인을 Controller → Service → Repository 순서로 추적
3. 대표 시나리오의 sequenceDiagram 작성에 필요한 participant와 메시지 추출
4. 첨부 예시 같은 업무 데이터플로우 작성에 필요한 처리 단계, 이벤트 버스, 저장소, 배치, 점선 참조 관계 추출
5. 상태값 변이 지점 (@Transactional 내부에서 Entity 상태가 바뀌는 코드) 추출
6. 외부 호출(Feign, WebClient, @KafkaListener, @Async) 지점과 오류 처리 패턴 파악
7. 캐시 히트/미스 흐름 (@Cacheable, Redis 직접 조작 코드) 문서화
8. 핵심 알고리즘/설계 의사결정 Deep Dive 작성

작성 규칙:
- 모든 흐름은 실제 클래스명, 메서드명, 라인번호로 검증
- 추측 금지 — 확인 불가 시 > ⚠️ 확인 필요 표기
- 대표 흐름마다 sequenceDiagram과 업무 데이터플로우 flowchart LR를 모두 작성
- Rate Limiter, 캐시 분산 key, 재처리 배치, 정산 판정, token 검증처럼 핵심 알고리즘이 발견되면 별도 Deep Dive 섹션에 문제/알고리즘/키/상태/설정/코드 근거/운영 근거를 작성
- 업무 데이터플로우는 왼쪽에서 오른쪽으로 시간이 흐르도록 배치하고, 저장소는 원통형 노드로 표현
- 실선은 데이터 생성/전달/상태 변경, 점선은 조회/참조 의존성으로 구분
- Mermaid는 graph TD/LR 대신 flowchart TD/LR를 사용하고 fanout 축약 문법을 쓰지 않음
- Confluence Mermaid 호환을 위해 노드 라벨을 `"1. ..."`, `"- ..."`, `<br/>1. ...`, `<br/>- ...`처럼 Markdown list로 시작하지 않음. 단계는 `"Step 1 - ..."` 또는 `"S1: ..."`로 작성
- Mermaid 라벨/메시지 안에 literal backslash+n을 쓰지 않음. 줄바꿈은 `<br/>`를 사용하고, sequenceDiagram 메시지는 한 줄 문장 또는 ` - `로 연결
- Excalidraw 산출물을 함께 만들거나 변환할 때는 `scripts/render-excalidraw-from-mermaid.js`를 우선 사용. Arrow Type `직각`, `elbowed: true`, `roundness: null`, port/rail routing, 수평/수직 `points`를 사용하고 대각선 2-point arrow, 노드 관통, 라벨 겹침을 만들지 않음
- 모든 관련 문서는 [[문서명]] 위키링크로 연결
```
