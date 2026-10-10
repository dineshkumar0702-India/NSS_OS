#!/usr/bin/env bash
# Stage files into live-build config/includes.chroot before lb build.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LB_DIR="${REPO_ROOT}/build/live-build"
STAGE="${LB_DIR}/config/includes.chroot"

rm -rf "${STAGE}/etc/calamares" "${STAGE}/usr/lib/calamares/modules" "${STAGE}/usr/share/opennas" "${STAGE}/usr/src/opennas-nasd"
mkdir -p "${STAGE}/etc/calamares" "${STAGE}/usr/lib/calamares/modules" \
	"${STAGE}/usr/share/opennas/profiles" "${STAGE}/usr/share/opennas/nasd" \
	"${STAGE}/usr/share/opennas/packaging/caddy" "${STAGE}/usr/share/opennas/packaging/systemd"

cp -a "${REPO_ROOT}/build/calamares/etc/calamares/." "${STAGE}/etc/calamares/"
cp -a "${REPO_ROOT}/build/calamares/branding" "${STAGE}/etc/calamares/branding"
cp -a "${REPO_ROOT}/build/calamares/modules/opennaspartition" "${STAGE}/usr/lib/calamares/modules/opennaspartition"
cp -a "${REPO_ROOT}/build/calamares/modules/opennasprofile" "${STAGE}/usr/lib/calamares/modules/opennasprofile"
cp -a "${REPO_ROOT}/config/profiles/." "${STAGE}/usr/share/opennas/profiles/"
cp -a "${REPO_ROOT}/config/nasd/config.seed.json" "${STAGE}/usr/share/opennas/nasd/config.seed.json"

# nasd source, packaging, apps, web UI (from prepare-iso-assets.sh)
cp -a "${REPO_ROOT}/src/daemon/." "${STAGE}/usr/src/opennas-nasd/"
rm -rf "${STAGE}/usr/src/opennas-nasd/.venv" "${STAGE}/usr/src/opennas-nasd/"*.egg-info 2>/dev/null || true
cp -a "${REPO_ROOT}/packaging/caddy/opennas.caddy" "${STAGE}/usr/share/opennas/packaging/caddy/"
cp -a "${REPO_ROOT}/packaging/systemd/nasd.service" "${STAGE}/usr/share/opennas/packaging/systemd/"
if [ -d "${REPO_ROOT}/apps" ]; then
	mkdir -p "${STAGE}/usr/share/opennas/apps-staging"
	cp -a "${REPO_ROOT}/apps/." "${STAGE}/usr/share/opennas/apps-staging/"
fi
WEB_OUT="${REPO_ROOT}/build/output/web"
if [ -f "${WEB_OUT}/index.html" ]; then
	mkdir -p "${STAGE}/usr/share/opennas/web-staging"
	cp -a "${WEB_OUT}/." "${STAGE}/usr/share/opennas/web-staging/"
else
	echo "Warning: ${WEB_OUT}/index.html missing — run prepare-iso-assets.sh first." >&2
fi

chmod +x "${STAGE}/usr/lib/calamares/modules/opennaspartition/opennaspartition.py" 2>/dev/null || true
find "${LB_DIR}/config/hooks" -name '*.hook*' -exec chmod +x {} + 2>/dev/null || true

echo "Staged includes into ${STAGE}"
