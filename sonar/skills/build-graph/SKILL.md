# Build Graph Skill

이 스킬은 `sonar-out/` 에 생성된 여러 도메인별 `ANALYZE.md` 산출물들을 파싱하여, 시스템 전체의 연관 관계를 보여주는 지식그래프(Knowledge Graph)를 생성하거나 갱신합니다.

## 0. 렌더러 결정

`.env`에서 `SONAR_DIAGRAM_RENDERER` 값을 읽는다.

| 값 | 동작 |
|:---|:---|
| `mermaid` (기본, 미설정 시) | STEP 3에서 Mermaid 코드 블록 생성 |
| `excalidraw` | STEP 3에서 excalidraw-mcp `create_view` 호출 후 `.excalidraw` 파일 저장 |

`excalidraw`가 설정됐더라도 excalidraw-mcp 도구(`read_me`, `create_view`)를 사용할 수 없으면 `mermaid`로 폴백하고 경고를 남긴다.

## 1. 사전 조건
- `sonar-out/` 디렉토리에 1개 이상의 `ANALYZE.md` 문서가 존재해야 함
- `sonar/config/sonar-config.md` 로드 완료

## 2. 작업 흐름 (Workflow)

### STEP 1: 산출물 스캔
`sonar-out/` 내의 모든 마크다운 파일을 읽어들입니다.

### STEP 2: 의존성 및 연결점 추출 (옵시디언 노트용)
각 분석 문서에서 다음 요소들을 추출합니다:
- 외부 시스템 호출 (API, DB)
- 공통 모듈 의존성
- 서브 시스템 간의 데이터 흐름
**주의:** 추출된 모든 노드(개념, 파일, DB 등)는 `[[노드명]]` 형태의 옵시디언 위키링크로 표기해야 합니다.

### STEP 2.5: 아키텍처 모델 정규화
Mermaid를 바로 작성하기 전에 아래 구조로 시스템 모델을 먼저 정리합니다.

```yaml
system: "{시스템명}"
containers:
  - id: "{영문 snake_case 또는 kebab-case}"
    name: "{표시명}"
    layer: "{external|frontend|gateway|admin|backend-core|event|batch|storage}"
    type: "{web|api|bff|domain-api|producer|consumer|batch|database|cache|search|broker|external}"
    responsibility: "{확인된 책임}"
    tech: "{확인된 기술}"
relations:
  - from: "{source-id}"
    to: "{target-id}"
    protocol: "{HTTPS|Feign|WebClient|Kafka|JDBC/JPA|Route|HTTP 등}"
    purpose: "{관계 목적}"
```

모델 작성 규칙:
- `id`는 Mermaid 렌더링 안정성을 위해 영문, 숫자, `_`만 사용합니다.
- 화면에 표시되는 `name`과 설명은 한국어를 허용합니다.
- 관계선에는 `protocol` 또는 `purpose` 중 하나 이상을 반드시 둡니다.
- 확인되지 않은 연결은 Mermaid에 넣지 말고 표나 본문에 `> ⚠️ 확인 필요`로 남깁니다.

### STEP 3: MOC (Map of Content) 및 다이어그램 생성

추출한 데이터를 바탕으로 다음 두 가지를 작성합니다:
1. **옵시디언 MOC (Index):** 관련된 모든 노트를 `[[ ]]` 링크로 묶어놓은 허브 페이지를 작성합니다.
2. **다이어그램:** `SONAR_DIAGRAM_RENDERER` 값에 따라 아래 방식으로 생성합니다.

#### 렌더러: `mermaid` (기본)

System Index에는 한 장짜리 통합 시스템 그래프를 작성하고, 상세 그래프는 프로젝트별 세부 문서에 주제별로 작성합니다. Mermaid 작성 규칙은 `sonar/config/sonar-config.md` 섹션 7을 따릅니다.

#### 렌더러: `excalidraw`

Mermaid 코드 블록을 원본 모델로 삼아 `.excalidraw` 파일을 생성합니다. 우선 `scripts/render-excalidraw-from-mermaid.js`를 사용하고, excalidraw-mcp는 인터랙티브 미리보기나 보조 렌더링이 필요할 때만 사용합니다.

권장 CLI:

```bash
node scripts/render-excalidraw-from-mermaid.js --input "{System Index.md}" --output "{diagram.excalidraw}"
```

**실행 순서:**

1. **Mermaid 원본 추출**: System Index의 `flowchart LR` 블록을 읽고 노드, subgraph, class, edge를 정규화한다.

2. **elements JSON 작성**: Mermaid 모델 또는 STEP 2.5에서 만든 아키텍처 모델을 Excalidraw elements JSON으로 변환한다.

   변환 규칙:
   - **컨테이너 노드** → `rectangle` 요소. `backgroundColor`는 레이어별로 구분한다.
     - `external`: `#fef3c7`(노랑 계열)
     - `frontend` / `gateway` / `admin`: `#dbeafe`(파랑 계열)
     - `backend-core` / `event` / `batch`: `#dcfce7`(초록 계열)
     - `storage`: `#fce7f3`(핑크 계열)
   - **관계 엣지** → `arrow` 요소. `label`에 `protocol` 또는 `purpose`를 표기한다.
   - **레이어 그룹** → `frame` 요소로 레이어 subgraph를 감싼다. `name`은 레이어명(한국어 허용).
   - 노드 배치는 외부 → 프론트엔드/게이트웨이 → 백엔드 핵심 → 이벤트/배치 → 저장소 순서로 왼쪽에서 오른쪽으로 배열한다.
   - 관계선은 20개 안팎으로 유지하고 보조 관계는 별도 표로 내린다.
   - 모든 arrow는 Arrow Type `직각`, `elbowed: true`, `roundness: null`, 수평/수직 `points`를 사용한다.
   - 여러 입력이 하나의 BFF/API로 모이면 target frame 왼쪽에 vertical merge rail을 만들고 마지막 segment만 target port로 진입한다.
   - 저장소 방향 edge는 저장소 frame 왼쪽 storage rail에서 각 저장소 y-lane으로 분기한다.
   - 이벤트 consumer가 backend API로 들어갈 때는 이벤트 frame에서 대각선으로 올리지 않고 backend 하단/좌측 진입 lane을 거친다.
   - 시작/끝점은 source/target의 left/right/top/bottom port에만 붙인다. 선이 노드 중앙을 관통하면 안 된다.
   - Area 박스 내부에는 균일한 패딩과 node gap을 둔다. 기본값은 좌우 `48px`, 상단 `56px`, 하단 `44px`, node gap 가로 `40px`, 세로 `36px`이다. node text는 rectangle에 binding하고 중앙 정렬한다.
   - 저장소/외부 리소스 edge는 색상만으로 구분하지 말고 별도 rail, label 위치, label text/background를 함께 사용한다. `JDBC/JPA`는 blue, `Redis`는 rose, `Spring Data`는 violet, `Elasticsearch`/`index/read`는 amber 계열을 절제된 채도로 사용한다.
   - 여러 색이 한 rail 위에 겹치면 가독성이 떨어지므로 protocol별 rail offset을 둔다.

3. **다이어그램 렌더링/검증**: 생성 스크립트의 내장 QA 또는 별도 검증으로 아래 조건을 확인한다.
   - arrow 수가 Mermaid edge 수와 일치
   - 모든 arrow segment가 수평/수직
   - source/target 외 노드 bbox 관통 0건
   - arrow label과 node bbox 겹침 0건
   - node label이 컴포넌트 박스를 넘치는 경우 0건
   - frame-child padding/gap/center alignment 위반 0건
   - 저장소 edge가 모두 같은 색이면 반려

4. **파일 저장**: elements JSON을 Excalidraw 파일 포맷으로 `SONAR_OUTPUT_DIR`의 해당 경로에 저장한다.

   저장 위치 및 파일명:
   - System Index 통합 그래프: `{SONAR_OUTPUT_DIR}/{시스템명}-system-graph.excalidraw`
   - 프로젝트별 세부 그래프: `{SONAR_OUTPUT_DIR}/{project-name}/{다이어그램-주제}.excalidraw`

   파일 구조 (Excalidraw JSON 포맷):
   ```json
   {
     "type": "excalidraw",
     "version": 2,
     "source": "https://github.com/excalidraw/excalidraw-mcp",
     "elements": [ /* create_view에 전달한 elements 배열 */ ],
     "appState": {
       "viewBackgroundColor": "#ffffff",
       "gridSize": null
     },
     "files": {}
   }
   ```

5. **Markdown 참조 삽입**: Markdown 문서에서 Mermaid 코드 블록 자리에 아래 형태로 삽입한다.

   ```markdown
   > 다이어그램 렌더러: Excalidraw

   ![[{파일명}.excalidraw]]
   ```

   Obsidian Excalidraw 플러그인이 설치된 경우 `![[...]]` 위키링크로 인라인 렌더링된다.

### STEP 3.5: 운영/서버 인벤토리 반영
System Index에는 통합 그래프와 별개로 운영자가 바로 확인해야 하는 서버/도메인/인수인계 정보를 표로 작성합니다.

수집 대상:
- `_wiki-sources/`의 인수인계, 운영, 서버, DB 세팅, 모니터링, Fusion, RMS, Swagger, host, pod, TPS 관련 페이지
- 각 프로젝트 `README.md`, `application*.yaml`, `docker-compose*.yml`, 배포/프로파일 설정
- 기존 프로젝트별 `Architecture & Dependencies.md`에 추출된 server/domain/swagger/Fusion/RMS 정보

작성 규칙:
- System Index의 대표 그래프는 계속 한 장으로 유지하고, 서버 상세 정보는 표와 본문으로 내립니다.
- 서비스별로 `도메인/Host`, `환경(local/dev/av/prod)`, `Fusion/RMS/Swagger`, `로컬/운영 포트`, `운영 정책`, `근거`를 분리합니다.
- Wiki 인수인계 문서의 gate 정책, target-url, service-code fallback, 대기열, Open API rate limit/timeout/ShutterMan 같은 운영 규칙은 누락하지 않습니다.
- password, token, secret, Vault 값은 원문으로 쓰지 않고 `redacted`, `문의 필요`, `환경변수 참조`로 표기합니다.
- 코드/설정과 Wiki의 값이 다르면 확정하지 말고 양쪽 근거와 `확인 필요`를 남깁니다.

#### Mermaid 작성 규칙

1. System Index의 시스템 구성도는 반드시 한 장짜리 통합 그래프로 작성합니다.
   - C4/sequence/event/storage처럼 여러 Mermaid 블록으로 쪼개지 않습니다.
   - 상세 설명은 표와 본문으로 보완하되, 대표 시스템 구성도는 하나만 둡니다.
   - 상세 아키텍처, 요청 흐름, 이벤트 흐름, 저장소 의존성, 데이터플로우는 System Index가 아니라 프로젝트별 세부 문서에 작성합니다.
2. `flowchart`는 기본적으로 좌우 흐름을 사용합니다.
   - 외부 → 프론트엔드/게이트웨이/어드민 → BFF/도메인 API → 이벤트/배치 → 저장소 순서
   - 복잡한 시스템 구성도에는 아래 init 블록을 붙입니다.
   - Confluence와 Obsidian 문서 배경은 흰색인 경우가 많으므로 `theme: "dark"`를 쓰지 않습니다. System Index는 밝은 base 테마와 파스텔 계층 색상을 기본으로 합니다.

```mermaid
%%{init: {"theme": "base", "flowchart": {"defaultRenderer": "elk", "curve": "stepBefore", "htmlLabels": true}, "themeVariables": {"background": "#ffffff", "primaryColor": "#fff7ed", "primaryTextColor": "#111827", "primaryBorderColor": "#fed7aa", "lineColor": "#3f3f46", "clusterBkg": "#f8fafc", "clusterBorder": "#d1d5db", "edgeLabelBackground": "#f3e8ff", "fontFamily": "Pretendard, Inter, Arial, sans-serif"}}}%%
flowchart LR
```

3. 레이어는 반드시 `subgraph`로 묶습니다.
   - 권장 레이어: `외부`, `프론트엔드 계층`, `게이트웨이 계층`, `어드민 계층`, `백엔드 핵심 계층`, `이벤트 계층 / Kafka`, `배치 계층`, `저장소`
   - 각 `subgraph` 내부에는 필요한 경우 `direction LR`를 명시해 노드가 가로로 펼쳐지도록 합니다.
4. 통합 그래프는 관계선을 20개 안팎으로 유지합니다.
   - 핵심 연결은 유지하되, 외부 사내 API나 세부 토픽처럼 그래프를 복잡하게 만드는 보조 연결은 표로 내립니다.
   - 그래프에서 같은 레이어 안의 노드는 역할 단위로 합칩니다. 예: 여러 Kafka consumer는 `Consumers`로 묶습니다.
5. 팬아웃 축약 문법을 쓰지 않습니다.
   - 금지: `A --> B & C`, `A & B --> C`
   - 허용: `A --> B`, `A --> C`처럼 한 줄에 한 관계
6. API path, URL, 괄호, 슬래시(`/`), 콜론(`:`), `<br/>`가 들어간 노드 라벨은 반드시 quote 처리합니다.
   - 금지: `B[/v1/order/inflow/list 조회]`
   - 허용: `B["GET /v1/order/inflow/list 조회"]`
7. 선 꼬임을 줄이기 위해 엣지는 왼쪽에서 오른쪽 방향이 되도록 선언 순서를 맞춥니다.
   - 예외적으로 storage 반환/참조처럼 역방향이 필요한 선은 만들지 않고 목적 라벨로 설명합니다.
8. 모든 Mermaid 블록 앞에는 이 다이어그램이 답하는 질문을 한 문장으로 설명합니다.
9. `graph TD`, `graph LR` 대신 `flowchart TD`, `flowchart LR`를 사용합니다.
10. 통합 그래프의 색상은 문서 가독성을 위해 밝은 계열로 유지합니다.
   - 레이어 subgraph: `#f8fafc`, `#f0fdf4`, `#fffbeb`, `#fff7ed`처럼 낮은 채도의 배경
   - 서비스 노드: `#eef2ff`, `#ecfeff`, `#fff7ed` 같은 파스텔 fill
   - 저장소 노드: `#fef3c7` 계열
   - 텍스트는 `#111827`, 선은 `#3f3f46` 기준
   - 엣지 라벨 배경은 `#f3e8ff`처럼 옅은 보라 계열을 사용해 2번 예시처럼 읽히게 합니다.
11. Confluence Mermaid는 노드 라벨 내부 Markdown list를 지원하지 않으므로 라벨을 숫자/불릿 목록처럼 시작하지 않습니다.
   - 금지: `A["1. 요청 수신"]`, `A["- 요청 수신"]`, `A["처리<br/>1. 검증"]`, `A["처리<br/>- 검증"]`
   - 허용: `A["Step 1 - 요청 수신"]`, `A["S1: 요청 수신"]`, `A["처리<br/>Step 1 - 검증"]`
   - `Unsupported markdown: list`가 보이면 이 규칙 위반을 먼저 의심합니다.
12. Mermaid 라벨/메시지에 literal backslash+n을 쓰지 않습니다.
   - 금지: `A["서비스 backslash+n API"]`, `A[처리 backslash+n 결과]`, `S->>T: 처리 backslash+n 재시도`
   - 허용: `A["서비스<br/>API"]`, `A["처리<br/>결과"]`, `S->>T: 처리 - 재시도`
   - Confluence Wiki에서는 backslash+n이 그대로 보일 수 있으므로 `<br/>` 또는 짧은 단일 문장으로 작성합니다.

#### 상세 그래프 배치 규칙

System Index에 넣지 않는 상세 그래프는 아래 문서에 주제별로 배치합니다.

| 그래프 주제 | 작성 위치 | Mermaid 타입 | 목적 |
|:---|:---|:---|:---|
| 프로젝트 내부 모듈/컨테이너 구조 | `Architecture & Dependencies.md` | `flowchart LR` | 한 프로젝트 안의 모듈, 서버, 저장소 관계 |
| 외부 요청/사용자 시나리오 | `Data Flow.md` | `sequenceDiagram` | 요청이 어떤 서비스/저장소를 거치는지 시간순 표현 |
| 업무 데이터 흐름 | `Data Flow.md` | `flowchart LR` | 첨부 예시처럼 처리 단계, 이벤트, 저장소, 배치, 참조 관계 표현 |
| 이벤트 처리 흐름 | `Data Flow.md` 또는 `Architecture & Dependencies.md` | `flowchart LR` | Producer → Broker → Consumer → 후속 API/DB |
| 저장소 의존성 | `Architecture & Dependencies.md` 또는 `Database Schema.md` | `flowchart LR` | DB/Redis/Mongo/ES의 역할과 사용 모듈 |

상세 그래프도 한 주제 안에서는 가능한 한 한 장으로 그립니다. 다만 서로 다른 질문에 답하는 그래프를 System Index에 합치지 않습니다.

### STEP 4: 옵시디언 Vault 업데이트
생성된 다이어그램과 MOC를 타겟 출력 경로(Obsidian Vault)의 최상위 `_{프로젝트명} System Index.md` 문서에 작성(또는 갱신)합니다.

### STEP 5: 검수
결과물에 대해 `qa-reviewer` 에이전트를 스폰하여 위키링크 `[[ ]]` 문법이 깨지지 않았는지, Mermaid 렌더링 오류가 없는지 확인합니다.
