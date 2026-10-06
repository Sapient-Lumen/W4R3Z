# Time-travel snapshots as leases (Fossil/"previous versions" lesson)

Snapshots are a core ergonomic tool for:
- debugging regressions (“what changed yesterday?”)
- recovering user files (“restore previous version”)
- incident response (“what executed before the compromise?”)

But snapshots are also a common **security footgun** when old data remains readable after permissions change,
when secret material lingers longer than intended, or when snapshot directories become ambiently browsable.

Greenfield advantage: make snapshot access **explicit, leased, and policy-governed**.

## Prior art worth stealing

### Plan 9 Fossil (snapshots as a first-class user interface)

Fossil exposed snapshots as part of the filesystem interface: users can browse prior states without admin help.
Permanent archives were backed by a content-addressed, write-once store (Venti), making archival history durable.

Key lesson: *time travel is only useful if it’s cheap to invoke under pressure*.

### Mainstream “previous versions” UX

Windows/macOS file recovery flows normalize “show previous versions” as a standard workflow.
This is an expectation, not a luxury.

## DeriveBSD direction

### 1) Do not expose snapshots as ambient directories

ZFS-style snapshot directories are convenient, but they can create surprising access paths.
In particular, if a user once had access to a file and later loses it, old snapshots may still leak the old data
unless the access model is deliberately designed.

Therefore:
- no default `.zfs/snapshot` browsing surface for unprivileged users
- no “snapshots are always mounted somewhere” assumption

### 2) Provide a portalized “time travel” interface

Expose snapshot reads via a **Time Travel Portal**, not by mounting snapshot directories into everyone’s namespace.

- Request: `time.travel.request` (who, what paths/datasets, time window, purpose class)
- Decision: policy engine grants a **lease** (timeboxed; path-scoped)
- Result: a read-only handle to a view of prior bytes

The portal can offer:
- “previous versions” UI for users
- diff view against current
- export to support bundle (through export policy + deterministic redaction)

### 3) Re-check authority at access time

Time travel reads should respect current policy and current access expectations.
Two practical models:

**Model A (default): policy re-check + filtered view**
- snapshot contents remain intact
- portal only materializes paths the principal may read **now**
- revocations take effect immediately (the view is filtered)

**Model B (high assurance): per-principal encryption domains**
- datasets/snapshots can be sealed such that revoked principals cannot decrypt old bytes
- heavier operationally; reserve for high-risk datasets

### 4) Treat snapshot views as evidence-bearing objects

Snapshot access is often security-relevant. So the act of opening a time-travel view produces evidence:
- which snapshot/time window
- which principal
- lease duration
- whether redaction transforms were applied

The evidence itself must be policy-governed (no ambient surveillance).

## Why this matters

If DeriveBSD doesn’t provide a clean “previous versions” story:
- people will create ad-hoc backup mounts
- teams will leak snapshot paths into containers/VMs
- incident response will rely on folklore

Greenfield advantage: keep the UX **good** without making snapshots an ambient data-exfil surface.

## See also

- Evidence spine overview: `docs/229-evidence-spine-overview.md`
- Incident snapshots + support bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- Export policies + support-bundle portal: `docs/251-export-policies-and-support-bundle-portal.md`
- Deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- Bootenv switching as evidence (separate but related): `docs/284-bootenv-switching-as-evidence.md`

Last updated: 2026-02-26
