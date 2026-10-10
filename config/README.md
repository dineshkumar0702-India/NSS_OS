# Configuration defaults

| File | Role |
|------|------|
| [profiles/minimal.yaml](profiles/minimal.yaml) | 2 GB+ RAM profile |
| [profiles/standard.yaml](profiles/standard.yaml) | 4 GB+ RAM, Docker |
| [profiles/full.yaml](profiles/full.yaml) | 8 GB+, ZFS/VM packages offered |
| [nasd/config.seed.json](nasd/config.seed.json) | Initial `nasd` DB seed (Phase 3 consumes) |

Staged into the ISO by `build/scripts/stage-includes.sh` → `/usr/share/opennas/`.
