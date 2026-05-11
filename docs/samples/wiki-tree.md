# Wiki Tree Sample

Code-Sonar publishes the local output tree directly below the selected parent page.

```text
Project Analysis
├── Index
├── Business Analysis
│   ├── Business Workflow
│   ├── Scenarios
│   └── Cross Project Traceability
├── Evidence
│   ├── Evidence Ledger
│   └── Evidence Audit
├── commerce-admin
│   ├── Index
│   ├── commerce-admin - Architecture & Dependencies
│   ├── commerce-admin - Backend API
│   ├── commerce-admin - Business Logic
│   └── commerce-admin - Data Flow
├── commerce-api
│   ├── Index
│   ├── commerce-api - Architecture & Dependencies
│   ├── commerce-api - Backend API
│   ├── commerce-api - Business Logic
│   ├── commerce-api - Data Flow
│   └── commerce-api - Database Schema
└── commerce-gateway
    ├── Index
    ├── commerce-gateway - Architecture & Dependencies
    ├── commerce-gateway - Data Flow
    └── commerce-gateway - Routing & Security
```

## Publish Rules

- The output root directory name is not created as a middle page.
- Directory pages are ToC-only.
- Index files publish with visible title `Index`.
- `_wiki-sources` and `_github` are not published.
- Mermaid fences are preserved through the Confluence markdown macro.
