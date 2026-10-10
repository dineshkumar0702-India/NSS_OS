# Tests

| Phase | Scope |
|-------|--------|
| 2 | ISO build smoke, QEMU boot |
| 3 | `nasd` unit + API integration (pytest) |
| 4 | Web UI e2e (Playwright) |
| 6 | RAID failure matrix, update rollback |

Destructive storage tests must run only in dedicated CI jobs with virtual disks.
