# ATLS Source Connector Master PRD

## 문서 목적

이 문서는 `ATLS Platform`이 Jira / Confluence뿐 아니라 `Notion`, `Obsidian`, `Figma`까지 포함해 다양한 source와 evidence를 연결할 수 있도록 하는 `Source Connector` 체계의 통합 PRD다.

이 문서는 아래를 하나의 제품 기능으로 본다.

- 운영 source connector
- 문서 source connector
- visual evidence connector
- AI-assisted normalization layer
- metadata normalization
- source trust / priority 체계
- requirement/evidence 매핑

## 제품 비전

`ATLS`는 특정 문서 툴에 묶인 도구가 아니라,  
여러 source system에서 요구사항과 evidence를 수집해
`source-backed requirement -> acceptance manifest -> test -> evidence review`
로 연결하는 플랫폼이어야 한다.

즉 이 기능의 목표는 다음과 같다.

- Jira / Confluence를 기본 source로 사용한다.
- Notion / Obsidian을 문서 source로 확장한다.
- Figma를 visual source와 evidence oracle로 연결한다.
- AI provider를 통해 source normalize / summarize / mapping을 수행하되, source-backed contract를 유지한다.
- source마다 신뢰도와 역할을 구분한다.
- MCP / API / local file 기반 connector를 일관된 contract로 통합한다.

## 핵심 원칙

1. `source type`과 `evidence type`을 구분한다.
2. source마다 `trust level`과 `priority`를 갖는다.
3. connector는 raw data를 가져오되, requirement 판단은 normalization 이후에만 한다.
4. 시각 자료는 `evidence`이면서 동시에 `requirement oracle`이 될 수 있다.
5. source가 늘어나도 workflow는 동일해야 한다.
6. fallback으로 추정 source를 만들지 않는다.
7. AI provider는 source 생성자가 아니라 normalization/mapping 보조자여야 한다.

## 왜 필요한가

현재도 `ATLS`는 Jira / Confluence / PRD / API / 코드 / 실행 증거를 다루고 있다.
하지만 실제 팀 운영에서는 source가 더 분산되어 있다.

예:

- Jira: 이슈, 상태, 코멘트
- Confluence: 운영 문서, 배포 메모
- Notion: PRD, 회의록, 요구사항 초안
- Obsidian: 설계 메모, 개인/팀 기술 문서
- Figma: UI 시안, interaction spec, exact visual oracle

이들을 별도 로직으로 각각 다루면 시스템이 깨지기 쉽다.  
따라서 connector contract를 공통화해야 한다.

## 지원 대상 source

### 1. Jira

역할:

- issue source
- workflow/status source
- comment source
- attachment source

주요 데이터:

- issue key
- title
- description
- assignee
- status
- priority
- comments
- attachments
- links

분류:

- `operational_source`

### 2. Confluence

역할:

- 운영 문서 source
- 배경 문서 source
- 팀 합의 문서 source

주요 데이터:

- page title
- page body
- page hierarchy
- labels
- version
- page url

분류:

- `document_source`

### 3. Notion

역할:

- PRD source
- 요구사항 초안 source
- 회의록 source
- 체크리스트 source

주요 데이터:

- page title
- page content
- database properties
- block hierarchy
- page url
- last edited time

분류:

- `document_source`

주의:

- Notion 문서는 신뢰도 차이가 크므로 page/database 별 trust policy가 필요하다.

### 4. Obsidian

역할:

- 로컬 설계 문서 source
- 개인/팀 메모 source
- 기술 조사 source

주요 데이터:

- markdown content
- frontmatter
- tags
- wikilinks
- local path
- modified time

분류:

- `local_document_source`

주의:

- 개인 메모와 공식 문서를 구분해야 한다.
- vault path와 trusted folder 정책이 필요하다.

### 5. Figma

역할:

- visual requirement source
- interaction oracle
- design metadata source
- evidence comparison source

주요 데이터:

- file key
- page/frame/node metadata
- component / variant metadata
- text layers
- spacing / color / typography metadata
- prototype links
- comments
- exported image refs

분류:

- `visual_source`
- `visual_evidence_source`

핵심 포인트:

- Figma는 단순 이미지 링크가 아니라 실제 metadata source가 될 수 있다.
- MCP를 통해 node metadata를 가져오면 exact visual spec을 requirement oracle로 사용할 수 있다.

## Source Connector 모델

각 connector는 공통적으로 아래 필드를 제공해야 한다.

- `connector_id`
- `connector_type`
- `display_name`
- `source_kind`
- `access_mode`
- `trust_level`
- `default_priority`
- `enabled`
- `scope`
- `last_sync_at`
- `validation_status`

### connector_type 예시

- `jira`
- `confluence`
- `notion`
- `obsidian`
- `figma`

### access_mode 예시

- `api`
- `mcp`
- `local_filesystem`
- `hybrid`

### source_kind 예시

- `operational_source`
- `document_source`
- `local_document_source`
- `visual_source`
- `api_contract_source`
- `execution_evidence_source`

## Source 신뢰도 모델

각 source item은 아래 메타데이터를 가져야 한다.

- `source_type`
- `source_ref`
- `source_title`
- `source_priority`
- `trust_level`
- `last_verified_at`
- `is_primary`
- `relevance_score`

### trust_level 예시

- `high`
- `medium`
- `low`
- `unknown`

### source_priority 예시

1. `prd`
2. `jira_body`
3. `jira_comment`
4. `jira_attachment`
5. `confluence_page`
6. `notion_page`
7. `figma_node`
8. `obsidian_note`
9. `existing_behavior`
10. `code_constraint`

주의:

- 이 우선순위는 절대 고정값이 아니라 프로젝트 정책에 따라 override 가능해야 한다.
- 예를 들어 어떤 팀은 Notion PRD가 Confluence보다 상위일 수 있다.

## Source Item 정규화 모델

모든 connector 결과는 아래 공통 구조로 normalize 되어야 한다.

- `item_id`
- `connector_type`
- `source_type`
- `title`
- `content_summary`
- `raw_ref`
- `web_url`
- `local_path`
- `metadata`
- `trust_level`
- `source_priority`
- `tags`
- `updated_at`

## AI-assisted Normalization 요구사항

AI는 source connector 위에서 아래 역할을 수행할 수 있다.

- 한국어 요약
- requirement candidate 추출
- source relevance ranking
- evidence gap 설명
- figma metadata 요약

하지만 아래는 금지한다.

- source가 없는 requirement 생성
- trust level 없는 임의 결론
- exact visual spec 추정
- exact interaction spec 추정

따라서 AI 실행 결과는 항상 아래 메타데이터를 동반해야 한다.

- `ai_provider`
- `ai_auth_mode`
- `model`
- `reasoning_mode`
- `generated_at`
- `source_refs`
- `confidence`

## Requirement 매핑 모델

각 requirement는 하나 이상의 source item과 연결된다.

- `requirement_id`
- `statement`
- `requirement_type`
- `sources[]`
- `primary_source`
- `evidence_sufficiency`
- `needs_user_materials`
- `missing_evidence[]`

### source -> requirement 예시

- Jira 본문 -> 기능 요구사항
- Notion PRD -> 상세 행동 규칙
- Figma node metadata -> exact visual requirement
- Obsidian 설계 노트 -> 기술 제약 또는 추가 배경

## Evidence 매핑 모델

각 requirement 결과는 아래 evidence와 연결될 수 있다.

- video
- screenshot
- dom assertion
- network assertion
- state assertion
- figma comparison metadata

### Figma evidence 활용

Figma는 아래 두 역할을 동시에 할 수 있다.

1. `requirement source`
   - 시안/프로토타입/디자인 토큰 기반 expected spec
2. `evidence oracle`
   - 실제 캡처와 figma metadata를 비교할 기준

예:

- 버튼 label text
- padding / spacing
- color token
- icon visibility
- state variation

## Connector별 기능 요구사항

### Jira Connector

필수 기능:

- issue fetch
- comments fetch
- attachment metadata fetch
- status transition prep

### Confluence Connector

필수 기능:

- page fetch
- hierarchy fetch
- labels fetch
- version metadata fetch

### Notion Connector

필수 기능:

- page fetch
- database query
- block tree normalize
- trusted database policy

### Obsidian Connector

필수 기능:

- vault root 등록
- trusted folder policy
- markdown/frontmatter parse
- wikilink resolve

### Figma Connector

필수 기능:

- file/frame/node metadata fetch
- text/style token extraction
- component/variant metadata fetch
- comment fetch
- exportable node reference

권장 기능:

- screenshot comparison prep
- figma node deep-link
- exact visual requirement extraction

## MCP 연동 요구사항

### Figma MCP

활용 목적:

- frame/node metadata 수집
- text/content/style 정보 추출
- visual oracle 연결

필수 메타데이터:

- node id
- page id
- frame title
- text layers
- fill/stroke/color
- spacing/padding
- typography
- component state

### Notion MCP

활용 목적:

- page/database 검색 및 fetch
- trusted source 판별

### 향후 MCP 일반화

connector는 MCP를 특별취급하지 않고 아래 access mode 중 하나로 취급한다.

- `mcp`
- `api`
- `local_filesystem`

즉 MCP든 API든 normalize 후에는 같은 pipeline을 탄다.

## 설정 관리 요구사항

connector는 dashboard에서 설정 가능해야 한다.

### 공통 설정 필드

- enabled
- workspace/scope
- trust level default
- priority override
- validation status

### connector별 추가 설정

#### Jira / Confluence

- base URL
- api token
- default space / assignee

#### Notion

- workspace connection
- trusted databases/pages

#### Obsidian

- vault root
- trusted folders
- ignored folders

#### Figma

- team/file scope
- trusted pages
- preferred node depth
- image export policy

## Dashboard 요구사항

dashboard는 connector 관점에서 아래를 제공해야 한다.

### 1. Connector Registry

- 등록된 connector 목록
- enabled/disabled 상태
- validation 상태
- trust policy 요약

### 2. Source Explorer

- source item 검색
- issue별 연결된 source 보기
- source별 requirement 연결 보기

### 3. Source Trust Panel

- 각 source의 trust level
- primary source 여부
- outdated source 경고

### 4. Evidence Source Panel

- requirement에 연결된 evidence type
- figma visual oracle 존재 여부
- 추가 자료 필요 여부

## API / Contract 요구사항

### Connector Registry API

- `GET /api/connectors`
- `POST /api/connectors`
- `PATCH /api/connectors/:connectorId`
- `POST /api/connectors/:connectorId/validate`
- `POST /api/connectors/:connectorId/archive`

### Source Query API

- `GET /api/sources`
- `GET /api/sources/:sourceId`
- `GET /api/issues/:issueKey/sources`
- `GET /api/issues/:issueKey/evidence-sources`

### Connector-specific API 예시

- `GET /api/connectors/figma/files/:fileKey`
- `GET /api/connectors/figma/nodes/:nodeId`
- `GET /api/connectors/notion/pages/:pageId`
- `GET /api/connectors/obsidian/notes`

## 필요한 추가 기능 점검

이 PRD 기준으로 connector 체계에 반드시 필요한 기능은 아래다.

### 필수

1. connector registry
2. connector validation
3. source normalization pipeline
4. trust/priority policy
5. source explorer
6. requirement source mapping
7. evidence source mapping

### 강권장

8. figma visual oracle support
9. notion trusted page/database policy
10. obsidian trusted folder policy
11. outdated source detection

## MVP 범위

### 포함

- Jira connector
- Confluence connector
- Notion connector
- Obsidian connector
- Figma connector metadata read
- source normalization
- dashboard source explorer

### 제외

- full visual diff engine
- automatic figma-to-dom pixel comparison
- multi-tenant connector sharing

## 단계별 개발 제안

### Phase 1

- connector registry
- Jira / Confluence / Notion read connector
- source normalization contract

### Phase 2

- Obsidian local connector
- Figma metadata connector
- source explorer UI

### Phase 3

- requirement/evidence source mapping UI
- figma visual oracle integration
- trust policy override UI

### Phase 4

- advanced visual comparison
- outdated source alerts
- connector analytics

## 하네스 엔지니어링 관점의 최종 결론

이 기능이 완성되면 `ATLS`는 Jira/Confluence 중심 도구를 넘어,
여러 source system에서 requirement와 evidence를 수집해
AI 기반 테스트 자동화와 증거 기반 검증을 수행하는 플랫폼이 된다.

특히 다음이 가능해진다.

1. Jira / Confluence / Notion / Obsidian / Figma를 같은 workflow에 묶는다.
2. source의 신뢰도와 역할을 구분해 유령 requirement 생성을 막는다.
3. Figma를 단순 참고 이미지가 아니라 metadata-backed evidence source로 다룬다.
4. source가 늘어나도 workflow와 manifest 구조는 유지된다.

즉 이 문서는 `ATLS`를 connector 확장형 AI 테스트 플랫폼으로 만드는 기준 PRD다.
