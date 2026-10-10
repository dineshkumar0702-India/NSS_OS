#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SPEC="${REPO_ROOT}/openapi/openapi.yaml"

LINT_ARGS=(lint "$SPEC")
if [ -f "${REPO_ROOT}/redocly.yaml" ]; then
	LINT_ARGS=(lint --config "${REPO_ROOT}/redocly.yaml" "$SPEC")
fi

if command -v npx >/dev/null 2>&1; then
	npx --yes @redocly/cli@latest "${LINT_ARGS[@]}"
elif command -v docker >/dev/null 2>&1; then
	docker run --rm -v "${REPO_ROOT}:/work" -w /work node:22-bookworm-slim \
		bash -lc "npx --yes @redocly/cli@latest lint --config redocly.yaml openapi/openapi.yaml"
else
	echo "Install Node.js+npx or Docker to lint OpenAPI" >&2
	exit 1
fi
