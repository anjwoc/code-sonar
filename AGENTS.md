## Global Execution Rule

For every coding or repository instruction in this project, first reinterpret the request using Harness Engineering.

### Mandatory Workflow

1. Extract the true goal, constraints, risks, and acceptance criteria.
2. Convert the request into an execution harness:
   - objective
   - scope / non-scope
   - assumptions
   - repo/context to inspect
   - verification steps
   - output format
3. Execute from that harness.
4. Inspect before editing.
5. Prefer small verifiable changes.
6. After changes, run the minimal relevant checks.

### Output Behavior

Briefly show:

- Interpreted Goal
- Plan
- Execution
- Verification

When the request is vague, make the safest reasonable assumptions and state them. When the request is large, split it into phases before editing.

## Code-Sonar Philosophy

Code-Sonar is evidence-first system cartography, not a reused command-tree shell.

- Evidence before prose: source facts, config values, API paths, tables, topics, and file paths come before narrative.
- Output topology matters: `SONAR_OUTPUT_DIR` is the knowledge map, and wiki publishing must preserve that tree.
- Index is a map: System Index keeps one integrated overview graph; detailed flows live in project documents.
- Markdown stays Markdown: Confluence publishing must use markdown macro or `atls ... --markdown-file`.
- Graphs are contracts: use stable Mermaid syntax and avoid speculative edges.

## Repo-Specific Rules

- Read `.env`, `sonar/SONAR.md`, and `sonar/config/sonar-config.md` before changing analysis or publishing behavior.
- For analysis pipeline changes, inspect `sonar/skills/analyze-project/SKILL.md` and relevant templates first.
- For graph changes, inspect `sonar/skills/build-graph/SKILL.md` and Mermaid rules first.
- For wiki changes, inspect `sonar/skills/publish-wiki/SKILL.md` and preserve the output tree rules.
- Never add dependencies unless clearly required.
- Do not replace detailed documentation with thinner prompts just to remove resemblance to another project.

## Verification Shortlist

- Prompt/config edits: `find .claude-plugin .codex -type f | sort` and search for upstream project-specific terminology before finishing.
- Markdown edits: check headings and fenced Mermaid blocks with `rg -n "graph TD|graph LR|--> .*&|& .*-->"`.
- Wiki logic edits: verify root-page, Index-title, markdown-macro, and child-page rules remain explicit.
