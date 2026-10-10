#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WEB_DIR="${REPO_ROOT}/src/web"
OUT="${REPO_ROOT}/build/output/web"

cd "${WEB_DIR}"
if ! command -v npm >/dev/null 2>&1; then
	echo "npm required to build web UI" >&2
	exit 1
fi
if [ -f package-lock.json ]; then
	npm ci || npm install
else
	npm install
fi
npm run build

rm -rf "${OUT}"
mkdir -p "${OUT}"
cp -a build/* "${OUT}/"
echo "Web UI built to ${OUT}"
