#!/usr/bin/env bash
# Build web UI (if npm available) and verify staged assets before live-build.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WEB_OUT="${REPO_ROOT}/build/output/web"
FALLBACK="${REPO_ROOT}/build/assets/web-fallback"

build_web() {
	if [ -f "${WEB_OUT}/index.html" ]; then
		echo "Web UI already built at ${WEB_OUT}"
		return 0
	fi
	if command -v npm >/dev/null 2>&1; then
		bash "${REPO_ROOT}/build/scripts/build-web.sh"
		return 0
	fi
	echo "npm not found — using minimal web fallback (re-run with Node/npm for full UI)." >&2
	mkdir -p "${WEB_OUT}"
	cp -a "${FALLBACK}/." "${WEB_OUT}/"
}

main() {
	build_web
	bash "${REPO_ROOT}/build/scripts/stage-includes.sh"
	echo "ISO assets ready."
}

main "$@"
