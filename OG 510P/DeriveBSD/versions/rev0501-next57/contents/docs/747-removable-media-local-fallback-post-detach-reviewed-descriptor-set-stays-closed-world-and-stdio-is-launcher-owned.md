# Removable-media local fallback post-detach reviewed descriptor set stays closed-world and stdio is launcher-owned

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, present-device-instance-only approval, attach receipts that keep observed hints evidence-only, capture-first processing, early detach once capture verifies, a fresh post-detach worker with `/ingest` absent, preserved capture instead of in-place rewrite, authoritative quarantine-store commit before detach, single-object store-opaque post-detach delivery, digest-bound continuity between the preserved capture and the later worker-visible object, launcher-preopened read-only delivery instead of later path re-open, broker-collected derivative egress instead of trusting `/work/output/...` as authoritative derivative identity, one declared writable derivative slot with no extra worker result surface, an append-open append-only-protected seekable-file sink that still keeps readback/truncate/fcntl-clear out, and capability mode entry before later tool mainline begins.

This page closes the next smaller execution seam:

> **the first lane already says later tool code starts after capability mode entry on a reviewed preopened set; it must also say that the descriptor set crossing that boundary is closed-world and that stdio does not quietly smuggle parent-session authority back in.**

See also:
- ADR: `adrs/ADR-0337-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`
- previous cut: `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- capability posture: `docs/49-capsicum-casper-hardening.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The archive already says the later worker gets one preserved input object, one declared derivative sink, and enters capability mode before later tool code starts.
But one honest implementation question remained open:
**what exact descriptor set crosses that handoff boundary?**

If that stays vague, an implementation can still smuggle authority through startup:

- leak a parent TTY or interactive session socket into later tool code,
- leave stale helper pipes or broader directory handles open “because the wrapper already had them”,
- or describe a tiny reviewed preopen map while the real worker starts with extra inherited descriptors that nobody reviewed.

That is now too large for this first lane.
The smaller honest answer is:
**the reviewed descriptor set stays closed-world, non-reviewed inherited descriptors are closed before later tool mainline begins, stdin stays inert null/empty input only, and stdout/stderr stay launcher-owned observation channels or reviewed append-only log sinks rather than inherited parent-session surfaces.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) The post-detach later worker inherits only the reviewed descriptor set

The reviewed set is now closed-world.
If a descriptor is not explicitly admitted for that later worker, it stays out.
The first lane no longer allows “reviewed descriptors plus whatever else the launcher happened to leave open”.

### 2) Non-reviewed descriptors are closed before later tool mainline begins

The launcher or its approved shim must close or spawn-closefrom all non-reviewed descriptors before handing control to later classify/scan/sanitize tool code.
The portable contract is the outcome — no extra inherited descriptors cross the boundary — not one exact launcher API.

### 3) stdio stays launcher-owned and non-parent-session-shaped

This first lane does not inherit a parent TTY, interactive console, or session socket into later tool code.
`stdin` stays inert null/empty input only.
`stdout` and `stderr` may exist only as launcher-owned observation channels or reviewed append-only log sinks.
If richer interactive or session-shaped stdio is needed, that is a later explicit wrapper/broker lane rather than baseline removable-media convenience.

### 4) Helper descriptors remain explicit reviewed surface

This cut does not forbid every helper descriptor forever.
It only fixes that helpers must be explicit reviewed surface in the preopen map and receipts.
If a tool needs more than the preserved input object, the one declared derivative sink, and launcher-owned observation/logging channels, that need must be made visible instead of arriving by inheritance folklore.

## Canonical first-cut example stack

The closed-world-reviewed-descriptor-set cut is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- the selected regular file is captured and verified,
- the preserved capture commits into authoritative quarantine store before detach,
- the host detaches the medium and restarts later work in a fresh worker,
- later work receives only one digest-bound preserved subject on launcher-preopened read-only delivery,
- the later worker gets exactly one declared append-open append-only-protected derivative sink slot,
- the launcher or its approved shim enters capability mode before handing control to later tool code,
- the descriptor set crossing that handoff stays closed-world and reviewed-only,
- non-reviewed inherited descriptors are closed before later tool mainline begins,
- `stdin` stays inert null/empty input only,
- `stdout`/`stderr` stay launcher-owned observation channels or reviewed append-only log sinks rather than inherited parent-session surfaces,
- and helper descriptors remain explicit reviewed surface rather than inheritance folklore.

## Why this cut is worth making now

Without this decision, the archive would still contain one hidden implementation-sized authority leak inside the first coding target:

- the worker would look preopened and capability-mode-bounded on paper,
- but extra inherited descriptors or parent-session stdio could still be the real authority story,
- and the preopen map would stop being the whole review surface.

This page keeps the first coding target smaller and more honest: reviewed descriptors only, no hidden inherited descriptor tail, no parent-session stdio smuggled across the post-detach boundary.

## What remains open

Still intentionally open:

- exact launcher mechanics (`closefrom()`, `posix_spawn_file_actions_addclosefrom_np()`, reviewed dup/close choreography, `fexecve()`, or approved equivalents) for satisfying this rule,
- whether a later explicit lane should admit richer reviewed helper-descriptor sets for specific sanitizers/classifiers,
- and whether a later explicit lane should admit interactive/session-shaped stdio under a stronger reviewed wrapper/broker contract.

Last updated: 2026-03-28r478
