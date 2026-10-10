# Web UI (Phase 4)

SvelteKit **static** management UI (English), served from `/usr/share/opennas/web` via Caddy.

## Development

Start `nasd` on `127.0.0.1:8741`, then:

```bash
cd src/web
npm install
npm run dev
```

Vite proxies `/api` to nasd.

## Production build

```bash
bash build/scripts/build-web.sh
# output: build/output/web/
```

## Pages

| Route | Feature |
|-------|---------|
| `/setup` | First-boot wizard |
| `/login` | Session auth |
| `/dashboard` | Status, capabilities, services |
| `/storage` | Disks, pools, dry-run pool create |
| `/shares` | SMB share list/create |
| `/users` | Local users |
| `/files` | Directory browser (`/api/v1/files`) |
| `/apps` | App Center shell (Phase 5) |

Specification: [docs/architecture/tech-stack.md](../../docs/architecture/tech-stack.md).
