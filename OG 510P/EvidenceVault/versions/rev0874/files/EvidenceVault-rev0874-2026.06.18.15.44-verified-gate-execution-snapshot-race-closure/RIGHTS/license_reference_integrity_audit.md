# License reference integrity audit

This audit is intentionally narrow: it checks whether shipped payload/documentation files point to local `LICENSE`, `COPYING`, or `NOTICE` files that are not present in the canonical archive.

- Status: `license_references_locally_resolved`
- Files examined: **2673**
- References found: **1**
- Local references resolved: **1**
- Local references missing: **0**
- Local references outside archive: **0**

## Resolved reference

| Source | Line | Target | Resolved archive path | Status |
| --- | ---: | --- | --- | --- |
| `sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md` | 1645 | `LICENSE` | `sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE` | `ok` |

Recovery identity and upstream pinning are recorded in `RIGHTS/MCP_SERVERS_LICENSE_RECOVERY_REV0864.json`. This audit checks reference integrity only; it does not infer an archive-wide license.
