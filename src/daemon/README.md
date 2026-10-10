# nasd

OpenNAS-Lite management API (`nasd`) and `nasctl` CLI.

## Development

```bash
cd src/daemon
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

export NASD_DATA_DIR=/tmp/nasd
export NASD_COOKIE_SECURE=false
nasd --host 127.0.0.1 --port 8741
```

## Tests

From repository root:

```bash
cd src/daemon && pip install -e ".[dev]" && pytest ../../tests -q
```

## Production paths

| Path | Purpose |
|------|---------|
| `/var/lib/nasd/config.db` | SQLite configuration |
| `/run/nasd/` | Runtime |
| `127.0.0.1:8741` | HTTP API (Caddy upstream) |

systemd: [packaging/systemd/nasd.service](../../packaging/systemd/nasd.service)
