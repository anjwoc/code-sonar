#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ATLS_PY="$SCRIPT_DIR/atls.py"
ATLS_WRAPPER="$SCRIPT_DIR/bin/atls"

echo "=== atls 설치 ==="

chmod +x "$ATLS_PY"
chmod +x "$ATLS_WRAPPER"
chmod +x "$SCRIPT_DIR/atls"

if command -v python3.11 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.11)"
elif command -v python3.10 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.10)"
elif [ -x /Users/jaecjeong/.asdf/installs/python/3.10.1/bin/python3 ]; then
  PYTHON_BIN="/Users/jaecjeong/.asdf/installs/python/3.10.1/bin/python3"
else
  PYTHON_BIN="$(command -v python3)"
fi

echo "의존성 확인 중..."
"$PYTHON_BIN" -c "import requests" 2>/dev/null || {
  echo "  requests 설치 중..."
  "$PYTHON_BIN" -m pip install requests -q
}
echo "  ✓ 의존성 OK"

echo "editable install 시도 중..."
"$PYTHON_BIN" -m pip install -e "$SCRIPT_DIR" -q && echo "  ✓ editable install 완료" || echo "  editable install은 건너뛰고 wrapper 링크만 설정합니다."

USER_BIN="$HOME/.local/bin"

if [ -w /usr/local/bin ]; then
  ln -sf "$ATLS_WRAPPER" /usr/local/bin/atls
  echo "  ✓ /usr/local/bin/atls 설치 완료"
elif mkdir -p "$USER_BIN" && [ -w "$USER_BIN" ]; then
  ln -sf "$ATLS_WRAPPER" "$USER_BIN/atls"
  echo "  ✓ $USER_BIN/atls 설치 완료"
else
  echo "  /usr/local/bin, $USER_BIN 쓰기 권한 없음."
  echo ""
  echo "다음 중 하나를 사용하세요:"
  echo "  alias atls='$ATLS_WRAPPER'"
  echo "  export PATH=\"$USER_BIN:\$PATH\""
fi

echo ""
echo "기본 점검:"
echo "  atls doctor"
echo "  atls meta"
echo "  atls workflow qa-gemini-harness --no-jira --workspace-root /path/to/adcenter"
