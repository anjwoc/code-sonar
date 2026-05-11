#!/usr/bin/env bash
# install-antigravity.sh — Antigravity용 Code-Sonar 설치 스크립트
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AG_BIN="$HOME/.antigravity/antigravity/bin/antigravity"
CLAUDE_SETTINGS="$REPO_ROOT/.claude/settings.json"

# ─── 색상 & 유틸 ──────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
GRAY='\033[0;90m'; BOLD='\033[1m'; NC='\033[0m'

ok()    { echo -e "${GREEN}✔${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
fail()  { echo -e "${RED}✘${NC} $*"; }
log()   { echo -e "${GRAY}  → $*${NC}"; }
step()  { echo -e "\n${BOLD}[$1/$2]${NC} $3"; }

# 스피너: spin <pid> <메시지>
spin() {
  local pid=$1 msg=$2
  local frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
  local i=0
  while kill -0 "$pid" 2>/dev/null; do
    printf "\r  ${GRAY}%s${NC} %s..." "${frames[$((i % 10))]}" "$msg"
    sleep 0.1
    ((i++)) || true
  done
  printf "\r\033[2K"  # 스피너 줄 지우기
}

echo ""
echo -e "${BOLD}Code-Sonar × Antigravity 설치${NC}"
echo "================================"
echo "Repo: $REPO_ROOT"
echo ""

# ─── Antigravity 확인 ────────────────────────────────────
if [ -f "$AG_BIN" ]; then
  AG_VERSION=$("$AG_BIN" --version 2>/dev/null | head -1 || echo "unknown")
  ok "Antigravity: $AG_VERSION"
elif [ -d "/Applications/Antigravity.app" ]; then
  ok "Antigravity.app"
  AG_BIN=""
else
  fail "Antigravity를 찾을 수 없습니다. https://antigravity.dev"
  exit 1
fi

# ─── Node.js 확인 ────────────────────────────────────────
if ! command -v node >/dev/null 2>&1; then
  fail "Node.js 없음. https://nodejs.org 에서 설치하세요."
  exit 1
fi
ok "Node.js $(node --version)"

# ═══════════════════════════════════════════════════════
step 1 3 "Excalidraw MCP 확인"
# ═══════════════════════════════════════════════════════

log "npm에서 excalidraw-mcp 패키지 확인 중..."

# npx --yes는 첫 실행 시 다운로드가 오래 걸리므로 실시간 출력 + 타임아웃
MCP_AVAILABLE=false

# 이미 캐시됐는지 먼저 확인 (빠름)
if npm list -g excalidraw-mcp --depth=0 >/dev/null 2>&1 || \
   npm list excalidraw-mcp --depth=0 >/dev/null 2>&1; then
  ok "excalidraw-mcp 설치 확인"
  MCP_AVAILABLE=true
else
  log "캐시 없음 — 설치합니다 (네트워크 상태에 따라 30초 이상 소요될 수 있습니다)"
  echo ""

  # 실시간 npm 출력 표시 (suppress 하지 않음)
  if npm install -g excalidraw-mcp 2>&1 | while IFS= read -r line; do
       echo -e "  ${GRAY}${line}${NC}"
     done; then
    ok "excalidraw-mcp 전역 설치 완료"
    MCP_AVAILABLE=true
  else
    warn "전역 설치 실패 — 로컬 설치 시도 중..."
    if npm install --save-dev excalidraw-mcp 2>&1 | while IFS= read -r line; do
         echo -e "  ${GRAY}${line}${NC}"
       done; then
      ok "excalidraw-mcp 로컬 설치 완료"
      MCP_AVAILABLE=true
    else
      warn "자동 설치 실패. 수동으로 설치하세요:"
      echo "     npm install -g excalidraw-mcp"
    fi
  fi
fi

# ═══════════════════════════════════════════════════════
step 2 3 "프로젝트 MCP 설정 (.claude/settings.json)"
# ═══════════════════════════════════════════════════════

mkdir -p "$REPO_ROOT/.claude"

if [ -f "$CLAUDE_SETTINGS" ]; then
  if python3 -c "
import json, sys
d = json.load(open('$CLAUDE_SETTINGS'))
sys.exit(0 if 'excalidraw' in d.get('mcpServers', {}) else 1)
" 2>/dev/null; then
    ok "excalidraw MCP 이미 등록됨"
    log "$CLAUDE_SETTINGS"
  else
    python3 -c "
import json
path = '$CLAUDE_SETTINGS'
with open(path) as f:
    d = json.load(f)
d.setdefault('mcpServers', {})['excalidraw'] = {
    'command': 'npx', 'args': ['excalidraw-mcp'], 'env': {}
}
with open(path, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
    ok "excalidraw MCP 추가됨"
    log "$CLAUDE_SETTINGS"
  fi
else
  cat > "$CLAUDE_SETTINGS" <<'JSON'
{
  "mcpServers": {
    "excalidraw": {
      "command": "npx",
      "args": ["excalidraw-mcp"],
      "env": {}
    }
  }
}
JSON
  ok "MCP 설정 파일 생성"
  log "$CLAUDE_SETTINGS"
fi

# ═══════════════════════════════════════════════════════
step 3 3 "Antigravity 글로벌 워크플로우 & Workspace"
# ═══════════════════════════════════════════════════════

# ─── Excalidraw 워크플로우 글로벌 등록 ──────────────────
GLOBAL_SKILLS="$HOME/.antigravity/skills"
mkdir -p "$GLOBAL_SKILLS/excalidraw"

if [ -f "$REPO_ROOT/.antigravity/prompts/excalidraw.md" ]; then
  cp "$REPO_ROOT/.antigravity/prompts/excalidraw.md" "$GLOBAL_SKILLS/excalidraw/prompt.md"
  cp "$REPO_ROOT/.antigravity/tasks/excalidraw-diagram.md" "$GLOBAL_SKILLS/excalidraw/task.md"
  ok "Excalidraw 워크플로우 글로벌 등록"
  log "$GLOBAL_SKILLS/excalidraw/"
else
  warn "Excalidraw 워크플로우 파일을 찾을 수 없음"
fi

# ─── 프로젝트 로컬 Skills 확인 ──────────────────────────
SKILLS_DIR="$REPO_ROOT/.antigravity/skills"
if [ -d "$SKILLS_DIR" ]; then
  SKILL_COUNT=$(find "$SKILLS_DIR" -name "*.md" | wc -l | xargs)
  ok "로컬 Skills 디렉토리 (${SKILL_COUNT}개)"
  find "$SKILLS_DIR" -name "*.md" | sort | while read -r f; do
    log "$(basename "$f")"
  done
else
  log "로컬 skills 없음 (선택사항)"
fi

WORKSPACE_FILE="$REPO_ROOT/code-sonar.code-workspace"
if [ ! -f "$WORKSPACE_FILE" ]; then
  cat > "$WORKSPACE_FILE" <<JSON
{
  "folders": [{ "path": "." }],
  "settings": {
    "claudeCode.preferredLocation": "panel",
    "claudeCode.allowDangerouslySkipPermissions": true,
    "ralphLoop.promptFile": ".antigravity/prompts/excalidraw.md",
    "ralphLoop.taskFile": ".antigravity/tasks/excalidraw-diagram.md",
    "ralphLoop.progressFile": "progress.txt",
    "ralphLoop.defaultMode": "Fast",
    "ralphLoop.maxIterations": 10,
    "ralphLoop.enabledBackpressure": []
  }
}
JSON
  ok "Workspace 파일 생성 (Ralph Loop 워크플로우 포함)"
  log "$WORKSPACE_FILE"
else
  # ralphLoop 설정이 없으면 추가
  if ! python3 -c "import json; d=json.load(open('$WORKSPACE_FILE')); exit(0 if 'ralphLoop.promptFile' in d.get('settings',{}) else 1)" 2>/dev/null; then
    python3 -c "
import json
path = '$WORKSPACE_FILE'
with open(path) as f:
    d = json.load(f)
s = d.setdefault('settings', {})
s.setdefault('ralphLoop.promptFile',       '.antigravity/prompts/excalidraw.md')
s.setdefault('ralphLoop.taskFile',         '.antigravity/tasks/excalidraw-diagram.md')
s.setdefault('ralphLoop.progressFile',     'progress.txt')
s.setdefault('ralphLoop.defaultMode',      'Fast')
s.setdefault('ralphLoop.maxIterations',    10)
s.setdefault('ralphLoop.enabledBackpressure', [])
with open(path, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
    ok "Workspace에 Ralph Loop 워크플로우 설정 추가"
  else
    ok "Workspace 파일 확인 (Ralph Loop 이미 등록됨)"
  fi
  log "$WORKSPACE_FILE"
fi

# ─── 완료 ─────────────────────────────────────────────────
echo ""
echo "================================"
ok "설치 완료"
echo ""
echo "다음 단계:"
if [ -n "${AG_BIN:-}" ] && [ -f "${AG_BIN:-/dev/null}" ]; then
  echo "  Antigravity 열기:"
  echo "    $AG_BIN \"$REPO_ROOT\""
else
  echo "  Antigravity 열기:"
  echo "    open -a Antigravity \"$REPO_ROOT\""
fi
echo ""
echo "  Excalidraw 워크플로우:"
echo "    1. \"기존 mermaid 코드에서 스타일 제거하고 관계만 재작성해줘\""
echo "    2. \"diagram.excalidraw를 위 mermaid로 그려줘\""
echo ""
