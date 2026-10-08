# Archive index

## Top-level control surfaces

- `README.md` — project overview and stable orientation surface.
- `START_HERE.md` — human-readable mirror of the canonical entry surfaces, current release identity, current revision delta, canonical restart tiers, compact live posture, compact public-head status, compact restart-priority open-question slice, compact operator-warning subset, compact followthrough / standby-state summary, compact assumption-state summary, and compact rebuild-command subset; exact restart mirrors should be tool-rendered and lint-enforced.
- `AGENTS.md` — future-editor operating posture.
- `CHANGELOG.md` — terse revision history; details live in revision receipts and canonical surfaces.
- `RELEASE-MANIFEST.json` — canonical bundle identity for the current release; mirrored compactly in `START_HERE.md`.
- `REVISION-RECEIPT.json` — canonical current-revision rationale; mirrored compactly in `START_HERE.md`.
- `SURFACE-STATUS.json` — public head / citation status.
- `context-pack.json` — canonical machine handoff with authoritative restart tiers, posture, restart-priority open-question slice, compact operator-warning subset, compact followthrough / standby-state summary, compact assumption-state summary, and compact rebuild-command subset.
- `ASSUMPTION-LEDGER.json` — revisionless durable assumption states: live assumptions, standby thresholds, and grouped retired phase history.
- `FOLLOWTHROUGH-QUEUE.json` — active next tasks only; may be empty when only stop rules remain.
- `WITNESS-VOCABULARY.json` — revisionless durable status families.
- `DATACUBE-TRANSFER-LEDGER.json` — revisionless bounded record of imported machinery.
- `FOREIGN-PRESSURE-LEDGER.json` — revisionless external pressure preserved explicitly.

## Documentation spine

### `docs/00-meta`
- Charter and archive-control surfaces: `charter.md`, `archive-policy.md`, `canonical-homes.md`, `trajectory-map.md`, `llm-runbook.md`, `router-topology-and-scope-map.md`, `ROUTER-TOPOLOGY.json`.
- Support surfaces: `bibliography.md`, `id-conventions.md`.

### `docs/10-method`
- Method and compression surfaces: `method-overview.md`, `salience-first-research-method.md`, `cross-scale-bridge-rules.md`, `claim-ladder-and-promotion-rules.md`, `compression-and-deduping-protocol.md`, `router-economy-and-demotion-rules.md`, `source-admission-and-eviction-sieve.md`.

### `docs/20-constitution`
- Core registries: `claim-registry.md`, `open-question-registry.md`, `invariant-registry.md`, `move-registry.md`.

### `docs/30-program`
- Program state: `research-frontiers.md`, `workstreams.md`, `bridge-experiments.md`.

### `docs/40-model`
- Core model routers: the current-head control router, the cross-family pressure router, `spine.md`, the empirical-contact burden router, the broad ToE credit router, the completion-bid credit router family, the witness-router family, the current-family readout router, the family-B and family-C burden router families, the vacuum-energy burden router, and the burden-split / discriminator routers.
- Subordinate family, cosmological, and witness audits live alongside these routers; use `ARCHIVE_INDEX.generated.md` for the full file-level map.

### `docs/90-quarantine`
- `speculative-branches.md` — live but unpromoted bold ideas.

## Tooling

- `tools/sync_generated_surfaces.py` — rebuild generated restart handoff surfaces and the raw filesystem index.
- `tools/restart_mirror_family.py` — shared declarative restart-mirror family spec / renderer used by sync and lint.
- `tools/lint_archive.py` — archive integrity checks.
- `tools/package_release.py` — build a zip release with a manifest-derived canonical root and predictable naming.
- `Makefile` — execution source for the compact rebuild-command subset mirrored in the restart handoffs.
