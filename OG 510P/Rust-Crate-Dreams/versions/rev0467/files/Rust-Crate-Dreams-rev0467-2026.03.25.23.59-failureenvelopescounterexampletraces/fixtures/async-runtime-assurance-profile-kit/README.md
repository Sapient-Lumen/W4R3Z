# Async Runtime Assurance Profile Kit fixtures

This fixture set exists to keep runtime choice from collapsing into one fake “uses async runtime” story.

The first compact artifacts are now:

- `runtime-profile.receipt.json`
- `shutdown-behavior.report.json`
- `qualification-basis.receipt.json`
- `runtime-profile-diff.report.json`
- `runtime-assurance-bundle.manifest.json`

The proving-ground scenarios are intentionally small:

1. Tokio shutdown timeout does not mean all work stopped.
2. Static embedded executors/schedulers are not the same runtime profile as a hosted threadpool/I/O runtime.
3. Tokio docs + metrics still do not make an on-target qualification claim.
4. Embassy’s no-`alloc` / static-task story can be docs-strong while still leaving board-scope review gaps.
5. Tokio → RTIC is runtime-model drift, not merely evidence drift.
6. Mixed host Tokio + target Embassy projects need a multi-lane bundle, not one uniform runtime label.

## Added 2026-03-23 — service topology and capability routes

This fixture family now also covers:

- `runtime-service-topology.receipt.json` for where async services actually come from,
- `capability-route.receipt.json` for what exact activation/provider route a capability depends on,
- `compatibility-bridge.report.json` for what adapters actually bridge and what debt remains.

Use these fixtures when a runtime name alone would hide whether time, I/O, blocking, or dispatcher-scoped services are really available.
Do not infer those capabilities from dependency presence or from a bridge crate alone.



## Added 2026-03-23 — deployment topology and guarded capability matrices

This fixture family now also covers:

- `runtime-deployment-topology.receipt.json` for which host/CI/target lanes exist,
- `capability-availability.matrix.json` for which runtime-sensitive capabilities exist in which lane,
- `surface-guard.report.json` for cfg/feature/runtime-context/provider guards around public support claims.

Use these fixtures when a runtime family name or one working demo would otherwise flatten Linux, Windows, host-example, and embedded-target support into one fake support story.
