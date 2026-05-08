---
name: code-sonar
description: Use when working inside the code-sonar repository to improve analysis prompts, Claude/Codex plugin settings, Mermaid graph rules, output-tree documentation, or Confluence publishing behavior.
---

# Code-Sonar

Code-Sonar is evidence-first system cartography. Treat source code and config as the ground truth, keep Markdown output topology stable, and publish the output tree to Confluence without flattening or converting Markdown.

## Quick Start

1. Start with a Harness Engineering capsule: goal, scope, assumptions, inspected context, verification, output format.
2. Read `.env` when runtime paths matter.
3. Read `sonar/SONAR.md` for project identity and invariants.
4. Read `sonar/config/sonar-config.md` for path, graph, wiki, and quality rules.
5. Load only the relevant skill:
   - Analysis generation: `sonar/skills/analyze-project/SKILL.md`
   - System graph: `sonar/skills/build-graph/SKILL.md`
   - Wiki publishing: `sonar/skills/publish-wiki/SKILL.md`
6. If `SONAR_WIKI_SOURCE_URLS` is configured, run the Wiki source scan layer before project analysis.
7. If `SONAR_GITHUB_ENABLED=true`, run the GitHub source scan layer with MCP/gh/local git before project analysis.

## Core Contracts

- Evidence before prose: keep file paths, symbols, API paths, tables, topics, and config keys as claims' support.
- Wiki source scan: recursively collect configured Confluence roots into `_wiki-sources/` and treat them as design/policy context, not as stronger evidence than code.
- GitHub source scan: collect PR, commit, workflow, CODEOWNERS, and repository context into `_github/`; treat it as change/operation context, not stronger evidence than code.
- Business workflow layer: after project-level analysis, generate `_business/Business Workflow.md`, `_business/Scenarios.md`, and `_business/Cross Project Traceability.md` as an independent business-decision layer, not a recap of project docs.
- Evidence audit: maintain `_evidence/Evidence Ledger.md` and `_evidence/Evidence Audit.md`; inferred claims must remain marked as inferred.
- Output topology: preserve `SONAR_OUTPUT_DIR/{project}/...`; do not merge project documents into one page.
- Index policy: local `_... Index.md`, `_... System Index.md`, and `Index.md` publish with visible title `Index`.
- System graph: one integrated `flowchart LR` in System Index; detailed sequence/event/storage/dataflow graphs live in project documents.
- System Index operations inventory: when Wiki/source/config contains handover, server, domain, Fusion/RMS, Swagger, DB/cache, monitoring, port, pod, TPS, target-url, service-code, rate limit, or timeout facts, include them in a dedicated operations/server inventory table in the System Index. Do not push this detail into the integrated graph.
- Core algorithm preservation: rate limiters, cache/Redis key distribution, token validation, routing, batch reprocessing, settlement decisions, idempotency, locks, retries, and compensation flows require a Deep Dive in the relevant project document. The Deep Dive must cover problem, algorithm, key/state model, config values, code entry points, operational/performance evidence, and limits/failure modes.
- Reject shallow infrastructure claims: do not let docs say only "uses Redis/Kafka/rate limit"; include key patterns, thresholds, algorithm behavior, and code/config/wiki evidence.
- Sensitive information: never write password/token/secret/Vault values into generated docs or wiki pages. Keep host/port/domain/access path and replace credentials with `redacted`, `문의 필요`, or `환경변수 참조`.
- Mermaid safety: use `flowchart`, quote labels containing slash/colon/URL/API path, avoid fanout shorthand, never start node-label lines with Markdown list syntax such as `1.`, `-`, or `*`, and never put literal backslash+n in Mermaid labels/messages; use `Step 1 - ...`, `S1: ...`, `<br/>`, or a short single-line message instead.
- Wiki publishing: use Confluence markdown macro or `atls wiki ... --markdown-file`; keep Mermaid fences intact.
- Wiki publishing exclusions: never publish `_wiki-sources` or `_github`; publish `_business` as `Business Analysis` and `_evidence` as `Evidence`.
- Wiki directory pages: every directory page is ToC-only. This includes project directories, `Business Analysis`, and `Evidence`. Body must be `# {title}`, `## Pages`, and child page links only. Do not add placeholder prose, summaries, Mermaid, tables, or literal `\n` text to directory pages.
- Business workflow graph: do not make `_business/Business Workflow.md` look like the System Index architecture map. Use numbered business stages from left to right, with stores/monitoring as dotted support edges.
- Business workflow content: require `업무 질문`, `판정 조건`, `담당 프로젝트`, `확인 근거`, `운영 확인 위치`.
- Business scenarios: require at least 6 operation/exception scenarios, including order event missing, LAST_TARGET_URL missing, order-inflow mapping failure, delivery/refund correction, monthly payout consistency failure, and Open API token validation failure.
- Business traceability: structure `_business/Cross Project Traceability.md` by business question with `Question`, `When to use`, `Check order`, `Evidence`, `Decision`, `Next action`.
- Business independence QA: reject `_business` outputs that repeat 70%+ of `System Index`, project `Data Flow`, `Batch Jobs`, or `Business Logic` instead of adding decision/operation value.

## Editing Guidance

- Keep changes small and verifiable.
- Preserve Korean output guidance while keeping technical identifiers in their original spelling.
- Do not add dependencies unless the user explicitly accepts the need.
- Do not thin out document quality to make prompts look different; change architecture, responsibility boundaries, and execution language instead.
- If updating `.claude-plugin`, make it read as Code-Sonar's own operating model: Evidence Ledger, Output Cartography, Graph Contract, Wiki Projection.
- If updating analysis prompts, keep Wiki source scan, GitHub source scan, business layer generation, and evidence audit wired into both common `sonar/` rules and Claude/Codex command surfaces.

## Verification

Use the smallest relevant checks:

```bash
find .claude-plugin .codex -type f | sort
rg -n "flowchart|sequenceDiagram|markdown macro|SONAR_OUTPUT_DIR" .claude-plugin .codex AGENTS.md
rg -n "```mermaid|flowchart|sequenceDiagram" sonar .claude-plugin .codex
```

For wiki behavior changes, also inspect the changed instructions for:

- no output-root middle page
- directory pages before file pages
- directory pages are ToC-only and contain no literal `\n` placeholder text
- separate child page per Markdown file
- Index title policy
- markdown macro preservation
