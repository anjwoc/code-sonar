#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code CLI was not found."
  echo "Install Claude Code, then run: claude plugin install \"$REPO_ROOT\""
  exit 0
fi

if claude plugin install "$REPO_ROOT"; then
  echo "Installed Code-Sonar Claude plugin from $REPO_ROOT"
else
  echo "Claude plugin install failed. Verify Claude Code plugin support and run manually:"
  echo "  claude plugin install \"$REPO_ROOT\""
  exit 1
fi
