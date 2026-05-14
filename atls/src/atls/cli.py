#!/usr/bin/env python3
"""
atls - Atlassian CLI (Jira & Confluence)

AI 에이전트가 안정적으로 호출할 수 있도록 JSON 입출력, 삭제 확인,
프로파일 기반 설정, 그리고 raw API 확장 계층을 제공하는 범용 CLI.
"""

import argparse
import contextlib
import copy
import fcntl
import html
import json
import os
import re
import shutil
import shlex
import socket
import subprocess
import sys
import time
import urllib.parse
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests


GLOBAL_CONFIG_PATH = Path.home() / ".atls_config.json"
LOCAL_CONFIG_NAME = ".atls.json"
LEGACY_DEFAULT_ARTIFACT_ROOT = Path.home() / "Documents" / "atls"
DEFAULT_ARTIFACT_ROOT = Path(__file__).resolve().parents[2] / ".atls-data"
DEFAULT_WORKFLOWS_CONFIG = {
    "daily_review": {
        "wiki_space": "",
        "wiki_parent_page_id": "",
        "wiki_page_id": "",
        "wiki_title_template": "summary",
        "wiki_date_title_template": "{date}",
        "wiki_use_date_container": True,
        "wiki_auto_publish": False,
        "wiki_parent_title": "",
        "wiki_path_hint": "",
    },
    "daily_review_detail": {
        "wiki_space": "",
        "wiki_parent_page_id": "",
        "wiki_page_id": "",
        "wiki_title_template": "detail",
        "wiki_date_title_template": "{date}",
        "wiki_use_date_container": True,
        "wiki_auto_publish": False,
        "wiki_parent_title": "",
        "wiki_path_hint": "",
    }
}
RUNTIME_CONTEXT = {
    "cfg": None,
    "service": None,
    "task_name": None,
    "command": None,
    "skip_auto_artifact": False,
    "dry_run": False,
}

# 토큰은 환경변수(ATLS_JIRA_TOKEN, ATLS_CONFLUENCE_TOKEN)에서 주입합니다.
# 소스코드에 토큰을 하드코딩하지 마세요.
DEFAULT_GLOBAL_CONFIG = {
    "default_profile": "gmarket",
    "profiles": {
        "gmarket": {
            "jira_token": "",
            "jira_base_url": "https://jira.gmarket.com",
            "confluence_token": "",
            "confluence_base_url": "https://wiki.gmarket.com",
            "default_space": "~jaecjeong",
            "default_assignee": "jaecjeong",
            "artifact_root": str(DEFAULT_ARTIFACT_ROOT),
            "workflows": DEFAULT_WORKFLOWS_CONFIG,
            "description": "Gmarket Jira/Confluence",
        }
    },
}

PROFILE_KEYS = [
    "jira_token",
    "jira_base_url",
    "confluence_token",
    "confluence_base_url",
    "default_space",
    "default_assignee",
    "artifact_root",
]

WORKFLOW_ENV_KEYS = {
    "daily_review": {
        "wiki_space": "ATLS_DAILY_REVIEW_WIKI_SPACE",
        "wiki_parent_page_id": "ATLS_DAILY_REVIEW_WIKI_PARENT_PAGE_ID",
        "wiki_page_id": "ATLS_DAILY_REVIEW_WIKI_PAGE_ID",
        "wiki_title_template": "ATLS_DAILY_REVIEW_WIKI_TITLE_TEMPLATE",
        "wiki_date_title_template": "ATLS_DAILY_REVIEW_WIKI_DATE_TITLE_TEMPLATE",
        "wiki_use_date_container": "ATLS_DAILY_REVIEW_WIKI_USE_DATE_CONTAINER",
        "wiki_auto_publish": "ATLS_DAILY_REVIEW_WIKI_AUTO_PUBLISH",
        "wiki_parent_title": "ATLS_DAILY_REVIEW_WIKI_PARENT_TITLE",
        "wiki_path_hint": "ATLS_DAILY_REVIEW_WIKI_PATH_HINT",
    },
    "daily_review_detail": {
        "wiki_space": "ATLS_DAILY_REVIEW_DETAIL_WIKI_SPACE",
        "wiki_parent_page_id": "ATLS_DAILY_REVIEW_DETAIL_WIKI_PARENT_PAGE_ID",
        "wiki_page_id": "ATLS_DAILY_REVIEW_DETAIL_WIKI_PAGE_ID",
        "wiki_title_template": "ATLS_DAILY_REVIEW_DETAIL_WIKI_TITLE_TEMPLATE",
        "wiki_date_title_template": "ATLS_DAILY_REVIEW_DETAIL_WIKI_DATE_TITLE_TEMPLATE",
        "wiki_use_date_container": "ATLS_DAILY_REVIEW_DETAIL_WIKI_USE_DATE_CONTAINER",
        "wiki_auto_publish": "ATLS_DAILY_REVIEW_DETAIL_WIKI_AUTO_PUBLISH",
        "wiki_parent_title": "ATLS_DAILY_REVIEW_DETAIL_WIKI_PARENT_TITLE",
        "wiki_path_hint": "ATLS_DAILY_REVIEW_DETAIL_WIKI_PATH_HINT",
    }
}

JIRA_DEFAULT_FIELDS = [
    "summary",
    "description",
    "status",
    "assignee",
    "priority",
    "comment",
    "labels",
    "issuetype",
]

JIRA_SEARCH_FIELDS = [
    "summary",
    "status",
    "assignee",
    "priority",
    "updated",
    "issuetype",
    "labels",
]

WORKFLOW_TITLE_GLOSSARY = [
    ("recommended title for the campaign and adgroup does not match the seller id", "캠페인/광고그룹 추천 타이틀이 셀러 ID와 불일치"),
    ("first-slot bidding module has some discrepancies between the current frontend implementation and the prd", "퍼스트 슬롯 비딩 모듈의 현재 프론트 구현이 PRD와 불일치"),
    ("for the", ""),
    ("the", ""),
    ("module", "모듈"),
    ("and", "/"),
    ("does not match", "불일치"),
    ("do not match", "불일치"),
    ("is not user-friendly", "사용성이 좋지 않음"),
    ("needs to be prompted", "프론트 안내 필요"),
    ("has two problems", "2건 이슈"),
    ("has three issues", "3건 이슈"),
    ("was not marked with a recommendation tag", "추천 태그 미노출"),
    ("passed to the backend was incorrect", "백엔드 전달값 오류"),
    ("secondary confirmation pop-up", "2차 확인 팝업"),
    ("fails to restore the user’s saved value", "저장값 복원 실패"),
    ("fails to restore the user's saved value", "저장값 복원 실패"),
    ("has some discrepancies between the current frontend implementation and the prd", "현재 프론트 구현과 PRD 불일치"),
    ("when clicking", "클릭 시"),
    ("after selecting", "선택 후"),
    ("creation process", "생성 과정"),
    ("time selection function", "시간 선택 기능"),
    ("the recommended title", "추천 타이틀"),
    ("campaign and adgroup", "캠페인/광고그룹"),
    ("campaign group", "캠페인 그룹"),
    ("campaign title", "캠페인 타이틀"),
    ("registration page", "등록 페이지"),
    ("recommendation tag", "추천 태그"),
    ("seller id", "셀러 ID"),
    ("front end", "프론트"),
    ("backend", "백엔드"),
    ("upper and lower limits", "상하한"),
    ("recommended", "추천"),
    ("prompted", "안내"),
    ("incorrect", "오류"),
    ("first-slot bidding", "퍼스트 슬롯 비딩"),
    ("prd mismatch", "PRD 불일치"),
    ("prd", "PRD"),
    ("quality score", "품질 점수"),
    ("qualityscore", "품질 점수"),
    ("campaign group", "캠페인 그룹"),
    ("campaign", "캠페인"),
    ("adgroup", "광고그룹"),
    ("group", "그룹"),
    ("title", "타이틀"),
    ("duplicate", "중복"),
    ("multiple", "복수"),
    ("productid", "상품 ID"),
    ("products", "상품들"),
    ("product", "상품"),
    ("exclude", "제외"),
    ("search", "검색"),
    ("filter", "필터"),
    ("save", "저장"),
    ("restore", "복원"),
    ("failed", "실패"),
    ("failure", "실패"),
    ("fail", "실패"),
    ("error", "오류"),
    ("issue", "이슈"),
    ("confirm", "확인"),
    ("confirmation", "확인"),
    ("cancel", "취소"),
    ("popup", "팝업"),
    ("modal", "모달"),
    ("page", "페이지"),
    ("display", "노출"),
    ("missing", "누락"),
    ("default", "기본값"),
    ("slot", "슬롯"),
    ("bidding", "비딩"),
]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def slugify(text: str, limit: int = 80) -> str:
    lowered = (text or "").strip().lower()
    lowered = lowered.replace("-", "_")
    lowered = re.sub(r"[^a-z0-9_]+", "_", lowered)
    lowered = re.sub(r"_+", "_", lowered).strip("_")
    if not lowered:
        lowered = "task"
    return lowered[:limit].strip("_") or "task"


def normalize_artifact_root(value: str | None) -> Path:
    if not value:
        return DEFAULT_ARTIFACT_ROOT
    resolved = Path(value).expanduser()
    if resolved == LEGACY_DEFAULT_ARTIFACT_ROOT:
        return DEFAULT_ARTIFACT_ROOT
    return resolved


def artifact_root_path(cfg: dict | None) -> Path:
    if not cfg:
        return DEFAULT_ARTIFACT_ROOT
    value = cfg.get("artifact_root") or str(DEFAULT_ARTIFACT_ROOT)
    return normalize_artifact_root(value)


def artifact_namespace_root(cfg: dict, service: str, project_key: str | None = None) -> Path:
    root = artifact_root_path(cfg)
    project_bucket = slugify(project_key or "shared", 80)
    target_dir = root / "projects" / project_bucket / service
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def infer_service_bucket(cmd: str | None) -> str | None:
    if cmd in ("issue", "worklog", "comment", "project", "user", "jira-api"):
        return "jira"
    if cmd in ("wiki", "wiki-api"):
        return "wiki"
    if cmd == "workflow":
        return "jira"
    if cmd == "ping":
        target = RUNTIME_CONTEXT.get("ping_target")
        if target in ("jira", "wiki"):
            return target
        return "jira"
    return None


def atls_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def extract_search_hint(text: str) -> str | None:
    lowered = (text or "").lower()
    hint_patterns = [
        ("unresolved", "unresolved"),
        ("in progress", "in_progress"),
        ("in review", "in_review"),
        ("to do", "to_do"),
        ("done", "done"),
        ("open", "open"),
        ("closed", "closed"),
    ]
    for needle, hint in hint_patterns:
        if needle in lowered:
            return hint
    tokens = [slugify(token, 24) for token in re.findall(r"[A-Za-z0-9가-힣]+", text or "")]
    tokens = [token for token in tokens if token and token not in {"and", "or", "order", "by", "currentuser", "assignee", "resolution", "status"}]
    return "_".join(tokens[:2]) if tokens else None


def derive_task_name(args) -> str:
    if getattr(args, "task_name", None):
        return slugify(args.task_name, 120)

    cmd = slugify(getattr(args, "cmd", None) or "task", 40)
    subcmd = slugify(getattr(args, "subcmd", None) or "", 40)
    parts = [cmd]
    if subcmd:
        parts.append(subcmd)

    if args.cmd == "issue":
        if args.subcmd == "search":
            hint = extract_search_hint(getattr(args, "jql", ""))
            if hint:
                parts.append(hint)
        elif args.subcmd in ("get", "update", "transition", "transitions", "delete"):
            parts.append(slugify(getattr(args, "issue_id", ""), 40))
        elif args.subcmd == "create":
            parts.append(slugify(getattr(args, "project", ""), 24))
            parts.append(slugify(getattr(args, "summary", ""), 40))
        elif args.subcmd == "mget":
            parts.append("batch")

    elif args.cmd == "worklog":
        parts.append(slugify(getattr(args, "issue_id", ""), 40))
        if getattr(args, "worklog_id", None):
            parts.append(slugify(args.worklog_id, 24))

    elif args.cmd == "comment":
        parts.append(slugify(getattr(args, "issue_id", ""), 40))
        if getattr(args, "comment_id", None):
            parts.append(slugify(args.comment_id, 24))

    elif args.cmd == "project":
        if getattr(args, "project_key", None):
            parts.append(slugify(args.project_key, 24))

    elif args.cmd == "user":
        if getattr(args, "query", None):
            parts.append(slugify(args.query, 32))

    elif args.cmd == "wiki":
        if args.subcmd == "search":
            hint = extract_search_hint(getattr(args, "title", "") or getattr(args, "text", "") or getattr(args, "cql", ""))
            if hint:
                parts.append(hint)
        elif getattr(args, "page_id", None):
            parts.append(slugify(args.page_id, 32))
        elif getattr(args, "title", None):
            parts.append(slugify(args.title, 40))

    elif args.cmd in ("jira-api", "wiki-api"):
        parts.append(slugify(getattr(args, "method", ""), 12))
        parts.append(slugify(getattr(args, "path", ""), 60))
    elif args.cmd == "workflow":
        parts.append(slugify(getattr(args, "subcmd", "run"), 24))
        parts.append(slugify(getattr(args, "scope", ""), 40))
    elif args.cmd == "ping":
        parts.append(slugify(getattr(args, "target", "all"), 16))

    return "_".join([part for part in parts if part])[:160]


def summarize_result_for_markdown(data) -> list[str]:
    lines = []
    if isinstance(data, dict):
        if "total" in data:
            lines.append(f"- total: `{data['total']}`")
        if "issue" in data:
            lines.append(f"- issue: `{data['issue']}`")
        if "key" in data:
            lines.append(f"- key: `{data['key']}`")
        if "page_id" in data:
            lines.append(f"- page_id: `{data['page_id']}`")
        if "id" in data and "page_id" not in data:
            lines.append(f"- id: `{data['id']}`")
        if "success" in data:
            lines.append(f"- success: `{data['success']}`")
        if "status_code" in data:
            lines.append(f"- status_code: `{data['status_code']}`")
    return lines


def unique_artifact_path(base_dir: Path, filename: str) -> Path:
    candidate = base_dir / filename
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        alt = base_dir / f"{stem}_{counter}{suffix}"
        if not alt.exists():
            return alt
        counter += 1


def current_day_slug() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def workflow_daily_review_dir_parts() -> list[str]:
    return ["workflow", "daily_review", current_day_slug()]


def workflow_qa_gemini_harness_dir_parts() -> list[str]:
    return ["workflow", "qa_gemini_harness", current_day_slug()]


def workflow_project_task_flow_dir_parts(project_name: str | None = None) -> list[str]:
    parts = ["workflow", "project_task_flow", current_day_slug()]
    if project_name:
        parts.append(slugify(project_name, 80))
    return parts


def workflow_issue_delivery_dir_parts(project_name: str | None = None) -> list[str]:
    parts = ["workflow", "issue_delivery", current_day_slug()]
    if project_name:
        parts.append(slugify(project_name, 80))
    return parts


def workflow_project_detail_v2_dir_parts() -> list[str]:
    return ["workflow", "project_detail_v2", current_day_slug()]


def workflow_named_artifact_path(cfg: dict, service: str, filename: str, subdirs: list[str]) -> Path:
    target_dir = artifact_namespace_root(cfg, service)
    for subdir in subdirs:
        target_dir = target_dir / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / filename


@contextlib.contextmanager
def workflow_publish_lock(cfg: dict):
    lock_path = artifact_root_path(cfg) / "system" / "locks" / ".atls_wiki_publish.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def save_markdown_artifact(data, success: bool = True):
    cfg = RUNTIME_CONTEXT.get("cfg")
    service = RUNTIME_CONTEXT.get("service")
    task_name = RUNTIME_CONTEXT.get("task_name")
    command = RUNTIME_CONTEXT.get("command")
    if not cfg or not service or not task_name or RUNTIME_CONTEXT.get("skip_auto_artifact"):
        return

    target_dir = artifact_namespace_root(cfg, service) / "auto_results" / current_day_slug()
    target_dir.mkdir(parents=True, exist_ok=True)

    day = datetime.now().strftime("%Y_%m_%d")
    filename = f"{day}_{task_name}.md"
    artifact_path = unique_artifact_path(target_dir, filename)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
    status = "success" if success else "failed"
    summary_lines = summarize_result_for_markdown(data)
    payload_text = json.dumps(data, ensure_ascii=False, indent=2)

    lines = [
        f"# ATLS Result: {task_name}",
        "",
        f"- status: `{status}`",
        f"- executed_at: `{timestamp}`",
        f"- profile: `{cfg.get('active_profile', '')}`",
        f"- service: `{service}`",
        f"- command: `{command}`",
        f"- artifact_path: `{artifact_path}`",
    ]
    if summary_lines:
        lines.extend(["", "## Summary", ""])
        lines.extend(summary_lines)
    lines.extend(["", "## Result", "", "```json", payload_text, "```", ""])
    artifact_path.write_text("\n".join(lines), encoding="utf-8")
    RUNTIME_CONTEXT["last_artifact_path"] = str(artifact_path)


def out(data):
    save_markdown_artifact(data, success=True)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def err_exit(msg: str, code: int = 1):
    save_markdown_artifact({"error": msg}, success=False)
    eprint(f"[오류] {msg}")
    sys.exit(code)


def load_global_config() -> dict:
    if GLOBAL_CONFIG_PATH.exists():
        with open(GLOBAL_CONFIG_PATH) as f:
            return json.load(f)
    GLOBAL_CONFIG_PATH.write_text(
        json.dumps(DEFAULT_GLOBAL_CONFIG, indent=2, ensure_ascii=False)
    )
    eprint(f"[atls] 설정 파일 생성됨: {GLOBAL_CONFIG_PATH}")
    return DEFAULT_GLOBAL_CONFIG


def load_local_config() -> dict:
    path = Path.cwd()
    for _ in range(6):
        candidate = path / LOCAL_CONFIG_NAME
        if candidate.exists():
            with open(candidate) as f:
                return json.load(f)
        parent = path.parent
        if parent == path:
            break
        path = parent
    return {}


def deep_merge_dicts(base: dict | None, override: dict | None) -> dict:
    merged = copy.deepcopy(base or {})
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def parse_env_bool(value: str | None):
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return None


def resolve_workflows_config(profile: dict, local_cfg: dict) -> dict:
    workflows = deep_merge_dicts(DEFAULT_WORKFLOWS_CONFIG, profile.get("workflows", {}))
    workflows = deep_merge_dicts(workflows, local_cfg.get("workflows", {}))

    for workflow_name, env_map in WORKFLOW_ENV_KEYS.items():
        current = dict(workflows.get(workflow_name, {}))
        for field_name, env_key in env_map.items():
            env_value = os.environ.get(env_key)
            if env_value is None:
                continue
            if field_name == "wiki_auto_publish":
                parsed = parse_env_bool(env_value)
                if parsed is not None:
                    current[field_name] = parsed
            else:
                current[field_name] = env_value
        workflows[workflow_name] = current

    return workflows


def workflow_config(cfg: dict, workflow_name: str) -> dict:
    return copy.deepcopy((cfg.get("workflows") or {}).get(workflow_name, {}))


def resolve_config(profile_override: str = None) -> dict:
    global_cfg = load_global_config()
    local_cfg = load_local_config()

    profile_name = (
        profile_override
        or os.environ.get("ATLS_PROFILE")
        or local_cfg.get("profile")
        or global_cfg.get("default_profile", "gmarket")
    )

    profiles = global_cfg.get("profiles", {})
    profile = profiles.get(profile_name, {})
    if not profile:
        eprint(f"[경고] 프로파일 '{profile_name}' 없음. 기본 프로파일 사용.")
        profile_name = global_cfg.get("default_profile", "gmarket")
        profile = profiles.get(profile_name, {})

    cfg = {"active_profile": profile_name}
    for key in PROFILE_KEYS:
        env_key = f"ATLS_{key.upper()}"
        cfg[key] = os.environ.get(env_key) or local_cfg.get(key) or profile.get(key, "")
    if not cfg.get("artifact_root"):
        cfg["artifact_root"] = str(DEFAULT_ARTIFACT_ROOT)
    cfg["artifact_root"] = str(normalize_artifact_root(cfg.get("artifact_root")))
    cfg["workflows"] = resolve_workflows_config(profile, local_cfg)
    return cfg


def confirm_delete(target_lines: list[str]) -> bool:
    if not sys.stdin.isatty():
        eprint("")
        eprint("┌─ [거부] 삭제 작업 차단 ──────────────────────────────────────")
        eprint("│  삭제 명령은 반드시 터미널에서 직접 실행해야 합니다.")
        eprint("│  AI 에이전트가 자동으로 삭제를 실행하는 것을 허용하지 않습니다.")
        eprint("│")
        eprint("│  터미널을 열고 아래 명령을 직접 실행하세요:")
        for line in target_lines:
            eprint(f"│    {line}")
        eprint("└──────────────────────────────────────────────────────────────")
        sys.exit(2)

    eprint("")
    eprint("┌─ 삭제 대상 ──────────────────────────────────────────────────")
    for line in target_lines:
        eprint(f"│  {line}")
    eprint("└──────────────────────────────────────────────────────────────")
    eprint("")

    try:
        answer = input("정말 삭제하시겠습니까? [y/N] ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        eprint("\n취소됨.")
        sys.exit(0)

    if answer not in ("y", "yes"):
        eprint("취소됨.")
        sys.exit(0)
    return True


def parse_json_text(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        err_exit(f"JSON 파싱 실패: {exc}")


def parse_json_input(raw: str = None, file_path: str = None):
    if raw and file_path:
        err_exit("--json 과 --json-file 은 동시에 사용할 수 없습니다.")
    if file_path:
        return parse_json_text(Path(file_path).read_text())
    if raw:
        return parse_json_text(raw)
    return None


def parse_scalar(value: str):
    lowered = value.lower()
    if lowered in ("true", "false", "null"):
        return json.loads(lowered)
    try:
        if value and value[0] in "[{\"":
            return json.loads(value)
    except json.JSONDecodeError:
        pass
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_key_value(entry: str):
    if "=" not in entry:
        err_exit(f"KEY=VALUE 형식이 아닙니다: {entry}")
    key, value = entry.split("=", 1)
    return key.strip(), parse_scalar(value.strip())


def parse_kv_list(entries: list[str] | None) -> dict:
    data = {}
    for entry in entries or []:
        key, value = parse_key_value(entry)
        data[key] = value
    return data


def merge_dicts(*dicts):
    merged = {}
    for item in dicts:
        if isinstance(item, dict):
            merged.update(item)
    return merged


def read_text_arg(value: str = None, file_path: str = None, label: str = "content") -> str:
    if value and file_path:
        err_exit(f"{label}: 값과 파일 옵션을 동시에 사용할 수 없습니다.")
    if file_path:
        return Path(file_path).read_text()
    if value is not None:
        return value
    err_exit(f"{label}: 내용이 필요합니다.")


def confluence_markdown_macro(markdown: str) -> str:
    escaped = markdown.replace("]]>", "]]]]><![CDATA[>")
    return (
        '<ac:structured-macro ac:name="markdown" ac:schema-version="1">'
        f"<ac:plain-text-body><![CDATA[{escaped}]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    )


def read_wiki_content_arg(args, label: str) -> str:
    html_set = args.content_html is not None or args.content_file is not None
    markdown_set = args.markdown is not None or args.markdown_file is not None
    if html_set and markdown_set:
        err_exit(f"{label}: HTML 입력과 Markdown 입력을 동시에 사용할 수 없습니다.")
    if markdown_set:
        markdown = read_text_arg(args.markdown, args.markdown_file, label)
        return confluence_markdown_macro(markdown)
    return read_text_arg(args.content_html, args.content_file, label)


def init_runtime_context(cfg: dict, args):
    RUNTIME_CONTEXT["cfg"] = cfg
    RUNTIME_CONTEXT["ping_target"] = ping_target_name(args) if getattr(args, "cmd", None) == "ping" else None
    RUNTIME_CONTEXT["service"] = infer_service_bucket(getattr(args, "cmd", None))
    RUNTIME_CONTEXT["task_name"] = derive_task_name(args)
    argv = ["atls"] + list(sys.argv[1:])
    RUNTIME_CONTEXT["command"] = " ".join(shlex.quote(arg) for arg in argv)
    RUNTIME_CONTEXT["last_artifact_path"] = None
    RUNTIME_CONTEXT["skip_auto_artifact"] = getattr(args, "cmd", None) == "workflow"
    RUNTIME_CONTEXT["dry_run"] = getattr(args, "dry_run", False)


def is_dry_run() -> bool:
    return bool(RUNTIME_CONTEXT.get("dry_run"))


def dry_run_preview(action: str, payload: dict | None = None):
    """dry-run 모드에서 실제 API 호출 없이 실행 예정 내용을 출력하고 종료합니다."""
    preview = {"dry_run": True, "action": action}
    if payload:
        preview["payload"] = payload
    out(preview)
    sys.exit(0)


def resolve_service_token(cfg: dict, service: str) -> str:
    """토큰 해석 우선순위: 환경변수 > 설정 파일."""
    if service == "jira":
        return os.environ.get("ATLS_JIRA_TOKEN") or cfg.get("jira_token", "")
    if service == "wiki":
        return os.environ.get("ATLS_CONFLUENCE_TOKEN") or cfg.get("confluence_token", "")
    return ""


def ensure_service_token(cfg: dict, service: str):
    token = resolve_service_token(cfg, service)
    if not token:
        env_key = "ATLS_JIRA_TOKEN" if service == "jira" else "ATLS_CONFLUENCE_TOKEN"
        err_exit(
            f"토큰이 없습니다. 환경변수 {env_key}를 설정하거나 "
            f"~/.atls_config.json의 profile에 토큰을 추가하세요."
        )


def api_base_url(cfg: dict, service: str) -> str:
    if service == "jira":
        return cfg["jira_base_url"]
    if service == "wiki":
        return cfg["confluence_base_url"]
    err_exit(f"알 수 없는 서비스: {service}")


def api_default_prefix(service: str) -> str:
    return "/rest/api/2" if service == "jira" else "/rest/api"


def build_headers(cfg: dict, service: str, extra_headers: dict = None) -> dict:
    token = resolve_service_token(cfg, service)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    headers.update(extra_headers or {})
    return headers


def resolve_api_url(cfg: dict, service: str, path: str) -> str:
    if re.match(r"^https?://", path):
        return path
    normalized = path if path.startswith("/") else f"/{path}"
    if normalized.startswith("/rest/"):
        return api_base_url(cfg, service) + normalized
    return api_base_url(cfg, service) + api_default_prefix(service) + normalized


def request_api(
    cfg: dict,
    service: str,
    method: str,
    path: str,
    params: dict = None,
    payload=None,
    extra_headers: dict = None,
    timeout: int = 30,
) -> requests.Response:
    ensure_service_token(cfg, service)
    url = resolve_api_url(cfg, service, path)
    headers = build_headers(cfg, service, extra_headers)
    return requests.request(
        method.upper(),
        url,
        headers=headers,
        params=params,
        json=payload,
        timeout=timeout,
    )


def ping_target_name(args) -> str:
    target = getattr(args, "target", "all")
    return target if target in ("jira", "wiki") else "all"


def host_port_from_url(url: str) -> tuple[str, int, str]:
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    scheme = parsed.scheme or "https"
    return host, port, scheme


def socket_ping(host: str, port: int, timeout: float) -> dict:
    started = time.monotonic()
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        resolved = sorted({info[4][0] for info in infos})
        resolve_ms = round((time.monotonic() - started) * 1000, 2)
    except socket.gaierror as exc:
        return {
            "ok": False,
            "stage": "dns",
            "host": host,
            "port": port,
            "error": str(exc),
        }

    tcp_started = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            tcp_ms = round((time.monotonic() - tcp_started) * 1000, 2)
            return {
                "ok": True,
                "stage": "tcp",
                "host": host,
                "port": port,
                "resolved_ips": resolved,
                "dns_ms": resolve_ms,
                "tcp_ms": tcp_ms,
            }
    except OSError as exc:
        return {
            "ok": False,
            "stage": "tcp",
            "host": host,
            "port": port,
            "resolved_ips": resolved,
            "dns_ms": resolve_ms,
            "error": str(exc),
        }


def http_ping(url: str, timeout: float) -> dict:
    started = time.monotonic()
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
        elapsed_ms = round((time.monotonic() - started) * 1000, 2)
        return {
            "ok": True,
            "url": url,
            "status_code": resp.status_code,
            "elapsed_ms": elapsed_ms,
            "final_url": resp.url,
        }
    except requests.exceptions.RequestException as exc:
        return {
            "ok": False,
            "url": url,
            "error": str(exc),
        }


def api_ping(cfg: dict, service: str, timeout: float) -> dict:
    try:
        if service == "jira":
            resp = request_api(cfg, "jira", "GET", "/myself", timeout=timeout)
            if resp.status_code >= 400:
                return {
                    "ok": False,
                    "endpoint": "/rest/api/2/myself",
                    "status_code": resp.status_code,
                    "body_preview": resp.text[:300],
                }
            data = resp.json()
            return {
                "ok": True,
                "endpoint": "/rest/api/2/myself",
                "status_code": resp.status_code,
                "user": data.get("displayName") or data.get("name"),
            }

        resp = request_api(cfg, "wiki", "GET", "/space", params={"limit": 1}, timeout=timeout)
        if resp.status_code >= 400:
            return {
                "ok": False,
                "endpoint": "/rest/api/space?limit=1",
                "status_code": resp.status_code,
                "body_preview": resp.text[:300],
            }
        data = resp.json()
        return {
            "ok": True,
            "endpoint": "/rest/api/space?limit=1",
            "status_code": resp.status_code,
            "results": data.get("size") or len(data.get("results", [])),
        }
    except requests.exceptions.RequestException as exc:
        return {
            "ok": False,
            "endpoint": "/rest/api/2/myself" if service == "jira" else "/rest/api/space?limit=1",
            "error": str(exc),
        }


def ping_service(cfg: dict, service: str, timeout: float = 5.0) -> dict:
    base_url = cfg["jira_base_url"] if service == "jira" else cfg["confluence_base_url"]
    host, port, _scheme = host_port_from_url(base_url)
    socket_result = socket_ping(host, port, timeout)
    http_result = http_ping(base_url, timeout)
    api_result = api_ping(cfg, service, timeout)
    overall_ok = bool(socket_result.get("ok") and http_result.get("ok") and api_result.get("ok"))
    return {
        "service": service,
        "base_url": base_url,
        "ok": overall_ok,
        "dns_tcp": socket_result,
        "http": http_result,
        "api": api_result,
    }


def cmd_ping(cfg: dict, args):
    targets = ["jira", "wiki"] if args.target == "all" else [args.target]
    results = []
    for service in targets:
        results.append(ping_service(cfg, service, timeout=args.timeout))
    out(
        {
            "success": all(item.get("ok") for item in results),
            "target": args.target,
            "results": results,
        }
    )


def chunked(items: list, size: int):
    for idx in range(0, len(items), size):
        yield items[idx:idx + size]


def jira_search_raw(cfg: dict, jql: str, max_results: int, fields: list[str]) -> dict:
    payload = {
        "jql": jql,
        "maxResults": max_results,
        "fields": fields,
    }
    resp = request_api(cfg, "jira", "POST", "/search", payload=payload)
    handle_response(resp, "이슈 검색 실패")
    return resp.json()


def jira_fetch_issue_details(cfg: dict, issue_ids: list[str], fields: list[str]) -> list[dict]:
    detailed = []
    for batch in chunked(issue_ids, 50):
        payload = {
            "jql": "issuekey in (" + ",".join(batch) + ") ORDER BY updated DESC",
            "maxResults": len(batch),
            "fields": fields,
        }
        resp = request_api(cfg, "jira", "POST", "/search", payload=payload)
        handle_response(resp, "이슈 상세 조회 실패")
        detailed.extend(resp.json().get("issues", []))
    return detailed


def workflow_clean_text(value: str, limit: int = 280) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    return text[:limit]


def workflow_clean_rich_text(value: str, limit: int = 280) -> str:
    text = value or ""
    text = re.sub(r"!\S+?!", " ", text)
    text = re.sub(r"\{[^}]+\}", " ", text)
    text = re.sub(r"\[~[^\]]+\]", " ", text)
    text = re.sub(r"#+\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def workflow_ascii_ratio(text: str) -> float:
    cleaned = text or ""
    if not cleaned:
        return 0.0
    ascii_letters = len(re.findall(r"[A-Za-z]", cleaned))
    meaningful = len(re.findall(r"[A-Za-z가-힣]", cleaned))
    if meaningful == 0:
        return 0.0
    return ascii_letters / meaningful


def parse_atlassian_datetime(value: str):
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def workflow_days_since(value: str) -> int | None:
    parsed = parse_atlassian_datetime(value)
    if not parsed:
        return None
    now = datetime.now(parsed.tzinfo) if parsed.tzinfo else datetime.now()
    delta = now - parsed
    return max(delta.days, 0)


def workflow_stale_status(issue: dict) -> str:
    bucket = issue.get("workflow_bucket")
    open_days = issue.get("open_days")
    idle_days = issue.get("idle_days")

    if track := issue.get("track"):
        if track in {"gemini", "qa"} and bucket in {"active", "review"}:
            return "urgent-active"

    if idle_days is not None and idle_days >= 14:
        return "stale"
    if open_days is not None and open_days >= 21 and bucket == "todo":
        return "stale"
    if idle_days is not None and idle_days >= 7:
        return "aging"
    if open_days is not None and open_days >= 10 and bucket == "todo":
        return "aging"
    return "fresh"


def workflow_attention_bucket(issue: dict) -> str:
    track = issue.get("track")
    bucket = issue.get("workflow_bucket")
    stale_status = issue.get("stale_status")

    if track in {"gemini", "qa"} and bucket in {"active", "review"}:
        return "urgent_qa_active"
    if track in {"gemini", "qa"} and stale_status == "stale":
        return "urgent_qa_stale"
    if track in {"gemini", "qa"}:
        return "urgent_qa_todo"
    if stale_status == "stale":
        return "stale_backlog"
    if stale_status == "aging":
        return "aging_backlog"
    return "normal_backlog"


def workflow_stale_label(stale_status: str) -> str:
    return {
        "urgent-active": "긴급 진행중",
        "stale": "방치 가능성 높음",
        "aging": "지연 주의",
        "fresh": "최근 흐름 유지",
    }.get(stale_status or "fresh", "최근 흐름 유지")


def workflow_html_escape(value) -> str:
    return html.escape(str(value or ""), quote=True)


def workflow_attention_label(attention_bucket: str) -> str:
    return {
        "urgent_qa_active": "긴급 QA 진행",
        "urgent_qa_stale": "긴급 QA 방치 점검",
        "urgent_qa_todo": "긴급 QA 착수 필요",
        "stale_backlog": "장기 방치 백로그",
        "aging_backlog": "지연 중인 백로그",
        "normal_backlog": "일반 백로그",
    }.get(attention_bucket or "normal_backlog", "일반 백로그")


def workflow_track(issue: dict) -> str:
    key = issue.get("key", "")
    summary = issue.get("summary", "")
    labels = set(issue.get("labels", []))
    if key.startswith("GEMINI-") or "GEMINI" in summary.upper():
        return "gemini"
    if key.startswith("QA-"):
        return "qa"
    if key.startswith("SYSCHECK-"):
        return "ops"
    if "UI" in summary.upper() or summary.startswith("[UI]"):
        return "adcenter_ui"
    if "OLD ADCENTER" in summary.upper():
        return "legacy_adcenter"
    if "infra" in summary.lower() or any("infra" in label.lower() for label in labels):
        return "infra"
    return "other"


def workflow_bucket(status: str) -> str:
    normalized = (status or "").strip().lower()
    if normalized in {"to do", "open", "booked"}:
        return "todo"
    if normalized in {"in progress"}:
        return "active"
    if normalized in {"in review"}:
        return "review"
    if normalized in {"blocked", "on hold"}:
        return "blocked"
    return "other"


def workflow_action_needed(issue: dict) -> list[str]:
    labels = {label.lower() for label in issue.get("labels", [])}
    summary = issue.get("summary", "").lower()
    issue_type = issue.get("issue_type", "").lower()
    actions = []
    if "pd_sync" in labels or "prd_sync" in labels:
        actions.append("needs_prd_confirmation")
    if "ux" in labels:
        actions.append("needs_ux_confirmation")
    if "문의" in issue.get("summary", ""):
        actions.append("needs_comment_followup")
    if issue_type == "bug":
        actions.append("needs_dev")
    if workflow_bucket(issue.get("status", "")) == "review":
        actions.append("needs_review_confirmation")
    if workflow_bucket(issue.get("status", "")) == "active":
        actions.append("needs_progress_check")
    if "alert" in summary or "tooltip" in summary or "문구" in issue.get("summary", ""):
        actions.append("needs_qa_retest")
    deduped = []
    for action in actions:
        if action not in deduped:
            deduped.append(action)
    return deduped


def workflow_risk(issue: dict) -> str:
    priority = (issue.get("priority") or "").lower()
    track = issue.get("track")
    bucket = issue.get("workflow_bucket")
    if priority in {"highest", "high"}:
        return "high"
    if track in {"gemini", "qa"} and bucket in {"active", "review"}:
        return "high"
    if track in {"gemini", "qa"}:
        return "medium"
    return "low"


def workflow_analysis(issue: dict) -> dict:
    description = workflow_clean_rich_text(issue.get("description", ""), 420)
    comments = issue.get("recent_comments", [])
    recent_comment = workflow_clean_rich_text(comments[-1]["body"], 260) if comments else ""
    one_line = workflow_clean_rich_text(issue.get("summary", ""), 180)
    next_action = "상태와 담당자 맥락 확인"
    actions = issue.get("action_needed", [])
    if "needs_prd_confirmation" in actions:
        next_action = "PRD 기대 동작과 이슈 범위를 다시 맞춰보기"
    elif "needs_ux_confirmation" in actions:
        next_action = "UX 동작과 화면 플로우 기대값 확인"
    elif "needs_review_confirmation" in actions:
        next_action = "리뷰 피드백 확인 후 재테스트 필요 여부 판단"
    elif "needs_qa_retest" in actions:
        next_action = "재테스트 시나리오를 준비하고 기대 UI 동작 확인"
    elif "needs_dev" in actions:
        next_action = "구현 현황과 남은 수정 범위 확인"
    elif "needs_comment_followup" in actions:
        next_action = "코멘트 히스토리를 읽고 열린 질문에 답변"
    return {
        "one_line_summary": one_line,
        "description_excerpt": description,
        "recent_comment_excerpt": recent_comment,
        "next_recommended_action": next_action,
    }


def workflow_recent_comment_entries(issue: dict, limit: int = 3) -> list[dict]:
    comments = issue.get("recent_comments", [])[-limit:]
    entries = []
    for comment in comments:
        body = workflow_clean_rich_text(comment.get("body", ""), 420)
        localized = workflow_localize_text(body, 320)
        entries.append(
            {
                "author": comment.get("author") or "unknown",
                "created": comment.get("created") or "",
                "created_short": workflow_short_datetime(comment.get("created") or ""),
                "body": body,
                "localized_body": localized or "영문 코멘트 확인 필요",
            }
        )
    return entries


def workflow_current_situation(issue: dict) -> str:
    analysis = issue.get("analysis", {})
    detail = issue.get("detail_analysis", {})
    comments = workflow_recent_comment_entries(issue, 3)
    next_action = analysis.get("next_recommended_action", "상태와 담당자 맥락 확인")
    status = issue.get("status") or "n/a"
    localized_desc = detail.get("description_localized") or workflow_compact_problem(issue)
    latest_body = ((comments[-1].get("body") if comments else "") or "").lower()

    blocker = ""
    if "querycampaigngroupcountcreatedtoday" in latest_body or "querycampaigncountcreatedtoday" in latest_body:
        blocker = "타입별 count 정보를 제공하는 API가 없어 suffix 계산 로직 적용이 막혀 있습니다."
    elif "mapping error" in latest_body:
        blocker = "필드 매핑 오류가 핵심 원인으로 보이며 데이터 매핑 수정이 필요합니다."
    elif "null" in latest_body:
        blocker = "응답값이 null로 내려와 화면 반영이 되지 않는 문제가 남아 있습니다."
    elif "review" in latest_body or issue.get("workflow_bucket") == "review":
        blocker = "리뷰 피드백 반영 여부와 재테스트 결과 확인이 필요합니다."
    elif issue.get("workflow_bucket") == "active":
        blocker = "구현 진행 중이며 남은 수정 범위와 적용 일정 확인이 필요합니다."
    elif issue.get("workflow_bucket") == "todo":
        blocker = "구현 착수 전 요구사항과 처리 범위를 먼저 확정해야 합니다."
    else:
        blocker = "현재 이슈 상태와 최신 코멘트 기준으로 추가 확인이 필요합니다."

    lines = [
        f"핵심 이슈는 {localized_desc} 입니다.",
        f"현재 상태는 {status} 이며, {detail.get('aging_statement', '')} 단계입니다.",
        blocker,
        f"해결 방향은 {next_action} 입니다.",
    ]
    return " ".join(line for line in lines if line).strip()


def workflow_contains_hangul(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text or ""))


def workflow_looks_english_title(text: str) -> bool:
    cleaned = (text or "").strip()
    if not cleaned or workflow_contains_hangul(cleaned):
        return False
    ascii_letters = re.findall(r"[A-Za-z]", cleaned)
    return bool(ascii_letters)


def workflow_translate_english_title(summary: str) -> str:
    core = re.sub(r"^(?:\[[^\]]+\]\s*)+", "", summary or "").strip()
    translated = f" {core.lower()} "
    for english, korean in sorted(WORKFLOW_TITLE_GLOSSARY, key=lambda item: len(item[0]), reverse=True):
        translated = re.sub(rf"(?i)(?<![a-z0-9]){re.escape(english)}(?![a-z0-9])", f" {korean} ", translated)
    translated = re.sub(r"[_/]+", " ", translated)
    translated = translated.replace("'", "")
    translated = re.sub(r"\s+", " ", translated).strip(" -_:")
    if not translated:
        return core or summary
    if re.fullmatch(r"[A-Za-z0-9 .,_()/+-]+", translated):
        return "영문 원문 확인이 필요한 기능 이슈"
    translated = translated.replace(" ,", ",").replace(" .", ".")
    return translated


def workflow_localize_text(text: str, limit: int = 320) -> str:
    cleaned = workflow_clean_rich_text(text, limit * 2)
    if not cleaned:
        return ""
    if workflow_contains_hangul(cleaned):
        return cleaned[:limit]
    translated = f" {cleaned.lower()} "
    for english, korean in sorted(WORKFLOW_TITLE_GLOSSARY, key=lambda item: len(item[0]), reverse=True):
        translated = re.sub(rf"(?i)(?<![a-z0-9]){re.escape(english)}(?![a-z0-9])", f" {korean} ", translated)
    translated = re.sub(r"\s+", " ", translated).strip(" -_:")
    if not translated:
        return cleaned[:limit]
    if re.fullmatch(r"[A-Za-z0-9 .,_()/+-]+", translated):
        return ""
    if workflow_ascii_ratio(translated) > 0.15:
        return ""
    return translated[:limit]


def workflow_display_title(issue: dict) -> dict:
    summary = issue.get("summary", "").strip()
    if workflow_looks_english_title(summary):
        return {
            "localized": workflow_translate_english_title(summary),
            "original": summary,
            "show_original": True,
        }
    return {
        "localized": summary,
        "original": summary,
        "show_original": False,
    }


def workflow_track_label(track: str) -> str:
    return {
        "gemini": "GEMINI QA",
        "qa": "QA",
        "ops": "운영",
        "adcenter_ui": "UI",
        "legacy_adcenter": "구 광고센터",
        "infra": "인프라",
        "other": "기타",
    }.get(track or "other", "기타")


def workflow_issue_narrative(issue: dict) -> list[str]:
    analysis = issue.get("analysis", {})
    issue_type = issue.get("issue_type") or "Task"
    priority = issue.get("priority") or "n/a"
    display_title = workflow_display_title(issue)
    description = analysis.get("description_excerpt") or analysis.get("one_line_summary") or issue.get("summary", "")
    description = workflow_clean_text(description, 180)
    recent_comment = workflow_clean_text(analysis.get("recent_comment_excerpt", ""), 160)
    next_action = analysis.get("next_recommended_action", "현황과 담당 맥락 확인")
    action_labels = ", ".join(issue.get("action_needed") or []) or "특이 액션 라벨 없음"
    detail_line = description if workflow_contains_hangul(description) else display_title["localized"]

    lines = [
        f"이 이슈는 {workflow_track_label(issue.get('track'))} 트랙의 {issue_type} 건으로, 현재 상태는 {issue.get('status')}이며 우선순위는 {priority}입니다.",
        f"핵심 내용은 {detail_line or issue.get('summary', '')} 관련 이슈입니다.",
    ]
    if recent_comment and workflow_contains_hangul(recent_comment):
        lines.append(f"최근 코멘트 기준으로는 {recent_comment} 흐름이며, 다음 확인 포인트는 {next_action} 입니다.")
    else:
        lines.append(f"현재 액션 라벨은 {action_labels} 이고, 다음 확인 포인트는 {next_action} 입니다.")
    return lines[:3]


def workflow_detail_analysis(issue: dict) -> dict:
    title = workflow_display_title(issue)
    analysis = issue.get("analysis", {})
    summary_basis = title["localized"] if title.get("show_original") else issue.get("summary", "")
    summary_basis = workflow_clean_rich_text(summary_basis, 120)
    description = workflow_clean_rich_text(analysis.get("description_excerpt", ""), 320)
    open_days = issue.get("open_days")
    idle_days = issue.get("idle_days")
    stale_label = workflow_stale_label(issue.get("stale_status"))
    attention_label = workflow_attention_label(issue.get("attention_bucket"))
    next_action = analysis.get("next_recommended_action", "상태와 담당자 맥락 확인")
    comment_entries = workflow_recent_comment_entries(issue, 3)

    problem_statement = summary_basis
    if description:
        problem_statement = description

    impact_statement = f"{workflow_track_label(issue.get('track'))} / {attention_label}"
    if issue.get("track") in {"gemini", "qa"}:
        impact_statement = f"{workflow_track_label(issue.get('track'))} / QA 흐름 직접 영향"

    aging_statement = f"생성 {open_days}일 / 최근 업데이트 {idle_days}일 / {stale_label}"
    if open_days is None or idle_days is None:
        aging_statement = f"{stale_label} / 생성일 또는 업데이트 시각 추가 확인 필요"

    localized_description = workflow_localize_text(description or summary_basis, 320)
    if not localized_description:
        localized_description = workflow_compact_problem(issue)

    return {
        "problem_statement": problem_statement,
        "description_statement": description or summary_basis,
        "description_localized": localized_description,
        "current_situation_statement": "",
        "impact_statement": impact_statement,
        "aging_statement": aging_statement,
        "next_action_statement": next_action,
        "comment_entries": comment_entries,
        "situation_analysis_statement": "",
    }


def workflow_compact_problem(issue: dict) -> str:
    title = workflow_display_title(issue)
    if title.get("localized"):
        return workflow_clean_text(title["localized"], 120)
    analysis = issue.get("analysis", {})
    description = workflow_clean_text(analysis.get("description_excerpt", ""), 140)
    return description or workflow_clean_text(issue.get("summary", ""), 120)


def workflow_recent_note(issue: dict) -> str:
    analysis = issue.get("analysis", {})
    recent = workflow_clean_text(analysis.get("recent_comment_excerpt", ""), 120)
    return recent


def workflow_status_line(issue: dict) -> list[tuple[str, str]]:
    return [
        ("Track", workflow_track_label(issue.get("track"))),
        ("Type", issue.get("issue_type") or "n/a"),
        ("Current Status", issue.get("status") or "n/a"),
        ("Priority", issue.get("priority") or "n/a"),
        ("Created", issue.get("created") or "n/a"),
        ("Open Days", str(issue.get("open_days", "n/a"))),
        ("Idle Days", str(issue.get("idle_days", "n/a"))),
        ("Stale", workflow_stale_label(issue.get("stale_status"))),
    ]


def workflow_detail_status_line(issue: dict) -> list[tuple[str, str]]:
    rows = workflow_status_line(issue)
    rows.insert(5, ("Updated", issue.get("updated") or "n/a"))
    rows.append(("Attention", workflow_attention_label(issue.get("attention_bucket"))))
    return rows


def workflow_short_datetime(value: str) -> str:
    return (value or "").replace("T", " ")[:16] or "n/a"


def workflow_short_date(value: str) -> str:
    return (value or "")[:10] or "n/a"


def workflow_days_text(value) -> str:
    if value is None or value == "":
        return "n/a"
    return f"{value}d"


def workflow_issue_title_markdown(issue: dict) -> str:
    title = workflow_display_title(issue)
    parts = [f"**{title['localized']}**"]
    if title["show_original"]:
        parts.append(f"<br><span style=\"color:#6b778c\">({title['original']})</span>")
    return "".join(parts)


def workflow_issue_title_html(issue: dict) -> str:
    title = workflow_display_title(issue)
    parts = [f"<strong>{workflow_html_escape(title['localized'])}</strong>"]
    if title["show_original"]:
        parts.append(
            f"<br/><span style=\"color:#6b778c\">({workflow_html_escape(title['original'])})</span>"
        )
    return "".join(parts)


def workflow_issue_key_link_markdown(issue: dict) -> str:
    return f"[`{issue['key']}`]({issue['url']})"


def workflow_issue_key_link_html(issue: dict) -> str:
    return f"<a href=\"{workflow_html_escape(issue['url'])}\"><code>{workflow_html_escape(issue['key'])}</code></a>"


def workflow_markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        safe_row = [str(cell).replace("\n", "<br>") for cell in row]
        lines.append("| " + " | ".join(safe_row) + " |")
    return lines


def workflow_html_table(headers: list[str], rows: list[list[str]]) -> str:
    parts = [
        "<table><tbody>",
        "<tr>" + "".join(f"<th>{workflow_html_escape(header)}</th>" for header in headers) + "</tr>",
    ]
    for row in rows:
        parts.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def workflow_issue_summary_cells(issue: dict) -> list[str]:
    analysis = issue.get("analysis", {})
    return [
        workflow_issue_key_link_markdown(issue),
        issue.get("status") or "n/a",
        issue.get("priority") or "n/a",
        workflow_short_date(issue.get("created")),
        workflow_days_text(issue.get("open_days")),
        workflow_days_text(issue.get("idle_days")),
        workflow_issue_title_markdown(issue),
        workflow_compact_problem(issue),
        analysis.get("next_recommended_action") or "",
    ]


def workflow_issue_summary_html_cells(issue: dict) -> list[str]:
    analysis = issue.get("analysis", {})
    return [
        workflow_issue_key_link_html(issue),
        workflow_html_escape(issue.get("status") or "n/a"),
        workflow_html_escape(issue.get("priority") or "n/a"),
        workflow_html_escape(workflow_short_date(issue.get("created"))),
        workflow_html_escape(workflow_days_text(issue.get("open_days"))),
        workflow_html_escape(workflow_days_text(issue.get("idle_days"))),
        workflow_issue_title_html(issue),
        workflow_html_escape(workflow_compact_problem(issue)),
        workflow_html_escape(analysis.get("next_recommended_action") or ""),
    ]


def workflow_compact_counts(counts: dict, labeler=None) -> str:
    if not counts:
        return "-"
    parts = []
    for key, value in counts.items():
        label = labeler(key) if labeler else key
        parts.append(f"{label} {value}")
    return " / ".join(parts)


def workflow_expand_html(title: str, body_html: str) -> str:
    return (
        "<ac:structured-macro ac:name=\"expand\">"
        f"<ac:parameter ac:name=\"title\">{workflow_html_escape(title)}</ac:parameter>"
        f"<ac:rich-text-body>{body_html}</ac:rich-text-body>"
        "</ac:structured-macro>"
    )


def workflow_markdown_issue_card(issue: dict, detailed: bool = False) -> list[str]:
    detail = issue.get("detail_analysis", {})
    analysis = issue.get("analysis", {})
    lines = [
        f"#### {workflow_issue_key_link_markdown(issue)}",
        "",
        workflow_issue_title_markdown(issue),
    ]
    lines.append("")
    meta_rows = [
        ["Status", issue.get("status") or "n/a", "Priority", issue.get("priority") or "n/a"],
        ["Created", workflow_short_datetime(issue.get("created")), "Updated", workflow_short_datetime(issue.get("updated") if detailed else issue.get("created"))],
        ["Open", workflow_days_text(issue.get("open_days")), "Idle", workflow_days_text(issue.get("idle_days"))],
    ]
    if detailed:
        meta_rows.append(["Stale", workflow_stale_label(issue.get("stale_status")), "Attention", workflow_attention_label(issue.get("attention_bucket"))])
        meta_rows.append(["Assignee", issue.get("assignee") or "Unassigned", "Type", issue.get("issue_type") or "n/a"])
    else:
        meta_rows.append(["Stale", workflow_stale_label(issue.get("stale_status")), "Assignee", issue.get("assignee") or "Unassigned"])
    lines.extend(workflow_markdown_table(["Field", "Value", "Field", "Value"], meta_rows))
    lines.append("")
    lines.append(f"- 문제: {workflow_compact_problem(issue)}")
    lines.append("")
    if detailed:
        lines.append("[본문]")
        lines.append(detail.get("description_statement", ""))
        lines.append("")
        lines.append("[번역]")
        lines.append(detail.get("description_localized", ""))
        lines.append("")
        lines.append("[상황 분석 및 해결방안]")
        lines.append(detail.get("situation_analysis_statement", ""))
        lines.append("")
        lines.append(f"- 영향: {detail.get('impact_statement', '')}")
        lines.append(f"- 상태 판단: {detail.get('aging_statement', '')}")
        comment_entries = detail.get("comment_entries") or []
        if comment_entries:
            lines.append("- 최근 코멘트:")
            for entry in comment_entries:
                lines.append(
                    f"  - {entry.get('created_short', 'n/a')} / {entry.get('author', 'unknown')}: {entry.get('body', '')}"
                )
        else:
            lines.append("- 최근 코멘트: 없음")
    else:
        recent_note = workflow_recent_note(issue)
        if recent_note:
            lines.append(f"- 최근 코멘트: {recent_note}")
    next_action = analysis.get("next_recommended_action") or detail.get("next_action_statement", "")
    if next_action:
        lines.append(f"- 다음 액션: {next_action}")
    if issue.get("action_needed"):
        lines.append(f"- 액션 라벨: `{', '.join(issue['action_needed'])}`")
    lines.append(f"- 링크: {issue['url']}")
    lines.append("")
    return lines


def workflow_html_summary_table(result: dict, detailed: bool = False) -> str:
    rows = [
        "<table><tbody>",
        "<tr><th>Group</th><th>Total</th><th>Status</th></tr>",
    ]
    for group_name in ("gemini", "qa", "other"):
        group = result["groups"].get(group_name, {})
        status_text = json.dumps(group.get("status_counts", {}), ensure_ascii=False)
        if detailed:
            status_text = (
                f"attention {json.dumps(group.get('attention_counts', {}), ensure_ascii=False)} / "
                f"stale {json.dumps(group.get('stale_counts', {}), ensure_ascii=False)}"
            )
        rows.append(
            "<tr>"
            f"<td>{workflow_html_escape(group_name)}</td>"
            f"<td>{workflow_html_escape(group.get('total', 0))}</td>"
            f"<td>{workflow_html_escape(status_text)}</td>"
            "</tr>"
        )
    rows.append("</tbody></table>")
    return "".join(rows)


def workflow_html_meta_table(rows: list[tuple[str, str]]) -> str:
    parts = ["<table><tbody>"]
    for label, value in rows:
        parts.append(
            "<tr>"
            f"<th>{workflow_html_escape(label)}</th>"
            f"<td>{workflow_html_escape(value)}</td>"
            "</tr>"
        )
    parts.append("</tbody></table>")
    return "".join(parts)


def workflow_html_issue_card(issue: dict, detailed: bool = False) -> str:
    detail = issue.get("detail_analysis", {})
    analysis = issue.get("analysis", {})
    next_action = analysis.get("next_recommended_action") or detail.get("next_action_statement", "")
    meta_rows = [
        [
            workflow_html_escape("Status"),
            workflow_html_escape(issue.get("status") or "n/a"),
            workflow_html_escape("Priority"),
            workflow_html_escape(issue.get("priority") or "n/a"),
        ],
        [
            workflow_html_escape("Created"),
            workflow_html_escape(workflow_short_datetime(issue.get("created"))),
            workflow_html_escape("Updated"),
            workflow_html_escape(workflow_short_datetime(issue.get("updated") if detailed else issue.get("created"))),
        ],
        [
            workflow_html_escape("Open"),
            workflow_html_escape(workflow_days_text(issue.get("open_days"))),
            workflow_html_escape("Idle"),
            workflow_html_escape(workflow_days_text(issue.get("idle_days"))),
        ],
    ]
    if detailed:
        meta_rows.append(
            [
                workflow_html_escape("Stale"),
                workflow_html_escape(workflow_stale_label(issue.get("stale_status"))),
                workflow_html_escape("Attention"),
                workflow_html_escape(workflow_attention_label(issue.get("attention_bucket"))),
            ]
        )
        meta_rows.append(
            [
                workflow_html_escape("Assignee"),
                workflow_html_escape(issue.get("assignee") or "Unassigned"),
                workflow_html_escape("Type"),
                workflow_html_escape(issue.get("issue_type") or "n/a"),
            ]
        )
    else:
        meta_rows.append(
            [
                workflow_html_escape("Stale"),
                workflow_html_escape(workflow_stale_label(issue.get("stale_status"))),
                workflow_html_escape("Assignee"),
                workflow_html_escape(issue.get("assignee") or "Unassigned"),
            ]
        )

    body = [
        "<div style=\"border:1px solid #DFE1E6;border-radius:8px;padding:14px 16px;margin:12px 0;background:#FFFFFF;\">",
        f"<h4 style=\"margin:0 0 8px 0;\">{workflow_issue_key_link_html(issue)}</h4>",
        f"<p style=\"margin:0 0 12px 0;\">{workflow_issue_title_html(issue)}</p>",
        workflow_html_table(["Field", "Value", "Field", "Value"], meta_rows),
        f"<p><strong>문제</strong><br/>{workflow_html_escape(workflow_compact_problem(issue))}</p>",
    ]
    if detailed:
        body.append(
            "<div>"
            f"<p><strong>[본문]</strong><br/>{workflow_html_escape(detail.get('description_statement', ''))}</p>"
            f"<p><strong>[번역]</strong><br/>{workflow_html_escape(detail.get('description_localized', ''))}</p>"
            f"<p><strong>[상황 분석 및 해결방안]</strong><br/>{workflow_html_escape(detail.get('situation_analysis_statement', ''))}</p>"
            "</div>"
        )
        body.append(f"<p><strong>영향</strong><br/>{workflow_html_escape(detail.get('impact_statement', ''))}</p>")
        body.append(f"<p><strong>상태 판단</strong><br/>{workflow_html_escape(detail.get('aging_statement', ''))}</p>")
        comment_entries = detail.get("comment_entries") or []
        if comment_entries:
            comment_parts = ["<ul>"]
            for entry in comment_entries:
                comment_parts.append(
                    "<li>"
                    f"<strong>{workflow_html_escape(entry.get('created_short', 'n/a'))} / {workflow_html_escape(entry.get('author', 'unknown'))}</strong><br/>"
                    f"{workflow_html_escape(entry.get('body', ''))}"
                    "</li>"
                )
            comment_parts.append("</ul>")
            body.append(f"<div><strong>최근 코멘트</strong>{''.join(comment_parts)}</div>")
        else:
            body.append("<p><strong>최근 코멘트</strong><br/>없음</p>")
    else:
        recent_note = workflow_recent_note(issue)
        if recent_note:
            body.append(f"<p><strong>최근 코멘트</strong><br/>{workflow_html_escape(recent_note)}</p>")
    if next_action:
        body.append(f"<p><strong>다음 액션</strong><br/>{workflow_html_escape(next_action)}</p>")
    if issue.get("action_needed"):
        body.append(f"<p><strong>액션 라벨</strong><br/>{workflow_html_escape(', '.join(issue['action_needed']))}</p>")
    body.append("</div>")
    return "".join(body)


def workflow_enrich_issue(cfg: dict, raw_issue: dict) -> dict:
    base = jira_issue_brief(raw_issue, cfg)
    base["updated"] = ((raw_issue.get("fields") or {}).get("updated") or "")[:19]
    base["open_days"] = workflow_days_since(base.get("created_raw"))
    base["idle_days"] = workflow_days_since(base.get("updated_raw"))
    base["track"] = workflow_track(base)
    base["workflow_bucket"] = workflow_bucket(base.get("status", ""))
    base["action_needed"] = workflow_action_needed(base)
    base["stale_status"] = workflow_stale_status(base)
    base["attention_bucket"] = workflow_attention_bucket(base)
    base["risk_level"] = workflow_risk(base)
    base["analysis"] = workflow_analysis(base)
    base["detail_analysis"] = workflow_detail_analysis(base)
    base["detail_analysis"]["current_situation_statement"] = workflow_current_situation(base)
    base["detail_analysis"]["situation_analysis_statement"] = base["detail_analysis"]["current_situation_statement"]
    return base


def workflow_group_summary(issues: list[dict]) -> dict:
    return {
        "total": len(issues),
        "status_counts": dict(Counter(issue.get("status", "") for issue in issues)),
        "workflow_counts": dict(Counter(issue.get("workflow_bucket", "") for issue in issues)),
        "attention_counts": dict(Counter(issue.get("attention_bucket", "") for issue in issues)),
        "stale_counts": dict(Counter(issue.get("stale_status", "") for issue in issues)),
    }


def workflow_report_markdown(result: dict) -> str:
    lines = [
        f"# Daily Review {result['date']}",
        "",
        "## Overview",
        "",
    ]
    lines.extend(
        workflow_markdown_table(
            ["Scope", "Total", "JQL"],
            [[result["scope"], str(result["total"]), result["jql"]]],
        )
    )
    lines.extend(["", "## Track Summary", ""])
    summary_rows = []
    for group_name in ("gemini", "qa", "other"):
        group = result["groups"].get(group_name, {})
        summary_rows.append(
            [
                group_name.upper(),
                str(group.get("total", 0)),
                workflow_compact_counts(group.get("status_counts", {})),
                workflow_compact_counts(group.get("stale_counts", {}), workflow_stale_label),
            ]
        )
    lines.extend(workflow_markdown_table(["Track", "Total", "Status", "Stale"], summary_rows))

    lines.extend(["", "## GEMINI", ""])
    gemini = [issue for issue in result["issues"] if issue["track"] == "gemini"]
    lines.extend(render_workflow_issue_section(gemini))

    lines.extend(["", "## QA", ""])
    qa = [issue for issue in result["issues"] if issue["track"] == "qa"]
    lines.extend(render_workflow_issue_section(qa))

    lines.extend(["", "## Other", ""])
    other = [issue for issue in result["issues"] if issue["track"] not in {"gemini", "qa"}]
    lines.extend(render_workflow_issue_section(other, limit_per_status=15))
    lines.append("")
    return "\n".join(lines)


def render_workflow_issue_section(issues: list[dict], limit_per_status: int = 50) -> list[str]:
    if not issues:
        return ["- none", ""]
    ordered_statuses = ["In Progress", "In Review", "To Do", "Open", "Booked"]
    by_status = {status: [] for status in ordered_statuses}
    for issue in issues:
        by_status.setdefault(issue["status"], []).append(issue)
    lines = []
    for status in ordered_statuses + [status for status in by_status.keys() if status not in ordered_statuses]:
        bucket = by_status.get(status, [])
        if not bucket:
            continue
        lines.append(f"### {status} ({len(bucket)})")
        lines.append("")
        rows = [workflow_issue_summary_cells(issue) for issue in bucket[:limit_per_status]]
        lines.extend(
            workflow_markdown_table(
                ["Key", "Status", "Priority", "Created", "Open", "Idle", "Issue", "Analysis", "Next Action"],
                rows,
            )
        )
        lines.extend(["", f"- listed: `{min(len(bucket), limit_per_status)}` / `{len(bucket)}`", ""])
    return lines


def workflow_storage_html(result: dict) -> str:
    summary_rows = []
    for group_name in ("gemini", "qa", "other"):
        group = result["groups"].get(group_name, {})
        summary_rows.append(
            [
                workflow_html_escape(group_name.upper()),
                workflow_html_escape(group.get("total", 0)),
                workflow_html_escape(workflow_compact_counts(group.get("status_counts", {}))),
                workflow_html_escape(workflow_compact_counts(group.get("stale_counts", {}), workflow_stale_label)),
            ]
        )
    sections = [
        f"<h1>Daily Review {workflow_html_escape(result['date'])}</h1>",
        "<h2>Overview</h2>",
        workflow_html_table(
            ["Scope", "Total", "JQL"],
            [[
                workflow_html_escape(result["scope"]),
                workflow_html_escape(result["total"]),
                workflow_html_escape(result["jql"]),
            ]],
        ),
        "<h2>Track Summary</h2>",
        workflow_html_table(["Track", "Total", "Status", "Stale"], summary_rows),
    ]

    for title, track in (("GEMINI", "gemini"), ("QA", "qa"), ("Other", "other")):
        group_issues = [issue for issue in result["issues"] if (issue["track"] == track if track != "other" else issue["track"] not in {'gemini', 'qa'})]
        section_parts = [f"<h2>{title}</h2>"]
        if not group_issues:
            section_parts.append("<p>none</p>")
            section_html = "".join(section_parts)
            if track == "other":
                sections.append(workflow_expand_html(f"{title} ({len(group_issues)})", section_html))
            else:
                sections.append(section_html)
            continue
        statuses = []
        for issue in group_issues:
            if issue["status"] not in statuses:
                statuses.append(issue["status"])
        for status in statuses:
            bucket = [issue for issue in group_issues if issue["status"] == status]
            section_parts.append(f"<h3>{status} ({len(bucket)})</h3>")
            section_parts.append(
                workflow_html_table(
                    ["Key", "Status", "Priority", "Created", "Open", "Idle", "Issue", "Analysis", "Next Action"],
                    [workflow_issue_summary_html_cells(issue) for issue in bucket],
                )
            )
        section_html = "".join(section_parts)
        if track == "other":
            sections.append(workflow_expand_html(f"{title} ({len(group_issues)})", section_html))
        else:
            sections.append(section_html)
    return "".join(sections)


def workflow_detail_report_markdown(result: dict) -> str:
    lines = [
        f"# Detailed Analysis {result['date']}",
        "",
        "## Overview",
        "",
    ]
    lines.extend(
        workflow_markdown_table(
            ["Scope", "Total", "JQL"],
            [[result["scope"], str(result["total"]), result["jql"]]],
        )
    )
    lines.extend(["", "## Attention Summary", ""])
    summary_rows = []
    for group_name in ("gemini", "qa", "other"):
        group = result["groups"].get(group_name, {})
        summary_rows.append(
            [
                group_name.upper(),
                str(group.get("total", 0)),
                workflow_compact_counts(group.get("attention_counts", {}), workflow_attention_label),
                workflow_compact_counts(group.get("stale_counts", {}), workflow_stale_label),
            ]
        )
    lines.extend(
        workflow_markdown_table(
            ["Track", "Total", "Attention", "Stale"],
            summary_rows,
        )
    )

    for title, track in (("GEMINI", "gemini"), ("QA", "qa"), ("Other", "other")):
        lines.extend(["", f"## {title}", ""])
        if track == "other":
            group_issues = [issue for issue in result["issues"] if issue["track"] not in {"gemini", "qa"}]
        else:
            group_issues = [issue for issue in result["issues"] if issue["track"] == track]
        lines.extend(render_workflow_detail_section(group_issues))
    lines.append("")
    return "\n".join(lines)


def render_workflow_detail_section(issues: list[dict]) -> list[str]:
    if not issues:
        return ["- none", ""]
    attention_order = [
        "urgent_qa_active",
        "urgent_qa_stale",
        "urgent_qa_todo",
        "stale_backlog",
        "aging_backlog",
        "normal_backlog",
    ]
    by_attention = {name: [] for name in attention_order}
    for issue in issues:
        by_attention.setdefault(issue.get("attention_bucket"), []).append(issue)

    lines = []
    for attention in attention_order + [name for name in by_attention.keys() if name not in attention_order]:
        bucket = by_attention.get(attention, [])
        if not bucket:
            continue
        lines.append(f"### {workflow_attention_label(attention)} ({len(bucket)})")
        lines.append("")
        for issue in bucket:
            lines.extend(workflow_markdown_issue_card(issue, detailed=True))
        lines.append("")
    return lines


def workflow_detail_storage_html(result: dict) -> str:
    summary_rows = []
    for group_name in ("gemini", "qa", "other"):
        group = result["groups"].get(group_name, {})
        summary_rows.append(
            [
                workflow_html_escape(group_name.upper()),
                workflow_html_escape(group.get("total", 0)),
                workflow_html_escape(workflow_compact_counts(group.get("attention_counts", {}), workflow_attention_label)),
                workflow_html_escape(workflow_compact_counts(group.get("stale_counts", {}), workflow_stale_label)),
            ]
        )
    sections = [
        f"<h1>Detailed Analysis {workflow_html_escape(result['date'])}</h1>",
        "<h2>Overview</h2>",
        workflow_html_table(
            ["Scope", "Total", "JQL"],
            [[
                workflow_html_escape(result["scope"]),
                workflow_html_escape(result["total"]),
                workflow_html_escape(result["jql"]),
            ]],
        ),
        "<h2>Attention Summary</h2>",
        workflow_html_table(["Track", "Total", "Attention", "Stale"], summary_rows),
    ]

    for title, track in (("GEMINI", "gemini"), ("QA", "qa"), ("Other", "other")):
        if track == "other":
            group_issues = [issue for issue in result["issues"] if issue["track"] not in {"gemini", "qa"}]
        else:
            group_issues = [issue for issue in result["issues"] if issue["track"] == track]
        section_parts = [f"<h2>{title}</h2>"]
        if not group_issues:
            section_parts.append("<p>none</p>")
            section_html = "".join(section_parts)
            if track == "other":
                sections.append(workflow_expand_html(f"{title} ({len(group_issues)})", section_html))
            else:
                sections.append(section_html)
            continue
        attention_order = [
            "urgent_qa_active",
            "urgent_qa_stale",
            "urgent_qa_todo",
            "stale_backlog",
            "aging_backlog",
            "normal_backlog",
        ]
        by_attention = {name: [] for name in attention_order}
        for issue in group_issues:
            by_attention.setdefault(issue.get("attention_bucket"), []).append(issue)
        for attention in attention_order + [name for name in by_attention.keys() if name not in attention_order]:
            bucket = by_attention.get(attention, [])
            if not bucket:
                continue
            section_parts.append(f"<h3>{workflow_attention_label(attention)} ({len(bucket)})</h3>")
            for issue in bucket:
                section_parts.append(workflow_html_issue_card(issue, detailed=True))
        section_html = "".join(section_parts)
        if track == "other":
            sections.append(workflow_expand_html(f"{title} ({len(group_issues)})", section_html))
        else:
            sections.append(section_html)
    return "".join(sections)


def workflow_title_from_template(template: str, result: dict, args) -> str:
    safe_template = template or "Daily Review {date}"
    return safe_template.format(
        date=result["date"],
        year=result["date"][:4],
        month=result["date"][5:7],
        day=result["date"][8:10],
        scope=args.scope,
    )


def workflow_cql_escape(value: str) -> str:
    return (value or "").replace("\\", "\\\\").replace('"', '\\"')


def workflow_find_wiki_page(cfg: dict, space: str, parent_id: str, title: str):
    if not parent_id:
        return None
    cql = f'space="{workflow_cql_escape(space)}" AND type=page AND ancestor={parent_id} AND title="{workflow_cql_escape(title)}"'
    resp = request_api(cfg, "wiki", "GET", "/content/search", params={"cql": cql, "expand": "version", "limit": 20})
    handle_response(resp, "위키 페이지 검색 실패")
    results = resp.json().get("results", [])
    if not results:
        return None
    return sorted(results, key=lambda item: int(item.get("id", "0") or "0"))[0]


def workflow_find_wiki_page_by_space_title(cfg: dict, space: str, title: str):
    cql = f'space="{workflow_cql_escape(space)}" AND type=page AND title="{workflow_cql_escape(title)}"'
    resp = request_api(cfg, "wiki", "GET", "/content/search", params={"cql": cql, "expand": "version", "limit": 20})
    handle_response(resp, "위키 페이지 검색 실패")
    results = resp.json().get("results", [])
    if not results:
        return None
    return sorted(results, key=lambda item: int(item.get("id", "0") or "0"))[0]


def workflow_fetch_wiki_page_with_ancestors(cfg: dict, page_id: str):
    resp = request_api(cfg, "wiki", "GET", f"/content/{page_id}", params={"expand": "body.storage,version,ancestors,space"})
    handle_response(resp, "페이지 조회 실패")
    return resp.json()


def workflow_extract_date_ancestor_title(page: dict) -> str:
    for ancestor in reversed(page.get("ancestors") or []):
        title = (ancestor or {}).get("title", "")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", title):
            return title
    return ""


def workflow_archive_space_title_conflict(cfg: dict, space: str, parent_id: str, title: str):
    existing = workflow_find_wiki_page_by_space_title(cfg, space, title)
    if not existing:
        return None

    current = workflow_fetch_wiki_page_with_ancestors(cfg, existing.get("id"))
    ancestor_ids = {str((ancestor or {}).get("id", "")) for ancestor in current.get("ancestors") or []}
    if parent_id and str(parent_id) in ancestor_ids:
        return {
            "mode": "same-parent",
            "page_id": current.get("id"),
            "title": current.get("title", ""),
        }

    archived_title = f"{title} {workflow_extract_date_ancestor_title(current)}".strip()
    if archived_title == title:
        archived_title = f"{title} archived {current.get('id')}"
    if current.get("title") == archived_title:
        return {
            "mode": "already-archived",
            "page_id": current.get("id"),
            "title": current.get("title", ""),
        }

    payload = {
        "type": "page",
        "title": archived_title,
        "version": {"number": current["version"]["number"] + 1},
        "body": {
            "storage": {
                "value": ((current.get("body") or {}).get("storage") or {}).get("value", ""),
                "representation": "storage",
            }
        },
    }
    resp = request_api(cfg, "wiki", "PUT", f"/content/{current.get('id')}", payload=payload)
    handle_response(resp, "기존 위키 제목 정리 실패")
    data = resp.json()
    return {
        "mode": "archived",
        "page_id": data.get("id"),
        "title": data.get("title", ""),
        "url": cfg["confluence_base_url"] + data.get("_links", {}).get("webui", ""),
    }


def workflow_safe_wiki_current_user(cfg: dict) -> dict:
    try:
        resp = request_api(cfg, "wiki", "GET", "/user/current", timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "error": str(exc)}
    if resp.status_code >= 400:
        return {"ok": False, "status_code": resp.status_code}
    data = resp.json()
    return {
        "ok": True,
        "username": data.get("username") or data.get("name") or "",
        "display_name": data.get("displayName") or "",
        "user_key": data.get("userKey") or data.get("key") or "",
    }


def workflow_safe_wiki_page_summary(cfg: dict, page_id: str) -> dict | None:
    if not page_id:
        return None
    try:
        resp = request_api(cfg, "wiki", "GET", f"/content/{page_id}", params={"expand": "space"}, timeout=10)
    except requests.exceptions.RequestException:
        return None
    if resp.status_code >= 400:
        return None
    data = resp.json()
    return {
        "page_id": data.get("id"),
        "title": data.get("title", ""),
        "space": ((data.get("space") or {}).get("key") or ""),
        "url": cfg["confluence_base_url"] + data.get("_links", {}).get("webui", ""),
    }


def workflow_build_publish_preview(
    cfg: dict,
    result: dict,
    wf_cfg: dict,
    page_id: str,
    space: str,
    parent_id: str,
    title: str,
) -> dict:
    use_date_container = bool(not page_id and wf_cfg.get("wiki_use_date_container"))
    date_title = workflow_title_from_template(wf_cfg.get("wiki_date_title_template") or "{date}", result, argparse.Namespace(scope=result.get("scope", ""))) if use_date_container else ""
    path_parts = []
    if wf_cfg.get("wiki_path_hint"):
        path_parts.append(wf_cfg["wiki_path_hint"])
    elif wf_cfg.get("wiki_parent_title"):
        path_parts.append(wf_cfg["wiki_parent_title"])
    elif parent_id:
        path_parts.append(f"parent:{parent_id}")
    if date_title:
        path_parts.append(date_title)
    if title:
        path_parts.append(title)

    account = workflow_safe_wiki_current_user(cfg)
    parent_page = workflow_safe_wiki_page_summary(cfg, parent_id)
    preview = {
        "profile": cfg.get("active_profile", ""),
        "base_url": cfg.get("confluence_base_url", ""),
        "space": space,
        "path_hint": " > ".join(part for part in path_parts if part),
        "parent_page_id": parent_id or "",
        "parent_page_title": (
            (parent_page or {}).get("title")
            or wf_cfg.get("wiki_parent_title")
            or ""
        ),
        "parent_page_url": (parent_page or {}).get("url", ""),
        "target_page_id": page_id or "",
        "target_title": title or "",
        "date_container_title": date_title,
        "date_container_enabled": use_date_container,
        "report_markdown_path": result.get("report_markdown_path", ""),
    }
    if account.get("ok"):
        preview["wiki_account"] = {
            "username": account.get("username", ""),
            "display_name": account.get("display_name", ""),
            "user_key": account.get("user_key", ""),
        }
    else:
        preview["wiki_account"] = {
            "username": "",
            "display_name": "",
            "user_key": "",
            "error": account.get("error", "") or (f"http_{account.get('status_code')}" if account.get("status_code") else ""),
        }
    return preview


def workflow_report_publish_preview(preview: dict):
    account = preview.get("wiki_account") or {}
    display_name = account.get("display_name", "")
    username = account.get("username", "")
    if display_name and username:
        account_label = f"{display_name} ({username})"
    else:
        account_label = display_name or username or preview.get("profile", "-")

    eprint("")
    eprint("┌─ 위키 업로드 예정 ───────────────────────────────────────────")
    eprint(f"│  프로파일:    {preview.get('profile') or '-'}")
    eprint(f"│  계정:        {account_label}")
    eprint(f"│  스페이스:    {preview.get('space') or '-'}")
    eprint(f"│  상위 경로:   {preview.get('path_hint') or '-'}")
    eprint(f"│  상위 페이지: {preview.get('parent_page_title') or '-'} ({preview.get('parent_page_id') or '-'})")
    if preview.get("date_container_enabled"):
        eprint(f"│  날짜 폴더:   {preview.get('date_container_title') or '-'}")
    eprint(f"│  제목:        {preview.get('target_title') or '-'}")
    eprint(f"│  로컬 리포트: {preview.get('report_markdown_path') or '-'}")
    eprint("└──────────────────────────────────────────────────────────────")


def workflow_ensure_wiki_page(cfg: dict, space: str, parent_id: str, title: str, content_html: str) -> dict:
    existing = workflow_find_wiki_page(cfg, space, parent_id, title) if parent_id else None
    if existing:
        return {
            "mode": "existing",
            "page_id": existing.get("id"),
            "title": existing.get("title"),
            "url": cfg["confluence_base_url"] + existing.get("_links", {}).get("webui", ""),
        }

    payload = build_wiki_content_payload(title, content_html, space, parent_id)
    resp = request_api(cfg, "wiki", "POST", "/content", payload=payload)
    handle_response(resp, "위키 생성 실패")
    data = resp.json()
    return {
        "mode": "create",
        "page_id": data.get("id"),
        "title": data.get("title"),
        "url": cfg["confluence_base_url"] + data.get("_links", {}).get("webui", ""),
    }


def workflow_publish_report(cfg: dict, args, result: dict, report_html: str, workflow_config_key: str, default_title_template: str) -> dict:
    with workflow_publish_lock(cfg):
        wf_cfg = workflow_config(cfg, workflow_config_key)
        page_id = args.page_id or wf_cfg.get("wiki_page_id")
        space = args.space or wf_cfg.get("wiki_space") or cfg.get("default_space", "~jaecjeong")
        parent_id = args.parent_id or wf_cfg.get("wiki_parent_page_id")
        title = args.wiki_title or workflow_title_from_template(wf_cfg.get("wiki_title_template") or default_title_template, result, args)
        result["wiki_publish_preview"] = workflow_build_publish_preview(cfg, result, wf_cfg, page_id, space, parent_id, title)
        workflow_report_publish_preview(result["wiki_publish_preview"])
        date_container = None

        if not page_id and wf_cfg.get("wiki_use_date_container"):
            date_title = workflow_title_from_template(wf_cfg.get("wiki_date_title_template") or "{date}", result, args)
            date_page = workflow_ensure_wiki_page(
                cfg,
                space,
                parent_id,
                date_title,
                f"<h1>{workflow_html_escape(date_title)}</h1><p>ATLS Daily Review index page.</p>",
            )
            parent_id = date_page["page_id"]
            date_container = date_page

        if not page_id:
            result["wiki_title_conflict_resolution"] = workflow_archive_space_title_conflict(cfg, space, parent_id, title)

        if page_id:
            current = fetch_wiki_page_for_update(cfg, page_id)
            payload = {
                "type": "page",
                "title": title or current.get("title", ""),
                "version": {"number": current["version"]["number"] + 1},
                "body": {"storage": {"value": report_html, "representation": "storage"}},
            }
            resp = request_api(cfg, "wiki", "PUT", f"/content/{page_id}", payload=payload)
            handle_response(resp, "위키 업데이트 실패")
            data = resp.json()
            return {
                "mode": "update",
                "page_id": page_id,
                "title": data.get("title"),
                "url": cfg["confluence_base_url"] + data.get("_links", {}).get("webui", ""),
                "space": space,
                "parent_id": parent_id,
                "date_container": date_container,
            }

        existing = workflow_find_wiki_page(cfg, space, parent_id, title) if parent_id else None
        if existing:
            existing_id = existing.get("id")
            current = fetch_wiki_page_for_update(cfg, existing_id)
            payload = {
                "type": "page",
                "title": title,
                "version": {"number": current["version"]["number"] + 1},
                "body": {"storage": {"value": report_html, "representation": "storage"}},
            }
            resp = request_api(cfg, "wiki", "PUT", f"/content/{existing_id}", payload=payload)
            handle_response(resp, "위키 업데이트 실패")
            data = resp.json()
            return {
                "mode": "upsert-update",
                "page_id": existing_id,
                "title": data.get("title"),
                "url": cfg["confluence_base_url"] + data.get("_links", {}).get("webui", ""),
                "space": space,
                "parent_id": parent_id,
                "date_container": date_container,
            }

        payload = build_wiki_content_payload(title, report_html, space, parent_id)
        resp = request_api(cfg, "wiki", "POST", "/content", payload=payload)
        handle_response(resp, "위키 생성 실패")
        data = resp.json()
        return {
            "mode": "create",
            "page_id": data.get("id"),
            "title": data.get("title"),
            "url": cfg["confluence_base_url"] + data.get("_links", {}).get("webui", ""),
            "space": space,
            "parent_id": parent_id,
            "date_container": date_container,
        }


def write_workflow_extra_artifact(
    cfg: dict,
    service: str,
    base_task_name: str,
    extension: str,
    content: str,
    subdirs: list[str] | None = None,
) -> str:
    root = artifact_root_path(cfg)
    target_dir = root / service
    for subdir in subdirs or []:
        target_dir = target_dir / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    day = datetime.now().strftime("%Y_%m_%d")
    path = unique_artifact_path(target_dir, f"{day}_{base_task_name}.{extension}")
    path.write_text(content, encoding="utf-8")
    return str(path)


def write_workflow_named_artifact(cfg: dict, service: str, filename: str, content: str, subdirs: list[str]) -> str:
    path = workflow_named_artifact_path(cfg, service, filename, subdirs)
    path.write_text(content, encoding="utf-8")
    return str(path)


def load_existing_workflow_json(cfg: dict, service: str, filename: str, subdirs: list[str]):
    path = workflow_named_artifact_path(cfg, service, filename, subdirs)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def merge_issue_records(existing_issues: list[dict] | None, incoming_issues: list[dict] | None) -> list[dict]:
    existing_items = existing_issues or []
    incoming_items = incoming_issues or []
    merged: list[dict] = []
    index_by_key: dict[str, int] = {}

    for issue in existing_items:
        if not isinstance(issue, dict):
            continue
        key = str(issue.get("key") or "").strip()
        if not key:
            continue
        if key in index_by_key:
            merged[index_by_key[key]] = issue
            continue
        index_by_key[key] = len(merged)
        merged.append(issue)

    for issue in incoming_items:
        if not isinstance(issue, dict):
            continue
        key = str(issue.get("key") or "").strip()
        if not key:
            continue
        if key in index_by_key:
            merged[index_by_key[key]] = issue
            continue
        index_by_key[key] = len(merged)
        merged.append(issue)

    return merged


def apply_append_only_issue_merge(result: dict, issue_field: str) -> dict:
    issues = result.get(issue_field)
    if not isinstance(issues, list):
        return result

    merged_issues = merge_issue_records([], issues)
    merged_result = dict(result)
    merged_result[issue_field] = merged_issues
    merged_result["merge_policy"] = "append_only_update_same_issue"
    return merged_result


def merge_issue_collected_results(existing_result: dict | None, incoming_result: dict, issue_field: str) -> dict:
    if not existing_result:
        return apply_append_only_issue_merge(incoming_result, issue_field)

    existing_issues = existing_result.get(issue_field)
    incoming_issues = incoming_result.get(issue_field)
    if not isinstance(existing_issues, list) or not isinstance(incoming_issues, list):
        return apply_append_only_issue_merge(incoming_result, issue_field)

    merged_issues = merge_issue_records(existing_issues, incoming_issues)
    merged_result = dict(incoming_result)
    merged_result[issue_field] = merged_issues
    merged_result["merge_policy"] = "append_only_update_same_issue"
    merged_result["merged_existing_issue_count"] = len(existing_issues)
    merged_result["merged_total_issue_count"] = len(merged_issues)
    return merged_result


def workflow_collect_daily_review_result(cfg: dict, args, workflow_name: str) -> dict:
    fields = [
        "summary", "description", "status", "assignee", "priority",
        "comment", "labels", "issuetype", "updated", "created",
    ]
    search_data = jira_search_raw(cfg, args.jql, args.max_results, fields)
    issue_ids = [issue.get("key") for issue in search_data.get("issues", [])]
    detailed_raw = jira_fetch_issue_details(cfg, issue_ids, fields) if issue_ids else []
    detailed = [workflow_enrich_issue(cfg, raw_issue) for raw_issue in detailed_raw]
    detailed.sort(key=lambda issue: (issue.get("track") != "gemini", issue.get("track") != "qa", issue.get("status"), issue.get("key")))

    groups = {
        "gemini": workflow_group_summary([issue for issue in detailed if issue["track"] == "gemini"]),
        "qa": workflow_group_summary([issue for issue in detailed if issue["track"] == "qa"]),
        "other": workflow_group_summary([issue for issue in detailed if issue["track"] not in {"gemini", "qa"}]),
    }

    result = {
        "success": True,
        "workflow": workflow_name,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "scope": args.scope,
        "jql": args.jql,
        "total": len(detailed),
        "groups": groups,
        "issues": detailed,
        "workflow_config": workflow_config(cfg, workflow_name.replace("-", "_")),
    }
    return result


def workflow_daily_review(cfg: dict, args):
    ensure_service_token(cfg, "jira")
    result = workflow_collect_daily_review_result(cfg, args, "daily-review")
    review_subdirs = workflow_daily_review_dir_parts()
    existing_result = load_existing_workflow_json(cfg, "jira", "summary.json", review_subdirs)
    result = merge_issue_collected_results(existing_result, result, "issues")
    merged_issues = result.get("issues", [])
    result["total"] = len(merged_issues)
    result["groups"] = {
        "gemini": workflow_group_summary([issue for issue in merged_issues if issue.get("track") == "gemini"]),
        "qa": workflow_group_summary([issue for issue in merged_issues if issue.get("track") == "qa"]),
        "other": workflow_group_summary([issue for issue in merged_issues if issue.get("track") not in {"gemini", "qa"}]),
    }

    # --collect-only: 수집까지만 하고 분석/발행 생략
    if getattr(args, "collect_only", False):
        result["stage"] = "collected"
        out(result)
        return

    report_md = workflow_report_markdown(result)
    report_html = workflow_storage_html(result)
    result["report_markdown_path"] = write_workflow_named_artifact(cfg, "jira", "summary.md", report_md, review_subdirs)
    result["analysis_json_path"] = str(workflow_named_artifact_path(cfg, "jira", "summary.json", review_subdirs))

    wf_cfg = workflow_config(cfg, "daily_review")
    publish_requested = False if getattr(args, "no_publish", False) else bool(args.publish or wf_cfg.get("wiki_auto_publish"))

    # --dry-run: 발행 없이 생성될 리포트 미리보기
    if is_dry_run():
        dry_run_preview("workflow daily-review publish", {"report_preview": report_md[:500] + "...", "total_issues": result["total"], "publish_would_run": publish_requested})

    if publish_requested:
        ensure_service_token(cfg, "wiki")
        result["wiki_publish"] = workflow_publish_report(cfg, args, result, report_html, "daily_review", "Daily Review {date}")

    Path(result["analysis_json_path"]).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    out(result)


def workflow_daily_review_detail(cfg: dict, args):
    ensure_service_token(cfg, "jira")
    result = workflow_collect_daily_review_result(cfg, args, "daily-review-detail")
    detail_subdirs = workflow_daily_review_dir_parts()
    existing_result = load_existing_workflow_json(cfg, "jira", "detailed_analysis.json", detail_subdirs)
    result = merge_issue_collected_results(existing_result, result, "issues")
    merged_issues = result.get("issues", [])
    result["total"] = len(merged_issues)
    result["groups"] = {
        "gemini": workflow_group_summary([issue for issue in merged_issues if issue.get("track") == "gemini"]),
        "qa": workflow_group_summary([issue for issue in merged_issues if issue.get("track") == "qa"]),
        "other": workflow_group_summary([issue for issue in merged_issues if issue.get("track") not in {"gemini", "qa"}]),
    }
    report_md = workflow_detail_report_markdown(result)
    report_html = workflow_detail_storage_html(result)
    result["report_markdown_path"] = write_workflow_named_artifact(cfg, "jira", "detailed_analysis.md", report_md, detail_subdirs)
    result["analysis_json_path"] = str(workflow_named_artifact_path(cfg, "jira", "detailed_analysis.json", detail_subdirs))

    wf_cfg = workflow_config(cfg, "daily_review_detail")
    publish_requested = False if getattr(args, "no_publish", False) else bool(args.publish or wf_cfg.get("wiki_auto_publish"))
    if publish_requested:
        ensure_service_token(cfg, "wiki")
        result["wiki_publish"] = workflow_publish_report(
            cfg,
            args,
            result,
            report_html,
            "daily_review_detail",
            "Daily Review Detail {date}",
        )

    Path(result["analysis_json_path"]).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    out(result)


def resolve_harness_workspace_root(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    cwd = Path.cwd().resolve()
    candidates = [
        cwd / "adcenter",
        cwd,
    ]
    for candidate in candidates:
        if (candidate / "src").exists() and (candidate / "docs").exists():
            return candidate
    return cwd


def workflow_qa_gemini_harness(cfg: dict, args):
    warnings = []
    jira_result = None
    jira_issues = []

    if not getattr(args, "no_jira", False):
        try:
            ensure_service_token(cfg, "jira")
            jira_result = workflow_collect_daily_review_result(cfg, args, "qa-gemini-harness")
            jira_issues = jira_result.get("issues", [])
        except Exception as exc:
            warnings.append(f"live Jira fetch skipped: {exc}")

    workspace_root = resolve_harness_workspace_root(getattr(args, "workspace_root", None))
    from atls.analysis.harness import (
        build_harness_report,
        render_harness_summary_markdown,
        render_prompt_markdown,
        render_task_analysis_markdown,
    )

    subdirs = workflow_qa_gemini_harness_dir_parts()
    existing_report = load_existing_workflow_json(cfg, "jira", "harness_summary.json", subdirs)
    existing_jira_issues = existing_report.get("jira_issues", []) if isinstance(existing_report, dict) else []
    merged_jira_issues = merge_issue_records(existing_jira_issues, jira_issues)

    report = build_harness_report(
        atls_root=atls_project_root(),
        workspace_root=workspace_root,
        jira_issues=merged_jira_issues,
        jira_context={
            "scope": args.scope,
            "jql": args.jql,
            "max_results": args.max_results,
            "live_issue_count": len(merged_jira_issues),
            "live_fetch_enabled": not getattr(args, "no_jira", False),
        },
    )
    report["warnings"] = warnings
    report["merge_policy"] = "append_only_update_same_issue"
    report["merged_existing_issue_count"] = len(existing_jira_issues) if isinstance(existing_jira_issues, list) else 0
    summary_md = render_harness_summary_markdown(report)
    task_analysis_md = render_task_analysis_markdown(report)
    prompt_md = render_prompt_markdown(report["prompt_pack"])

    summary_md_path = write_workflow_named_artifact(cfg, "jira", "harness_summary.md", summary_md, subdirs)
    task_analysis_md_path = write_workflow_named_artifact(cfg, "jira", "harness_task_analysis.md", task_analysis_md, subdirs)
    prompt_md_path = write_workflow_named_artifact(cfg, "jira", "harness_prompts.md", prompt_md, subdirs)

    summary_json_path = workflow_named_artifact_path(cfg, "jira", "harness_summary.json", subdirs)
    task_analysis_json_path = workflow_named_artifact_path(cfg, "jira", "harness_task_analysis.json", subdirs)
    prompt_json_path = workflow_named_artifact_path(cfg, "jira", "harness_prompts.json", subdirs)

    summary_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    task_analysis_json_path.write_text(json.dumps(report["task_analysis"], ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_json_path.write_text(json.dumps(report["prompt_pack"], ensure_ascii=False, indent=2), encoding="utf-8")

    out(
        {
            "success": True,
            "workflow": "qa-gemini-harness",
            "workspace_root": str(workspace_root),
            "live_jira_issue_count": len(merged_jira_issues),
            "warnings": warnings,
            "artifact_paths": {
                "summary_markdown": summary_md_path,
                "summary_json": str(summary_json_path),
                "task_analysis_markdown": task_analysis_md_path,
                "task_analysis_json": str(task_analysis_json_path),
                "prompt_markdown": prompt_md_path,
                "prompt_json": str(prompt_json_path),
            },
            "counts": {
                "qa_worklist": len(report.get("qa_worklist", [])),
                "gemini_worklist": len(report.get("gemini_worklist", [])),
                "task_analysis": len(report.get("task_analysis", [])),
                "open_gaps": len(report.get("open_gaps", [])),
            },
        }
    )


def workflow_project_task_flow_bundle(cfg: dict, args) -> dict:
    warnings = []
    jira_issues = []

    if not getattr(args, "no_jira", False):
        try:
            ensure_service_token(cfg, "jira")
            live_result = workflow_collect_daily_review_result(cfg, args, "project-task-flow")
            jira_issues = live_result.get("issues", [])
        except Exception as exc:
            warnings.append(f"live Jira fetch skipped: {exc}")

    workspace_root = resolve_harness_workspace_root(getattr(args, "workspace_root", None))
    project_name = workspace_root.name or "project"
    from atls.analysis.harness import (
        build_acceptance_manifest_pack,
        build_playwright_spec_pack,
        build_project_adapter_pack,
        build_task_plan_cards,
        build_execution_workflow_cards,
        build_harness_report,
        build_project_task_list,
        render_acceptance_manifest_markdown,
        render_execution_workflow_markdown,
        render_playwright_spec_pack_markdown,
        render_project_adapter_markdown,
        render_project_summary_markdown,
        render_project_task_list_markdown,
        render_task_plan_markdown,
    )

    subdirs = workflow_project_task_flow_dir_parts(project_name)
    existing_report = load_existing_workflow_json(cfg, "jira", "summary.json", subdirs)
    existing_jira_issues = existing_report.get("jira_issues", []) if isinstance(existing_report, dict) else []
    merged_jira_issues = jira_issues if jira_issues else existing_jira_issues

    report = build_harness_report(
        atls_root=atls_project_root(),
        workspace_root=workspace_root,
        jira_issues=merged_jira_issues,
        jira_context={
            "scope": args.scope,
            "jql": args.jql,
            "max_results": args.max_results,
            "live_issue_count": len(merged_jira_issues),
            "live_fetch_enabled": not getattr(args, "no_jira", False),
        },
    )
    report["warnings"] = warnings
    report["merge_policy"] = "live_overwrites_existing_for_current_run"
    report["merged_existing_issue_count"] = len(existing_jira_issues) if isinstance(existing_jira_issues, list) else 0

    project_tasks = build_project_task_list(report)
    execution_cards = build_execution_workflow_cards(report, project_tasks)
    task_plan_cards = build_task_plan_cards(report, project_tasks)
    acceptance_manifest_pack = build_acceptance_manifest_pack(project_name, task_plan_cards)
    project_adapter_pack = build_project_adapter_pack(workspace_root, project_name)
    playwright_spec_pack = build_playwright_spec_pack(project_name, acceptance_manifest_pack, project_adapter_pack)

    return {
        "workspace_root": workspace_root,
        "project_name": project_name,
        "warnings": warnings,
        "report": report,
        "project_tasks": project_tasks,
        "execution_cards": execution_cards,
        "task_plan_cards": task_plan_cards,
        "acceptance_manifest_pack": acceptance_manifest_pack,
        "project_adapter_pack": project_adapter_pack,
        "playwright_spec_pack": playwright_spec_pack,
        "subdirs": subdirs,
    }


def write_project_task_flow_artifacts(cfg: dict, bundle: dict) -> dict:
    from atls.analysis.harness import (
        render_acceptance_manifest_markdown,
        render_execution_workflow_markdown,
        render_playwright_spec_pack_markdown,
        render_project_adapter_markdown,
        render_project_summary_markdown,
        render_project_task_list_markdown,
        render_task_plan_markdown,
    )

    workspace_root = bundle["workspace_root"]
    project_name = bundle["project_name"]
    report = bundle["report"]
    project_tasks = bundle["project_tasks"]
    execution_cards = bundle["execution_cards"]
    task_plan_cards = bundle["task_plan_cards"]
    acceptance_manifest_pack = bundle["acceptance_manifest_pack"]
    project_adapter_pack = bundle["project_adapter_pack"]
    playwright_spec_pack = bundle["playwright_spec_pack"]
    subdirs = bundle["subdirs"]

    summary_md = render_project_summary_markdown(report)
    task_list_md = render_project_task_list_markdown(project_name, project_tasks)
    workflow_md = render_execution_workflow_markdown(project_name, execution_cards)
    task_plans_md = render_task_plan_markdown(project_name, task_plan_cards)
    acceptance_manifest_md = render_acceptance_manifest_markdown(acceptance_manifest_pack)
    project_adapter_md = render_project_adapter_markdown(project_adapter_pack)
    playwright_specs_md = render_playwright_spec_pack_markdown(playwright_spec_pack)

    summary_md_path = write_workflow_named_artifact(cfg, "jira", "summary.md", summary_md, subdirs)
    task_list_md_path = write_workflow_named_artifact(cfg, "jira", "project_task_list.md", task_list_md, subdirs)
    workflow_md_path = write_workflow_named_artifact(cfg, "jira", "execution_workflow.md", workflow_md, subdirs)
    task_plans_md_path = write_workflow_named_artifact(cfg, "jira", "task_plans.md", task_plans_md, subdirs)
    acceptance_manifest_md_path = write_workflow_named_artifact(cfg, "jira", "acceptance_manifest.md", acceptance_manifest_md, subdirs)
    project_adapter_md_path = write_workflow_named_artifact(cfg, "jira", "project_adapter.md", project_adapter_md, subdirs)
    playwright_specs_md_path = write_workflow_named_artifact(cfg, "jira", "playwright_specs.md", playwright_specs_md, subdirs)

    summary_json_path = workflow_named_artifact_path(cfg, "jira", "summary.json", subdirs)
    task_list_json_path = workflow_named_artifact_path(cfg, "jira", "project_task_list.json", subdirs)
    workflow_json_path = workflow_named_artifact_path(cfg, "jira", "execution_workflow.json", subdirs)
    task_plans_json_path = workflow_named_artifact_path(cfg, "jira", "task_plans.json", subdirs)
    acceptance_manifest_json_path = workflow_named_artifact_path(cfg, "jira", "acceptance_manifest.json", subdirs)
    project_adapter_json_path = workflow_named_artifact_path(cfg, "jira", "project_adapter.json", subdirs)
    playwright_specs_json_path = workflow_named_artifact_path(cfg, "jira", "playwright_specs.json", subdirs)
    playwright_specs_dir = workflow_named_artifact_path(cfg, "jira", "playwright_specs", subdirs)

    summary_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    task_list_json_path.write_text(json.dumps(project_tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    workflow_json_path.write_text(json.dumps(execution_cards, ensure_ascii=False, indent=2), encoding="utf-8")
    task_plans_json_path.write_text(json.dumps(task_plan_cards, ensure_ascii=False, indent=2), encoding="utf-8")
    acceptance_manifest_json_path.write_text(json.dumps(acceptance_manifest_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    project_adapter_json_path.write_text(json.dumps(project_adapter_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    playwright_specs_json_path.write_text(json.dumps(playwright_spec_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    playwright_specs_dir.mkdir(parents=True, exist_ok=True)
    for spec in playwright_spec_pack.get("specs", []):
        (playwright_specs_dir / spec["filename"]).write_text(spec["content"], encoding="utf-8")

    return {
        "summary_markdown": summary_md_path,
        "summary_json": str(summary_json_path),
        "project_task_list_markdown": task_list_md_path,
        "project_task_list_json": str(task_list_json_path),
        "execution_workflow_markdown": workflow_md_path,
        "execution_workflow_json": str(workflow_json_path),
        "task_plans_markdown": task_plans_md_path,
        "task_plans_json": str(task_plans_json_path),
        "acceptance_manifest_markdown": acceptance_manifest_md_path,
        "acceptance_manifest_json": str(acceptance_manifest_json_path),
        "project_adapter_markdown": project_adapter_md_path,
        "project_adapter_json": str(project_adapter_json_path),
        "playwright_specs_markdown": playwright_specs_md_path,
        "playwright_specs_json": str(playwright_specs_json_path),
        "playwright_specs_dir": str(playwright_specs_dir),
    }


def workflow_project_task_flow(cfg: dict, args):
    bundle = workflow_project_task_flow_bundle(cfg, args)
    artifact_paths = write_project_task_flow_artifacts(cfg, bundle)
    report = bundle["report"]
    out(
        {
            "success": True,
            "workflow": "project-task-flow",
            "workspace_root": str(bundle["workspace_root"]),
            "project_name": bundle["project_name"],
            "live_jira_issue_count": len(report.get("jira_issues", [])),
            "warnings": bundle["warnings"],
            "artifact_paths": artifact_paths,
            "counts": {
                "qa_worklist": len(report.get("qa_worklist", [])),
                "gemini_worklist": len(report.get("gemini_worklist", [])),
                "project_tasks": len(bundle["project_tasks"]),
                "execution_cards": len(bundle["execution_cards"]),
                "task_plans": len(bundle["task_plan_cards"]),
                "acceptance_manifests": bundle["acceptance_manifest_pack"].get("manifest_count", 0),
                "playwright_specs": bundle["playwright_spec_pack"].get("spec_count", 0),
            },
        }
    )


def workflow_issue_delivery_summary_markdown(result: dict) -> str:
    lines = [
        f"# {result.get('project_name', 'project')} Issue Delivery",
        "",
        f"- prepared_at: {result.get('prepared_at')}",
        f"- execute_tests: {result.get('execute_tests')}",
        f"- total_delivery_issues: {result.get('counts', {}).get('delivery_issues', 0)}",
        f"- runnable_specs: {result.get('counts', {}).get('execution_ready', 0)}",
        f"- completed: {result.get('counts', {}).get('completed', 0)}",
        f"- failed: {result.get('counts', {}).get('failed', 0)}",
        f"- blocked: {result.get('counts', {}).get('blocked', 0)}",
        "",
        "## Delivery Issues",
        "",
    ]
    for item in result.get("delivery_issues", []):
        lines.extend(
            [
                f"- {item.get('issue_key')}: {item.get('delivery_status')}",
                f"  title: {item.get('title') or '-'}",
                f"  spec_source: {item.get('spec_source') or '-'}",
                f"  execution_ready: {item.get('execution_ready')}",
                f"  case_count: {item.get('case_count', 0)}",
                f"  note: {item.get('note') or '-'}",
            ]
        )
    return "\n".join(lines) + "\n"


def workflow_issue_delivery_report_markdown(result: dict) -> str:
    lines = [
        f"# {result.get('project_name', 'project')} Issue Delivery Execution Report",
        "",
    ]
    for item in result.get("delivery_issues", []):
        lines.extend(
            [
                f"## {item.get('issue_key')}",
                "",
                f"- title: {item.get('title') or '-'}",
                f"- delivery_status: {item.get('delivery_status') or '-'}",
                f"- spec_source: {item.get('spec_source') or '-'}",
                f"- workspace_spec_path: {item.get('workspace_spec_path') or '-'}",
                f"- result_directory: {item.get('result_directory') or '-'}",
                f"- note: {item.get('note') or '-'}",
                "",
            ]
        )
    return "\n".join(lines)


def _is_generated_issue_spec(text: str) -> bool:
    return "ATLS_GENERATED_PLACEHOLDER" in (text or "")


def _count_issue_evidence_assets(result_dir: Path) -> tuple[int, int]:
    video_count = 0
    screenshot_count = 0
    if not result_dir.exists():
        return video_count, screenshot_count
    for file_path in result_dir.rglob("*"):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        if suffix in {".webm", ".mp4"}:
            video_count += 1
        elif suffix in {".png", ".jpg", ".jpeg"}:
            screenshot_count += 1
    return video_count, screenshot_count


def _write_issue_delivery_result_report(
    issue_key: str,
    result_dir: Path,
    command: str,
    exit_code: int,
    video_count: int,
    screenshot_count: int,
):
    result_dir.mkdir(parents=True, exist_ok=True)
    report_path = result_dir / "REPORT.md"
    report_lines = [
        f"# {issue_key} Delivery Report",
        "",
        f"- generated_at: {datetime.now().isoformat()}",
        f"- command: `{command}`",
        f"- exit_code: `{exit_code}`",
        f"- videos: `{video_count}`",
        f"- screenshots: `{screenshot_count}`",
        "",
        "이 리포트는 issue-delivery 실행 결과를 요약한다.",
        "",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")


def workflow_materialize_issue_specs(cfg: dict, issue_spec_pack: dict, workspace_root: Path, subdirs: list[str]) -> dict:
    issue_specs_dir = workflow_named_artifact_path(cfg, "jira", "issue_specs", subdirs)
    issue_specs_dir.mkdir(parents=True, exist_ok=True)
    workspace_specs_dir = workspace_root / "tests" / "e2e" / "issues"
    workspace_specs_dir.mkdir(parents=True, exist_ok=True)
    runner_path = workspace_specs_dir / "run-issue-spec.sh"

    issue_items = []
    for spec in issue_spec_pack.get("specs", []):
        issue_key = str(spec.get("issue_key") or "").strip().upper()
        title = str(spec.get("title") or issue_key).strip()
        artifact_spec_path = issue_specs_dir / str(spec.get("filename") or f"{issue_key.lower()}.spec.ts")
        artifact_spec_path.write_text(spec.get("content", ""), encoding="utf-8")

        workspace_spec_path = workspace_specs_dir / artifact_spec_path.name
        note = ""
        spec_source = "generated_placeholder"
        if workspace_spec_path.exists():
            existing_text = workspace_spec_path.read_text(encoding="utf-8")
            if _is_generated_issue_spec(existing_text):
                workspace_spec_path.write_text(spec.get("content", ""), encoding="utf-8")
                note = "기존 generated placeholder spec를 최신 acceptance case 기준으로 갱신했다."
            else:
                spec_source = "custom_existing"
                note = "기존 custom issue spec를 보존했다."
        else:
            workspace_spec_path.write_text(spec.get("content", ""), encoding="utf-8")
            note = "새 generated placeholder issue spec를 생성했다."

        execution_ready = spec_source == "custom_existing" and runner_path.exists()
        if spec_source != "custom_existing":
            note = f"{note} placeholder spec는 바로 실행하지 않고 수동 selector/flow 구현이 필요하다.".strip()
        elif not runner_path.exists():
            execution_ready = False
            note = f"{note} run-issue-spec.sh가 없어 자동 실행은 보류한다.".strip()

        issue_items.append(
            {
                "issue_key": issue_key,
                "title": title,
                "track": spec.get("track", ""),
                "jira_status": spec.get("jira_status", ""),
                "priority": spec.get("priority", ""),
                "case_count": spec.get("case_count", 0),
                "case_ids": spec.get("case_ids", []),
                "task_ids": spec.get("task_ids", []),
                "categories": spec.get("categories", []),
                "touchpoints": spec.get("touchpoints", []),
                "artifact_spec_path": str(artifact_spec_path),
                "workspace_spec_path": str(workspace_spec_path),
                "runner_path": str(runner_path),
                "spec_source": spec_source,
                "generated_placeholder": spec_source != "custom_existing",
                "execution_ready": execution_ready,
                "delivery_status": "ready_to_run" if execution_ready else "prepared_blocked",
                "note": note,
            }
        )

    return {
        "issue_specs_dir": str(issue_specs_dir),
        "workspace_specs_dir": str(workspace_specs_dir),
        "runner_path": str(runner_path),
        "runner_ready": runner_path.exists(),
        "issues": issue_items,
    }


def workflow_execute_issue_delivery(delivery_items: list[dict], project_adapter_pack: dict, workspace_root: Path) -> list[dict]:
    base_url = str(project_adapter_pack.get("base_url") or "http://localhost:3000")
    auth = project_adapter_pack.get("auth", {}) if isinstance(project_adapter_pack.get("auth"), dict) else {}
    storage_state_rel = str(auth.get("storage_state_path") or "tests/.auth/user.json")
    storage_state_path = workspace_root / storage_state_rel

    executed = []
    for item in delivery_items:
        next_item = dict(item)
        issue_key = str(item.get("issue_key") or "").strip().upper()
        result_dir = workspace_root / "tests" / "results" / "issues" / issue_key
        next_item["result_directory"] = str(result_dir)

        if not item.get("execution_ready"):
            next_item["delivery_status"] = "blocked"
            next_item["note"] = item.get("note") or "자동 실행 준비가 되지 않았다."
            executed.append(next_item)
            continue

        if not storage_state_path.exists():
            next_item["delivery_status"] = "blocked"
            next_item["note"] = f"storage state가 없어 실행을 보류했다: {storage_state_path}"
            executed.append(next_item)
            continue

        runner_path = Path(str(item.get("runner_path") or ""))
        workspace_spec_path = Path(str(item.get("workspace_spec_path") or ""))
        spec_rel = os.path.relpath(workspace_spec_path, workspace_root)
        command = f"{runner_path} {spec_rel}"
        env = dict(os.environ)
        env["PORT"] = env.get("PORT") or "3000"
        env["E2E_BASE_URL"] = base_url
        env["E2E_STORAGE_STATE_PATH"] = str(storage_state_path)
        completed = subprocess.run(
            [str(runner_path), spec_rel],
            cwd=str(workspace_root),
            env=env,
            capture_output=True,
            text=True,
        )
        video_count, screenshot_count = _count_issue_evidence_assets(result_dir)
        if completed.returncode == 0 or video_count or screenshot_count:
            _write_issue_delivery_result_report(
                issue_key=issue_key,
                result_dir=result_dir,
                command=command,
                exit_code=completed.returncode,
                video_count=video_count,
                screenshot_count=screenshot_count,
            )

        next_item["delivery_status"] = "completed" if completed.returncode == 0 else "failed"
        next_item["note"] = "Issue delivery execution completed." if completed.returncode == 0 else (
            completed.stderr.strip() or completed.stdout.strip() or "Issue delivery execution failed."
        )
        next_item["command"] = command
        next_item["exit_code"] = completed.returncode
        next_item["video_count"] = video_count
        next_item["screenshot_count"] = screenshot_count
        executed.append(next_item)

    return executed


def workflow_issue_delivery(cfg: dict, args):
    bundle = workflow_project_task_flow_bundle(cfg, args)
    project_task_flow_artifacts = write_project_task_flow_artifacts(cfg, bundle)
    workspace_root = bundle["workspace_root"]
    project_name = bundle["project_name"]
    report = bundle["report"]

    from atls.analysis.harness import build_issue_spec_pack

    subdirs = workflow_issue_delivery_dir_parts(project_name)
    issue_spec_pack = build_issue_spec_pack(
        project_name=project_name,
        jira_issues=report.get("jira_issues", []),
        manifest_pack=bundle["acceptance_manifest_pack"],
        project_adapter=bundle["project_adapter_pack"],
    )
    issue_specs_json_path = workflow_named_artifact_path(cfg, "jira", "issue_specs.json", subdirs)
    issue_specs_json_path.write_text(json.dumps(issue_spec_pack, ensure_ascii=False, indent=2), encoding="utf-8")

    materialized = workflow_materialize_issue_specs(cfg, issue_spec_pack, workspace_root, subdirs)
    delivery_issues = materialized["issues"]
    execute_tests = not getattr(args, "prepare_only", False)
    if execute_tests:
        delivery_issues = workflow_execute_issue_delivery(delivery_issues, bundle["project_adapter_pack"], workspace_root)

    counts = {
        "delivery_issues": len(delivery_issues),
        "execution_ready": len([item for item in delivery_issues if item.get("execution_ready")]),
        "completed": len([item for item in delivery_issues if item.get("delivery_status") == "completed"]),
        "failed": len([item for item in delivery_issues if item.get("delivery_status") == "failed"]),
        "blocked": len([item for item in delivery_issues if item.get("delivery_status") == "blocked" or item.get("delivery_status") == "prepared_blocked"]),
    }
    result = {
        "success": True,
        "workflow": "issue-delivery",
        "prepared_at": datetime.now().isoformat(),
        "execute_tests": execute_tests,
        "workspace_root": str(workspace_root),
        "project_name": project_name,
        "warnings": bundle["warnings"],
        "jira_context": report.get("jira_context", {}),
        "counts": counts,
        "delivery_issues": delivery_issues,
        "artifact_paths": {
            "project_task_flow": project_task_flow_artifacts,
            "issue_specs_json": str(issue_specs_json_path),
            "issue_specs_dir": materialized["issue_specs_dir"],
            "workspace_specs_dir": materialized["workspace_specs_dir"],
        },
    }
    summary_md_path = write_workflow_named_artifact(cfg, "jira", "summary.md", workflow_issue_delivery_summary_markdown(result), subdirs)
    execution_md_path = write_workflow_named_artifact(cfg, "jira", "execution_report.md", workflow_issue_delivery_report_markdown(result), subdirs)
    summary_json_path = workflow_named_artifact_path(cfg, "jira", "summary.json", subdirs)
    summary_json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result["artifact_paths"]["summary_markdown"] = summary_md_path
    result["artifact_paths"]["execution_report_markdown"] = execution_md_path
    result["artifact_paths"]["summary_json"] = str(summary_json_path)
    summary_json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    out(result)


def workflow_project_detail_v2(cfg: dict, args):
    warnings = []
    jira_issues = []

    if not getattr(args, "no_jira", False):
        try:
            ensure_service_token(cfg, "jira")
            jira_result = workflow_collect_daily_review_result(cfg, args, "project-detail-v2")
            jira_issues = jira_result.get("issues", [])
        except Exception as exc:
            warnings.append(f"live Jira fetch skipped: {exc}")

    workspace_root = resolve_harness_workspace_root(getattr(args, "workspace_root", None))
    from atls.analysis.harness import (
        build_detail_v2_cards,
        build_harness_report,
        build_project_task_list,
        render_detail_v2_markdown,
    )

    subdirs = workflow_project_detail_v2_dir_parts()
    existing_project_flow = load_existing_workflow_json(
        cfg,
        "jira",
        "summary.json",
        workflow_project_task_flow_dir_parts(workspace_root.name or "project"),
    )
    existing_jira_issues = existing_project_flow.get("jira_issues", []) if isinstance(existing_project_flow, dict) else []
    merged_jira_issues = merge_issue_records(existing_jira_issues, jira_issues)

    report = build_harness_report(
        atls_root=atls_project_root(),
        workspace_root=workspace_root,
        jira_issues=merged_jira_issues,
        jira_context={
            "scope": args.scope,
            "jql": args.jql,
            "max_results": args.max_results,
            "live_issue_count": len(merged_jira_issues),
            "live_fetch_enabled": not getattr(args, "no_jira", False),
        },
    )
    report["warnings"] = warnings

    project_name = workspace_root.name or "project"
    project_tasks = build_project_task_list(report)
    detail_cards = build_detail_v2_cards(report, project_tasks)
    detail_md = render_detail_v2_markdown(project_name, detail_cards)

    detail_md_path = write_workflow_named_artifact(cfg, "jira", "detail_v2.md", detail_md, subdirs)
    detail_json_path = workflow_named_artifact_path(cfg, "jira", "detail_v2.json", subdirs)
    detail_json_path.write_text(json.dumps(detail_cards, ensure_ascii=False, indent=2), encoding="utf-8")

    out(
        {
            "success": True,
            "workflow": "project-detail-v2",
            "workspace_root": str(workspace_root),
            "project_name": project_name,
            "live_jira_issue_count": len(merged_jira_issues),
            "warnings": warnings,
            "artifact_paths": {
                "detail_markdown": detail_md_path,
                "detail_json": str(detail_json_path),
            },
            "counts": {
                "project_tasks": len(project_tasks),
                "detail_cards": len(detail_cards),
            },
        }
    )


def handle_response(resp: requests.Response, fail_message: str):
    if resp.status_code >= 400:
        err_exit(f"{fail_message} ({resp.status_code}): {resp.text[:500]}")
    return resp


def raw_response_data(resp: requests.Response):
    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            return resp.json()
        except json.JSONDecodeError:
            return resp.text
    return resp.text


def raw_result(resp: requests.Response, service: str, method: str, path: str):
    out(
        {
            "success": 200 <= resp.status_code < 300,
            "service": service,
            "method": method.upper(),
            "path": path,
            "status_code": resp.status_code,
            "data": raw_response_data(resp),
        }
    )


def normalize_api_path(path: str) -> str:
    if re.match(r"^https?://", path):
        return urllib.parse.urlparse(path).path
    return path if path.startswith("/") else f"/{path}"


def summarize_jira_issue(cfg: dict, issue_id: str) -> list[str]:
    resp = request_api(
        cfg,
        "jira",
        "GET",
        f"/issue/{issue_id}",
        params={"fields": "summary,status,assignee,issuetype,priority"},
    )
    handle_response(resp, "이슈 조회 실패")
    data = resp.json()
    fields = data.get("fields", {})
    return [
        "종류:      Jira 이슈",
        f"키:        {data.get('key', issue_id)}",
        f"제목:      {fields.get('summary', '')}",
        f"상태:      {(fields.get('status') or {}).get('name', '')}",
        f"담당자:    {(fields.get('assignee') or {}).get('displayName', 'Unassigned')}",
        f"유형:      {(fields.get('issuetype') or {}).get('name', '')}",
        f"URL:       {cfg['jira_base_url']}/browse/{data.get('key', issue_id)}",
    ]


def summarize_jira_comment(cfg: dict, issue_id: str, comment_id: str) -> list[str]:
    resp = request_api(cfg, "jira", "GET", f"/issue/{issue_id}/comment/{comment_id}")
    handle_response(resp, "댓글 조회 실패")
    data = resp.json()
    return [
        "종류:      Jira 댓글",
        f"이슈:      {issue_id}",
        f"ID:        {comment_id}",
        f"작성자:    {(data.get('author') or {}).get('displayName', '')}",
        f"작성일:    {(data.get('created') or '')[:19]}",
        f"내용:      {(data.get('body') or '')[:120]}",
    ]


def summarize_jira_worklog(cfg: dict, issue_id: str, worklog_id: str) -> list[str]:
    resp = request_api(cfg, "jira", "GET", f"/issue/{issue_id}/worklog/{worklog_id}")
    handle_response(resp, "워크로그 조회 실패")
    data = resp.json()
    return [
        "종류:      Jira 워크로그",
        f"이슈:      {issue_id}",
        f"ID:        {worklog_id}",
        f"작성자:    {(data.get('author') or {}).get('displayName', '')}",
        f"시작:      {(data.get('started') or '')[:19]}",
        f"소요시간:  {data.get('timeSpent', '')}",
        f"내용:      {(data.get('comment') or '')[:120]}",
    ]


def summarize_wiki_page(cfg: dict, page_id: str) -> list[str]:
    resp = request_api(
        cfg,
        "wiki",
        "GET",
        f"/content/{page_id}",
        params={"expand": "version,space,children.page"},
    )
    handle_response(resp, "페이지 조회 실패")
    data = resp.json()
    children = ((data.get("children") or {}).get("page") or {}).get("results", [])
    lines = [
        "종류:      Confluence 페이지",
        f"ID:        {page_id}",
        f"제목:      {data.get('title', '')}",
        f"스페이스:  {(data.get('space') or {}).get('key', '')}",
        f"버전:      v{(data.get('version') or {}).get('number', '?')}",
        f"URL:       {cfg['confluence_base_url']}{data.get('_links', {}).get('webui', '')}",
    ]
    if children:
        lines.append(f"하위 페이지: {len(children)}개")
    return lines


def maybe_confirm_raw_delete(cfg: dict, service: str, path: str, params: dict = None, payload=None):
    normalized = normalize_api_path(path)

    if service == "jira":
        match = re.search(r"/issue/([^/]+)/comment/([^/]+)$", normalized)
        if match:
            confirm_delete(summarize_jira_comment(cfg, match.group(1), match.group(2)))
            return
        match = re.search(r"/issue/([^/]+)/worklog/([^/]+)$", normalized)
        if match:
            confirm_delete(summarize_jira_worklog(cfg, match.group(1), match.group(2)))
            return
        match = re.search(r"/issue/([^/]+)$", normalized)
        if match:
            confirm_delete(summarize_jira_issue(cfg, match.group(1)))
            return

    if service == "wiki":
        match = re.search(r"/content/([^/]+)$", normalized)
        if match:
            confirm_delete(summarize_wiki_page(cfg, match.group(1)))
            return

    lines = [
        f"종류:      Raw DELETE ({service})",
        f"경로:      {normalized}",
    ]
    if params:
        lines.append(f"쿼리:      {json.dumps(params, ensure_ascii=False)}")
    if payload is not None:
        lines.append(f"페이로드:  {json.dumps(payload, ensure_ascii=False)[:300]}")
    confirm_delete(lines)


def jira_issue_brief(issue: dict, cfg: dict) -> dict:
    fields = issue.get("fields", {})
    comments = []
    for comment in ((fields.get("comment") or {}).get("comments") or [])[-5:]:
        comments.append(
            {
                "author": (comment.get("author") or {}).get("displayName", ""),
                "body": (comment.get("body") or "")[:1200],
                "created": (comment.get("created") or "")[:19],
            }
        )
    return {
        "key": issue.get("key"),
        "summary": fields.get("summary", ""),
        "status": (fields.get("status") or {}).get("name", ""),
        "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
        "priority": (fields.get("priority") or {}).get("name", ""),
        "issue_type": (fields.get("issuetype") or {}).get("name", ""),
        "created": (fields.get("created") or "")[:19],
        "created_raw": fields.get("created") or "",
        "updated_raw": fields.get("updated") or "",
        "description": (fields.get("description") or "")[:2000],
        "labels": fields.get("labels", []),
        "recent_comments": comments,
        "url": f"{cfg['jira_base_url']}/browse/{issue.get('key')}",
    }


def cmd_issue_get(cfg: dict, issue_id: str, fields_arg: str = None):
    fields = fields_arg or ",".join(JIRA_DEFAULT_FIELDS)
    resp = request_api(cfg, "jira", "GET", f"/issue/{issue_id}", params={"fields": fields})
    handle_response(resp, "이슈 조회 실패")
    out(jira_issue_brief(resp.json(), cfg))


def cmd_issue_mget(cfg: dict, issue_ids: list[str], fields_arg: str = None):
    payload = {
        "jql": "issuekey in (" + ",".join(issue_ids) + ") ORDER BY key ASC",
        "maxResults": len(issue_ids),
        "fields": (fields_arg.split(",") if fields_arg else JIRA_DEFAULT_FIELDS),
    }
    resp = request_api(cfg, "jira", "POST", "/search", payload=payload)
    handle_response(resp, "이슈 조회 실패")
    issues = [jira_issue_brief(issue, cfg) for issue in resp.json().get("issues", [])]
    out({"total": len(issues), "issues": issues})


def cmd_issue_search(cfg: dict, jql: str, max_results: int = 20, fields_arg: str = None):
    payload = {
        "jql": jql,
        "maxResults": max_results,
        "fields": (fields_arg.split(",") if fields_arg else JIRA_SEARCH_FIELDS),
    }
    resp = request_api(cfg, "jira", "POST", "/search", payload=payload)
    handle_response(resp, "이슈 검색 실패")
    data = resp.json()
    issues = []
    for issue in data.get("issues", []):
        fields = issue.get("fields", {})
        issues.append(
            {
                "key": issue.get("key"),
                "summary": fields.get("summary", ""),
                "status": (fields.get("status") or {}).get("name", ""),
                "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
                "priority": (fields.get("priority") or {}).get("name", ""),
                "issue_type": (fields.get("issuetype") or {}).get("name", ""),
                "updated": (fields.get("updated") or "")[:19],
                "labels": fields.get("labels", []),
            }
        )
    out({"total": data.get("total", 0), "issues": issues})


def build_issue_fields(args) -> dict:
    fields = {}
    if getattr(args, "project", None):
        fields["project"] = {"key": args.project}
    if getattr(args, "summary", None):
        fields["summary"] = args.summary
    if getattr(args, "description", None) is not None:
        fields["description"] = args.description
    if getattr(args, "issue_type", None):
        fields["issuetype"] = {"name": args.issue_type}
    if getattr(args, "assignee", None):
        fields["assignee"] = {"name": args.assignee}
    if getattr(args, "priority", None):
        fields["priority"] = {"name": args.priority}
    if getattr(args, "parent", None):
        fields["parent"] = {"key": args.parent}
    if getattr(args, "labels", None):
        fields["labels"] = args.labels
    return fields


def cmd_issue_create(cfg: dict, args):
    extra_fields = parse_json_input(args.json, args.json_file) or {}
    payload = {"fields": merge_dicts(build_issue_fields(args), parse_kv_list(args.field), extra_fields)}
    if "project" not in payload["fields"]:
        err_exit("issue create: --project 가 필요합니다.")
    if "summary" not in payload["fields"]:
        err_exit("issue create: --summary 가 필요합니다.")
    if "issuetype" not in payload["fields"]:
        payload["fields"]["issuetype"] = {"name": args.issue_type or "Task"}
    if is_dry_run():
        dry_run_preview("issue create", payload)
    resp = request_api(cfg, "jira", "POST", "/issue", payload=payload)
    handle_response(resp, "이슈 생성 실패")
    data = resp.json()
    out(
        {
            "success": True,
            "issue_id": data.get("id"),
            "key": data.get("key"),
            "url": f"{cfg['jira_base_url']}/browse/{data.get('key')}",
        }
    )


def cmd_issue_update(cfg: dict, args):
    extra = parse_json_input(args.json, args.json_file) or {}
    fields = merge_dicts(build_issue_fields(args), parse_kv_list(args.field), extra.get("fields"))
    update = extra.get("update", {})

    if args.add_label:
        update.setdefault("labels", [])
        update["labels"].extend({"add": label} for label in args.add_label)
    if args.remove_label:
        update.setdefault("labels", [])
        update["labels"].extend({"remove": label} for label in args.remove_label)
    if args.set_labels is not None:
        fields["labels"] = args.set_labels

    payload = {}
    if fields:
        payload["fields"] = fields
    if update:
        payload["update"] = update
    if not payload:
        err_exit("issue update: 변경할 값이 없습니다.")
    if is_dry_run():
        dry_run_preview(f"issue update {args.issue_id}", payload)
    resp = request_api(cfg, "jira", "PUT", f"/issue/{args.issue_id}", payload=payload)
    handle_response(resp, "이슈 수정 실패")
    out({"success": True, "issue": args.issue_id})


def cmd_issue_transitions(cfg: dict, issue_id: str):
    resp = request_api(cfg, "jira", "GET", f"/issue/{issue_id}/transitions")
    handle_response(resp, "전이 목록 조회 실패")
    transitions = []
    for item in resp.json().get("transitions", []):
        transitions.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "to_status": (item.get("to") or {}).get("name", ""),
            }
        )
    out({"issue": issue_id, "transitions": transitions})


def cmd_issue_transition(cfg: dict, args):
    transition_id = args.transition_id
    if not transition_id and args.transition_name:
        resp = request_api(cfg, "jira", "GET", f"/issue/{args.issue_id}/transitions")
        handle_response(resp, "전이 목록 조회 실패")
        match = None
        for item in resp.json().get("transitions", []):
            if item.get("name", "").lower() == args.transition_name.lower():
                match = item
                break
        if not match:
            err_exit(f"전이 이름을 찾지 못했습니다: {args.transition_name}")
        transition_id = match.get("id")

    if not transition_id:
        err_exit("issue transition: --id 또는 --name 이 필요합니다.")

    payload = {"transition": {"id": transition_id}}
    if args.comment:
        payload["update"] = {"comment": [{"add": {"body": args.comment}}]}
    if is_dry_run():
        dry_run_preview(f"issue transition {args.issue_id}", payload)
    resp = request_api(cfg, "jira", "POST", f"/issue/{args.issue_id}/transitions", payload=payload)
    handle_response(resp, "이슈 전이 실패")
    out({"success": True, "issue": args.issue_id, "transition_id": transition_id})


def cmd_issue_delete(cfg: dict, issue_id: str):
    confirm_delete(summarize_jira_issue(cfg, issue_id))
    resp = request_api(cfg, "jira", "DELETE", f"/issue/{issue_id}")
    handle_response(resp, "이슈 삭제 실패")
    out({"success": True, "deleted": "issue", "issue": issue_id})


def cmd_worklog_list(cfg: dict, issue_id: str):
    resp = request_api(cfg, "jira", "GET", f"/issue/{issue_id}/worklog")
    handle_response(resp, "워크로그 조회 실패")
    logs = resp.json().get("worklogs", [])
    out(
        {
            "issue": issue_id,
            "total": len(logs),
            "worklogs": [
                {
                    "id": log.get("id"),
                    "author": (log.get("author") or {}).get("displayName", ""),
                    "time_spent": log.get("timeSpent", ""),
                    "started": (log.get("started") or "")[:19],
                    "comment": (log.get("comment") or "")[:300],
                }
                for log in logs
            ],
        }
    )


def cmd_worklog_get(cfg: dict, issue_id: str, worklog_id: str):
    resp = request_api(cfg, "jira", "GET", f"/issue/{issue_id}/worklog/{worklog_id}")
    handle_response(resp, "워크로그 조회 실패")
    data = resp.json()
    out(
        {
            "issue": issue_id,
            "id": data.get("id"),
            "author": (data.get("author") or {}).get("displayName", ""),
            "time_spent": data.get("timeSpent", ""),
            "started": (data.get("started") or "")[:19],
            "comment": data.get("comment", ""),
        }
    )


def cmd_worklog_add(cfg: dict, issue_id: str, comment: str, time_spent: str, started: str = None):
    payload = {"comment": comment, "timeSpent": time_spent}
    if started:
        payload["started"] = started
    resp = request_api(cfg, "jira", "POST", f"/issue/{issue_id}/worklog", payload=payload)
    handle_response(resp, "워크로그 추가 실패")
    data = resp.json()
    out(
        {
            "success": True,
            "worklog_id": data.get("id"),
            "issue": issue_id,
            "time_spent": time_spent,
            "started": (data.get("started") or "")[:19],
            "comment": comment,
        }
    )


def cmd_worklog_update(cfg: dict, issue_id: str, worklog_id: str, started: str = None, time_spent: str = None, comment: str = None):
    payload = {}
    if started:
        payload["started"] = started
    if time_spent:
        payload["timeSpent"] = time_spent
    if comment is not None:
        payload["comment"] = comment
    if not payload:
        err_exit("worklog update: 변경할 값이 없습니다.")
    if "started" not in payload:
        current = request_api(cfg, "jira", "GET", f"/issue/{issue_id}/worklog/{worklog_id}")
        handle_response(current, "기존 워크로그 조회 실패")
        payload["started"] = current.json().get("started")
    resp = request_api(cfg, "jira", "PUT", f"/issue/{issue_id}/worklog/{worklog_id}", payload=payload)
    handle_response(resp, "워크로그 수정 실패")
    out({"success": True, "issue": issue_id, "worklog_id": worklog_id})


def cmd_worklog_delete(cfg: dict, issue_id: str, worklog_id: str):
    confirm_delete(summarize_jira_worklog(cfg, issue_id, worklog_id))
    resp = request_api(cfg, "jira", "DELETE", f"/issue/{issue_id}/worklog/{worklog_id}")
    handle_response(resp, "워크로그 삭제 실패")
    out({"success": True, "deleted": "worklog", "issue": issue_id, "worklog_id": worklog_id})


def cmd_comment_list(cfg: dict, issue_id: str):
    resp = request_api(cfg, "jira", "GET", f"/issue/{issue_id}/comment")
    handle_response(resp, "댓글 목록 조회 실패")
    data = resp.json()
    comments = []
    for item in data.get("comments", []):
        comments.append(
            {
                "id": item.get("id"),
                "author": (item.get("author") or {}).get("displayName", ""),
                "created": (item.get("created") or "")[:19],
                "updated": (item.get("updated") or "")[:19],
                "body": (item.get("body") or "")[:1000],
            }
        )
    out({"issue": issue_id, "total": data.get("total", len(comments)), "comments": comments})


def cmd_comment_get(cfg: dict, issue_id: str, comment_id: str):
    resp = request_api(cfg, "jira", "GET", f"/issue/{issue_id}/comment/{comment_id}")
    handle_response(resp, "댓글 조회 실패")
    data = resp.json()
    out(
        {
            "issue": issue_id,
            "id": data.get("id"),
            "author": (data.get("author") or {}).get("displayName", ""),
            "created": (data.get("created") or "")[:19],
            "updated": (data.get("updated") or "")[:19],
            "body": data.get("body", ""),
        }
    )


def cmd_comment_add(cfg: dict, issue_id: str, body: str):
    resp = request_api(cfg, "jira", "POST", f"/issue/{issue_id}/comment", payload={"body": body})
    handle_response(resp, "댓글 추가 실패")
    out({"success": True, "issue": issue_id, "comment_id": resp.json().get("id")})


def cmd_comment_update(cfg: dict, issue_id: str, comment_id: str, body: str):
    resp = request_api(cfg, "jira", "PUT", f"/issue/{issue_id}/comment/{comment_id}", payload={"body": body})
    handle_response(resp, "댓글 수정 실패")
    out({"success": True, "issue": issue_id, "comment_id": comment_id})


def cmd_comment_delete(cfg: dict, issue_id: str, comment_id: str):
    confirm_delete(summarize_jira_comment(cfg, issue_id, comment_id))
    resp = request_api(cfg, "jira", "DELETE", f"/issue/{issue_id}/comment/{comment_id}")
    handle_response(resp, "댓글 삭제 실패")
    out({"success": True, "deleted": "comment", "issue": issue_id, "comment_id": comment_id})


def cmd_project_list(cfg: dict):
    resp = request_api(cfg, "jira", "GET", "/project")
    handle_response(resp, "프로젝트 목록 조회 실패")
    projects = []
    for project in resp.json():
        projects.append(
            {
                "id": project.get("id"),
                "key": project.get("key"),
                "name": project.get("name"),
                "project_type": project.get("projectTypeKey"),
            }
        )
    out({"total": len(projects), "projects": projects})


def cmd_project_get(cfg: dict, project_key: str):
    resp = request_api(cfg, "jira", "GET", f"/project/{project_key}")
    handle_response(resp, "프로젝트 조회 실패")
    data = resp.json()
    out(
        {
            "id": data.get("id"),
            "key": data.get("key"),
            "name": data.get("name"),
            "lead": ((data.get("lead") or {}).get("displayName") or ""),
            "project_type": data.get("projectTypeKey"),
            "description": data.get("description", ""),
        }
    )


def cmd_user_me(cfg: dict):
    resp = request_api(cfg, "jira", "GET", "/myself")
    handle_response(resp, "현재 사용자 조회 실패")
    data = resp.json()
    out(
        {
            "name": data.get("name"),
            "display_name": data.get("displayName"),
            "email": data.get("emailAddress"),
            "active": data.get("active"),
        }
    )


def cmd_user_search(cfg: dict, query: str, max_results: int = 20):
    resp = request_api(
        cfg,
        "jira",
        "GET",
        "/user/search",
        params={"username": query, "maxResults": max_results},
    )
    handle_response(resp, "사용자 검색 실패")
    users = []
    for user in resp.json():
        users.append(
            {
                "name": user.get("name"),
                "display_name": user.get("displayName"),
                "email": user.get("emailAddress"),
                "active": user.get("active"),
            }
        )
    out({"total": len(users), "users": users})


def build_wiki_content_payload(title: str, content_html: str, space_key: str = None, parent_id: str = None) -> dict:
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {"storage": {"value": content_html, "representation": "storage"}},
    }
    if parent_id:
        payload["ancestors"] = [{"id": str(parent_id)}]
    return payload


def cmd_wiki_search(cfg: dict, args):
    space = args.space or cfg.get("default_space", "~jaecjeong")
    if args.cql:
        cql = args.cql
    else:
        cql_parts = [f'space="{space}"', "type=page"]
        if args.title:
            cql_parts.append(f'title~"{args.title}"')
        if args.text:
            cql_parts.append(f'text~"{args.text}"')
        cql = " AND ".join(cql_parts)
    params = {"cql": cql, "expand": args.expand, "limit": args.limit}
    resp = request_api(cfg, "wiki", "GET", "/content/search", params=params)
    handle_response(resp, "위키 검색 실패")
    results = []
    for page in resp.json().get("results", []):
        results.append(
            {
                "id": page.get("id"),
                "title": page.get("title", ""),
                "type": page.get("type", ""),
                "version": (page.get("version") or {}).get("number", 1),
                "url": cfg["confluence_base_url"] + page.get("_links", {}).get("webui", ""),
            }
        )
    out({"total": len(results), "cql": cql, "pages": results})


def cmd_wiki_get(cfg: dict, page_id: str, expand: str):
    resp = request_api(cfg, "wiki", "GET", f"/content/{page_id}", params={"expand": expand})
    handle_response(resp, "페이지 조회 실패")
    data = resp.json()
    body_html = ((data.get("body") or {}).get("storage") or {}).get("value", "")
    text = re.sub(r"<[^>]+>", " ", body_html)
    text = re.sub(r"\s+", " ", text).strip()
    out(
        {
            "id": data.get("id"),
            "title": data.get("title", ""),
            "version": (data.get("version") or {}).get("number", 1),
            "space": (data.get("space") or {}).get("key", ""),
            "url": cfg["confluence_base_url"] + data.get("_links", {}).get("webui", ""),
            "content_text": text[:3000],
            "content_html": body_html[:10000],
        }
    )


def cmd_wiki_children(cfg: dict, page_id: str, limit: int):
    resp = request_api(
        cfg,
        "wiki",
        "GET",
        f"/content/{page_id}/child/page",
        params={"expand": "version", "limit": limit},
    )
    handle_response(resp, "하위 페이지 조회 실패")
    children = []
    for page in resp.json().get("results", []):
        children.append(
            {
                "id": page.get("id"),
                "title": page.get("title"),
                "version": (page.get("version") or {}).get("number", 1),
                "url": cfg["confluence_base_url"] + page.get("_links", {}).get("webui", ""),
            }
        )
    out({"page_id": page_id, "total": len(children), "children": children})


def cmd_wiki_create(cfg: dict, args):
    content_html = read_wiki_content_arg(args, "wiki create")
    space = args.space or cfg.get("default_space", "~jaecjeong")
    payload = build_wiki_content_payload(args.title, content_html, space, args.parent_id)
    if is_dry_run():
        dry_run_preview("wiki create", {"title": args.title, "space": space, "parent_id": args.parent_id, "content_length": len(content_html)})
    resp = request_api(cfg, "wiki", "POST", "/content", payload=payload)
    handle_response(resp, "페이지 생성 실패")
    data = resp.json()
    out(
        {
            "success": True,
            "id": data.get("id"),
            "title": data.get("title"),
            "url": cfg["confluence_base_url"] + data.get("_links", {}).get("webui", ""),
        }
    )


def fetch_wiki_page_for_update(cfg: dict, page_id: str):
    resp = request_api(cfg, "wiki", "GET", f"/content/{page_id}", params={"expand": "body.storage,version,space"})
    handle_response(resp, "페이지 조회 실패")
    return resp.json()


def cmd_wiki_update(cfg: dict, args):
    current = fetch_wiki_page_for_update(cfg, args.page_id)
    title = args.title or current.get("title", "")
    content_html = read_wiki_content_arg(args, "wiki update")
    payload = {
        "type": "page",
        "title": title,
        "version": {"number": current["version"]["number"] + 1},
        "body": {"storage": {"value": content_html, "representation": "storage"}},
    }
    if is_dry_run():
        dry_run_preview(f"wiki update {args.page_id}", {"title": title, "new_version": current["version"]["number"] + 1, "content_length": len(content_html)})
    resp = request_api(cfg, "wiki", "PUT", f"/content/{args.page_id}", payload=payload)
    handle_response(resp, "페이지 업데이트 실패")
    out({"success": True, "page_id": args.page_id, "new_version": current["version"]["number"] + 1})


def cmd_wiki_append(cfg: dict, args):
    current = fetch_wiki_page_for_update(cfg, args.page_id)
    append_html = read_wiki_content_arg(args, "wiki append")
    current_html = ((current.get("body") or {}).get("storage") or {}).get("value", "")
    payload = {
        "type": "page",
        "title": current.get("title", ""),
        "version": {"number": current["version"]["number"] + 1},
        "body": {"storage": {"value": current_html + append_html, "representation": "storage"}},
    }
    if is_dry_run():
        dry_run_preview(f"wiki append {args.page_id}", {"title": current.get("title"), "append_length": len(append_html), "new_version": current["version"]["number"] + 1})
    resp = request_api(cfg, "wiki", "PUT", f"/content/{args.page_id}", payload=payload)
    handle_response(resp, "페이지 append 실패")
    out({"success": True, "page_id": args.page_id, "new_version": current["version"]["number"] + 1})


def cmd_wiki_delete(cfg: dict, page_id: str):
    confirm_delete(summarize_wiki_page(cfg, page_id))
    resp = request_api(cfg, "wiki", "DELETE", f"/content/{page_id}")
    handle_response(resp, "페이지 삭제 실패")
    out({"success": True, "deleted": "wiki_page", "page_id": page_id})


def cmd_raw_api(cfg: dict, service: str, args):
    params = {k: str(v) for k, v in parse_kv_list(args.param).items()}
    payload = parse_json_input(args.json, args.json_file)
    if args.method.upper() == "DELETE":
        maybe_confirm_raw_delete(cfg, service, args.path, params=params, payload=payload)
    resp = request_api(
        cfg,
        service,
        args.method,
        args.path,
        params=params,
        payload=payload,
        extra_headers={k: str(v) for k, v in parse_kv_list(args.header).items()},
    )
    handle_response(resp, f"{service} raw 호출 실패")
    raw_result(resp, service, args.method, args.path)


def atls_script_path() -> Path:
    return atls_project_root() / "atls.py"


def atls_wrapper_path() -> Path:
    return atls_project_root() / "bin" / "atls"


def atls_meta_payload() -> dict:
    script_path = str(atls_script_path())
    wrapper_path = str(atls_wrapper_path())
    return {
        "name": "atls",
        "summary": "AI-friendly Atlassian CLI for Jira and Confluence",
        "preferred_invocation": {
            "command_on_path": "atls",
            "absolute_python": f"python3 {script_path}",
            "absolute_wrapper": wrapper_path,
        },
        "startup_rule": "When an agent is unfamiliar with this tool, run `atls meta` first, then prefer high-level commands before raw API.",
        "safety_policy": {
            "delete_requires_confirmation": True,
            "non_tty_delete_blocked": True,
            "safe_default": "read and write operations are allowed; delete operations must be user-confirmed in a real terminal",
        },
        "artifact_policy": {
            "enabled_for": ["jira", "wiki"],
            "default_root": str(DEFAULT_ARTIFACT_ROOT),
            "subdirectories": ["jira", "wiki"],
            "filename_pattern": "{YYYY}_{MM}_{DD}_{task_name}.md",
            "example": "2026_04_03_issue_search_unresolved.md",
            "override_methods": [
                "CLI --artifact-root /path",
                "ATLS_ARTIFACT_ROOT=/path",
                ".atls.json artifact_root",
                "~/.atls_config.json profile.artifact_root",
            ],
        },
        "config": {
            "global_config_path": str(GLOBAL_CONFIG_PATH),
            "local_config_name": LOCAL_CONFIG_NAME,
            "default_artifact_root": str(DEFAULT_ARTIFACT_ROOT),
            "profile_resolution_order": [
                "CLI --profile",
                "ATLS_PROFILE",
                ".atls.json profile",
                "~/.atls_config.json default_profile",
            ],
            "workflow_override_methods": [
                ".atls.json workflows.daily_review.*",
                "~/.atls_config.json profiles.<name>.workflows.daily_review.*",
                "ATLS_DAILY_REVIEW_WIKI_*",
            ],
        },
        "high_level_commands": {
            "issue": ["get", "mget", "search", "create", "update", "transitions", "transition", "delete"],
            "worklog": ["list", "get", "add", "update", "delete"],
            "comment": ["list", "get", "add", "update", "delete"],
            "project": ["list", "get"],
            "user": ["me", "search"],
            "wiki": ["search", "get", "create", "update", "append", "children", "delete"],
            "workflow": ["daily-review", "daily-review-detail", "qa-gemini-harness", "project-task-flow", "issue-delivery", "project-detail-v2"],
            "ping": ["jira", "wiki", "all"],
        },
        "raw_commands": {
            "jira-api": "Any Jira REST or Agile REST endpoint",
            "wiki-api": "Any Confluence REST endpoint",
        },
        "examples": [
            "atls issue get GEMINI-1234",
            "atls issue search \"assignee=jaecjeong AND status='In Progress'\" --max 20",
            "atls issue create --project GEMINI --summary \"로그인 오류\" --type Bug",
            "atls worklog add GEMINI-1234 \"QA 검토\" 2h --started 2026-04-01T09:00:00.000+0900",
            "atls comment add GEMINI-1234 \"수정 완료했습니다\"",
            "atls wiki search --title \"QA Status\"",
            "atls wiki create \"제목\" \"<h1>내용</h1>\" --space ~jaecjeong",
            "atls jira-api GET /rest/agile/1.0/board",
            "atls wiki-api GET /content/543080607/child/comment",
            "atls workflow daily-review",
            "atls workflow daily-review-detail",
            "atls workflow qa-gemini-harness --no-jira --workspace-root /path/to/adcenter",
            "atls workflow project-task-flow --workspace-root /path/to/project",
            "atls workflow issue-delivery --workspace-root /path/to/project",
            "atls workflow project-detail-v2 --workspace-root /path/to/project",
            "atls workflow daily-review --publish",
            "ATLS_DAILY_REVIEW_WIKI_PARENT_PAGE_ID=543086649 atls workflow daily-review --publish",
            "atls ping jira",
            "atls ping all --timeout 3",
        ],
        "agent_prompt_template": [
            "Use atls for Jira/Confluence operations in this workspace.",
            "Run `atls meta` first if you need capabilities or safety rules.",
            "Prefer high-level commands.",
            "Use jira-api or wiki-api when a high-level command does not exist.",
            "Use `atls workflow qa-gemini-harness` when you need QA/GEMINI-focused harness prompts and adcenter analysis scaffolding.",
            "Use `atls workflow project-task-flow` when you want summary -> task list -> execution card workflow artifacts with approval gates.",
            "Use `atls workflow issue-delivery` when you want task plan + acceptance manifest + issue spec sync + optional test execution in one flow.",
            "Use `atls workflow project-detail-v2` when you want a regenerated detail document from summary-based project analysis.",
            "Never expect delete to succeed non-interactively; ask the user to confirm in a terminal.",
        ],
    }


def cmd_meta():
    out(atls_meta_payload())


def cmd_doctor(cfg: dict):
    wrapper = atls_wrapper_path()
    script = atls_script_path()
    on_path = shutil.which("atls")
    local_cfg = load_local_config()
    daily_review_cfg = workflow_config(cfg, "daily_review")
    daily_review_detail_cfg = workflow_config(cfg, "daily_review_detail")
    out(
        {
            "success": True,
            "tool": "atls",
            "paths": {
                "script": str(script),
                "wrapper": str(wrapper),
                "on_path": on_path,
            },
            "executable": {
                "wrapper_exists": wrapper.exists(),
                "wrapper_executable": os.access(wrapper, os.X_OK) if wrapper.exists() else False,
                "python_available": shutil.which("python3") is not None,
            },
            "config": {
                "global_exists": GLOBAL_CONFIG_PATH.exists(),
                "global_path": str(GLOBAL_CONFIG_PATH),
                "local_detected": bool(local_cfg),
                "local_config": local_cfg,
                "active_profile": cfg.get("active_profile"),
                "jira_base_url": cfg.get("jira_base_url"),
                "confluence_base_url": cfg.get("confluence_base_url"),
                "jira_token_configured": bool(cfg.get("jira_token")),
                "confluence_token_configured": bool(cfg.get("confluence_token")),
                "artifact_root": str(artifact_root_path(cfg)),
                "daily_review_workflow": daily_review_cfg,
                "daily_review_detail_workflow": daily_review_detail_cfg,
            },
            "next_steps": [
                "Put `atls` on PATH or use the absolute wrapper/script path.",
                "Tell agents to run `atls meta` first when they have no context.",
                "Keep delete operations user-confirmed in a real terminal.",
            ],
        }
    )


def cmd_config(args: list[str]):
    global_cfg = load_global_config()
    subcmd = args[0] if args else "show"

    if subcmd == "show":
        cfg = resolve_config()
        daily_review_cfg = workflow_config(cfg, "daily_review")
        daily_review_detail_cfg = workflow_config(cfg, "daily_review_detail")
        print(f"활성 프로파일: {cfg['active_profile']}")
        print(f"  Jira URL:       {cfg['jira_base_url']}")
        print(f"  Confluence URL: {cfg['confluence_base_url']}")
        print(f"  기본 스페이스:  {cfg['default_space']}")
        print(f"  담당자:         {cfg['default_assignee']}")
        print(f"  저장 루트:      {cfg['artifact_root']}")
        print(f"  Daily Review Space:   {daily_review_cfg.get('wiki_space') or cfg['default_space']}")
        print(f"  Daily Review Parent:  {daily_review_cfg.get('wiki_parent_page_id') or '-'}")
        print(f"  Daily Review Page:    {daily_review_cfg.get('wiki_page_id') or '-'}")
        print(f"  Daily Review Title:   {daily_review_cfg.get('wiki_title_template') or '-'}")
        print(f"  Daily Review Publish: {daily_review_cfg.get('wiki_auto_publish')}")
        print(f"  Detail Review Parent:  {daily_review_detail_cfg.get('wiki_parent_page_id') or '-'}")
        print(f"  Detail Review Page:    {daily_review_detail_cfg.get('wiki_page_id') or '-'}")
        print(f"  Detail Review Title:   {daily_review_detail_cfg.get('wiki_title_template') or '-'}")
        print(f"  Detail Review Publish: {daily_review_detail_cfg.get('wiki_auto_publish')}")
        print(f"\n프로파일 목록:")
        for name, prof in global_cfg.get("profiles", {}).items():
            mark = "★" if name == global_cfg.get("default_profile") else " "
            desc = prof.get("description", prof.get("jira_base_url", ""))
            print(f"  {mark} {name}: {desc}")
        print(f"\n설정 파일: {GLOBAL_CONFIG_PATH}")
        local_cfg = load_local_config()
        if local_cfg:
            print(f"로컬 설정 적용됨: {local_cfg}")
        return

    if subcmd == "profiles":
        for name, prof in global_cfg.get("profiles", {}).items():
            print(f"{name}: {prof.get('jira_base_url')} / {prof.get('confluence_base_url')}")
        return

    if subcmd == "add-profile" and len(args) >= 2:
        name = args[1]
        print(f"새 프로파일 '{name}' 등록")
        jira_url = input("  Jira URL:             ").strip()
        jira_token = input("  Jira API Token:       ").strip()
        wiki_url = input("  Confluence URL:       ").strip()
        wiki_token = input("  Confluence Token:     ").strip()
        space = input("  기본 스페이스 키:     ").strip()
        assignee = input("  담당자 계정:          ").strip()
        artifact_root = input(f"  결과 저장 루트:       [{DEFAULT_ARTIFACT_ROOT}] ").strip()
        desc = input("  설명 (선택):          ").strip()
        global_cfg.setdefault("profiles", {})[name] = {
            "jira_token": jira_token,
            "jira_base_url": jira_url,
            "confluence_token": wiki_token,
            "confluence_base_url": wiki_url,
            "default_space": space,
            "default_assignee": assignee,
            "artifact_root": artifact_root or str(DEFAULT_ARTIFACT_ROOT),
            "description": desc or name,
        }
        GLOBAL_CONFIG_PATH.write_text(json.dumps(global_cfg, indent=2, ensure_ascii=False))
        print(f"✓ 프로파일 '{name}' 저장 완료")
        return

    if subcmd == "set-default" and len(args) >= 2:
        name = args[1]
        if name not in global_cfg.get("profiles", {}):
            err_exit(f"프로파일 '{name}' 없음")
        global_cfg["default_profile"] = name
        GLOBAL_CONFIG_PATH.write_text(json.dumps(global_cfg, indent=2, ensure_ascii=False))
        print(f"✓ 기본 프로파일 → '{name}'")
        return

    if subcmd == "init-local":
        profile = args[1] if len(args) > 1 else global_cfg.get("default_profile", "")
        local_path = Path.cwd() / LOCAL_CONFIG_NAME
        local_path.write_text(json.dumps({"profile": profile}, indent=2, ensure_ascii=False))
        print(f"✓ {local_path} 생성 (프로파일: {profile})")
        return

    print("사용법: atls config [show|profiles|add-profile <name>|set-default <name>|init-local [profile]]")
    print()
    print("환경변수:")
    print("  ATLS_PROFILE              활성 프로파일")
    print("  ATLS_JIRA_TOKEN           Jira 토큰 오버라이드")
    print("  ATLS_CONFLUENCE_TOKEN     Confluence 토큰 오버라이드")
    print("  ATLS_JIRA_BASE_URL        Jira URL 오버라이드")
    print("  ATLS_CONFLUENCE_BASE_URL  Confluence URL 오버라이드")
    print("  ATLS_ARTIFACT_ROOT        Markdown 저장 루트 오버라이드")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atls",
        description="Atlassian CLI (Jira & Confluence) - 범용 AI 친화 CLI",
    )
    parser.add_argument("--profile", "-p", help="프로파일 이름")
    parser.add_argument("--task-name", help="저장 파일명에 사용할 태스크 이름 override")
    parser.add_argument("--artifact-root", help="Markdown 결과 저장 루트 override")
    sub = parser.add_subparsers(dest="cmd")

    issue = sub.add_parser("issue", help="Jira 이슈")
    issue_sub = issue.add_subparsers(dest="subcmd")

    ig = issue_sub.add_parser("get", help="이슈 상세 조회")
    ig.add_argument("issue_id")
    ig.add_argument("--fields", default=None, help="comma-separated Jira fields")

    img = issue_sub.add_parser("mget", help="여러 이슈 한번에 조회")
    img.add_argument("issue_ids", nargs="+", metavar="ISSUE_ID")
    img.add_argument("--fields", default=None, help="comma-separated Jira fields")

    isc = issue_sub.add_parser("search", help="JQL 검색")
    isc.add_argument("jql")
    isc.add_argument("--max", type=int, default=20, dest="max_results")
    isc.add_argument("--fields", default=None, help="comma-separated Jira fields")

    icr = issue_sub.add_parser("create", help="이슈 생성")
    icr.add_argument("--project", required=True)
    icr.add_argument("--summary", required=True)
    icr.add_argument("--description", default=None)
    icr.add_argument("--type", dest="issue_type", default="Task")
    icr.add_argument("--assignee", default=None)
    icr.add_argument("--priority", default=None)
    icr.add_argument("--label", dest="labels", action="append", default=[])
    icr.add_argument("--parent", default=None)
    icr.add_argument("--field", action="append", default=[], help="custom Jira field KEY=VALUE")
    icr.add_argument("--json", default=None, help="extra JSON for fields")
    icr.add_argument("--json-file", default=None, help="file containing extra JSON for fields")
    icr.add_argument("--dry-run", action="store_true", dest="dry_run", help="API 호출 없이 전송 예정 payload 확인")

    iup = issue_sub.add_parser("update", help="이슈 수정")
    iup.add_argument("issue_id")
    iup.add_argument("--project", default=None)
    iup.add_argument("--summary", default=None)
    iup.add_argument("--description", default=None)
    iup.add_argument("--type", dest="issue_type", default=None)
    iup.add_argument("--assignee", default=None)
    iup.add_argument("--priority", default=None)
    iup.add_argument("--set-label", dest="set_labels", action="append", default=None)
    iup.add_argument("--add-label", action="append", default=[])
    iup.add_argument("--remove-label", action="append", default=[])
    iup.add_argument("--parent", default=None)
    iup.add_argument("--field", action="append", default=[], help="custom Jira field KEY=VALUE")
    iup.add_argument("--json", default=None, help='full update JSON: {"fields":...,"update":...}')
    iup.add_argument("--json-file", default=None)
    iup.add_argument("--dry-run", action="store_true", dest="dry_run", help="API 호출 없이 전송 예정 payload 확인")

    its = issue_sub.add_parser("transitions", help="가능한 상태 전이 조회")
    its.add_argument("issue_id")

    itr = issue_sub.add_parser("transition", help="상태 전이 실행")
    itr.add_argument("issue_id")
    itr.add_argument("--id", dest="transition_id", default=None)
    itr.add_argument("--name", dest="transition_name", default=None)
    itr.add_argument("--comment", default=None)
    itr.add_argument("--dry-run", action="store_true", dest="dry_run", help="API 호출 없이 전이 예정 payload 확인")

    ide = issue_sub.add_parser("delete", help="이슈 삭제 (interactive 확인 필수)")
    ide.add_argument("issue_id")

    worklog = sub.add_parser("worklog", help="Jira 워크로그")
    worklog_sub = worklog.add_subparsers(dest="subcmd")

    wll = worklog_sub.add_parser("list", help="워크로그 목록")
    wll.add_argument("issue_id")

    wlg = worklog_sub.add_parser("get", help="워크로그 상세")
    wlg.add_argument("issue_id")
    wlg.add_argument("worklog_id")

    wla = worklog_sub.add_parser("add", help="워크로그 추가")
    wla.add_argument("issue_id")
    wla.add_argument("comment")
    wla.add_argument("time_spent")
    wla.add_argument("--started", default=None)

    wlu = worklog_sub.add_parser("update", help="워크로그 수정")
    wlu.add_argument("issue_id")
    wlu.add_argument("worklog_id")
    wlu.add_argument("--started", default=None)
    wlu.add_argument("--time", dest="time_spent", default=None)
    wlu.add_argument("--comment", default=None)

    wld = worklog_sub.add_parser("delete", help="워크로그 삭제 (interactive 확인 필수)")
    wld.add_argument("issue_id")
    wld.add_argument("worklog_id")

    comment = sub.add_parser("comment", help="Jira 댓글")
    comment_sub = comment.add_subparsers(dest="subcmd")

    cml = comment_sub.add_parser("list", help="댓글 목록")
    cml.add_argument("issue_id")

    cmg = comment_sub.add_parser("get", help="댓글 상세")
    cmg.add_argument("issue_id")
    cmg.add_argument("comment_id")

    cma = comment_sub.add_parser("add", help="댓글 추가")
    cma.add_argument("issue_id")
    cma.add_argument("body")

    cmu = comment_sub.add_parser("update", help="댓글 수정")
    cmu.add_argument("issue_id")
    cmu.add_argument("comment_id")
    cmu.add_argument("body")

    cmd = comment_sub.add_parser("delete", help="댓글 삭제 (interactive 확인 필수)")
    cmd.add_argument("issue_id")
    cmd.add_argument("comment_id")

    project = sub.add_parser("project", help="Jira 프로젝트")
    project_sub = project.add_subparsers(dest="subcmd")
    project_sub.add_parser("list", help="프로젝트 목록")
    pg = project_sub.add_parser("get", help="프로젝트 상세")
    pg.add_argument("project_key")

    user = sub.add_parser("user", help="Jira 사용자")
    user_sub = user.add_subparsers(dest="subcmd")
    user_sub.add_parser("me", help="현재 사용자")
    us = user_sub.add_parser("search", help="사용자 검색")
    us.add_argument("query")
    us.add_argument("--max", type=int, default=20, dest="max_results")

    ping = sub.add_parser("ping", help="Jira/Confluence 연결 상태 점검")
    ping.add_argument("target", nargs="?", choices=["jira", "wiki", "all"], default="all")
    ping.add_argument("--timeout", type=float, default=5.0, help="각 단계 timeout (seconds)")

    workflow = sub.add_parser("workflow", help="수집/분석/리포트 워크플로우")
    workflow_sub = workflow.add_subparsers(dest="subcmd")
    daily = workflow_sub.add_parser("daily-review", help="assigned unresolved daily review")
    daily.add_argument("--scope", default="assigned-unresolved")
    daily.add_argument("--jql", default="assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC")
    daily.add_argument("--max", type=int, default=200, dest="max_results")
    daily.add_argument("--publish", action="store_true", help="Confluence wiki에 바로 publish")
    daily.add_argument("--no-publish", action="store_true", help="설정에 auto publish가 있어도 이번 실행에서는 publish 하지 않음")
    daily.add_argument("--collect-only", action="store_true", help="Jira 수집만 실행하고 분석/발행 생략")
    daily.add_argument("--page-id", default=None, help="기존 위키 page id가 있으면 update")
    daily.add_argument("--wiki-title", default=None, help="위키 제목 override")
    daily.add_argument("--space", default=None, help="위키 생성 시 대상 스페이스")
    daily.add_argument("--parent", dest="parent_id", default=None, help="위키 생성 시 parent page id")
    daily.add_argument("--dry-run", action="store_true", dest="dry_run", help="발행 없이 생성될 위키 내용 미리보기")
    daily_detail = workflow_sub.add_parser("daily-review-detail", help="assigned unresolved daily review detail")
    daily_detail.add_argument("--scope", default="assigned-unresolved")
    daily_detail.add_argument("--jql", default="assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC")
    daily_detail.add_argument("--max", type=int, default=200, dest="max_results")
    daily_detail.add_argument("--publish", action="store_true", help="Confluence wiki에 바로 publish")
    daily_detail.add_argument("--no-publish", action="store_true", help="설정에 auto publish가 있어도 이번 실행에서는 publish 하지 않음")
    daily_detail.add_argument("--collect-only", action="store_true", help="Jira 수집만 실행하고 분석/발행 생략")
    daily_detail.add_argument("--page-id", default=None, help="기존 위키 page id가 있으면 update")
    daily_detail.add_argument("--wiki-title", default=None, help="위키 제목 override")
    daily_detail.add_argument("--space", default=None, help="위키 생성 시 대상 스페이스")
    daily_detail.add_argument("--parent", dest="parent_id", default=None, help="위키 생성 시 parent page id")
    daily_detail.add_argument("--dry-run", action="store_true", dest="dry_run", help="발행 없이 생성될 위키 내용 미리보기")
    harness = workflow_sub.add_parser("qa-gemini-harness", help="QA/GEMINI harness prompt + adcenter analysis pack")
    harness.add_argument("--scope", default="qa-gemini")
    harness.add_argument("--jql", default="resolution = Unresolved AND (project = GEMINI OR project = QA) ORDER BY updated DESC")
    harness.add_argument("--max", type=int, default=200, dest="max_results")
    harness.add_argument("--workspace-root", default=None, help="adcenter project root path")
    harness.add_argument("--no-jira", action="store_true", help="live Jira fetch 없이 문서/코드 기준으로만 report 생성")
    project_flow = workflow_sub.add_parser("project-task-flow", help="summary 기반 프로젝트 태스크/실행 워크플로우")
    project_flow.add_argument("--scope", default="qa-gemini")
    project_flow.add_argument("--jql", default="resolution = Unresolved AND (project = GEMINI OR project = QA) ORDER BY updated DESC")
    project_flow.add_argument("--max", type=int, default=200, dest="max_results")
    project_flow.add_argument("--workspace-root", default=None, help="project root path")
    project_flow.add_argument("--no-jira", action="store_true", help="live Jira fetch 없이 문서/코드 기준으로만 workflow 생성")
    issue_delivery = workflow_sub.add_parser("issue-delivery", help="summary 기반 완성형 issue delivery workflow")
    issue_delivery.add_argument("--scope", default="qa-gemini")
    issue_delivery.add_argument("--jql", default="resolution = Unresolved AND (project = GEMINI OR project = QA) ORDER BY updated DESC")
    issue_delivery.add_argument("--max", type=int, default=200, dest="max_results")
    issue_delivery.add_argument("--workspace-root", default=None, help="project root path")
    issue_delivery.add_argument("--no-jira", action="store_true", help="live Jira fetch 없이 기존 산출물 기준으로만 workflow 생성")
    issue_delivery.add_argument("--prepare-only", action="store_true", help="issue spec/materialization까지만 수행하고 테스트 실행은 생략")
    detail_v2 = workflow_sub.add_parser("project-detail-v2", help="summary 기반 regenerated detail v2 문서 생성")
    detail_v2.add_argument("--scope", default="qa-gemini")
    detail_v2.add_argument("--jql", default="resolution = Unresolved AND (project = GEMINI OR project = QA) ORDER BY updated DESC")
    detail_v2.add_argument("--max", type=int, default=200, dest="max_results")
    detail_v2.add_argument("--workspace-root", default=None, help="project root path")
    detail_v2.add_argument("--no-jira", action="store_true", help="live Jira fetch 없이 문서/코드 기준으로만 detail 생성")

    wiki = sub.add_parser("wiki", help="Confluence 페이지")
    wiki_sub = wiki.add_subparsers(dest="subcmd")

    wis = wiki_sub.add_parser("search", help="페이지 검색")
    wis.add_argument("--space", default=None)
    wis.add_argument("--title", default=None)
    wis.add_argument("--text", default=None)
    wis.add_argument("--cql", default=None)
    wis.add_argument("--expand", default="version")
    wis.add_argument("--limit", type=int, default=20)

    wig = wiki_sub.add_parser("get", help="페이지 조회")
    wig.add_argument("page_id")
    wig.add_argument("--expand", default="body.storage,version,ancestors,space")

    wic = wiki_sub.add_parser("create", help="페이지 생성")
    wic.add_argument("title")
    wic.add_argument("content_html", nargs="?")
    wic.add_argument("--content-file", default=None)
    wic.add_argument("--markdown", default=None)
    wic.add_argument("--markdown-file", default=None)
    wic.add_argument("--space", default=None)
    wic.add_argument("--parent", dest="parent_id", default=None)
    wic.add_argument("--dry-run", action="store_true", dest="dry_run", help="API 호출 없이 생성 예정 payload 확인")

    wiu = wiki_sub.add_parser("update", help="페이지 업데이트")
    wiu.add_argument("page_id")
    wiu.add_argument("title", nargs="?")
    wiu.add_argument("content_html", nargs="?")
    wiu.add_argument("--content-file", default=None)
    wiu.add_argument("--markdown", default=None)
    wiu.add_argument("--markdown-file", default=None)
    wiu.add_argument("--dry-run", action="store_true", dest="dry_run", help="API 호출 없이 업데이트 예정 payload 확인")

    wia = wiki_sub.add_parser("append", help="페이지 끝에 HTML 추가")
    wia.add_argument("page_id")
    wia.add_argument("content_html", nargs="?")
    wia.add_argument("--content-file", default=None)
    wia.add_argument("--markdown", default=None)
    wia.add_argument("--markdown-file", default=None)
    wia.add_argument("--dry-run", action="store_true", dest="dry_run", help="API 호출 없이 append 예정 payload 확인")

    wich = wiki_sub.add_parser("children", help="하위 페이지 목록")
    wich.add_argument("page_id")
    wich.add_argument("--limit", type=int, default=50)

    wid = wiki_sub.add_parser("delete", help="페이지 삭제 (interactive 확인 필수)")
    wid.add_argument("page_id")

    for service_name in ("jira-api", "wiki-api"):
        raw = sub.add_parser(service_name, help=f"{service_name} raw REST 호출")
        raw.add_argument("method", help="GET/POST/PUT/DELETE/PATCH ...")
        raw.add_argument("path", help="/issue/KEY 또는 /rest/agile/1.0/board 등")
        raw.add_argument("--param", action="append", default=[], help="query string KEY=VALUE")
        raw.add_argument("--header", action="append", default=[], help="extra header KEY=VALUE")
        raw.add_argument("--json", default=None, help="JSON body")
        raw.add_argument("--json-file", default=None, help="JSON body file")

    sub.add_parser("meta", help="에이전트용 JSON 메타 정보")
    sub.add_parser("doctor", help="실행 가능 상태와 설정 점검")
    sub.add_parser("config", help="설정 관리").add_argument("config_args", nargs="*")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    if args.cmd == "meta":
        cmd_meta()
        return

    if args.cmd == "config":
        cmd_config(getattr(args, "config_args", []))
        return

    cfg = resolve_config(getattr(args, "profile", None))
    if getattr(args, "artifact_root", None):
        cfg["artifact_root"] = args.artifact_root

    init_runtime_context(cfg, args)

    if args.cmd == "doctor":
        cmd_doctor(cfg)
        return

    if args.cmd == "ping":
        cmd_ping(cfg, args)
        return

    if args.cmd == "workflow":
        if args.subcmd == "daily-review":
            workflow_daily_review(cfg, args)
            return
        if args.subcmd == "daily-review-detail":
            workflow_daily_review_detail(cfg, args)
            return
        if args.subcmd == "qa-gemini-harness":
            workflow_qa_gemini_harness(cfg, args)
            return
        if args.subcmd == "project-task-flow":
            workflow_project_task_flow(cfg, args)
            return
        if args.subcmd == "issue-delivery":
            workflow_issue_delivery(cfg, args)
            return
        if args.subcmd == "project-detail-v2":
            workflow_project_detail_v2(cfg, args)
            return
        err_exit("atls workflow [daily-review|daily-review-detail|qa-gemini-harness|project-task-flow|issue-delivery|project-detail-v2]")

    if args.cmd in ("issue", "worklog", "comment", "project", "user", "jira-api"):
        ensure_service_token(cfg, "jira")
    if args.cmd in ("wiki", "wiki-api"):
        ensure_service_token(cfg, "wiki")

    if args.cmd == "issue":
        if args.subcmd == "get":
            cmd_issue_get(cfg, args.issue_id, args.fields)
            return
        if args.subcmd == "mget":
            cmd_issue_mget(cfg, args.issue_ids, args.fields)
            return
        if args.subcmd == "search":
            cmd_issue_search(cfg, args.jql, args.max_results, args.fields)
            return
        if args.subcmd == "create":
            cmd_issue_create(cfg, args)
            return
        if args.subcmd == "update":
            cmd_issue_update(cfg, args)
            return
        if args.subcmd == "transitions":
            cmd_issue_transitions(cfg, args.issue_id)
            return
        if args.subcmd == "transition":
            cmd_issue_transition(cfg, args)
            return
        if args.subcmd == "delete":
            cmd_issue_delete(cfg, args.issue_id)
            return
        err_exit("atls issue [get|mget|search|create|update|transitions|transition|delete]")

    if args.cmd == "worklog":
        if args.subcmd == "list":
            cmd_worklog_list(cfg, args.issue_id)
            return
        if args.subcmd == "get":
            cmd_worklog_get(cfg, args.issue_id, args.worklog_id)
            return
        if args.subcmd == "add":
            cmd_worklog_add(cfg, args.issue_id, args.comment, args.time_spent, args.started)
            return
        if args.subcmd == "update":
            cmd_worklog_update(cfg, args.issue_id, args.worklog_id, args.started, args.time_spent, args.comment)
            return
        if args.subcmd == "delete":
            cmd_worklog_delete(cfg, args.issue_id, args.worklog_id)
            return
        err_exit("atls worklog [list|get|add|update|delete]")

    if args.cmd == "comment":
        if args.subcmd == "list":
            cmd_comment_list(cfg, args.issue_id)
            return
        if args.subcmd == "get":
            cmd_comment_get(cfg, args.issue_id, args.comment_id)
            return
        if args.subcmd == "add":
            cmd_comment_add(cfg, args.issue_id, args.body)
            return
        if args.subcmd == "update":
            cmd_comment_update(cfg, args.issue_id, args.comment_id, args.body)
            return
        if args.subcmd == "delete":
            cmd_comment_delete(cfg, args.issue_id, args.comment_id)
            return
        err_exit("atls comment [list|get|add|update|delete]")

    if args.cmd == "project":
        if args.subcmd == "list":
            cmd_project_list(cfg)
            return
        if args.subcmd == "get":
            cmd_project_get(cfg, args.project_key)
            return
        err_exit("atls project [list|get]")

    if args.cmd == "user":
        if args.subcmd == "me":
            cmd_user_me(cfg)
            return
        if args.subcmd == "search":
            cmd_user_search(cfg, args.query, args.max_results)
            return
        err_exit("atls user [me|search]")

    if args.cmd == "wiki":
        if args.subcmd == "search":
            cmd_wiki_search(cfg, args)
            return
        if args.subcmd == "get":
            cmd_wiki_get(cfg, args.page_id, args.expand)
            return
        if args.subcmd == "create":
            cmd_wiki_create(cfg, args)
            return
        if args.subcmd == "update":
            cmd_wiki_update(cfg, args)
            return
        if args.subcmd == "append":
            cmd_wiki_append(cfg, args)
            return
        if args.subcmd == "children":
            cmd_wiki_children(cfg, args.page_id, args.limit)
            return
        if args.subcmd == "delete":
            cmd_wiki_delete(cfg, args.page_id)
            return
        err_exit("atls wiki [search|get|create|update|append|children|delete]")

    if args.cmd == "jira-api":
        cmd_raw_api(cfg, "jira", args)
        return

    if args.cmd == "wiki-api":
        cmd_raw_api(cfg, "wiki", args)
        return


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as exc:
        err_exit(f"네트워크 요청 실패: {exc}")
