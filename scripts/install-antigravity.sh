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
step 1 4 "Excalidraw MCP 확인"
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
step 2 4 "프로젝트 MCP 설정 (.claude/settings.json)"
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
step 3 4 "Antigravity 글로벌 워크플로우 생성 (절대경로 주입)"
# ═══════════════════════════════════════════════════════
# 글로벌 워크플로우는 어느 프로젝트에서 열어도 실행되므로,
# 상대경로가 아닌 절대경로를 직접 파일에 구워 넣습니다.

AG_GLOBAL_WORKFLOWS="$HOME/.gemini/antigravity/global_workflows"
mkdir -p "$AG_GLOBAL_WORKFLOWS"

# .env에서 경로 값 추출
SONAR_ENV="$REPO_ROOT/.env"
SONAR_TARGET_DIR=""
SONAR_OUTPUT_DIR=""
SONAR_SYSTEM_ROOT=""
if [ -f "$SONAR_ENV" ]; then
  SONAR_TARGET_DIR=$(grep -E "^SONAR_TARGET_DIR=" "$SONAR_ENV" | cut -d'=' -f2- | tr -d '[:space:]"')
  SONAR_OUTPUT_DIR=$(grep -E "^SONAR_OUTPUT_DIR=" "$SONAR_ENV" | cut -d'=' -f2- | tr -d '[:space:]"')
  SONAR_SYSTEM_ROOT=$(grep -E "^SONAR_SYSTEM_ROOT=" "$SONAR_ENV" | cut -d'=' -f2- | tr -d '[:space:]"')
fi

if [ -z "$SONAR_TARGET_DIR" ] || [ -z "$SONAR_OUTPUT_DIR" ]; then
  warn ".env에서 SONAR_TARGET_DIR / SONAR_OUTPUT_DIR를 읽지 못했습니다."
  warn "설치 후 .env를 채우고 install-antigravity.sh를 다시 실행하세요."
else
  log "SONAR_TARGET_DIR  = $SONAR_TARGET_DIR"
  log "SONAR_OUTPUT_DIR  = $SONAR_OUTPUT_DIR"
fi

# ─── 1. 메인 분석 워크플로우: code-sonar ────────────────────
cat > "$AG_GLOBAL_WORKFLOWS/code-sonar.md" <<WORKFLOW
---
description: "Code-Sonar: 프로젝트 구조·비즈니스 플로우·데이터플로우·API 분석 및 문서 자동 생성"
---

# Code-Sonar 분석 에이전트

## 절대 경로 (이 파일 생성 시점에 고정됨)

| 항목 | 경로 |
|:---|:---|
| Plugin root | \`$REPO_ROOT\` |
| 분석 규칙 (SONAR.md) | \`$REPO_ROOT/sonar/SONAR.md\` |
| 실행 설정 (.env) | \`$REPO_ROOT/.env\` |
| 분석 대상 소스 | \`$SONAR_TARGET_DIR\` |
| 산출물 출력 경로 | \`$SONAR_OUTPUT_DIR\` |

## 시작 전 필수 작업 (반드시 이 순서를 따를 것)

**Step 1 — 규칙 파일 읽기**
다음 파일들을 순서대로 읽고 내용을 완전히 숙지한다:
1. \`$REPO_ROOT/sonar/SONAR.md\`
2. \`$REPO_ROOT/sonar/config/sonar-config.md\`
3. \`$REPO_ROOT/sonar/skills/analyze-project/SKILL.md\`
4. \`$REPO_ROOT/.env\`

**Step 2 — 경로 확인**
- 분석 대상: \`$SONAR_TARGET_DIR\`
- 산출물 저장: \`$SONAR_OUTPUT_DIR\`
- 이 경로 외 다른 곳에 파일을 생성하지 않는다.

**Step 3 — 분석 실행**
\`$REPO_ROOT/sonar/skills/analyze-project/SKILL.md\`의 STEP 0~4를 순서대로 실행한다.

**Step 4 — 비즈니스 레이어 생성**
\`sonar/agents/business-workflow-analyst.md\`를 실행하여 \`$SONAR_OUTPUT_DIR/_business/\`에 문서를 생성한다.

**Step 5 — Evidence 검증**
\`sonar/agents/evidence-auditor.md\`와 \`sonar/agents/qa-reviewer.md\`로 산출물을 검증한다.

## 출력 위치

모든 파일은 반드시 \`$SONAR_OUTPUT_DIR\` 하위에만 생성한다.
다른 경로(바탕화면, 현재 작업 폴더, adtech 등)에 절대 생성하지 않는다.

## 핵심 원칙

- 코드에서 확인한 사실만 쓴다. 추측이면 \`> ⚠️ 확인 필요\`로 표시한다.
- 산출물 언어: 한국어 (클래스명·메서드명·API path는 원문 유지)
- Mermaid는 \`flowchart LR\`과 quote된 라벨만 사용한다.
WORKFLOW

ok "메인 분석 워크플로우 등록 완료: code-sonar"
log "$AG_GLOBAL_WORKFLOWS/code-sonar.md"
log "(Antigravity에서 '/' 입력 후 code-sonar 검색)"

# ─── 2. Deep Research 워크플로우: code-sonar-deep ───────────
cat > "$AG_GLOBAL_WORKFLOWS/code-sonar-deep.md" <<WORKFLOW
---
description: "Code-Sonar: Deep Research — 단일 프로젝트 심층 분석 (환경 매트릭스, 인테그레이션 플로우, 비즈니스 상태 머신, 질문 기반 답변)"
---

# Code-Sonar Deep Research 에이전트

## 절대 경로 (이 파일 생성 시점에 고정됨)

| 항목 | 경로 |
|:---|:---|
| Plugin root | \`$REPO_ROOT\` |
| Deep Research 규칙 | \`$REPO_ROOT/sonar/skills/deep-research/SKILL.md\` |
| 실행 설정 (.env) | \`$REPO_ROOT/.env\` |
| 기본 분석 대상 | \`$SONAR_TARGET_DIR\` |
| 산출물 출력 경로 | \`$SONAR_OUTPUT_DIR\` |

## 시작 전 필수 작업

**Step 1 — 규칙 파일 읽기**
1. \`$REPO_ROOT/sonar/SONAR.md\`
2. \`$REPO_ROOT/sonar/skills/deep-research/SKILL.md\`
3. \`$REPO_ROOT/.env\`

**Step 2 — 분석 대상 결정**
- 사용자가 경로를 지정했으면 그 경로를 사용한다.
- 없으면 \`$SONAR_TARGET_DIR\` 의 단일 프로젝트를 사용한다.
- \`.env\`의 \`SONAR_DEEP_TARGET\`이 있으면 그 값을 우선한다.

**Step 3 — 에이전트 병렬 실행**
다음 에이전트를 동시에 스폰한다:
- \`$REPO_ROOT/sonar/agents/env-matrix-analyst.md\`
- \`$REPO_ROOT/sonar/agents/integration-flow-analyst.md\`
- \`$REPO_ROOT/sonar/agents/business-workflow-analyst.md\` (deep mode)
- \`$REPO_ROOT/sonar/agents/analyst-backend.md\` (deep mode)

**Step 4 — 질문 답변 (질문이 있는 경우)**
\`SONAR_DEEP_QUESTIONS\` 파일을 읽어 각 질문에 코드 근거 기반 답변을 생성한다.

## 출력 위치

\`$SONAR_OUTPUT_DIR/{프로젝트명}/deep-research/\` 하위에만 생성한다.
WORKFLOW

ok "Deep Research 워크플로우 등록 완료: code-sonar-deep"
log "$AG_GLOBAL_WORKFLOWS/code-sonar-deep.md"
log "(Antigravity에서 '/' 입력 후 code-sonar-deep 검색)"

# ─── 3. Excalidraw 워크플로우: code-sonar-excalidraw ────────
if [ -f "$REPO_ROOT/.antigravity/prompts/excalidraw.md" ]; then
  cat > "$AG_GLOBAL_WORKFLOWS/code-sonar-excalidraw.md" <<EOF
---
description: "Code-Sonar: Excalidraw 다이어그램 생성 (Mermaid → .excalidraw 변환)"
---

EOF
  cat "$REPO_ROOT/.antigravity/prompts/excalidraw.md" >> "$AG_GLOBAL_WORKFLOWS/code-sonar-excalidraw.md"
  if [ -f "$REPO_ROOT/.antigravity/skills/excalidraw-guide.md" ]; then
    echo -e "\n\n---\n" >> "$AG_GLOBAL_WORKFLOWS/code-sonar-excalidraw.md"
    cat "$REPO_ROOT/.antigravity/skills/excalidraw-guide.md" >> "$AG_GLOBAL_WORKFLOWS/code-sonar-excalidraw.md"
  fi
  ok "Excalidraw 워크플로우 등록 완료: code-sonar-excalidraw"
  log "$AG_GLOBAL_WORKFLOWS/code-sonar-excalidraw.md"
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

# ═══════════════════════════════════════════════════════
step 4 4 "Sonar Deep Research Workspace 설정"
# ═══════════════════════════════════════════════════════

DEEP_WORKSPACE="$REPO_ROOT/code-sonar.code-workspace"
python3 -c "
import json
path = '$DEEP_WORKSPACE'
try:
    with open(path) as f:
        d = json.load(f)
    s = d.setdefault('settings', {})
    changed = False
    if 'sonarDeep.promptFile' not in s:
        s['sonarDeep.promptFile'] = '.antigravity/prompts/sonar-deep.md'
        changed = True
    if 'sonarDeep.taskFile' not in s:
        s['sonarDeep.taskFile'] = '.antigravity/tasks/sonar-deep-research.md'
        changed = True
    if changed:
        with open(path, 'w') as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print('updated')
    else:
        print('already set')
except Exception as e:
    print(f'skip: {e}')
" | while IFS= read -r result; do
  case "$result" in
    updated)     ok "Workspace에 Sonar Deep Research 설정 추가" ;;
    "already set") ok "Workspace 파일 확인 (Deep Research 이미 등록됨)" ;;
    *)           log "$result" ;;
  esac
done
log "$DEEP_WORKSPACE"

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
echo "  등록된 워크플로우 (Antigravity에서 '/' 입력 후 선택):"
echo "    code-sonar            ← 프로젝트 전체 분석"
echo "    code-sonar-deep       ← 단일 프로젝트 심층 분석"
echo "    code-sonar-excalidraw ← Mermaid → Excalidraw 변환"
echo ""
