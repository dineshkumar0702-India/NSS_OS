# Phase 1 summary — Architecture

## What was done

1. **Repository layout** — Directories for `build/`, `config/`, `src/{daemon,cli,web}`, `packaging/`, `apps/`, `tests/`, `openapi/`, and `docs/`.
2. **Assumptions** — [ASSUMPTIONS.md](ASSUMPTIONS.md) records defaults (Debian 12, Calamares, FastAPI, SvelteKit, Caddy, Docker, Btrfs default, GPL-3.0).
3. **Block diagram** — Physical boot chain, logical layers, management flows, network surfaces ([block-diagram.md](architecture/block-diagram.md)).
4. **Module list** — Checklist A–H mapped to components and implementation phases ([modules.md](architecture/modules.md)).
5. **Tech stack** — Choices, alternatives, performance tactics, license hotspots ([tech-stack.md](architecture/tech-stack.md)).
6. **API design** — REST conventions, auth, errors, destructive confirm flow, WebSocket events ([api-design.md](architecture/api-design.md)).
7. **Security model** — Assets, threats, firewall defaults, secrets, audit ([security-model.md](architecture/security-model.md)).
8. **Data model** — SQLite schema, ER diagram, config rendering ([data-model.md](architecture/data-model.md)).
9. **OpenAPI stub** — [openapi/openapi.yaml](../openapi/openapi.yaml) with core paths for CI validation in later phases.

No ISO, installer, daemon, or UI code was implemented in Phase 1.

## How to review / test Phase 1

Phase 1 is documentation-only. Suggested review steps:

1. Read [ASSUMPTIONS.md](ASSUMPTIONS.md) and flag anything to change before build work.
2. Walk [modules.md](architecture/modules.md) against your priority list (must-have for v1 vs later).
3. Validate API ergonomics in [api-design.md](architecture/api-design.md) and the OpenAPI stub.
4. Confirm security defaults in [security-model.md](architecture/security-model.md) match your threat model (especially WAN firewall and SSH).
5. Optional: install an OpenAPI linter locally and run against `openapi/openapi.yaml` (wired in Phase 2 CI).

```bash
# Example when Node tooling is added in Phase 2
# npx @redocly/cli lint openapi/openapi.yaml
```

## What comes next (Phase 2 — do not start until you say "continue")

1. Complete **debian-live** configuration under `build/live-build/`.
2. Package lists, hooks, and ISO size budget (≤ 1.5 GB).
3. **Calamares** branding and partitioning module skeleton.
4. **GRUB** BIOS + UEFI, shim where needed.
5. **CI script** to produce ISO artifact and **QEMU** smoke-test instructions.
6. Initial `config/` seeds for hardware profiles.

Reply **`continue`** when you want Phase 2 started.
