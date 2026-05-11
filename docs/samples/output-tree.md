# Output Tree Sample

Code-Sonar는 분석 결과를 하나의 긴 문서로 합치지 않고, 읽기 쉬운 Markdown 파일 트리로 만든다.

```text
commerce-analysis/
├── Index.md
├── _business/
│   ├── Business Workflow.md
│   ├── Scenarios.md
│   └── Cross Project Traceability.md
├── _evidence/
│   ├── Evidence Ledger.md
│   └── Evidence Audit.md
├── _wiki-sources/
│   ├── WIKI-SOURCE-INDEX.md
│   └── pages/
├── _github/
│   ├── GITHUB-SOURCE-INDEX.md
│   └── commerce-api/
├── commerce-admin/
│   ├── Index.md
│   ├── Architecture & Dependencies.md
│   ├── Backend API.md
│   ├── Business Logic.md
│   └── Data Flow.md
├── commerce-api/
│   ├── Index.md
│   ├── Architecture & Dependencies.md
│   ├── Backend API.md
│   ├── Business Logic.md
│   ├── Data Flow.md
│   └── Database Schema.md
└── commerce-gateway/
    ├── Index.md
    ├── Architecture & Dependencies.md
    ├── Data Flow.md
    └── Routing & Security.md
```

## Notes

- `_wiki-sources`와 `_github`는 분석 캐시이며 Wiki 발행 대상이 아니다.
- `_business`는 프로젝트별 문서 요약이 아니라 업무 판단 레이어다.
- `_evidence`는 주요 주장과 코드, 설정, Wiki, GitHub 근거를 연결한다.
