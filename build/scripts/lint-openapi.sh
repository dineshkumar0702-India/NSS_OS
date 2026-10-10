#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SPEC="${REPO_ROOT}/openapi/openapi.yaml"

if command -v npx >/dev/null 2>&1; then
	npx --yes @redocly/cli@latest lint "$SPEC"
elif command -v docker >/dev/null 2>&1; then
	docker run --rm -v "${REPO_ROOT}:/work" -w /work node:20-bookworm-slim \
		bash -lc "npx --yes @redocly/cli@latest lint openapi/openapi.yaml"
else
	echo "Install Node.js+npx or Docker to lint OpenAPI" >&2
	exit 1
fi
