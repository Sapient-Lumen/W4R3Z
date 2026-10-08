# crash-symbolication-workbench lane boundaries — 2026-03-21

This note keeps **P-0101 Crash Artifact & Symbolication Workbench Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable crash support contract** over captured crash artifacts.
It should answer:

- how the crash was captured,
- which module identities are authoritative,
- which symbol sources were used,
- how complete/replayable the analysis really is,
- and whether the resulting bundle is safe to share.

## Keep this distinct from nearby lanes

### Distinct from `P-0073 Async Replay Debugger Kit`

`P-0073` is about replaying async incidents and schedule/time/effect truth.
`P-0101` is about postmortem crash artifacts, symbolication routes, and share-safe crash bundles.

### Distinct from debugger UX / visualizer lanes

Debugger lanes are about live or attached debugging experiences and visualizer compatibility.
`P-0101` is about portable artifact review after a crash already happened.

### Distinct from desktop shipkits

Desktop shipkits cover packaging, signing, updates, and crash pipeline handoff.
`P-0101` is the crash artifact and symbolication contract itself.

### Distinct from `P-0256 Evidence Bundle Core Kit`

`P-0256` is shared bundle substrate.
`P-0101` is the crash-specific profile above that substrate.

### Distinct from hosted crash-reporting services

Hosted services are substrate or consumers.
`P-0101` is the boring contract that keeps local/offline/support workflows reviewable.

## Six truths this lane must keep separate

1. **capture basis** — who wrote the dump and from what posture;
2. **module identity** — base/size/name and debug-id/code-id/build-id truth;
3. **symbol route** — bundled/local/native/server lookup order and timeout posture;
4. **analysis coverage** — loaded/missing/corrupt symbols, soft errors, unresolved frames, and inline posture;
5. **report determinism** — whether the report can be replayed from the bundle alone;
6. **share-safety** — memory, path, username, source-location, and symbol-file inclusion posture.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- a minidump and a replayable crash bundle,
- a stack trace and a verified symbol route,
- a debug ID and a code ID fallback story,
- a good-looking report and high coverage,
- a network symbol fetch and an offline replay guarantee,
- or “PII stripped” and a real share-safety receipt.

## Preferred artifact vocabulary

- `capture-basis.receipt`
- `module-identity.receipt`
- `symbol-route.receipt`
- `analysis-coverage.report`
- `report-determinism.receipt`
- `share-safety.receipt`
- `crash-bundle.manifest`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
