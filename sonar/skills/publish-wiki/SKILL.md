# Publish Wiki Skill

이 스킬은 검수 완료된 분석 보고서들을 Confluence Wiki에 일괄 업로드하여 전사 지식으로 공유하는 파이프라인입니다.

## 1. 사전 조건
- `sonar/config/sonar-config.md` 내의 Wiki 설정(스페이스 키, 상위 페이지 ID 등) 확인
- `sonar-out/` 내에 1개 이상의 마크다운 문서 존재

## 2. 작업 흐름 (Workflow)

### STEP 1: 업로드 대상 목록화
`.env`의 `SONAR_OUTPUT_DIR`을 우선 사용하고, 없으면 `sonar-out/` 디렉토리에서 업로드할 파일 리스트를 추출합니다.

디렉터리 구조는 Wiki 계층 구조와 1:1로 맞춥니다.

```text
{상위 페이지}
├── Index
├── Business Analysis
│   ├── Business Workflow
│   ├── Scenarios
│   └── Cross Project Traceability
├── Evidence
│   ├── Evidence Ledger
│   └── Evidence Audit
├── affiliate-admin
│   ├── Index
│   ├── affiliate-admin - Architecture & Dependencies
│   └── ...
└── affiliate-backend
    ├── Index
    └── ...
```

`SONAR_OUTPUT_DIR`의 basename이 `code-sonar`여도 그 이름의 중간 Wiki 페이지를 만들지 않고, 출력 루트의 하위 파일/디렉터리를 선택한 상위 페이지 바로 아래에 펼칩니다.

`_... Index.md`, `_... System Index.md`는 Wiki 제목을 항상 `Index`로 업로드합니다. Confluence가 동일 제목을 거절하면 API title만 `{디렉터리명} - Index`로 fallback하고 목차/링크 표시 텍스트는 `Index`를 유지합니다.

Confluence 제목 충돌 방지를 위해 여러 프로젝트에서 반복되는 비-인덱스 파일명은 `{프로젝트명} - {파일명}`으로 업로드합니다.

시스템 보조 디렉터리는 사람이 읽기 좋은 Wiki 제목으로 매핑합니다:

| 로컬 디렉터리 | Wiki 제목 |
|:---|:---|
| `_business` | `Business Analysis` |
| `_evidence` | `Evidence` |

아래 디렉터리는 분석 근거 캐시이므로 Wiki에 발행하지 않습니다:

| 로컬 디렉터리 | 처리 |
|:---|:---|
| `resources` | 발행 제외 (wiki, jira, docling, github 캐시) |

### STEP 2: Wiki Publisher 에이전트 스폰
`Agent(prompt, subagent_type: "wiki-publisher")`를 호출하여 실제 업로드 로직을 수행합니다.

### STEP 3: 위키 계층 구조 생성
선택한 상위 페이지 바로 아래에 출력 루트 Markdown 파일, `_business`, `_evidence`, 프로젝트 디렉터리를 연결합니다. 각 프로젝트 디렉터리 페이지 하위에는 해당 프로젝트의 Markdown 파일을 각각 별도 Child Page로 생성합니다.

디렉터리 페이지에는 상세 문서를 합쳐 넣지 않고, 하위 문서 링크 목록만 작성합니다. 이 규칙은 프로젝트 디렉터리뿐 아니라 `_business`를 매핑한 `Business Analysis`, `_evidence`를 매핑한 `Evidence`에도 동일하게 적용합니다.

디렉터리 페이지 본문은 반드시 ToC 전용 Markdown으로 작성합니다.

```markdown
# {directory-title}

## Pages

- [{child-title}]({child-url})
- [{child-title}]({child-url})
```

금지:

- `# Business Analysis\n\n...`처럼 literal backslash+n이 보이는 placeholder 본문
- 하위 문서의 내용을 디렉터리 페이지에 복사하거나 요약한 긴 본문
- Mermaid 차트, 표, 운영 설명을 디렉터리 페이지에 직접 삽입
- `_business`, `_evidence` 같은 로컬 디렉터리명을 그대로 노출

디렉터리 페이지는 하위 문서 탐색만 담당하고, 실제 내용은 child page에 둡니다.

### STEP 4: 결과 리포트
업로드 성공한 페이지들의 URL 리스트를 사용자에게 출력하고, Teams 웹훅이 설정되어 있다면 완료 알림을 보냅니다.
