#!/usr/bin/env bash
# install.sh — Code-Sonar 원클릭 설치
# Claude Code / Codex / Antigravity 중 감지된 환경에 자동 설치합니다.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$REPO_ROOT/scripts"
RESULTS=()

# ─── 색상 ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
ok()      { echo -e "  ${GREEN}✔${NC} $*"; }
warn()    { echo -e "  ${YELLOW}⚠${NC} $*"; }
fail()    { echo -e "  ${RED}✘${NC} $*"; }
section() { echo -e "\n${BOLD}${CYAN}━━  $*${NC}"; }

run_step() {
  local label="$1"
  local script="$2"
  if bash "$script" 2>&1 | sed 's/^/  /'; then
    RESULTS+=("${GREEN}✔${NC} $label")
  else
    RESULTS+=("${YELLOW}⚠${NC} $label — 일부 단계 실패 (위 출력 확인)")
  fi
}

# ─── 헤더 ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║        Code-Sonar  Install           ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"
echo "  Repo: $REPO_ROOT"

# ─── 환경 감지 ───────────────────────────────────────────────────────────────
HAS_CLAUDE=false; HAS_CODEX=false; HAS_ANTIGRAVITY=false

command -v claude >/dev/null 2>&1 && HAS_CLAUDE=true

if [ -d "${CODEX_HOME:-$HOME/.codex}" ] || command -v codex >/dev/null 2>&1; then
  HAS_CODEX=true
fi

if [ -f "$HOME/.antigravity/antigravity/bin/antigravity" ] || \
   [ -d "/Applications/Antigravity.app" ]; then
  HAS_ANTIGRAVITY=true
fi

section "감지된 환경"
$HAS_CLAUDE      && ok "Claude Code" || echo -e "  · Claude Code  — 미감지 (skip)"
$HAS_CODEX       && ok "Codex"       || echo -e "  · Codex        — 미감지 (skip)"
$HAS_ANTIGRAVITY && ok "Antigravity" || echo -e "  · Antigravity  — 미감지 (skip)"

if ! $HAS_CLAUDE && ! $HAS_CODEX && ! $HAS_ANTIGRAVITY; then
  echo ""
  warn "설치 대상 환경을 찾지 못했습니다."
  echo "  Claude Code : https://claude.ai/code"
  echo "  Codex       : https://openai.com/codex"
  echo "  Antigravity : https://antigravity.dev"
  exit 1
fi

# ─── Claude Code ─────────────────────────────────────────────────────────────
if $HAS_CLAUDE; then
  section "[Claude Code] 플러그인 설치"
  run_step "Claude Code" "$SCRIPTS/install-claude.sh"
fi

# ─── Codex ───────────────────────────────────────────────────────────────────
if $HAS_CODEX; then
  section "[Codex] 스킬 설치"
  run_step "Codex" "$SCRIPTS/install-codex.sh"
fi

# ─── Antigravity ─────────────────────────────────────────────────────────────
if $HAS_ANTIGRAVITY; then
  section "[Antigravity] 설치"
  run_step "Antigravity" "$SCRIPTS/install-antigravity.sh"
fi

# ─── 결과 요약 ───────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━  결과 요약${NC}"
for r in "${RESULTS[@]}"; do
  echo -e "  $r"
done
echo ""
