#!/usr/bin/env python3
"""
ATLS Harness Analysis

QA / GEMINI 중심의 harness-engineering 산출물을 만들기 위한 보조 모듈.
Jira live issue 결과가 있으면 병합하고, 없으면 adcenter 문서와 코드 흔적을
기반으로 worklist / analysis / prompt pack을 생성한다.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ATLS_DOC_RELATIVE_PATHS = [
    "docs/guides/USER_GUIDE.md",
    "docs/design/ATLS_GENERIC_CLI_DESIGN.md",
    "docs/design/ATLS_DAILY_TRIAGE_DESIGN.md",
    "docs/guides/MCP_vs_Scripts_Guide.md",
]

PROJECT_CONTEXT_CANDIDATES = [
    "README.md",
    "README",
    "CONTRIBUTING.md",
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
]

OPTIONAL_PROJECT_DOC_PATTERNS = {
    "manual_guide": [
        r"manual[-_ ]test[-_ ]guide\.md$",
        r"test[-_ ]guide\.md$",
    ],
    "checklist": [
        r"verification[-_ ]checklist\.md$",
        r"checklist\.md$",
    ],
    "gap_analysis": [
        r"gap[-_ ]analysis.*\.md$",
        r"analysis.*\.md$",
    ],
}

CATEGORY_SEARCH_HINTS = {
    "validation": ["validation", "validator", "schema", "message", "budget", "bid", "period", "error"],
    "payload mapping": ["payload", "request", "response", "service", "action", "api", "client", "mapper"],
    "state persistence": ["store", "slice", "state", "persist", "storage", "cache", "context", "session"],
    "modal UX": ["modal", "dialog", "alert", "confirm", "popup", "layer", "drawer"],
    "pagination/list rendering": ["list", "table", "pagination", "search", "filter", "grid", "column"],
    "naming/suffix policy": ["name", "title", "suffix", "naming", "slug", "label"],
    "backend dependency": ["service", "client", "api", "integration", "query", "backend", "response"],
    "QA 문서 정합성": ["qa", "test", "spec", "checklist", "manual", "verification", "docs"],
    "spec undecided": ["spec", "prd", "design", "requirement", "api", "policy"],
}

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "after", "before", "when", "then",
    "issue", "task", "bug", "fix", "feat", "feature", "project", "summary", "status", "need", "needs",
    "있는", "대한", "관련", "수정", "처리", "문제", "이슈", "작업", "기능", "화면", "항목", "확인",
}

LOW_SIGNAL_DOC_PATTERNS = (
    "docs/prompts",
    "docs/troubleshooting",
    "docs/example",
    "docs/examples",
)

TRUSTED_DOC_PREFIXES = (
    "docs/prd/",
    "docs/api/",
    "docs/openapi/",
)

DIRECT_CHECK_TEXT = "직접 확인 필요"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _project_label(workspace_root: Path) -> str:
    return workspace_root.name or "project"


def _safe_relpath(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except Exception:
        return str(path)


def _discover_context_docs(workspace_root: Path, limit: int = 12) -> list[str]:
    docs: list[Path] = []
    for relative in PROJECT_CONTEXT_CANDIDATES:
        path = workspace_root / relative
        if path.exists():
            docs.append(path)
    docs_root = workspace_root / "docs"
    if docs_root.exists():
        for prefix in TRUSTED_DOC_PREFIXES:
            prefix_root = workspace_root / prefix
            if prefix_root.exists():
                matches = sorted(prefix_root.rglob("*.md"))
                if matches:
                    docs.append(matches[0])
    deduped: list[str] = []
    for path in docs:
        rel = _safe_relpath(path, workspace_root)
        if rel not in deduped:
            deduped.append(rel)
    return [str(workspace_root / rel) for rel in deduped[:limit]]


def _discover_optional_analysis_docs(workspace_root: Path) -> dict[str, Path]:
    docs_root = workspace_root / "docs"
    if not docs_root.exists():
        return {}
    found: dict[str, Path] = {}
    for key, patterns in OPTIONAL_PROJECT_DOC_PATTERNS.items():
        for pattern in patterns:
            matches = sorted(
                path for path in docs_root.rglob("*.md")
                if re.search(pattern, str(path.relative_to(workspace_root)), re.IGNORECASE)
            )
            if matches:
                found[key] = matches[0]
                break
    return found


def _trusted_doc_paths(workspace_root: Path) -> list[Path]:
    paths: list[Path] = []
    for prefix in TRUSTED_DOC_PREFIXES:
        root = workspace_root / prefix
        if root.exists():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    return paths


def _extract_search_terms(text: str, limit: int = 8) -> list[str]:
    raw_tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|[가-힣]{2,}", text or "")
    tokens = []
    for token in raw_tokens:
        lowered = token.lower()
        if lowered in STOPWORDS:
            continue
        if re.fullmatch(r"(qa|prd|ux|ui|api)", lowered):
            tokens.append(token)
            continue
        if len(lowered) < 3 and not re.search(r"[가-힣]", token):
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens[:limit]


def _shorten_text(text: str, limit: int = 180) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _clean_issue_key_text(text: str) -> str:
    return re.sub(r"(GEMINI-\d+|QA-\d+)\?", r"\1", text or "")


def _cli_localizer_bundle():
    from atls.cli import workflow_contains_hangul, workflow_localize_text, workflow_translate_english_title

    return workflow_contains_hangul, workflow_localize_text, workflow_translate_english_title


def _cli_daily_review_bundle():
    from atls.cli import render_workflow_issue_section, workflow_compact_counts, workflow_markdown_table, workflow_stale_label

    return render_workflow_issue_section, workflow_compact_counts, workflow_markdown_table, workflow_stale_label


def _korean_only_summary(text: str, fallback: str = DIRECT_CHECK_TEXT) -> str:
    workflow_contains_hangul, workflow_localize_text, workflow_translate_english_title = _cli_localizer_bundle()
    cleaned = _clean_issue_key_text(re.sub(r"\s+", " ", text or "").strip())
    if not cleaned:
        return "-"
    localized = workflow_localize_text(cleaned, 260)
    candidate = localized or workflow_translate_english_title(cleaned)
    candidate = _clean_issue_key_text(candidate)
    if not candidate:
        return fallback
    if not workflow_contains_hangul(candidate):
        return fallback
    if re.search(r"[A-Za-z]{4,}", candidate):
        return fallback
    return candidate


def _korean_problem_statement(
    title: str,
    current_status: str,
    issue_key: str = "",
    issue_title_ko: str = "",
    issue_situation_ko: str = "",
) -> str:
    if issue_situation_ko and issue_situation_ko != "-":
        return issue_situation_ko
    subject = issue_key or _clean_issue_key_text(title)
    if issue_title_ko and issue_title_ko != "-":
        if current_status == "regression_check":
            return f"{subject} 이슈는 {issue_title_ko}와 관련해 구현 반영 후 회귀 검증과 상태 확인이 필요한 단계다."
        return f"{subject} 이슈는 {issue_title_ko}와 관련해 현재 상태와 구현 맥락을 함께 확인해야 하는 단계다."
    if current_status == "regression_check":
        return f"{subject} 이슈는 구현 반영 후 회귀 검증과 상태 확인이 필요한 단계다."
    return f"{subject} 이슈는 현재 상태와 구현 맥락을 함께 확인해야 하는 단계다."


def _compose_current_situation_ko(
    issue_key: str,
    issue_status: str,
    issue_title_ko: str,
    description_ko: str,
    comment_ko: str,
    current_situation_ko: str,
    next_action_ko: str,
) -> str:
    if current_situation_ko and current_situation_ko != "-":
        lines = [current_situation_ko]
        if next_action_ko and next_action_ko != "-" and next_action_ko not in current_situation_ko:
            lines.append(f"다음 확인 포인트는 {next_action_ko}이다.")
        return " ".join(lines)

    base = description_ko if description_ko and description_ko != "-" else issue_title_ko
    if not base or base == "-":
        base = DIRECT_CHECK_TEXT
    lines = []
    if base == DIRECT_CHECK_TEXT:
        lines.append(f"{issue_key} 이슈는 Jira 링크에서 본문 직접 확인이 필요하다." if issue_key else "Jira 링크에서 본문 직접 확인이 필요하다.")
    else:
        lines.append(f"{issue_key} 이슈의 핵심 내용은 {base}이다." if issue_key else f"핵심 내용은 {base}이다.")
    if issue_status:
        lines.append(f"현재 Jira 상태는 {issue_status}이다.")
    if comment_ko and comment_ko != "-":
        lines.append(f"최근 코멘트 기준으로는 {comment_ko}")
    if next_action_ko and next_action_ko != "-":
        lines.append(f"다음 확인 포인트는 {next_action_ko}이다.")
    return " ".join(line for line in lines if line).strip()


def _extract_table_after_heading(text: str, heading: str) -> list[list[str]]:
    if heading not in text:
        return []
    lines = text[text.index(heading):].splitlines()[1:]
    raw_rows = []
    started = False
    for line in lines:
        if line.strip().startswith("|"):
            raw_rows.append(line.rstrip())
            started = True
            continue
        if started:
            break
    rows: list[list[str]] = []
    for line in raw_rows:
        if set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if parts:
            rows.append(parts)
    if rows:
        return rows[1:]
    return []


def _extract_section_bullets(text: str, heading: str) -> dict[str, list[str]]:
    if heading not in text:
        return {}
    lines = text[text.index(heading):].splitlines()[1:]
    current = ""
    sections: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("### "):
            current = stripped[4:].strip()
            continue
        if stripped.startswith("- ") and current:
            sections[current].append(stripped[2:].strip())
    return dict(sections)


def _extract_open_gap_table(text: str) -> list[dict]:
    rows = _extract_table_after_heading(text, "### 스펙 확인 필요")
    items = []
    for row in rows:
        if len(row) < 3:
            continue
        items.append(
            {
                "item": row[0],
                "current_state": row[1],
                "needed_action": row[2],
            }
        )
    return items


def _normalize_issue_list(raw: str) -> list[str]:
    return [match for match in re.findall(r"(GEMINI-\d+|QA-\d+)", raw or "")]


def _parse_checklist_tasks(text: str) -> dict[str, dict]:
    rows = _extract_table_after_heading(text, "## 완료된 태스크 전체 목록")
    tasks: dict[str, dict] = {}
    for row in rows:
        if len(row) < 4:
            continue
        task_cell = row[0]
        status = row[1]
        commit = row[2]
        note = row[3]
        match = re.search(r"Task\s+([A-Z]-\d+)\s+(.*)", task_cell)
        if not match:
            continue
        task_id = match.group(1)
        title = match.group(2).strip()
        tasks[task_id] = {
            "task_id": task_id,
            "title": title,
            "completion_state": status,
            "commit": commit.strip("` "),
            "note": note,
            "source_doc": "docs/qa/2026-04-02-adcenter-registration-verification-checklist.md",
            "current_status": "regression_check" if "완료" in status else "pending",
        }
    return tasks


def _parse_manual_task_mapping(text: str) -> dict[str, dict]:
    rows = _extract_table_after_heading(text, "## 테스트 완료 후 Jira 상태 변경")
    mapping: dict[str, dict] = {}
    for row in rows:
        if len(row) < 3:
            continue
        issues = _normalize_issue_list(row[0])
        task_ids = [task.strip("` ") for task in re.findall(r"[A-Z]-\d+", row[1])]
        criteria = row[2]
        for task_id in task_ids:
            entry = mapping.setdefault(task_id, {"related_issues": [], "criteria": []})
            entry["related_issues"].extend(issue for issue in issues if issue not in entry["related_issues"])
            if criteria not in entry["criteria"]:
                entry["criteria"].append(criteria)
    return mapping


def _parse_gap_analysis(text: str) -> dict[str, list[str]]:
    return _extract_section_bullets(text, "## 중요도 높은 수정 태스크 리스트")


def _parse_gap_highlights(text: str) -> list[str]:
    if "## 핵심 해석" not in text:
        return []
    lines = text[text.index("## 핵심 해석"):].splitlines()[1:]
    bullets = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def _issue_lookup(jira_issues: list[dict]) -> dict[str, dict]:
    return {issue.get("key"): issue for issue in jira_issues if issue.get("key")}


def _derive_workflow_bucket(issue: dict | None, current_status: str) -> str:
    if issue and issue.get("workflow_bucket"):
        return issue["workflow_bucket"]
    if current_status == "regression_check":
        return "review"
    if current_status in {"pending", "needs_spec"}:
        return "todo"
    return "other"


def _derive_risk(issue: dict | None, related_issues: list[str], title: str) -> str:
    if issue and issue.get("risk_level"):
        return issue["risk_level"]
    lowered = (title or "").lower()
    if related_issues or any(keyword in lowered for keyword in ("payload", "validation", "period", "모달", "bid", "예산")):
        return "high"
    return "medium"


def _derive_action(issue: dict | None, title: str, current_status: str) -> str:
    if issue and issue.get("action_needed"):
        actions = issue["action_needed"]
        if isinstance(actions, list) and actions:
            return actions[0]
    lowered = (title or "").lower()
    if current_status == "regression_check":
        return "needs_qa_retest"
    if "spec" in lowered or "스펙" in lowered:
        return "needs_prd_confirmation"
    if "ux" in lowered or "문구" in lowered or "모달" in lowered:
        return "needs_ux_confirmation"
    return "needs_dev"


def _derive_category(text: str) -> str:
    lowered = (text or "").lower()
    if any(keyword in lowered for keyword in ("validation", "기간", "일예산", "입찰가", "메시지")):
        return "validation"
    if any(keyword in lowered for keyword in ("payload", "bidword", "itemblacklist", "전달", "매핑")):
        return "payload mapping"
    if any(keyword in lowered for keyword in ("복원", "localstorage", "state", "기본 선택", "fallback")):
        return "state persistence"
    if any(keyword in lowered for keyword in ("모달", "confirm", "팝업", "취소")):
        return "modal UX"
    if any(keyword in lowered for keyword in ("페이지네이션", "목록", "컬럼", "전체선택", "검색")):
        return "pagination/list rendering"
    if any(keyword in lowered for keyword in ("suffix", "이름", "campaign", "group")):
        return "naming/suffix policy"
    if any(keyword in lowered for keyword in ("backend", "api", "count", "0으로", "null", "응답")):
        return "backend dependency"
    if any(keyword in lowered for keyword in ("qa 표", "qa 문서", "체크리스트", "문서")):
        return "QA 문서 정합성"
    if any(keyword in lowered for keyword in ("스펙", "확정", "확인 필요")):
        return "spec undecided"
    return "payload mapping"


def _default_touchpoints(workspace_root: Path, category: str) -> list[str]:
    candidates: list[Path] = []
    preferred_roots = [
        workspace_root / "src",
        workspace_root / "app",
        workspace_root / "packages",
        workspace_root / "services",
        workspace_root / "actions",
        workspace_root / "tests",
    ]
    if category in {"backend dependency", "spec undecided"}:
        preferred_roots.extend(Path(path) for path in _trusted_doc_paths(workspace_root)[:3])
    hints = CATEGORY_SEARCH_HINTS.get(category, [])
    for root in preferred_roots:
        if root.exists():
            candidates.append(root)
    if not candidates:
        candidates.append(workspace_root)
    return [str(path) for path in candidates[:4]]


def _search_code_references(workspace_root: Path, identifiers: list[str]) -> dict[str, list[str]]:
    identifiers = [identifier for identifier in identifiers if identifier]
    if not identifiers:
        return {}
    if not shutil_which("rg"):
        return {}
    pattern = r"\b(?:%s)\b" % "|".join(re.escape(identifier) for identifier in identifiers)
    targets = []
    for relative in ("src", "app", "packages", "services", "actions", "lib", "tests"):
        path = workspace_root / relative
        if path.exists():
            targets.append(str(path))
    if not targets:
        return {}
    proc = subprocess.run(
        ["rg", "-n", "-S", pattern, *targets],
        capture_output=True,
        text=True,
        check=False,
    )
    refs: dict[str, list[str]] = defaultdict(list)
    if proc.returncode not in (0, 1):
        return {}
    for line in proc.stdout.splitlines():
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        path, lineno, _, content = parts
        refs[path].append(f"{path}:{lineno} {content.strip()}")
    return dict(refs)


def _search_trusted_doc_references(workspace_root: Path, identifiers: list[str]) -> dict[str, list[str]]:
    identifiers = [identifier for identifier in identifiers if identifier]
    if not identifiers or not shutil_which("rg"):
        return {}
    pattern = r"\b(?:%s)\b" % "|".join(re.escape(identifier) for identifier in identifiers)
    targets = [str(path) for path in _trusted_doc_paths(workspace_root)]
    if not targets:
        return {}
    proc = subprocess.run(
        ["rg", "-n", "-S", pattern, *targets],
        capture_output=True,
        text=True,
        check=False,
    )
    refs: dict[str, list[str]] = defaultdict(list)
    if proc.returncode not in (0, 1):
        return {}
    for line in proc.stdout.splitlines():
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        path, lineno, _, content = parts
        refs[path].append(f"{path}:{lineno} {content.strip()}")
    return dict(refs)


def shutil_which(binary: str) -> str | None:
    for path in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(path) / binary
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _discover_paths_by_keywords(workspace_root: Path, keywords: list[str], limit: int = 8) -> list[str]:
    paths: list[str] = []
    candidates = []
    for root_name in ("src", "app", "packages", "services", "actions", "docs", "tests"):
        root = workspace_root / root_name
        if root.exists():
            candidates.append(root)
    if not candidates:
        candidates.append(workspace_root)

    for root in candidates:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            haystack = str(path.relative_to(workspace_root)).lower()
            if any(keyword.lower() in haystack for keyword in keywords):
                full = str(path)
                if full not in paths:
                    paths.append(full)
                if len(paths) >= limit:
                    return paths
    return paths


def _target_roots(workspace_root: Path) -> list[Path]:
    roots = []
    for root_name in ("src", "app", "packages", "services", "actions", "lib", "tests"):
        root = workspace_root / root_name
        if root.exists():
            roots.append(root)
    return roots or [workspace_root]


def _path_weight(path: str, workspace_root: Path) -> int:
    rel = _safe_relpath(Path(path), workspace_root).lower()
    score = 0
    if rel.startswith(("src/", "app/", "packages/", "services/", "actions/", "lib/")):
        score += 10
    if rel.startswith(("src/components/", "src/features/", "src/services/", "src/actions/")):
        score += 6
    if rel.startswith(("docs/prd/", "docs/api/", "docs/openapi/")):
        score += 7
    elif rel.startswith(("docs/", "tests/")):
        score += 1
    if rel.endswith((".ts", ".tsx", ".js", ".jsx")):
        score += 4
    if rel.endswith(".json"):
        score += 2
    if rel.endswith(".md"):
        score += 1
    if any(rel.startswith(pattern) for pattern in LOW_SIGNAL_DOC_PATTERNS):
        score -= 6
    if "/report/" in rel:
        score -= 2
    return score


def _rank_paths_for_text_context(workspace_root: Path, text_context: str, category: str, limit: int = 8) -> list[str]:
    if not shutil_which("rg"):
        return _discover_paths_by_keywords(workspace_root, _extract_search_terms(text_context) + CATEGORY_SEARCH_HINTS.get(category, []), limit=limit)

    terms = _extract_search_terms(text_context, limit=10) + CATEGORY_SEARCH_HINTS.get(category, [])[:4]
    terms = [term for term in terms if term.lower() not in STOPWORDS]
    if not terms:
        return []

    scores: dict[str, int] = defaultdict(int)
    roots = [str(root) for root in _target_roots(workspace_root)]
    for term in terms:
        proc = subprocess.run(
            ["rg", "-l", "-i", term, *roots],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode not in (0, 1):
            continue
        for line in proc.stdout.splitlines():
            path = line.strip()
            if not path:
                continue
            rel = _safe_relpath(Path(path), workspace_root).lower()
            weight = 2
            if term.lower() in rel:
                weight += 4
            weight += _path_weight(path, workspace_root)
            scores[path] += weight

    if len(scores) < max(2, limit // 2) and category in {"backend dependency", "spec undecided", "QA 문서 정합성"}:
        doc_roots = [str(path) for path in _trusted_doc_paths(workspace_root)]
        for term in terms:
            if not doc_roots:
                break
            proc = subprocess.run(
                ["rg", "-l", "-i", term, *doc_roots],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode not in (0, 1):
                continue
            for line in proc.stdout.splitlines():
                path = line.strip()
                if not path:
                    continue
                rel = _safe_relpath(Path(path), workspace_root).lower()
                weight = 1
                if term.lower() in rel:
                    weight += 4
                weight += _path_weight(path, workspace_root)
                scores[path] += weight

    ranked = sorted(scores.items(), key=lambda item: (-item[1], _safe_relpath(Path(item[0]), workspace_root)))
    return [path for path, _ in ranked[:limit]]


def _rank_reference_paths(workspace_root: Path, refs: dict[str, list[str]]) -> list[str]:
    ranked = sorted(
        refs.keys(),
        key=lambda path: (-_path_weight(path, workspace_root), _safe_relpath(Path(path), workspace_root)),
    )
    return ranked


def _touchpoint_summary(
    workspace_root: Path,
    identifiers: list[str],
    category: str,
    text_context: str = "",
) -> tuple[list[str], list[str]]:
    normalized_identifiers = [identifier for identifier in identifiers if identifier and re.search(r"(GEMINI-\d+|QA-\d+)", identifier)]
    search_terms = normalized_identifiers + _extract_search_terms(text_context) + CATEGORY_SEARCH_HINTS.get(category, [])[:3]
    refs = _search_code_references(workspace_root, search_terms)
    if not refs and category in {"backend dependency", "spec undecided", "QA 문서 정합성"}:
        refs = _search_trusted_doc_references(workspace_root, search_terms)
    touchpoints = _rank_reference_paths(workspace_root, refs)[:6]
    evidence = []
    for path in touchpoints:
        for entry in refs.get(path, [])[:2]:
            evidence.append(_shorten_text(entry, 180))
    evidence = evidence[:8]
    if not touchpoints:
        touchpoints = _rank_paths_for_text_context(workspace_root, text_context, category, limit=6)
    if not touchpoints:
        touchpoints = _discover_paths_by_keywords(workspace_root, _extract_search_terms(text_context) + CATEGORY_SEARCH_HINTS.get(category, []))
    if not touchpoints:
        touchpoints = _default_touchpoints(workspace_root, category)
    return touchpoints, evidence


def _task_approach(category: str) -> str:
    mapping = {
        "validation": "등록 화면과 수정 화면에서 UI validation을 선행하고, 서비스/서버 validation과 문구를 맞추는 이중 방어 구조다.",
        "payload mapping": "GroupCreationModule에서 사용자 입력을 payload로 조립하고 registration service/action 계층에서 최종 API shape를 확정하는 구조다.",
        "state persistence": "로컬 상태, Redux 저장 상태, localStorage fallback을 조합해 등록 플로우 상태를 유지하는 구조다.",
        "modal UX": "공통 레이어 컴포넌트와 화면별 상태 플래그로 열림/닫힘/confirm 분기를 제어하는 구조다.",
        "pagination/list rendering": "상품 선택 모달과 그룹 생성 화면에서 파생 목록을 계산하고 현재 페이지 상태에 따라 렌더링하는 구조다.",
        "naming/suffix policy": "추천 이름 생성과 저장 payload 이름을 화면 상태에서 계산하고 scene/type 별 규칙을 적용하는 구조다.",
        "backend dependency": "프론트는 service/action 계층에서 API 응답을 받아 매핑하지만 count/추천값의 source of truth는 백엔드에 의존한다.",
        "QA 문서 정합성": "코드 반영 결과와 QA 문서/체크리스트를 수동 검증 문서로 연결하는 운영 구조다.",
        "spec undecided": "현재 코드보다 상위 결정이 필요한 항목을 문서에서 보류하고, 구현은 최소 안전장치만 두는 구조다.",
    }
    return mapping.get(category, "등록 UI와 service 계층을 연결해 동작을 구현하는 구조다.")


def _task_problem(title: str, note: str, current_status: str) -> str:
    if current_status == "regression_check":
        return f"{title}는 코드 반영은 되었지만 QA 회귀 검증과 문서 정합성 확인이 계속 필요한 상태다."
    if "스펙" in note or "확정" in note:
        return f"{title}는 기대 동작이 완전히 확정되지 않아 구현보다 스펙 확인이 먼저 필요한 상태다."
    return f"{title}에서 화면 동작, payload, 문구, 상태 복원 중 하나가 기대값과 어긋날 가능성이 남아 있는 상태다."


def _issue_context_map(jira_issues: list[dict]) -> dict[str, dict]:
    context = {}
    for issue in jira_issues:
        key = issue.get("key")
        if not key:
            continue
        analysis = issue.get("analysis", {}) or {}
        detail = issue.get("detail_analysis", {}) or {}
        comment_entries = detail.get("comment_entries") or []
        recent_comment_localized = ""
        if comment_entries:
            latest = comment_entries[-1] or {}
            recent_comment_localized = latest.get("localized_body") or ""
        issue_title_ko = _korean_only_summary(issue.get("summary", ""))
        issue_body_ko = _korean_only_summary(
            detail.get("description_localized")
            or analysis.get("description_excerpt")
            or detail.get("description_statement", "")
        )
        issue_comment_ko = _korean_only_summary(
            recent_comment_localized or analysis.get("recent_comment_excerpt", ""),
            fallback="-",
        )
        issue_current_situation_ko = _korean_only_summary(
            detail.get("current_situation_statement") or detail.get("situation_analysis_statement", ""),
            fallback="",
        )
        next_action_ko = _korean_only_summary(
            analysis.get("next_recommended_action") or detail.get("next_action_statement", ""),
            fallback="-",
        )
        context[key] = {
            "key": key,
            "url": issue.get("url", ""),
            "status": issue.get("status", ""),
            "workflow_bucket": issue.get("workflow_bucket", ""),
            "priority": issue.get("priority", ""),
            "assignee": issue.get("assignee", ""),
            "summary": issue.get("summary", ""),
            "description_excerpt": analysis.get("description_excerpt") or detail.get("description_statement", ""),
            "recent_comment_excerpt": analysis.get("recent_comment_excerpt", ""),
            "next_action": analysis.get("next_recommended_action") or detail.get("next_action_statement", ""),
            "current_situation": detail.get("current_situation_statement") or detail.get("situation_analysis_statement", ""),
            "attention_bucket": issue.get("attention_bucket", ""),
            "risk_level": issue.get("risk_level", ""),
            "summary_ko": issue_title_ko,
            "body_summary_ko": issue_body_ko,
            "comment_summary_ko": issue_comment_ko,
            "current_situation_ko": _compose_current_situation_ko(
                key,
                issue.get("status", ""),
                issue_title_ko,
                issue_body_ko,
                issue_comment_ko,
                issue_current_situation_ko,
                next_action_ko,
            ),
            "next_action_ko": next_action_ko,
        }
    return context


def _first_related_issue_key(raw: str) -> str:
    issues = _normalize_issue_list(raw)
    return issues[0] if issues else ""


def _task_root_cause(category: str) -> str:
    mapping = {
        "validation": "등록 화면과 수정 화면의 validation 규칙/문구가 분산되어 있거나 UI와 서버 검증 타이밍이 어긋나기 쉽다.",
        "payload mapping": "보이는 값과 실제 API payload source가 달라질 때 회귀가 발생하기 쉽다.",
        "state persistence": "scene/type 전환, localStorage fallback, Redux reset 시점이 엇갈리면 복원 불일치가 생긴다.",
        "modal UX": "닫기 경로가 여러 개인데 변경 감지와 confirm 조건이 한곳에 모이지 않으면 누락이 생긴다.",
        "pagination/list rendering": "필터링된 목록, 전체 선택, 페이지 보정이 다른 파생 상태를 쓰면 빈 페이지나 숨겨진 항목 선택 버그가 생긴다.",
        "naming/suffix policy": "추천명 규칙, sceneId, count API 응답, 표시 문자열 계산이 분산돼 정합성이 깨지기 쉽다.",
        "backend dependency": "프론트 fallback만으로는 API raw 응답 불일치나 0/null 정합성 문제를 해결할 수 없다.",
        "QA 문서 정합성": "코드는 수정됐지만 QA 체크 문서가 뒤늦게 반영되면 상태 판단이 엇갈린다.",
        "spec undecided": "기획/백엔드/QA 합의 전까지는 기준값이 흔들려 구현을 고정하기 어렵다.",
    }
    return mapping.get(category, "UI 상태와 API 연결 지점이 분산되어 회귀 여지가 있다.")


def _task_fix(category: str) -> str:
    mapping = {
        "validation": "상수/문구를 공통화하고 등록/수정 화면, service validation, 수동 QA 체크리스트를 하나의 기준으로 맞춘다.",
        "payload mapping": "payload 조립 위치를 좁히고 service 계층 테스트와 Network QA 시나리오를 함께 유지한다.",
        "state persistence": "scene/type source of truth를 하나로 줄이고 reset 시점과 localStorage fallback 우선순위를 명시한다.",
        "modal UX": "모든 닫기 경로를 공통 confirm 로직으로 수렴시키고 변경 감지 기준을 명시한다.",
        "pagination/list rendering": "displayed list 기준으로 전체선택/페이지 계산을 통일하고 페이지 감소 시 보정 로직을 둔다.",
        "naming/suffix policy": "추천명 생성 helper와 count 응답 파싱을 한곳으로 모으고 표시값/전달값을 같은 source로 계산한다.",
        "backend dependency": "프론트 로그와 raw API 응답을 함께 수집해 원인을 분리하고, 백엔드 확인 전에는 fallback 범위를 문서화한다.",
        "QA 문서 정합성": "체크리스트 status, 커밋, 연결 이슈를 주기적으로 갱신하고 회귀 테스트 케이스를 문서와 맞춘다.",
        "spec undecided": "기획/QA/API 팀 확인 항목을 먼저 닫고 그 결과를 기준으로 코드와 QA 문서를 동시에 갱신한다.",
    }
    return mapping.get(category, "source of truth를 줄이고 검증 시나리오를 코드와 문서 양쪽에 남긴다.")


def _task_validation_plan(task_id: str, related_issues: list[str], current_status: str) -> str:
    if current_status == "regression_check":
        return f"{task_id}는 수동 QA 가이드 또는 프로젝트 검증 문서 기준으로 회귀 테스트하고, 연결 이슈 {', '.join(related_issues) or '없음'} 상태를 다시 맞춘다."
    if related_issues:
        return f"Network payload, 화면 메시지, 저장 결과를 함께 확인하고 {', '.join(related_issues)} 이슈 상태와 연결한다."
    return "문서 기대값, 실제 UI, payload 또는 저장 결과를 함께 대조해 기준을 확정한다."


def _build_qa_worklist(
    checklist_tasks: dict[str, dict],
    manual_mapping: dict[str, dict],
    jira_by_key: dict[str, dict],
) -> list[dict]:
    rows = []
    for task_id in sorted(checklist_tasks):
        task = dict(checklist_tasks[task_id])
        related_issues = manual_mapping.get(task_id, {}).get("related_issues", [])
        criteria = manual_mapping.get(task_id, {}).get("criteria", [])
        linked_issue = jira_by_key.get(related_issues[0]) if related_issues else None
        task.update(
            {
                "related_issue": ", ".join(related_issues),
                "workflow_bucket": _derive_workflow_bucket(linked_issue, task["current_status"]),
                "risk_level": _derive_risk(linked_issue, related_issues, task["title"]),
                "action_needed": _derive_action(linked_issue, task["title"], task["current_status"]),
                "one_line_summary": task["title"],
                "evidence": criteria + [task["note"]],
            }
        )
        rows.append(task)
    return rows


def _build_qa_worklist_from_jira(jira_issues: list[dict]) -> list[dict]:
    rows = []
    for issue in jira_issues:
        if issue.get("track") != "qa":
            continue
        actions = issue.get("action_needed") or []
        rows.append(
            {
                "task_id": issue.get("key", ""),
                "title": issue.get("summary", issue.get("key", "")),
                "completion_state": issue.get("status", ""),
                "commit": "",
                "note": issue.get("analysis", {}).get("description_excerpt", ""),
                "source_doc": "live_jira",
                "current_status": issue.get("workflow_bucket") or "pending",
                "related_issue": issue.get("key", ""),
                "workflow_bucket": issue.get("workflow_bucket") or "other",
                "risk_level": issue.get("risk_level") or "medium",
                "action_needed": actions[0] if actions else "needs_dev",
                "one_line_summary": issue.get("summary", issue.get("key", "")),
                "evidence": [
                    f"Jira status={issue.get('status')}",
                    f"Priority={issue.get('priority')}",
                    issue.get("analysis", {}).get("next_recommended_action", ""),
                ],
            }
        )
    return rows


def _build_gemini_worklist(
    qa_worklist: list[dict],
    jira_issues: list[dict],
) -> list[dict]:
    issue_map: dict[str, dict] = {}
    for row in qa_worklist:
        for issue in _normalize_issue_list(row.get("related_issue", "")):
            entry = issue_map.setdefault(
                issue,
                {
                    "related_issue": issue,
                    "task_ids": [],
                    "source_docs": set(),
                    "current_status": row["current_status"],
                    "workflow_bucket": row["workflow_bucket"],
                    "risk_level": row["risk_level"],
                    "action_needed": row["action_needed"],
                    "one_line_summary": row["title"],
                    "evidence": [],
                },
            )
            if row["task_id"] not in entry["task_ids"]:
                entry["task_ids"].append(row["task_id"])
            entry["source_docs"].add(row["source_doc"])
            entry["evidence"].extend(row["evidence"][:2])

    for issue in jira_issues:
        if issue.get("track") != "gemini":
            continue
        key = issue.get("key")
        if not key:
            continue
        entry = issue_map.setdefault(
            key,
            {
                "related_issue": key,
                "task_ids": [],
                "source_docs": set(),
                "current_status": issue.get("workflow_bucket") or "pending",
                "workflow_bucket": issue.get("workflow_bucket") or "other",
                "risk_level": issue.get("risk_level") or "medium",
                "action_needed": ", ".join(issue.get("action_needed") or []),
                "one_line_summary": issue.get("summary") or key,
                "evidence": [],
            },
        )
        entry["workflow_bucket"] = issue.get("workflow_bucket") or entry["workflow_bucket"]
        entry["risk_level"] = issue.get("risk_level") or entry["risk_level"]
        entry["action_needed"] = ", ".join(issue.get("action_needed") or []) or entry["action_needed"]
        entry["one_line_summary"] = issue.get("summary") or entry["one_line_summary"]
        entry["evidence"].append(f"Jira status={issue.get('status')} priority={issue.get('priority')}")

    rows = []
    for key in sorted(issue_map):
        row = issue_map[key]
        rows.append(
            {
                "task_id": ", ".join(row["task_ids"]),
                "related_issue": key,
                "source_doc": ", ".join(sorted(row["source_docs"])) or "live_jira",
                "workflow_bucket": row["workflow_bucket"],
                "risk_level": row["risk_level"],
                "action_needed": row["action_needed"],
                "current_status": row["current_status"],
                "one_line_summary": row["one_line_summary"],
                "evidence": row["evidence"][:4],
            }
        )
    return rows


def _build_task_analysis(
    workspace_root: Path,
    qa_worklist: list[dict],
    gemini_worklist: list[dict],
    open_gap_items: list[dict],
    issue_context_by_key: dict[str, dict] | None = None,
) -> list[dict]:
    issue_context_by_key = issue_context_by_key or {}
    blockers_text = " / ".join(item["item"] for item in open_gap_items[:4])
    analysis_rows = []
    for track, worklist in (("qa", qa_worklist), ("gemini", gemini_worklist)):
        for row in worklist:
            title = row["one_line_summary"]
            primary_issue_key = _first_related_issue_key(row.get("related_issue", ""))
            issue_ctx = issue_context_by_key.get(primary_issue_key, {})
            category = _derive_category(" ".join([row.get("task_id", ""), title, " ".join(row.get("evidence", []))]))
            identifiers = [row.get("task_id", ""), row.get("related_issue", "")]
            touchpoints, code_evidence = _touchpoint_summary(
                workspace_root,
                identifiers,
                category,
                " ".join(
                    [
                        title,
                        row.get("related_issue", ""),
                        " ".join(row.get("evidence", [])),
                        issue_ctx.get("description_excerpt", ""),
                        issue_ctx.get("recent_comment_excerpt", ""),
                    ]
                ),
            )
            analysis_rows.append(
                {
                    "track": track,
                    "task_id": row.get("task_id", ""),
                    "related_issue": row.get("related_issue", ""),
                    "issue_url": issue_ctx.get("url", ""),
                    "issue_status": issue_ctx.get("status", ""),
                    "issue_workflow_bucket": issue_ctx.get("workflow_bucket", row.get("workflow_bucket", "")),
                    "issue_priority": issue_ctx.get("priority", row.get("risk_level", "")),
                    "issue_assignee": issue_ctx.get("assignee", ""),
                    "issue_body_summary": issue_ctx.get("body_summary_ko", "-"),
                    "issue_comment_summary": issue_ctx.get("comment_summary_ko", "-"),
                    "issue_current_situation": issue_ctx.get("current_situation_ko", "-"),
                    "category": category,
                    "current_project_approach": _task_approach(category),
                    "current_problem": _korean_problem_statement(
                        title,
                        row.get("current_status", ""),
                        issue_key=primary_issue_key,
                        issue_title_ko=issue_ctx.get("summary_ko", ""),
                        issue_situation_ko=issue_ctx.get("current_situation_ko", ""),
                    ),
                    "root_cause": _task_root_cause(category),
                    "recommended_fix": _task_fix(category),
                    "touchpoints": touchpoints,
                    "validation_plan": _task_validation_plan(
                        row.get("task_id", ""),
                        _normalize_issue_list(row.get("related_issue", "")),
                        row.get("current_status", ""),
                    ),
                    "blockers": blockers_text if category in {"backend dependency", "spec undecided"} else "",
                    "evidence": [row.get("source_doc", "")] + row.get("evidence", [])[:3] + code_evidence[:4],
                }
            )
    return analysis_rows


def _build_cross_track_insights(gap_highlights: list[str], qa_worklist: list[dict], gemini_worklist: list[dict]) -> list[str]:
    insights = [
        "반복 패턴은 validation, payload mapping, 상태 복원, 모달 confirm 누락, 문서-코드 정합성으로 수렴한다.",
        "QA 태스크는 구현 완료 후에도 regression_check 관점으로 다시 묶는 편이 운영에 유리하다.",
        "보이는 값과 실제 API payload 또는 저장 결과가 다른 케이스는 프로젝트 종류와 무관하게 대표 리스크다.",
        "Jira summary만으로 부족한 경우 코드 touchpoint와 프로젝트 문서를 함께 읽어야 원인 분리가 가능하다.",
    ]
    insights.extend(gap_highlights[:2])
    if len(qa_worklist) > len(gemini_worklist):
        insights.append("QA 문서 기준 task granularity가 GEMINI 이슈 granularity보다 더 세분화돼 있어 매핑 계층이 필요하다.")
    deduped = []
    for item in insights:
        if item and item not in deduped:
            deduped.append(item)
    return deduped[:5]


def _jira_group_summary(issues: list[dict]) -> dict[str, dict]:
    groups: dict[str, dict] = {}
    for track in ("gemini", "qa", "other"):
        if track == "other":
            bucket = [issue for issue in issues if issue.get("track") not in {"gemini", "qa"}]
        else:
            bucket = [issue for issue in issues if issue.get("track") == track]
        groups[track] = {
            "total": len(bucket),
            "status_counts": dict(Counter(issue.get("status", "") for issue in bucket)),
            "stale_counts": dict(Counter(issue.get("stale_status", "") for issue in bucket)),
        }
    return groups


def _relative_existing_paths(base: Path, relatives: list[str]) -> list[str]:
    return [str(base / relative) for relative in relatives if (base / relative).exists()]


def _render_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_empty_\n"
    sep = "| " + " | ".join(headers) + " |\n"
    sep += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    body = "".join("| " + " | ".join(row) + " |\n" for row in rows)
    return sep + body


def render_harness_summary_markdown(result: dict) -> str:
    qa_rows = [
        [
            row["task_id"],
            row["related_issue"] or "-",
            row["source_doc"],
            row["workflow_bucket"],
            row["risk_level"],
            row["action_needed"],
            row["current_status"],
            row["one_line_summary"],
            "<br>".join(row["evidence"][:2]) or "-",
        ]
        for row in result["qa_worklist"]
    ]
    gemini_rows = [
        [
            row["task_id"] or "-",
            row["related_issue"],
            row["source_doc"],
            row["workflow_bucket"],
            row["risk_level"],
            row["action_needed"],
            row["current_status"],
            row["one_line_summary"],
            "<br>".join(row["evidence"][:2]) or "-",
        ]
        for row in result["gemini_worklist"]
    ]
    lines = [
        "# QA / GEMINI Harness Summary",
        "",
        "## ATLS Summary",
    ]
    lines.extend(f"- {line}" for line in result["atls_summary_lines"])
    lines.extend(
        [
            "",
            "## QA Worklist",
            _render_table(
                ["task_id", "related_issue", "source_doc", "workflow_bucket", "risk_level", "action_needed", "current_status", "one_line_summary", "evidence"],
                qa_rows,
            ).rstrip(),
            "",
            "## GEMINI Worklist",
            _render_table(
                ["task_id", "related_issue", "source_doc", "workflow_bucket", "risk_level", "action_needed", "current_status", "one_line_summary", "evidence"],
                gemini_rows,
            ).rstrip(),
            "",
            "## Cross-track Insights",
        ]
    )
    lines.extend(f"- {line}" for line in result["cross_track_insights"])
    lines.extend(["", "## Open Gaps"])
    for item in result["open_gaps"]:
        lines.append(f"- {item['item']}: {item['current_state']} / {item['needed_action']}")
    return "\n".join(lines) + "\n"


def render_project_summary_markdown(result: dict) -> str:
    issues = result.get("jira_issues") or []
    if not issues:
        return render_harness_summary_markdown(result)

    render_workflow_issue_section, workflow_compact_counts, workflow_markdown_table, workflow_stale_label = _cli_daily_review_bundle()
    groups = _jira_group_summary(issues)
    report_date = result.get("date") or date.today().isoformat()
    scope = result.get("jira_context", {}).get("scope", "qa-gemini")
    jql = result.get("jira_context", {}).get("jql", "-")
    lines = [
        f"# Daily Review {report_date}",
        "",
        "## Overview",
        "",
    ]
    lines.extend(
        workflow_markdown_table(
            ["Scope", "Total", "JQL"],
            [[scope, str(len(issues)), jql]],
        )
    )
    lines.extend(["", "## Track Summary", ""])
    summary_rows = []
    for track in ("gemini", "qa"):
        group = groups.get(track, {})
        summary_rows.append(
            [
                track.upper(),
                str(group.get("total", 0)),
                workflow_compact_counts(group.get("status_counts", {})),
                workflow_compact_counts(group.get("stale_counts", {}), workflow_stale_label),
            ]
        )
    lines.extend(workflow_markdown_table(["Track", "Total", "Status", "Stale"], summary_rows))

    gemini = [issue for issue in issues if issue.get("track") == "gemini"]
    qa = [issue for issue in issues if issue.get("track") == "qa"]

    lines.extend(["", "## Project(GEMINI)", ""])
    lines.extend(render_workflow_issue_section(gemini))

    lines.extend(["", "## QA", ""])
    lines.extend(render_workflow_issue_section(qa))
    lines.append("")
    return "\n".join(lines)


def render_task_analysis_markdown(result: dict) -> str:
    rows = []
    for row in result["task_analysis"]:
        rows.append(
            [
                row["track"],
                row["task_id"] or "-",
                row["related_issue"] or "-",
                row["category"],
                row["current_project_approach"],
                row["current_problem"],
                row["root_cause"],
                row["recommended_fix"],
                "<br>".join(row["touchpoints"][:3]) or "-",
                row["validation_plan"],
                row["blockers"] or "-",
                "<br>".join(row["evidence"][:3]) or "-",
            ]
        )
    lines = [
        "# QA / GEMINI Task Analysis",
        "",
        _render_table(
            ["track", "task_id", "related_issue", "category", "current_project_approach", "current_problem", "root_cause", "recommended_fix", "touchpoints", "validation_plan", "blockers", "evidence"],
            rows,
        ).rstrip(),
    ]
    return "\n".join(lines) + "\n"


def _build_prompt_pack(result: dict) -> dict:
    workspace_root = result["workspace_root"]
    atls_docs = result["atls_doc_paths"]
    project_docs = result["project_doc_paths"]
    project_name = Path(workspace_root).name
    qa_task_ids = ", ".join(row["task_id"] for row in result["qa_worklist"][:12])
    gemini_issue_ids = ", ".join(row["related_issue"] for row in result["gemini_worklist"][:12])
    prompt_1 = f"""당신은 ATLS 기반 Jira triage analyst다.

목표:
1. ATLS 문서와 현재 수집된 QA/GEMINI 근거를 바탕으로 summary를 만든다.
2. QA와 GEMINI에 대해서만 작업 리스트를 정의한다.
3. deterministic 분류와 inference를 분리한다.

입력 컨텍스트:
- ATLS 문서: {', '.join(atls_docs)}
- 프로젝트 문서/코드: {', '.join(project_docs)}
- 현재 QA 태스크 후보: {qa_task_ids}
- 현재 GEMINI 이슈 후보: {gemini_issue_ids}

실행 규칙:
1. collect -> analyze -> report 구조를 유지한다.
2. QA/GEMINI 외 트랙은 제외한다.
3. completed 태스크는 regression_check로 표기한다.
4. evidence 없는 추론은 금지한다.
5. output에는 ATLS Summary, QA Worklist, GEMINI Worklist, Cross-track Insights, Open Gaps를 포함한다.
6. 한국어로 작성한다.
"""

    prompt_2 = f"""당신은 project implementation analyst다.

목표:
앞 단계에서 만든 QA/GEMINI worklist를 입력으로 받아 {project_name} 프로젝트에서의 현재 접근 방식, 문제상황, 원인, 해결방법, 검증방법을 태스크별로 분석한다.

분석 대상 프로젝트:
- {workspace_root}

반드시 먼저 읽을 것:
- {', '.join(project_docs)}

분석 규칙:
1. category는 validation / payload mapping / state persistence / modal UX / pagination/list rendering / naming/suffix policy / backend dependency / QA 문서 정합성 / spec undecided 중 하나로 분류한다.
2. page/component, actions, services, clients/api, store/local state 경계를 분리해서 설명한다.
3. 코드가 이미 반영된 태스크는 재개발이 아니라 regression_check 관점으로 분석한다.
4. 스펙 미확정 항목은 어느 팀 확인이 필요한지 먼저 적는다.
5. 출력에는 Executive Summary, Task-by-Task Analysis, Priority View, Final Recommendations를 포함한다.
6. 한국어로 작성한다.
"""

    combined = f"""{prompt_1}

---

그 결과를 입력으로 삼아 바로 아래 구현 분석도 이어서 수행하라.

{prompt_2}
"""
    return {
        "summary_and_worklist_prompt": prompt_1.strip(),
        "project_task_analysis_prompt": prompt_2.strip(),
        "combined_prompt": combined.strip(),
    }


def render_prompt_markdown(prompt_pack: dict) -> str:
    lines = ["# QA / GEMINI Harness Prompts", ""]
    for key, value in prompt_pack.items():
        lines.append(f"## {key}")
        lines.append("```text")
        lines.append(value)
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _derive_priority(track: str, category: str, current_status: str, blockers: str) -> str:
    if blockers or category in {"backend dependency", "spec undecided"}:
        return "P1"
    if current_status == "regression_check":
        return "P2"
    if track == "gemini" or category in {"validation", "payload mapping", "state persistence"}:
        return "P0"
    return "P1"


def _task_result_stub(current_status: str) -> str:
    if current_status == "regression_check":
        return "코드 반영 완료로 보이며 회귀 검증 또는 문서 정합성 확인이 남아 있다."
    if current_status in {"review", "active"}:
        return "진행 중이며 구현 또는 검증 결과를 확정하기 전 단계다."
    return "아직 최종 결과가 확정되지 않았고 승인 후 작업 또는 검증이 필요하다."


def build_project_task_list(report: dict) -> list[dict]:
    rows = []
    for item in report.get("task_analysis", []):
        rows.append(
            {
                "task_id": item.get("task_id") or item.get("related_issue") or "unknown",
                "track": item.get("track", ""),
                "related_issue": item.get("related_issue", ""),
                "category": item.get("category", ""),
                "priority": _derive_priority(
                    item.get("track", ""),
                    item.get("category", ""),
                    next((row.get("current_status", "") for row in report.get("qa_worklist", []) + report.get("gemini_worklist", []) if row.get("task_id") == item.get("task_id") or row.get("related_issue") == item.get("related_issue")), ""),
                    item.get("blockers", ""),
                ),
                "approval_status": "pending_scope_approval",
                "summary": item.get("current_problem", ""),
                "issue_status": item.get("issue_status", ""),
                "issue_workflow_bucket": item.get("issue_workflow_bucket", ""),
                "issue_priority": item.get("issue_priority", ""),
                "touchpoints": item.get("touchpoints", [])[:4],
                "blockers": item.get("blockers", ""),
                "validation_plan": item.get("validation_plan", ""),
            }
        )
    return rows


def build_execution_workflow_cards(report: dict, project_tasks: list[dict]) -> list[dict]:
    by_identity = {}
    for item in report.get("task_analysis", []):
        key = item.get("task_id") or item.get("related_issue")
        if key:
            by_identity[key] = item
    cards = []
    for task in project_tasks:
        item = by_identity.get(task["task_id"]) or by_identity.get(task["related_issue"])
        if not item:
            continue
        cards.append(
            {
                "task_id": task["task_id"],
                "priority": task["priority"],
                "approval_status": task["approval_status"],
                "related_issue": task["related_issue"],
                "category": task["category"],
                "issue_url": item.get("issue_url", ""),
                "issue_status": item.get("issue_status", ""),
                "issue_workflow_bucket": item.get("issue_workflow_bucket", ""),
                "issue_priority": item.get("issue_priority", ""),
                "issue_assignee": item.get("issue_assignee", ""),
                "issue_body_summary": item.get("issue_body_summary", ""),
                "issue_comment_summary": item.get("issue_comment_summary", ""),
                "issue_current_situation": item.get("issue_current_situation", ""),
                "problem": item.get("current_problem", ""),
                "approach_and_considerations": item.get("current_project_approach", ""),
                "solution": item.get("recommended_fix", ""),
                "result": _task_result_stub(next((row.get("current_status", "") for row in report.get("qa_worklist", []) + report.get("gemini_worklist", []) if row.get("task_id") == task["task_id"] or row.get("related_issue") == task["related_issue"]), "")),
                "touchpoints": item.get("touchpoints", [])[:4],
                "validation_plan": item.get("validation_plan", ""),
                "blockers": item.get("blockers", ""),
                "evidence": item.get("evidence", [])[:4],
            }
        )
    return cards


def _group_project_tasks(tasks: list[dict]) -> dict[str, dict[str, list[dict]]]:
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for task in tasks:
        grouped[task.get("track", "other")][task.get("category", "other")].append(task)
    return {track: dict(categories) for track, categories in grouped.items()}


def render_project_task_list_markdown(project_name: str, tasks: list[dict]) -> str:
    rows = []
    for task in tasks:
        rows.append(
            [
                task["priority"],
                task["approval_status"],
                task["track"],
                task["task_id"],
                task["related_issue"] or "-",
                task.get("issue_status", "-") or "-",
                task.get("issue_workflow_bucket", "-") or "-",
                task["category"],
                task["summary"],
                "<br>".join(task["touchpoints"]) or "-",
            ]
        )
    grouped = _group_project_tasks(tasks)
    priority_rank = {"P0": 0, "P1": 1, "P2": 2}
    lines = [
        f"# {project_name} Project Task List",
        "",
        "이 문서는 summary 기반 후보 태스크 리스트다. 구현 착수 전 scope 승인 단계를 거친다.",
        "",
        "## Overview",
        "",
    ]
    for track in sorted(grouped):
        categories = grouped[track]
        task_count = sum(len(items) for items in categories.values())
        category_count = len(categories)
        lines.append(f"- {track.upper()}: {task_count}개 태스크 / {category_count}개 카테고리")
    lines.extend(
        [
            "",
            "## Flat Table",
            "",
        ]
    )
    lines.extend(
        [
        _render_table(
            ["priority", "approval_status", "track", "task_id", "related_issue", "jira_status", "workflow_bucket", "category", "summary", "touchpoints"],
            rows,
        ).rstrip(),
        "",
            "## Grouped Task Management",
            "",
        ]
    )
    for track in sorted(grouped):
        lines.extend([f"### {track.upper()}", ""])
        categories = grouped[track]
        for category in sorted(categories):
            category_tasks = sorted(
                categories[category],
                key=lambda task: (
                    priority_rank.get(task.get("priority", "P9"), 9),
                    task.get("issue_status", ""),
                    task.get("task_id", ""),
                ),
            )
            category_rows = [
                [
                    task["priority"],
                    task["approval_status"],
                    task["task_id"],
                    task["related_issue"] or "-",
                    task.get("issue_status", "-") or "-",
                    task.get("issue_workflow_bucket", "-") or "-",
                    task["summary"],
                    "<br>".join(task["touchpoints"]) or "-",
                ]
                for task in category_tasks
            ]
            lines.extend(
                [
                    f"#### {category} ({len(category_tasks)})",
                    "",
                    _render_table(
                        ["priority", "approval_status", "task_id", "related_issue", "jira_status", "workflow_bucket", "summary", "touchpoints"],
                        category_rows,
                    ).rstrip(),
                    "",
                ]
            )
    return "\n".join(lines)


def render_execution_workflow_markdown(project_name: str, cards: list[dict]) -> str:
    lines = [
        f"# {project_name} Execution Workflow",
        "",
        "## Workflow",
        "",
        "1. Summary 추출: Jira summary와 프로젝트 문서를 기준으로 작업 후보를 수집한다.",
        "2. Task List Draft: 프로젝트 연동 태스크 리스트를 만들고 scope 승인을 기다린다.",
        "3. Project Analysis: 승인된 태스크만 코드 touchpoint와 연결해 분석한다.",
        "4. Execution: 아래 카드 형식으로 작업을 진행하고 결과를 누적한다.",
        "5. Validation / Publish: 검증 후 Jira/Confluence 반영 여부를 결정한다.",
        "",
        "## Approval Gates",
        "",
        "- Gate A: summary 기반 태스크 리스트 승인",
        "- Gate B: 태스크별 접근 방식과 해결 방향 승인",
        "- Gate C: 결과 검증 후 Jira/Confluence 반영 승인",
        "",
        "## Execution Cards",
        "",
    ]
    if not cards:
        lines.append("- none")
        return "\n".join(lines) + "\n"
    for card in cards:
        lines.extend(
            [
                f"### {card['task_id']} ({card['priority']}, {card['approval_status']})",
                "",
                f"- Related Issue: {card['related_issue'] or '-'}",
                f"- Category: {card['category']}",
                f"- Touchpoints: {', '.join(card['touchpoints']) or '-'}",
                f"- Blockers: {card['blockers'] or '-'}",
                "",
                "[문제 상황]",
                card["problem"] or "-",
                "",
                "[접근 방식 및 고려사항]",
                card["approach_and_considerations"] or "-",
                "",
                "[해결 방법]",
                card["solution"] or "-",
                "",
                "[결과]",
                card["result"] or "-",
                "",
                "[검증 계획]",
                card["validation_plan"] or "-",
                "",
            ]
        )
    return "\n".join(lines)


def build_detail_v2_cards(report: dict, project_tasks: list[dict]) -> list[dict]:
    cards = build_execution_workflow_cards(report, project_tasks)
    detailed = []
    seen = set()
    for card in cards:
        dedupe_key = (card["task_id"], card["related_issue"], card["category"])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        detailed.append(
            {
                "task_id": card["task_id"],
                "priority": card["priority"],
                "approval_status": card["approval_status"],
                "related_issue": card["related_issue"],
                "category": card["category"],
                "issue_url": card.get("issue_url", ""),
                "issue_status": card.get("issue_status", ""),
                "issue_workflow_bucket": card.get("issue_workflow_bucket", ""),
                "issue_priority": card.get("issue_priority", ""),
                "issue_assignee": card.get("issue_assignee", ""),
                "issue_body_summary": card.get("issue_body_summary", ""),
                "issue_comment_summary": card.get("issue_comment_summary", ""),
                "issue_current_situation": card.get("issue_current_situation", ""),
                "problem": card["problem"],
                "approach_and_considerations": card["approach_and_considerations"],
                "solution": card["solution"],
                "result": card["result"],
                "validation_plan": card["validation_plan"],
                "touchpoints": card["touchpoints"],
                "blockers": card["blockers"],
                "evidence": [_shorten_text(entry, 180) for entry in card["evidence"]],
                "document_status": "draft_from_summary",
            }
        )
    return detailed


def _task_plan_steps(card: dict) -> list[str]:
    steps = []
    issue_status = card.get("issue_status", "")
    if card.get("related_issue"):
        steps.append("Jira 본문, 최근 코멘트, 현재 상태를 먼저 다시 확인해 이번 작업 범위를 확정한다.")
    if issue_status == "In Review":
        steps.append("리뷰 피드백과 현재 반영 상태를 대조해 실제 수정이 필요한지, 회귀 검증만 필요한지 구분한다.")
    elif issue_status == "In Progress":
        steps.append("현재 구현 상태와 남은 수정 범위를 확인해 이어서 수정할 지점만 좁힌다.")
    elif issue_status == "To Do":
        steps.append("PRD, 코멘트, 체크리스트 기준으로 기대 동작과 예외 케이스를 먼저 확정한다.")
    elif issue_status in {"Done", "Closed"}:
        steps.append("기반 구현은 반영된 상태로 보고 회귀 검증 범위와 문서 정합성 확인 항목을 먼저 확정한다.")
    else:
        steps.append("현재 상태 정보가 불명확하면 담당자와 코멘트 히스토리를 기준으로 우선순위와 범위를 먼저 맞춘다.")
    if card.get("touchpoints"):
        steps.append("Touchpoints에 표시된 화면, 액션, 서비스 계층을 순서대로 확인해 실제 원인 지점을 좁힌다.")
    steps.append(card.get("solution", "해결 방법을 기준으로 수정 또는 검증 범위를 구체화한다."))
    steps.append(card.get("validation_plan", "작업 후 UI, payload, 저장 결과를 함께 검증한다."))
    steps.append("작업 결과를 Jira 상태와 코멘트에 반영하고, 필요 시 QA 재검증 요청까지 연결한다.")
    return steps


def build_task_plan_cards(report: dict, project_tasks: list[dict]) -> list[dict]:
    execution_cards = build_execution_workflow_cards(report, project_tasks)
    by_identity = {}
    for card in execution_cards:
        key = card.get("task_id") or card.get("related_issue")
        if key:
            by_identity[key] = card
    cards = []
    for task in project_tasks:
        card = by_identity.get(task.get("task_id")) or by_identity.get(task.get("related_issue"))
        if not card:
            continue
        cards.append(
            {
                "task_id": task["task_id"],
                "track": task.get("track", ""),
                "category": task.get("category", ""),
                "priority": task.get("priority", ""),
                "approval_status": task.get("approval_status", ""),
                "related_issue": task.get("related_issue", ""),
                "issue_url": card.get("issue_url", ""),
                "issue_status": card.get("issue_status", ""),
                "issue_workflow_bucket": card.get("issue_workflow_bucket", ""),
                "issue_priority": card.get("issue_priority", ""),
                "issue_assignee": card.get("issue_assignee", ""),
                "summary": task.get("summary", ""),
                "problem": card.get("problem", ""),
                "approach": card.get("approach_and_considerations", ""),
                "solution": card.get("solution", ""),
                "result": card.get("result", ""),
                "validation_plan": card.get("validation_plan", ""),
                "touchpoints": card.get("touchpoints", []),
                "blockers": card.get("blockers", ""),
                "work_steps": _task_plan_steps(card),
                "done_criteria": [
                    "관련 화면/기능이 기대 동작과 일치한다.",
                    "필요한 검증 시나리오와 회귀 테스트가 수행된다.",
                    "Jira 상태 또는 코멘트에 결과가 반영된다.",
                ],
            }
        )
    return cards


def render_task_plan_markdown(project_name: str, plans: list[dict]) -> str:
    grouped = _group_project_tasks(plans)
    lines = [
        f"# {project_name} Task Plans",
        "",
        "이 문서는 task list를 기준으로 각 태스크별 작업 계획을 정리한 실행 문서다.",
        "",
    ]
    for track in sorted(grouped):
        lines.extend([f"## {track.upper()}", ""])
        for category in sorted(grouped[track]):
            lines.extend([f"### {category}", ""])
            for plan in grouped[track][category]:
                issue_label = plan.get("related_issue") or "-"
                jira_link = f"[{issue_label}]({plan['issue_url']})" if issue_label != "-" and plan.get("issue_url") else issue_label
                lines.extend(
                    [
                        f"#### {plan['task_id']} ({plan['priority']}, {plan['approval_status']})",
                        "",
                        f"- Related Issue: {jira_link}",
                        f"- Jira Status: {plan.get('issue_status') or '-'}",
                        f"- Workflow Bucket: {plan.get('issue_workflow_bucket') or '-'}",
                        f"- Assignee: {plan.get('issue_assignee') or '-'}",
                        f"- Touchpoints: {', '.join(plan.get('touchpoints', [])) or '-'}",
                        f"- Blockers: {plan.get('blockers') or '-'}",
                        "",
                        "[문제 상황]",
                        plan.get("problem") or "-",
                        "",
                        "[접근 방식 및 고려사항]",
                        plan.get("approach") or "-",
                        "",
                        "[세부 작업]",
                    ]
                )
                lines.extend(f"{idx}. {step}" for idx, step in enumerate(plan.get("work_steps", []), start=1))
                lines.extend(
                    [
                        "",
                        "[검증 계획]",
                        plan.get("validation_plan") or "-",
                        "",
                        "[완료 기준]",
                    ]
                )
                lines.extend(f"- {criterion}" for criterion in plan.get("done_criteria", []))
                lines.append("")
    return "\n".join(lines)


def _manifest_case_tags(track: str, category: str, priority: str) -> list[str]:
    tags = [track, category.replace(" ", "-"), priority.lower()]
    deduped = []
    for tag in tags:
        if tag and tag not in deduped:
            deduped.append(tag)
    return deduped


def _build_acceptance_cases(plan: dict) -> list[dict]:
    category = plan.get("category", "")
    summary = " ".join([plan.get("summary", ""), plan.get("problem", "")]).lower()
    base_tags = _manifest_case_tags(plan.get("track", ""), category, plan.get("priority", ""))
    issue_key = plan.get("related_issue") or plan.get("task_id")

    if category == "modal UX" or any(keyword in summary for keyword in ("alert", "confirm", "모달", "팝업", "취소")):
        return [
            {
                "case_id": f"{issue_key}-alert-trigger".lower().replace(" ", "-").replace(",", ""),
                "title": "변경사항이 있는 상태에서 취소/X/dim 클릭 시 confirm alert가 노출된다.",
                "risk": "high",
                "preconditions": [
                    "대상 팝업 또는 레이어가 열린 상태다.",
                    "사용자가 선택 또는 입력으로 dirty state를 만든 상태다.",
                ],
                "actions": [
                    "취소 버튼을 클릭한다.",
                    "X 버튼을 클릭한다.",
                    "dim 영역을 클릭한다.",
                ],
                "expected": [
                    "각 이탈 경로에서 confirm alert가 노출된다.",
                    "alert 문구가 기획 문구와 정확히 일치한다.",
                ],
                "forbidden": [
                    "alert 없이 레이어가 바로 닫힌다.",
                    "문구가 이전 문구이거나 잘못된 문구다.",
                ],
                "evidence": ["screenshot", "trace", "dialog_text"],
                "tags": base_tags + ["alert", "dirty-state", "regression"],
            },
            {
                "case_id": f"{issue_key}-alert-branch".lower().replace(" ", "-").replace(",", ""),
                "title": "confirm alert 분기 동작이 기대값과 일치한다.",
                "risk": "high",
                "preconditions": [
                    "confirm alert가 노출된 상태다.",
                ],
                "actions": [
                    "예 또는 확인 버튼을 클릭한다.",
                    "아니오 또는 취소 버튼을 클릭한다.",
                ],
                "expected": [
                    "확인 분기에서는 이탈 또는 닫기 동작이 수행된다.",
                    "취소 분기에서는 현재 화면과 입력값이 유지된다.",
                ],
                "forbidden": [
                    "버튼 분기와 반대 동작을 수행한다.",
                    "입력값이 의도치 않게 초기화된다.",
                ],
                "evidence": ["screenshot", "trace", "route_change", "state_snapshot"],
                "tags": base_tags + ["branching", "state-retention"],
            },
        ]

    if category == "validation" or any(keyword in summary for keyword in ("validation", "문구", "메시지", "상한", "하한", "기간")):
        return [
            {
                "case_id": f"{issue_key}-validation-message".lower().replace(" ", "-").replace(",", ""),
                "title": "입력 오류 시 validation 문구가 정확히 노출된다.",
                "risk": "high",
                "preconditions": ["대상 입력 필드가 노출된 상태다."],
                "actions": ["요구조건을 위반하는 값을 입력한다."],
                "expected": ["validation 문구가 정확히 노출된다."],
                "forbidden": ["문구가 노출되지 않는다.", "문구가 기획과 다르다."],
                "evidence": ["screenshot", "trace", "dom_snapshot"],
                "tags": base_tags + ["validation", "message"],
            },
            {
                "case_id": f"{issue_key}-validation-recovery".lower().replace(" ", "-").replace(",", ""),
                "title": "정상 입력으로 복구하면 validation 상태가 해제된다.",
                "risk": "medium",
                "preconditions": ["validation 문구가 노출된 상태다."],
                "actions": ["정상 범위의 값을 다시 입력한다."],
                "expected": ["validation 문구가 사라지고 저장 가능 상태가 된다."],
                "forbidden": ["오류 상태가 유지된다."],
                "evidence": ["screenshot", "trace"],
                "tags": base_tags + ["recovery"],
            },
        ]

    if category == "payload mapping":
        return [
            {
                "case_id": f"{issue_key}-payload-shape".lower().replace(" ", "-").replace(",", ""),
                "title": "사용자 입력이 기대 payload shape로 전송된다.",
                "risk": "high",
                "preconditions": ["대상 입력 플로우가 열린 상태다."],
                "actions": ["폼을 채우고 저장 또는 다음 단계로 진행한다."],
                "expected": ["기대 필드와 값이 payload에 포함된다."],
                "forbidden": ["잘못된 필드가 전송된다.", "값 매핑이 누락되거나 뒤바뀐다."],
                "evidence": ["network_request", "trace", "payload_snapshot"],
                "tags": base_tags + ["payload", "network"],
            }
        ]

    if category == "state persistence":
        return [
            {
                "case_id": f"{issue_key}-state-restore".lower().replace(" ", "-").replace(",", ""),
                "title": "이전 선택 또는 저장 상태가 기대값대로 복원된다.",
                "risk": "high",
                "preconditions": ["대상 플로우에서 저장 또는 선택 이력이 있다."],
                "actions": ["페이지를 재진입하거나 다시 연다."],
                "expected": ["기대 상태가 복원된다."],
                "forbidden": ["기본값으로 초기화된다.", "다른 유형 상태가 잘못 복원된다."],
                "evidence": ["screenshot", "trace", "storage_snapshot"],
                "tags": base_tags + ["restore", "persistence"],
            }
        ]

    if category == "pagination/list rendering":
        return [
            {
                "case_id": f"{issue_key}-list-render".lower().replace(" ", "-").replace(",", ""),
                "title": "목록 렌더링과 페이지 이동이 기대값과 일치한다.",
                "risk": "medium",
                "preconditions": ["목록 데이터가 충분히 존재한다."],
                "actions": ["필터링, 선택, 페이지 이동을 수행한다."],
                "expected": ["현재 페이지 데이터와 전체 선택 상태가 일치한다."],
                "forbidden": ["빈 페이지가 보인다.", "숨겨진 항목이 선택 상태에 포함된다."],
                "evidence": ["screenshot", "trace", "dom_snapshot"],
                "tags": base_tags + ["list", "pagination"],
            }
        ]

    return [
        {
            "case_id": f"{issue_key}-core-flow".lower().replace(" ", "-").replace(",", ""),
            "title": "핵심 사용자 플로우가 요구조건과 일치한다.",
            "risk": "medium",
            "preconditions": ["대상 화면에 진입 가능한 상태다."],
            "actions": ["핵심 사용자 플로우를 수행한다."],
            "expected": ["수정 결과가 요구조건과 일치한다."],
            "forbidden": ["기존 이슈가 재발한다."],
            "evidence": ["screenshot", "trace"],
            "tags": base_tags + ["core-flow"],
        }
    ]


def build_acceptance_manifest_pack(project_name: str, plans: list[dict]) -> dict:
    manifests = []
    for plan in plans:
        manifests.append(
            {
                "manifest_version": "0.1",
                "project_key": project_name,
                "track": plan.get("track", ""),
                "task_id": plan.get("task_id", ""),
                "issue_key": plan.get("related_issue") or plan.get("task_id", ""),
                "category": plan.get("category", ""),
                "priority": plan.get("priority", ""),
                "goal": plan.get("problem") or plan.get("summary", ""),
                "touchpoints": plan.get("touchpoints", []),
                "cases": _build_acceptance_cases(plan),
            }
        )
    return {
        "manifest_pack_version": "0.1",
        "project_key": project_name,
        "manifest_count": len(manifests),
        "manifests": manifests,
    }


def render_acceptance_manifest_markdown(manifest_pack: dict) -> str:
    manifests = manifest_pack.get("manifests", [])
    grouped = _group_project_tasks(manifests)
    lines = [
        f"# {manifest_pack.get('project_key', 'project')} Acceptance Manifest",
        "",
        f"- manifest_count: {manifest_pack.get('manifest_count', 0)}",
        "",
    ]
    for track in sorted(grouped):
        lines.extend([f"## {track.upper()}", ""])
        for category in sorted(grouped[track]):
            lines.extend([f"### {category}", ""])
            for manifest in grouped[track][category]:
                lines.extend(
                    [
                        f"#### {manifest['task_id']} / {manifest['issue_key']}",
                        "",
                        f"- Priority: {manifest.get('priority') or '-'}",
                        f"- Goal: {manifest.get('goal') or '-'}",
                        f"- Touchpoints: {', '.join(manifest.get('touchpoints', [])) or '-'}",
                        "",
                    ]
                )
                for case in manifest.get("cases", []):
                    lines.extend(
                        [
                            f"- Case: `{case['case_id']}`",
                            f"  Title: {case['title']}",
                            f"  Expected: {' / '.join(case.get('expected', [])) or '-'}",
                            f"  Forbidden: {' / '.join(case.get('forbidden', [])) or '-'}",
                            f"  Evidence: {', '.join(case.get('evidence', [])) or '-'}",
                        ]
                    )
                lines.append("")
    return "\n".join(lines)


def build_project_adapter_pack(workspace_root: Path, project_name: str) -> dict:
    adapter = {
        "adapter_version": "0.1",
        "project_key": project_name,
        "runner": "playwright",
        "base_url": "http://localhost:3000",
        "local_only": True,
        "ci_gate": False,
        "auth": {
            "strategy": "storage_state_bootstrap",
            "login_provider": "GMKT" if project_name == "adcenter" else "default",
            "login_tab_selector": ".button__tab--gmarket" if project_name == "adcenter" else "",
            "env_file": ".env.e2e",
            "required_env": ["E2E_GMARKET_ID", "E2E_GMARKET_PASSWORD"] if project_name == "adcenter" else [],
            "storage_state_path": "tests/.auth/user.json",
        },
        "selectors": {
            "prefer_test_id": True,
            "fallback_order": ["data-testid", "role", "label", "text"],
        },
        "artifacts": {
            "html_report_dir": "tests/results/html-report",
            "artifact_dir": "tests/results/artifacts",
        },
        "workspace_root": str(workspace_root),
    }
    return adapter


def render_project_adapter_markdown(adapter: dict) -> str:
    auth = adapter.get("auth", {})
    lines = [
        f"# {adapter.get('project_key', 'project')} Project Adapter",
        "",
        f"- runner: {adapter.get('runner')}",
        f"- base_url: {adapter.get('base_url')}",
        f"- local_only: {adapter.get('local_only')}",
        f"- ci_gate: {adapter.get('ci_gate')}",
        "",
        "## Auth",
        "",
        f"- strategy: {auth.get('strategy')}",
        f"- login_provider: {auth.get('login_provider')}",
        f"- login_tab_selector: {auth.get('login_tab_selector') or '-'}",
        f"- env_file: {auth.get('env_file')}",
        f"- required_env: {', '.join(auth.get('required_env', [])) or '-'}",
        f"- storage_state_path: {auth.get('storage_state_path')}",
        "",
        "## Selectors",
        "",
        f"- prefer_test_id: {adapter.get('selectors', {}).get('prefer_test_id')}",
        f"- fallback_order: {', '.join(adapter.get('selectors', {}).get('fallback_order', []))}",
        "",
        "## Artifacts",
        "",
        f"- html_report_dir: {adapter.get('artifacts', {}).get('html_report_dir')}",
        f"- artifact_dir: {adapter.get('artifacts', {}).get('artifact_dir')}",
        "",
    ]
    return "\n".join(lines)


def _spec_slug(text: str) -> str:
    lowered = (text or "").strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    return lowered or "spec"


def _ts_string_literal(text: str) -> str:
    return json.dumps(text or "", ensure_ascii=False)


def _render_playwright_test_case(case: dict) -> str:
    title = case.get("title", "generated case")
    test_title = f"{case.get('case_id', 'case')} | {title}"
    lines = [
        f"test({_ts_string_literal(test_title)}, async ({{ page }}) => {{",
        "  test.skip(true, 'Generated skeleton: implement navigation, selectors, and assertions.');",
        "",
        "  // Preconditions:",
    ]
    for item in case.get("preconditions", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // Actions:",
        ]
    )
    for item in case.get("actions", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // Expected:",
        ]
    )
    for item in case.get("expected", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // Forbidden:",
        ]
    )
    for item in case.get("forbidden", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // Evidence to capture:",
        ]
    )
    for item in case.get("evidence", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // TODO: add page navigation",
            "  // TODO: add selectors based on project adapter",
            "  // TODO: add assertions for expected/forbidden conditions",
            "});",
        ]
    )
    return "\n".join(lines)


def build_playwright_spec_pack(project_name: str, manifest_pack: dict, project_adapter: dict) -> dict:
    specs = []
    for manifest in manifest_pack.get("manifests", []):
        issue_key = manifest.get("issue_key") or manifest.get("task_id") or "issue"
        task_id = manifest.get("task_id") or issue_key
        category = manifest.get("category") or "flow"
        filename = f"{_spec_slug(issue_key)}-{_spec_slug(task_id)}-{_spec_slug(category)}.spec.ts"
        auth = project_adapter.get("auth", {})
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            "/**",
            " * Generated by ATLS.",
            f" * Project: {project_name}",
            f" * Issue: {issue_key}",
            f" * Task: {task_id}",
            f" * Category: {category}",
            f" * Auth Provider: {auth.get('login_provider', 'default')}",
            f" * Login Strategy: {auth.get('strategy', 'unknown')}",
            " */",
            "",
            f"test.describe({_ts_string_literal(f'{issue_key} / {task_id} / {category}')}, () => {{",
            "  test.beforeEach(async ({ page }) => {",
            "    // TODO: navigate to the target route and prepare deterministic test state",
            "    await page.goto('/');",
            "  });",
            "",
        ]
        for case in manifest.get("cases", []):
            lines.append(_render_playwright_test_case(case))
            lines.append("")
        lines.append("});")
        specs.append(
            {
                "filename": filename,
                "issue_key": issue_key,
                "task_id": task_id,
                "track": manifest.get("track", ""),
                "category": category,
                "content": "\n".join(lines).rstrip() + "\n",
            }
        )
    return {
        "spec_pack_version": "0.1",
        "project_key": project_name,
        "spec_count": len(specs),
        "specs": specs,
    }


def _looks_like_jira_issue_key(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Z0-9]+-\d+", (value or "").strip().upper()))


def _render_issue_delivery_test_case(case: dict) -> str:
    title = case.get("title", "generated case")
    test_title = f"{case.get('case_id', 'case')} | {title}"
    lines = [
        f"test({_ts_string_literal(test_title)}, async ({{ page }}) => {{",
        "  test.skip(true, 'ATLS_GENERATED_PLACEHOLDER: implement selectors, navigation, and assertions for this issue case.');",
        "",
        "  // Preconditions:",
    ]
    for item in case.get("preconditions", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // Actions:",
        ]
    )
    for item in case.get("actions", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // Expected:",
        ]
    )
    for item in case.get("expected", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // Forbidden:",
        ]
    )
    for item in case.get("forbidden", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // Evidence to capture:",
        ]
    )
    for item in case.get("evidence", []):
        lines.append(f"  // - {item}")
    lines.extend(
        [
            "",
            "  // TODO: replace the placeholder flow with project-specific navigation and assertions.",
            "  await page.goto('/');",
            "});",
        ]
    )
    return "\n".join(lines)


def _render_issue_delivery_spec(issue_key: str, issue_title: str, issue_cases: list[dict], project_adapter: dict) -> str:
    auth = project_adapter.get("auth", {})
    lines = [
        "import { test } from '@playwright/test';",
        "",
        "/**",
        " * Generated by ATLS issue-delivery workflow.",
        " * ATLS_GENERATED_PLACEHOLDER",
        f" * Issue: {issue_key}",
        f" * Title: {issue_title}",
        f" * Auth Provider: {auth.get('login_provider', 'default')}",
        f" * Login Strategy: {auth.get('strategy', 'unknown')}",
        " */",
        "",
        f"test.describe({_ts_string_literal(f'{issue_key} | {issue_title or issue_key}')}, () => {{",
        "  test.beforeEach(async ({ page }) => {",
        "    // TODO: navigate to the real route for this issue before removing the placeholder skip.",
        "    await page.goto('/');",
        "  });",
        "",
    ]
    if not issue_cases:
        lines.extend(
            [
                "  test('atls-no-mapped-cases', async ({ page }) => {",
                "    test.skip(true, 'ATLS_GENERATED_PLACEHOLDER: no acceptance cases were mapped for this Jira issue yet.');",
                "    await page.goto('/');",
                "  });",
                "",
            ]
        )
    for case in issue_cases:
        lines.append(_render_issue_delivery_test_case(case))
        lines.append("")
    lines.append("});")
    return "\n".join(lines).rstrip() + "\n"


def build_issue_spec_pack(
    project_name: str,
    jira_issues: list[dict],
    manifest_pack: dict,
    project_adapter: dict,
) -> dict:
    jira_by_key = _issue_lookup(jira_issues)
    grouped: dict[str, dict] = {}

    for issue in jira_issues:
        issue_key = str(issue.get("key") or "").strip().upper()
        if not _looks_like_jira_issue_key(issue_key):
            continue
        if issue.get("track") not in {"qa", "gemini"}:
            continue
        grouped.setdefault(
            issue_key,
            {
                "issue_key": issue_key,
                "title": issue.get("summary") or issue_key,
                "track": issue.get("track") or "",
                "jira_status": issue.get("status") or "",
                "priority": issue.get("priority") or "",
                "case_rows": [],
                "task_ids": [],
                "categories": [],
                "touchpoints": [],
            },
        )

    for manifest in manifest_pack.get("manifests", []):
        raw_issue_value = str(manifest.get("issue_key") or manifest.get("task_id") or "").strip()
        related_issue_keys = _normalize_issue_list(raw_issue_value)
        if not related_issue_keys and _looks_like_jira_issue_key(raw_issue_value):
            related_issue_keys = [raw_issue_value.upper()]
        cases = manifest.get("cases", []) if isinstance(manifest.get("cases"), list) else []
        task_id = str(manifest.get("task_id") or "").strip()
        category = str(manifest.get("category") or "").strip()
        touchpoints = [str(item) for item in manifest.get("touchpoints", []) if str(item).strip()]

        for issue_key in related_issue_keys:
            issue_key = issue_key.upper()
            issue_meta = jira_by_key.get(issue_key, {})
            entry = grouped.setdefault(
                issue_key,
                {
                    "issue_key": issue_key,
                    "title": issue_meta.get("summary") or issue_key,
                    "track": issue_meta.get("track") or manifest.get("track") or "",
                    "jira_status": issue_meta.get("status") or "",
                    "priority": issue_meta.get("priority") or "",
                    "case_rows": [],
                    "task_ids": [],
                    "categories": [],
                    "touchpoints": [],
                },
            )
            if task_id and task_id not in entry["task_ids"]:
                entry["task_ids"].append(task_id)
            if category and category not in entry["categories"]:
                entry["categories"].append(category)
            for touchpoint in touchpoints:
                if touchpoint not in entry["touchpoints"]:
                    entry["touchpoints"].append(touchpoint)
            for case in cases:
                case_row = dict(case) if isinstance(case, dict) else {}
                case_row["task_id"] = task_id
                case_row["category"] = category
                entry["case_rows"].append(case_row)

    specs = []
    for issue_key in sorted(grouped):
        entry = grouped[issue_key]
        filename = f"{issue_key.lower()}.spec.ts"
        content = _render_issue_delivery_spec(
            issue_key=issue_key,
            issue_title=entry.get("title") or issue_key,
            issue_cases=entry.get("case_rows", []),
            project_adapter=project_adapter,
        )
        specs.append(
            {
                "issue_key": issue_key,
                "title": entry.get("title") or issue_key,
                "track": entry.get("track") or "",
                "jira_status": entry.get("jira_status") or "",
                "priority": entry.get("priority") or "",
                "task_ids": entry.get("task_ids", []),
                "categories": entry.get("categories", []),
                "touchpoints": entry.get("touchpoints", []),
                "case_count": len(entry.get("case_rows", [])),
                "case_ids": [
                    str(case.get("case_id") or "").strip()
                    for case in entry.get("case_rows", [])
                    if str(case.get("case_id") or "").strip()
                ],
                "filename": filename,
                "generated_placeholder": True,
                "content": content,
            }
        )

    return {
        "issue_spec_pack_version": "0.1",
        "project_key": project_name,
        "spec_count": len(specs),
        "specs": specs,
    }


def render_playwright_spec_pack_markdown(spec_pack: dict) -> str:
    specs = spec_pack.get("specs", [])
    grouped = _group_project_tasks(specs)
    lines = [
        f"# {spec_pack.get('project_key', 'project')} Playwright Spec Skeletons",
        "",
        f"- spec_count: {spec_pack.get('spec_count', 0)}",
        "",
    ]
    for track in sorted(grouped):
        lines.extend([f"## {track.upper()}", ""])
        for category in sorted(grouped[track]):
            lines.extend([f"### {category}", ""])
            for spec in grouped[track][category]:
                lines.extend(
                    [
                        f"- `{spec['filename']}`",
                        f"  issue: {spec.get('issue_key')}",
                        f"  task: {spec.get('task_id')}",
                    ]
                )
            lines.append("")
    return "\n".join(lines)


def render_detail_v2_markdown(project_name: str, cards: list[dict]) -> str:
    lines = [
        f"# {project_name} Detail V2",
        "",
        "이 문서는 summary 기반으로 재구성한 상세 실행 문서다.",
        "현재 status는 draft이며, 태스크 리스트 승인 이후 상세 내용 보강과 결과 갱신을 전제로 한다.",
        "",
        "## Detail Format",
        "",
        "- [문제 상황]: 현재 이슈와 프로젝트 맥락에서 무엇이 실제 문제인지",
        "- [접근 방식 및 고려사항]: 현재 구조, 영향 범위, 승인 전 체크할 포인트",
        "- [해결 방법]: 구현/문서/검증 차원의 실행 방법",
        "- [결과]: 현재 결과 상태 또는 작업 후 채워야 할 결과 요약",
        "",
        "## Cards",
        "",
    ]
    if not cards:
        lines.append("- none")
        return "\n".join(lines) + "\n"
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    ordered_cards = sorted(cards, key=lambda card: (priority_order.get(card["priority"], 9), card["task_id"]))
    for card in ordered_cards:
        issue_label = _clean_issue_key_text(card["related_issue"] or "-")
        jira_link = card.get("issue_url", "")
        jira_link_markdown = f"[{issue_label}]({jira_link})" if jira_link and issue_label != "-" else "-"
        lines.extend(
            [
                f"### {card['task_id']} ({card['priority']}, {card['approval_status']})",
                "",
                f"- 관련 이슈: {issue_label}",
                f"- Jira 링크: {jira_link_markdown}",
                f"- 카테고리: {card['category']}",
                f"- Jira 상태: {card['issue_status'] or '-'}",
                f"- 워크플로우 버킷: {card['issue_workflow_bucket'] or '-'}",
                f"- Jira 우선순위: {card['issue_priority'] or '-'}",
                f"- 담당자: {card['issue_assignee'] or '-'}",
                f"- 문서 상태: {card['document_status']}",
                f"- Touchpoints: {', '.join(card['touchpoints']) or '-'}",
                f"- Evidence: {' | '.join(card['evidence']) if card['evidence'] else '-'}",
                f"- Blockers: {card['blockers'] or '-'}",
                f"- Jira 본문 요약: {card['issue_body_summary'] or '-'}",
                f"- 최근 코멘트 요약: {card['issue_comment_summary'] or '-'}",
                f"- 현재 상황 판단: {card['issue_current_situation'] or '-'}",
                "",
                "[문제 상황]",
                card["problem"] or "-",
                "",
                "[접근 방식 및 고려사항]",
                card["approach_and_considerations"] or "-",
                "",
                "[해결 방법]",
                card["solution"] or "-",
                "",
                "[결과]",
                card["result"] or "-",
                "",
                "[검증 계획]",
                card["validation_plan"] or "-",
                "",
            ]
        )
    return "\n".join(lines)


def _build_open_gaps_from_jira(jira_issues: list[dict]) -> list[dict]:
    items = []
    for issue in jira_issues:
        actions = issue.get("action_needed") or []
        if not actions and issue.get("workflow_bucket") != "blocked":
            continue
        if "needs_prd_confirmation" in actions or "needs_ux_confirmation" in actions or issue.get("workflow_bucket") == "blocked":
            items.append(
                {
                    "item": issue.get("key") or issue.get("summary") or "unknown",
                    "current_state": f"status={issue.get('status')} track={issue.get('track')}",
                    "needed_action": ", ".join(actions) or "needs_followup",
                }
            )
    return items[:8]


def build_harness_report(
    atls_root: str | Path,
    workspace_root: str | Path,
    jira_issues: list[dict] | None = None,
    jira_context: dict | None = None,
) -> dict:
    atls_root = Path(atls_root).expanduser().resolve()
    workspace_root = Path(workspace_root).expanduser().resolve()
    jira_issues = jira_issues or []
    jira_context = jira_context or {}

    discovered_docs = _discover_optional_analysis_docs(workspace_root)
    manual_text = _read_text(discovered_docs["manual_guide"]) if "manual_guide" in discovered_docs else ""
    checklist_text = _read_text(discovered_docs["checklist"]) if "checklist" in discovered_docs else ""
    gap_text = _read_text(discovered_docs["gap_analysis"]) if "gap_analysis" in discovered_docs else ""

    checklist_tasks = _parse_checklist_tasks(checklist_text) if checklist_text else {}
    manual_mapping = _parse_manual_task_mapping(manual_text) if manual_text else {}
    gap_sections = _parse_gap_analysis(gap_text) if gap_text else {}
    gap_highlights = _parse_gap_highlights(gap_text) if gap_text else []
    open_gap_items = _extract_open_gap_table(checklist_text) if checklist_text else []
    jira_by_key = _issue_lookup(jira_issues)
    issue_context_by_key = _issue_context_map(jira_issues)

    qa_worklist = _build_qa_worklist(checklist_tasks, manual_mapping, jira_by_key) if checklist_tasks else _build_qa_worklist_from_jira(jira_issues)
    gemini_worklist = _build_gemini_worklist(qa_worklist, jira_issues)
    if not open_gap_items:
        open_gap_items = _build_open_gaps_from_jira(jira_issues)
    task_analysis = _build_task_analysis(workspace_root, qa_worklist, gemini_worklist, open_gap_items, issue_context_by_key)
    project_doc_paths = _discover_context_docs(workspace_root)
    prompt_pack = _build_prompt_pack(
        {
            "workspace_root": str(workspace_root),
            "atls_doc_paths": _relative_existing_paths(atls_root, ATLS_DOC_RELATIVE_PATHS),
            "project_doc_paths": project_doc_paths,
            "qa_worklist": qa_worklist,
            "gemini_worklist": gemini_worklist,
        }
    )

    report = {
        "success": True,
        "date": date.today().isoformat(),
        "workspace_root": str(workspace_root),
        "atls_root": str(atls_root),
        "jira_context": jira_context,
        "jira_issues": jira_issues,
        "atls_doc_paths": _relative_existing_paths(atls_root, ATLS_DOC_RELATIVE_PATHS),
        "project_doc_paths": project_doc_paths,
        "atls_summary_lines": [
            "ATLS는 Jira/Confluence용 AI 친화 CLI이며 JSON 중심 출력과 artifact 저장 규칙을 가진다.",
            "핵심 흐름은 collect -> analyze -> report -> publish 이다.",
            "규칙 기반 필드는 track, workflow_bucket, risk_level, action_needed이고 AI 분석 필드는 요약/다음 액션 중심이다.",
            "현재 harness 분석은 특정 프로젝트 하드코딩 대신 Jira summary와 프로젝트 루트 탐색을 우선 사용한다.",
            "이번 report는 QA/GEMINI만 남기고 other/ops/infra를 제외하도록 정제했다.",
            "프로젝트 체크리스트가 있으면 enrichment에 쓰고, 없으면 live Jira 이슈만으로도 worklist를 구성한다.",
            "분석은 문서 근거, 코드 touchpoint, live Jira issue를 분리해서 합친다.",
            "산출물은 summary/worklist, task analysis, prompt pack 세 묶음으로 구성한다.",
        ],
        "qa_worklist": qa_worklist,
        "gemini_worklist": gemini_worklist,
        "task_analysis": task_analysis,
        "cross_track_insights": _build_cross_track_insights(gap_highlights, qa_worklist, gemini_worklist),
        "open_gaps": open_gap_items,
        "gap_sections": gap_sections,
        "gap_highlights": gap_highlights,
        "prompt_pack": prompt_pack,
    }
    return report
