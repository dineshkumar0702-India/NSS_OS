# API design

The management API is the **single integration surface** for the web UI, `nasctl`, automation, and future mobile clients.

## Conventions

| Topic | Rule |
|-------|------|
| Base path | `/api/v1` |
| Format | JSON (`application/json`); file uploads `multipart/form-data` |
| Versioning | URL prefix; breaking changes bump to `/api/v2` |
| IDs | UUID v4 for resources; pools/volumes also expose stable `name` slug |
| Timestamps | ISO 8601 UTC with `Z` suffix |
| Pagination | `?limit=` (default 50, max 200), `?cursor=` opaque cursor |
| Sorting | `?sort=field` prefix `-` for desc where supported |
| Errors | RFC 7807–style JSON body (see below) |
| Idempotency | `Idempotency-Key` header on POST that create resources |

## Authentication and authorization

### Session (browser)

1. `POST /api/v1/auth/login` with username/password → sets `HttpOnly`, `Secure`, `SameSite=Strict` session cookie.
2. Session stored server-side (SQLite) with TTL and rotation on privilege change.
3. `POST /api/v1/auth/logout` invalidates session.
4. `GET /api/v1/auth/me` returns user, roles, capabilities.

### API token (scripting)

1. Admin creates token: `POST /api/v1/auth/tokens` → bearer token (shown once).
2. Clients send `Authorization: Bearer <token>`.
3. Tokens scoped: `read-only`, `operator`, `admin`.

### Local CLI

`nasctl` uses Unix socket `unix:///run/nasd/nas.sock` with peer credential check (root or `nas-admin` group) **or** bearer token in `~/.config/nasctl/credentials`.

### RBAC roles

| Role | Scope |
|------|--------|
| `viewer` | Read metrics, shares list |
| `operator` | Shares, users (non-admin), backups |
| `admin` | Storage, network, security, updates |
| `owner` | First admin; break-glass; token creation |

Destructive storage operations require role `admin` **and** re-auth or 2FA step-up when 2FA enabled.

## Error envelope

```json
{
  "type": "https://opennas.local/errors/storage/pool-busy",
  "title": "Pool operation in progress",
  "status": 409,
  "detail": "Pool 'tank' has running job scrub-7f2a.",
  "instance": "/api/v1/storage/pools/tank",
  "code": "POOL_BUSY",
  "confirm_token": null
}
```

Common `code` values: `VALIDATION_ERROR`, `NOT_FOUND`, `CAPABILITY_DENIED`, `CONFIRMATION_REQUIRED`, `POOL_BUSY`, `AUTH_FAILED`, `RATE_LIMITED`.

## Destructive operation flow

1. `POST /api/v1/storage/pools` with `"dry_run": true` → returns `plan` object + warnings.
2. Response includes `confirm_token` (short TTL, single use).
3. `POST /api/v1/storage/pools` with `"confirm_token": "..."` executes job.
4. Job ID returned: `GET /api/v1/jobs/{id}` and WebSocket stream.

Same pattern for: volume delete, RAID reshape, user wipe, factory reset.

## WebSocket

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/ws` | Authenticated (cookie or `?token=` one-time) |

Message envelope:

```json
{
  "type": "job.progress",
  "payload": {
    "job_id": "uuid",
    "percent": 42,
    "message": "balancing chunk 3/10"
  }
}
```

Event types: `job.progress`, `job.completed`, `job.failed`, `alert.new`, `metrics.tick` (optional, dashboard only when subscribed).

## Resource map (v1)

### System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/system/status` | Health, version, uptime |
| GET | `/system/capabilities` | virt, zfs, docker, ai, profiles |
| GET | `/system/metrics` | Point-in-time metrics |
| POST | `/system/setup` | First-boot wizard (locked after complete) |
| POST | `/system/reboot` | Requires confirm |
| POST | `/system/shutdown` | Requires confirm |

### Storage

| Method | Path | Description |
|--------|------|-------------|
| GET | `/storage/disks` | Block devices + SMART summary |
| GET | `/storage/pools` | List pools |
| POST | `/storage/pools` | Create (dry-run or confirm) |
| GET | `/storage/pools/{id}` | Detail |
| PATCH | `/storage/pools/{id}` | Extend, label |
| DELETE | `/storage/pools/{id}` | Destroy (confirm) |
| GET | `/storage/pools/{id}/volumes` | List volumes |
| POST | `/storage/pools/{id}/volumes` | Create volume |
| POST | `/storage/scrub` | Schedule/trigger scrub |
| GET | `/storage/snapshots` | List snapshots |
| POST | `/storage/snapshots` | Create |
| POST | `/storage/snapshots/{id}/restore` | Restore (confirm) |

### Shares and files

| Method | Path | Description |
|--------|------|-------------|
| GET | `/shares` | SMB/NFS/WebDAV shares |
| POST | `/shares` | Create share |
| PATCH | `/shares/{id}` | ACL, quotas |
| DELETE | `/shares/{id}` | Remove |
| GET | `/files` | Web file manager listing |
| POST | `/files/upload` | Upload |
| POST | `/files/shares` | Expiring link |

### Users and security

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users` | Local users |
| POST | `/users` | Create |
| PATCH | `/users/{id}` | Update |
| DELETE | `/users/{id}` | Delete |
| GET | `/security/firewall` | Ruleset |
| PUT | `/security/firewall` | Apply rules (dry-run optional) |
| GET | `/security/audit` | Audit log query |

### Network

| Method | Path | Description |
|--------|------|-------------|
| GET | `/network/interfaces` | |
| PATCH | `/network/interfaces/{name}` | static/DHCP, VLAN |
| GET | `/network/certificates` | |
| POST | `/network/certificates/acme` | LE order |

### Apps and VMs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/apps/catalog` | Template list |
| POST | `/apps/instances` | Install |
| GET | `/apps/instances` | |
| POST | `/apps/instances/{id}/action` | start/stop/restart/update |
| GET | `/vms` | libvirt domains |
| POST | `/vms` | Create |

### Jobs and notifications

| Method | Path | Description |
|--------|------|-------------|
| GET | `/jobs` | List |
| GET | `/jobs/{id}` | Detail + log tail |
| GET | `/notifications/channels` | |
| PUT | `/notifications/channels` | |

### Updates

| Method | Path | Description |
|--------|------|-------------|
| GET | `/updates/status` | |
| POST | `/updates/check` | |
| POST | `/updates/apply` | Snapshot + apt upgrade (confirm) |
| POST | `/updates/rollback` | Boot previous snapshot |

## OpenAPI artifact

Canonical spec: [openapi/openapi.yaml](../../openapi/openapi.yaml) (Phase 1 stub with core paths; expanded in Phase 3).

## Rate limiting

| Client | Limit |
|--------|-------|
| Session | 300 req/min per IP |
| Login | 10/min per IP + fail2ban |
| Token | 600 req/min per token |

## Acceptance criteria (API)

1. All mutating endpoints documented with request/response schemas.
2. OpenAPI validates in CI (`spectral` or `openapi-cli`).
3. Integration tests cover auth, dry-run storage, and job lifecycle.
4. No endpoint returns stack traces in production (`detail` sanitized).
