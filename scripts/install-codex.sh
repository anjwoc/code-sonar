#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILL_DIR="$CODEX_HOME/skills/code-sonar"

mkdir -p "$SKILL_DIR"

cat > "$SKILL_DIR/SKILL.md" <<EOF
---
name: code-sonar
description: Analyze source trees with the local code-sonar plugin, scan optional Confluence/GitHub roots, generate evidence-backed architecture/business workflow docs, and publish Markdown-native Confluence pages.
---

# Code Sonar

Use this skill when the user asks to run or improve Code-Sonar, regenerate analysis docs, validate evidence, fix Mermaid/wiki publishing, or upload SONAR_OUTPUT_DIR documentation.

## Local Repo

- Plugin repo: \`$REPO_ROOT\`
- Local config: \`$REPO_ROOT/.env\`
- Main rules: \`$REPO_ROOT/sonar/SONAR.md\`

## Workflow

1. Read \`$REPO_ROOT/.env\` and \`$REPO_ROOT/sonar/config/sonar-config.md\`.
2. Resolve \`SONAR_TARGET_DIR\`, \`SONAR_OUTPUT_DIR\`, \`SONAR_SYSTEM_ROOT\`.
3. If \`SONAR_WIKI_SOURCE_URLS\` is set, recursively scan those Confluence roots with \`atls\` and write \`_wiki-sources/\`.
4. If \`SONAR_GITHUB_ENABLED=true\`, scan GitHub MCP/gh/local git sources and write \`_github/\`.
5. Run project-level analysis from \`$REPO_ROOT/sonar/skills/analyze-project/SKILL.md\`.
6. Generate \`_business/Business Workflow.md\`, \`_business/Scenarios.md\`, and \`_business/Cross Project Traceability.md\`.
7. Maintain \`_evidence/Evidence Ledger.md\` and \`_evidence/Evidence Audit.md\`.
8. Publish Markdown through \`atls wiki ... --markdown-file\` so Mermaid fenced blocks render.
9. If Excalidraw output is generated, prefer \`scripts/render-excalidraw-from-mermaid.js\`. Force Arrow Type \`직각\`: JSON arrows must use \`elbowed: true\`, \`roundness: null\`, port/rail routing, and horizontal/vertical \`points\`; diagonal two-point arrows, non-target node crossings, and label-node overlaps are rejected. Storage/external-resource edges must be protocol-colored: \`JDBC/JPA\` blue, \`Redis\` rose, \`Spring Data\` violet, \`Elasticsearch\`/\`index/read\` amber, with labels in the same color family.

## Deep Research Mode (/sonar:deep)

Use when the user asks for deep analysis of a **single project** — e.g. "affiliate 프로젝트 딥리서치", "/sonar:deep", or when a questions file is provided.

1. Read \`$REPO_ROOT/sonar/skills/deep-research/SKILL.md\` instead of analyze-project.
2. Load \`SONAR_DEEP_TARGET\` (single project path or name), \`SONAR_DEEP_QUESTIONS\` (optional questions file), \`SONAR_DEEP_ENVS\`, \`SONAR_CROSS_REPO_SEARCH\`, \`SONAR_CROSS_REPO_ORG\` from \`.env\`.
3. Parse questions file (\`## Q\` sections) → extract \`SEARCH_KEYWORDS\` and \`FOCUS_AREAS\`.
4. If \`SONAR_CROSS_REPO_SEARCH=true\`, run \`$REPO_ROOT/sonar/agents/cross-repo-tracer.md\` with GitHub MCP.
5. Spawn in parallel: \`env-matrix-analyst\`, \`integration-flow-analyst\`, \`business-workflow-analyst\` (deep), \`analyst-backend\` (deep).
6. Generate \`QUESTION-ANSWER.md\` with \`[code: file:line]\` evidence for every question.
7. Output to \`{output_dir}/{project}/deep-research/\` with \`DEEP-RESEARCH.md\` as the unified index.

Key agents: \`$REPO_ROOT/sonar/agents/env-matrix-analyst.md\`, \`integration-flow-analyst.md\`, \`cross-repo-tracer.md\`
Key templates: \`$REPO_ROOT/sonar/templates/DEEP-RESEARCH.md\`, \`ENV-MATRIX.md\`, \`INTEGRATION-FLOW.md\`, \`QUESTION-ANSWER.md\`

## Wiki Tree Rules

- Do not create a middle page named after \`SONAR_OUTPUT_DIR\`.
- Publish children of \`SONAR_OUTPUT_DIR\` directly under the selected parent page.
- Directories become parent pages.
- Directory/folder pages are ToC-only. This includes project directories, \`Business Analysis\`, and \`Evidence\`. Use \`# {title}\`, \`## Pages\`, and child page links only; do not add placeholder prose, summaries, Mermaid, tables, or literal \`\\n\` text.
- Markdown files become child pages.
- \`_... Index.md\`, \`_... System Index.md\`, and \`Index.md\` are uploaded as visible title \`Index\`.
- Never publish \`_wiki-sources\` or \`_github\`; publish \`_business\` as \`Business Analysis\` and \`_evidence\` as \`Evidence\`.

## Business Layer Rules

- \`_business\` is a business-decision layer, not a recap of project docs.
- \`Business Workflow.md\` must include business questions, decision conditions, responsible projects, evidence, and operating check locations.
- \`Scenarios.md\` must include at least 6 operation/exception scenarios: order event missing, LAST_TARGET_URL missing, order-inflow mapping failure, delivery/refund correction, monthly payout consistency failure, Open API token validation failure.
- \`Cross Project Traceability.md\` must be a business-question investigation guide with \`Question\`, \`When to use\`, \`Check order\`, \`Evidence\`, \`Decision\`, and \`Next action\`.
- Reject \`_business\` outputs that mostly repeat System Index or project \`Data Flow\`/\`Batch Jobs\`.
EOF

echo "Installed Code-Sonar Codex skill to $SKILL_DIR"
echo "Open a new Codex session or reload skills before using it."
