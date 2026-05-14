#!/usr/bin/env bash
# install-gemini.sh — Gemini CLI용 Code-Sonar 설치 스크립트
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEMINI_EXT_DIR="$HOME/.gemini/extensions/code-sonar"
GEMINI_ENABLEMENT="$HOME/.gemini/extensions/extension-enablement.json"

# ─── 색상 & 유틸 ──────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
GRAY='\033[0;90m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✔${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
fail() { echo -e "${RED}✘${NC} $*"; }
log()  { echo -e "${GRAY}  → $*${NC}"; }
step() { echo -e "\n${BOLD}[$1/$2]${NC} $3"; }

echo ""
echo -e "${BOLD}Code-Sonar × Gemini CLI 설치${NC}"
echo "================================"
echo "Repo: $REPO_ROOT"
echo ""

# ─── Gemini CLI 확인 ────────────────────────────────────
GEMINI_BIN=""
if command -v gemini >/dev/null 2>&1; then
  GEMINI_BIN="$(command -v gemini)"
  GEMINI_VER=$(gemini --version 2>/dev/null || echo "unknown")
  ok "Gemini CLI: $GEMINI_VER ($GEMINI_BIN)"
else
  fail "Gemini CLI를 찾을 수 없습니다."
  echo "  설치: npm install -g @google/generative-ai-cli"
  echo "  또는: https://github.com/google-gemini/gemini-cli"
  exit 1
fi

# ═══════════════════════════════════════════════════════
step 1 3 "Extension 디렉토리 구성"
# ═══════════════════════════════════════════════════════

mkdir -p "$GEMINI_EXT_DIR/commands/sonar"

# ─── gemini-extension.json ─────────────────────────────
cat > "$GEMINI_EXT_DIR/gemini-extension.json" <<JSON
{
  "name": "code-sonar",
  "version": "1.0.0",
  "contextFileName": "sonar/SONAR.md"
}
JSON
ok "gemini-extension.json 생성"
log "$GEMINI_EXT_DIR/gemini-extension.json"

# ─── sonar/ 디렉토리 동기화 ────────────────────────────
rsync -a --delete \
  "$REPO_ROOT/sonar/" \
  "$GEMINI_EXT_DIR/sonar/" \
  --exclude='.git'
SKILL_COUNT=$(find "$GEMINI_EXT_DIR/sonar" -name "*.md" | wc -l | xargs)
ok "sonar/ 동기화 완료 (${SKILL_COUNT}개 파일)"
log "$GEMINI_EXT_DIR/sonar/"

# ─── .env 경로 읽기 (명령어에 절대경로 주입) ────────────
SONAR_ENV="$REPO_ROOT/.env"
SONAR_TARGET_DIR=""
SONAR_OUTPUT_DIR=""
if [ -f "$SONAR_ENV" ]; then
  SONAR_TARGET_DIR=$(grep -E "^SONAR_TARGET_DIR=" "$SONAR_ENV" | cut -d'=' -f2- | tr -d '[:space:]"')
  SONAR_OUTPUT_DIR=$(grep -E "^SONAR_OUTPUT_DIR=" "$SONAR_ENV" | cut -d'=' -f2- | tr -d '[:space:]"')
fi

# ═══════════════════════════════════════════════════════
step 2 3 "슬래시 커맨드 생성"
# ═══════════════════════════════════════════════════════

# ─── /sonar:start ──────────────────────────────────────
cat > "$GEMINI_EXT_DIR/commands/sonar/start.toml" <<TOML
description = "Code-Sonar 프로젝트 분석 시작. 구조·API·비즈니스 플로우·데이터플로우 문서를 자동 생성한다."
prompt = """
## Code-Sonar 분석 에이전트

### 절대 경로 (설치 시 고정됨)

| 항목 | 경로 |
|:---|:---|
| Plugin root | \`$REPO_ROOT\` |
| 분석 규칙 | \`$REPO_ROOT/sonar/SONAR.md\` |
| 실행 설정 | \`$REPO_ROOT/.env\` |
| 분석 대상 | \`$SONAR_TARGET_DIR\` |
| 산출물 출력 | \`$SONAR_OUTPUT_DIR\` |

### 실행 순서 (반드시 이 순서)

1. \`$REPO_ROOT/sonar/SONAR.md\` 를 읽는다.
2. \`$REPO_ROOT/sonar/config/sonar-config.md\` 를 읽는다.
3. \`$REPO_ROOT/sonar/skills/analyze-project/SKILL.md\` 를 읽는다.
4. \`$REPO_ROOT/.env\` 를 읽어 SONAR_TARGET_DIR, SONAR_OUTPUT_DIR 을 확인한다.
5. SKILL.md에 명시된 STEP 0~4를 순서대로 실행한다.
6. 분석 완료 후 \`$REPO_ROOT/sonar/agents/business-workflow-analyst.md\` 를 실행한다.
7. \`$REPO_ROOT/sonar/agents/evidence-auditor.md\` 와 \`$REPO_ROOT/sonar/agents/qa-reviewer.md\` 로 검증한다.

### 출력 위치

모든 파일은 반드시 \`$SONAR_OUTPUT_DIR\` 하위에만 생성한다.

### 핵심 원칙

- 코드에서 확인한 사실만 쓴다. 추측이면 \`> ⚠️ 확인 필요\` 로 표시한다.
- 산출물 언어: 한국어 (클래스명·메서드명·API path는 원문 유지)

### 사용자 입력

{{args}}
"""
TOML
ok "/sonar:start 생성"

# ─── /sonar:deep ───────────────────────────────────────
cat > "$GEMINI_EXT_DIR/commands/sonar/deep.toml" <<TOML
description = "Code-Sonar Deep Research — 단일 프로젝트 심층 분석 (환경 매트릭스, 인테그레이션 플로우, 비즈니스 상태 머신, 질문 기반 답변)"
prompt = """
## Code-Sonar Deep Research 에이전트

### 절대 경로 (설치 시 고정됨)

| 항목 | 경로 |
|:---|:---|
| Plugin root | \`$REPO_ROOT\` |
| Deep Research 규칙 | \`$REPO_ROOT/sonar/skills/deep-research/SKILL.md\` |
| 실행 설정 | \`$REPO_ROOT/.env\` |
| 기본 분석 대상 | \`$SONAR_TARGET_DIR\` |
| 산출물 출력 | \`$SONAR_OUTPUT_DIR\` |

### 실행 순서

1. \`$REPO_ROOT/sonar/SONAR.md\` 를 읽는다.
2. \`$REPO_ROOT/sonar/skills/deep-research/SKILL.md\` 를 읽는다.
3. \`$REPO_ROOT/.env\` 를 읽어 SONAR_DEEP_TARGET, SONAR_DEEP_QUESTIONS, SONAR_DEEP_ENVS 를 확인한다.
4. args에 프로젝트 경로가 있으면 그 경로를 타겟으로 사용한다.
5. SONAR_CROSS_REPO_SEARCH=true 이면 \`$REPO_ROOT/sonar/agents/cross-repo-tracer.md\` 로 GitHub MCP 탐색을 실행한다.
6. 다음 에이전트를 동시에 실행한다:
   - \`$REPO_ROOT/sonar/agents/env-matrix-analyst.md\`
   - \`$REPO_ROOT/sonar/agents/integration-flow-analyst.md\`
   - \`$REPO_ROOT/sonar/agents/business-workflow-analyst.md\` (deep mode)
   - \`$REPO_ROOT/sonar/agents/analyst-backend.md\` (deep mode)
7. SONAR_DEEP_QUESTIONS 파일이 있으면 각 질문에 코드 근거 기반 답변을 생성한다.
8. \`$SONAR_OUTPUT_DIR/{프로젝트명}/deep-research/DEEP-RESEARCH.md\` 를 생성한다.

### 사용자 입력

사용자가 \`/sonar:deep {프로젝트경로}\` 형태로 입력하면 그 경로를 분석 대상으로 사용한다.

{{args}}
"""
TOML
ok "/sonar:deep 생성"

# ─── /sonar:multi-scan ─────────────────────────────────
cat > "$GEMINI_EXT_DIR/commands/sonar/multi-scan.toml" <<TOML
description = "타겟 디렉토리 하위의 모든 프로젝트를 자동 탐색하고 전체 분석을 순차 실행한다."
prompt = """
## Code-Sonar Multi-Scan 에이전트

### 절대 경로

| 항목 | 경로 |
|:---|:---|
| Plugin root | \`$REPO_ROOT\` |
| 분석 규칙 | \`$REPO_ROOT/sonar/SONAR.md\` |
| 실행 설정 | \`$REPO_ROOT/.env\` |
| 기본 타겟 | \`$SONAR_TARGET_DIR\` |
| 산출물 출력 | \`$SONAR_OUTPUT_DIR\` |

### 실행 순서

1. \`$REPO_ROOT/sonar/SONAR.md\` 를 읽는다.
2. \`$REPO_ROOT/sonar/config/sonar-config.md\` 를 읽는다.
3. \`$REPO_ROOT/sonar/skills/analyze-project/SKILL.md\` 를 읽는다.
4. \`$REPO_ROOT/.env\` 를 읽어 SONAR_TARGET_DIR 을 확인한다.
5. args에 경로가 있으면 그 경로를, 없으면 SONAR_TARGET_DIR 을 타겟으로 사용한다.
6. 타겟 하위 프로젝트를 자동 탐색하고 목록을 사용자에게 보여준다.
7. 확인 후 각 프로젝트를 순차적으로 분석한다.

### 사용자 입력

{{args}}
"""
TOML
ok "/sonar:multi-scan 생성"

# ─── /sonar:graph ──────────────────────────────────────
cat > "$GEMINI_EXT_DIR/commands/sonar/graph.toml" <<TOML
description = "산출물에서 전체 시스템 지식그래프(Mermaid)를 생성한다."
prompt = """
## Code-Sonar Graph 에이전트

### 절대 경로

| 항목 | 경로 |
|:---|:---|
| Plugin root | \`$REPO_ROOT\` |
| Graph 규칙 | \`$REPO_ROOT/sonar/skills/build-graph/SKILL.md\` |
| 산출물 위치 | \`$SONAR_OUTPUT_DIR\` |

### 실행 순서

1. \`$REPO_ROOT/sonar/SONAR.md\` 를 읽는다.
2. \`$REPO_ROOT/sonar/skills/build-graph/SKILL.md\` 를 읽는다.
3. \`$SONAR_OUTPUT_DIR\` 하위 분석 문서를 읽어 지식그래프를 생성한다.
4. \`$SONAR_OUTPUT_DIR/Index.md\` 에 통합 flowchart LR 그래프를 기록한다.

### 사용자 입력

{{args}}
"""
TOML
ok "/sonar:graph 생성"

# ─── /sonar:wiki ───────────────────────────────────────
cat > "$GEMINI_EXT_DIR/commands/sonar/wiki.toml" <<TOML
description = "산출물을 Confluence Wiki에 업로드한다. atls CLI 우선, MCP 폴백."
prompt = """
## Code-Sonar Wiki 업로드 에이전트

### 절대 경로

| 항목 | 경로 |
|:---|:---|
| Plugin root | \`$REPO_ROOT\` |
| Wiki 규칙 | \`$REPO_ROOT/sonar/skills/publish-wiki/SKILL.md\` |
| Atlassian 어댑터 | \`$REPO_ROOT/sonar/agents/atlassian-adapter.md\` |
| 산출물 위치 | \`$SONAR_OUTPUT_DIR\` |

### 실행 순서

1. \`$REPO_ROOT/sonar/skills/publish-wiki/SKILL.md\` 를 읽는다.
2. \`$REPO_ROOT/sonar/agents/atlassian-adapter.md\` 를 읽어 Atlassian 연결 방법을 확인한다.
3. atls CLI 연결을 확인한다: \`atls ping wiki --timeout 3\`
4. atls 성공 시 atls로, 실패 시 Confluence MCP로 업로드한다.
5. \`$SONAR_OUTPUT_DIR\` 하위 마크다운 파일을 Confluence에 발행한다.

### 사용자 입력

args에 Confluence Space Key가 있으면 그 스페이스로 업로드한다.

{{args}}
"""
TOML
ok "/sonar:wiki 생성"

log "커맨드 파일 위치: $GEMINI_EXT_DIR/commands/sonar/"

# ═══════════════════════════════════════════════════════
step 3 3 "Extension 활성화"
# ═══════════════════════════════════════════════════════

mkdir -p "$(dirname "$GEMINI_ENABLEMENT")"

# extension-enablement.json 업데이트 (code-sonar 항목 추가/유지)
if [ -f "$GEMINI_ENABLEMENT" ]; then
  python3 -c "
import json
path = '$GEMINI_ENABLEMENT'
with open(path) as f:
    d = json.load(f)
entry = d.setdefault('code-sonar', {})
entry.setdefault('overrides', [])
# 현재 사용자 홈 디렉토리를 override로 추가
home_glob = '$HOME/*'
if home_glob not in entry['overrides']:
    entry['overrides'].append(home_glob)
with open(path, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('updated')
" && ok "Extension 활성화 (code-sonar 항목 유지)" || warn "extension-enablement.json 업데이트 실패"
else
  cat > "$GEMINI_ENABLEMENT" <<JSON
{
  "code-sonar": {
    "overrides": [
      "$HOME/*"
    ]
  }
}
JSON
  ok "Extension 활성화 (신규 생성)"
fi
log "$GEMINI_ENABLEMENT"

# ─── 완료 ─────────────────────────────────────────────────
echo ""
echo "================================"
ok "Gemini CLI 설치 완료"
echo ""
echo "등록된 커맨드 (gemini에서 / 입력 후 선택):"
echo "  /sonar:start      ← 프로젝트 전체 분석"
echo "  /sonar:deep       ← 단일 프로젝트 심층 분석"
echo "  /sonar:multi-scan ← 다중 프로젝트 전체 분석"
echo "  /sonar:graph      ← 지식그래프 생성"
echo "  /sonar:wiki       ← Confluence 발행"
echo ""
echo "Extension 위치: $GEMINI_EXT_DIR"
echo ""
