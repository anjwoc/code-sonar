#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_env(path: Path) -> dict:
    values = dict(os.environ)
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def page_id_from(value: str) -> str:
    value = value.strip()
    if value.isdigit():
        return value
    patterns = [
        r"/pages/(\d+)",
        r"pageId=(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)
    raise ValueError(f"Cannot extract Confluence page id from: {value}")


def slugify(title: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z가-힣._-]+", "-", title).strip("-")
    return slug[:80] or "page"


def run_json(args: list[str]) -> dict:
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout)


def wiki_get(page_id: str) -> dict:
    return run_json(["atls", "wiki", "get", page_id, "--expand", "body.storage,version,ancestors"])


def wiki_children(page_id: str, limit: int = 100) -> list[dict]:
    data = run_json(["atls", "wiki", "children", page_id, "--limit", str(limit)])
    return data.get("children", [])


def write_page(out_dir: Path, page: dict, depth: int, parent_id: str | None, collected_at: str) -> Path:
    page_id = str(page.get("id", ""))
    title = page.get("title", page_id)
    url = page.get("url", "")
    version = page.get("version", "")
    text = page.get("content_text", "").strip()
    page_path = out_dir / "pages" / f"{page_id}-{slugify(title)}.md"
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                "| 항목 | 값 |",
                "|:---|:---|",
                f"| Evidence ID | `wiki:{page_id}` |",
                f"| URL | {url} |",
                f"| Page ID | {page_id} |",
                f"| Version | {version} |",
                f"| Parent Page ID | {parent_id or ''} |",
                f"| Depth | {depth} |",
                f"| Collected At | {collected_at} |",
                "",
                "## Key Facts",
                "",
                *[f"- {line.strip()}" for line in split_facts(text)[:12]],
                "",
                "## Body",
                "",
                text or "> 본문 텍스트를 추출하지 못했습니다.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return page_path


def split_facts(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []
    candidates = re.split(r"(?<=[.!?。])\s+| Overview | Monitoring | Github Repository | 서비스 flow:", compact)
    facts = []
    for item in candidates:
        item = item.strip(" -:\t")
        if 12 <= len(item) <= 220:
            facts.append(item)
    return facts


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    env = load_env(repo_root / ".env")
    urls = [x.strip() for x in env.get("SONAR_WIKI_SOURCE_URLS", "").split(",") if x.strip()]
    if not urls:
        print("SONAR_WIKI_SOURCE_URLS is empty; nothing to scan.")
        return 0
    output_dir = Path(env.get("SONAR_OUTPUT_DIR", "sonar-out"))
    wiki_out = Path(env.get("SONAR_WIKI_SOURCE_OUTPUT_DIR") or output_dir / "_wiki-sources")
    max_depth = int(env.get("SONAR_WIKI_SOURCE_MAX_DEPTH") or "3")
    max_pages = int(env.get("SONAR_WIKI_SOURCE_MAX_PAGES") or "200")
    recursive = env.get("SONAR_WIKI_SOURCE_RECURSIVE", "true").lower() != "false"
    collected_at = datetime.now(timezone.utc).isoformat()

    wiki_out.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    queue: list[tuple[str, int, str | None]] = [(page_id_from(url), 0, None) for url in urls]
    records = []

    while queue and len(records) < max_pages:
        page_id, depth, parent_id = queue.pop(0)
        if page_id in seen:
            continue
        seen.add(page_id)
        page = wiki_get(page_id)
        page_path = write_page(wiki_out, page, depth, parent_id, collected_at)
        records.append(
            {
                "id": str(page.get("id", page_id)),
                "title": page.get("title", page_id),
                "version": page.get("version", ""),
                "url": page.get("url", ""),
                "depth": depth,
                "parent_id": parent_id or "",
                "path": page_path.relative_to(wiki_out).as_posix(),
                "facts": split_facts(page.get("content_text", ""))[:3],
            }
        )
        if recursive and depth < max_depth:
            for child in wiki_children(page_id):
                queue.append((str(child["id"]), depth + 1, page_id))

    index_lines = [
        "# Wiki Source Index",
        "",
        "> `SONAR_WIKI_SOURCE_URLS`에서 수집한 Confluence 원본 페이지 목록입니다. Wiki는 설계/정책/운영 맥락의 보조 근거이며, 구현 사실은 코드와 설정 근거를 우선합니다.",
        "",
        "## Scan Scope",
        "",
        "| 항목 | 값 |",
        "|:---|:---|",
        f"| Root URLs | {'<br/>'.join(urls)} |",
        f"| Recursive | {recursive} |",
        f"| Max Depth | {max_depth} |",
        f"| Max Pages | {max_pages} |",
        f"| Collected At | {collected_at} |",
        "",
        "## Pages",
        "",
        "| Evidence ID | Title | Depth | Parent | URL | Local Cache | Key Facts |",
        "|:---|:---|---:|:---|:---|:---|:---|",
    ]
    for record in records:
        facts = "<br/>".join(record["facts"]).replace("|", "\\|")
        index_lines.append(
            f"| `wiki:{record['id']}` | {record['title']} | {record['depth']} | {record['parent_id']} | {record['url']} | `{record['path']}` | {facts} |"
        )
    index_lines.extend(["", "## Conflicts / Open Questions", "", "> 해당 없음", ""])
    (wiki_out / "WIKI-SOURCE-INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"Scanned {len(records)} wiki pages into {wiki_out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"wiki source scan failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
