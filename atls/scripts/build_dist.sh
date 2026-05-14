#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$SCRIPT_DIR"

python3 -m pip install -q build
rm -rf build dist *.egg-info
python3 -m build

echo ""
echo "빌드 완료:"
echo "  ls -la dist"
