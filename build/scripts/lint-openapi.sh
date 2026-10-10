#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${REPO_ROOT}"

REDOCLY_CLI_VERSION="${REDOCLY_CLI_VERSION:-1.34.4}"
SPEC="openapi/openapi.yaml"
CONFIG="redocly.yaml"

ARGS=(lint "${SPEC}")
if [ -f "${CONFIG}" ]; then
	ARGS=(lint --config "${CONFIG}" "${SPEC}")
fi

if command -v npx >/dev/null 2>&1; then
	npx --yes "@redocly/cli@${REDOCLY_CLI_VERSION}" "${ARGS[@]}"
elif command -v docker >/dev/null 2>&1; then
	docker run --rm -v "${REPO_ROOT}:/work" -w /work node:22-bookworm-slim \
		bash -lc "npx --yes @redocly/cli@${REDOCLY_CLI_VERSION} lint --config redocly.yaml openapi/openapi.yaml"
else
	echo "Install Node.js+npx or Docker to lint OpenAPI" >&2
	exit 1
fi
