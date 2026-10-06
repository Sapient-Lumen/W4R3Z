# Removable-media local fallback post-detach credential envelope stays launcher-fixed and non-elevating

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, reviewed environment/argv/cwd, launcher-pinned executable identity, and launcher-pinned runtime dependency closure.

This page closes the next kernel-authority seam:

> **the later worker must not inherit root, operator groups, saved-ID regain, or ambient privilege just because its descriptors and executable are already reviewed.**

See also:
- ADR: `adrs/ADR-0341-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md`
- previous cut: `docs/751-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md`
- capability-mode handoff: `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- process ownership background: `docs/235-process-contracts-and-service-ownership.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The first lane now pins what the worker can see, how it starts, which executable it runs, and which runtime dependency closure that executable may use.
That still does not say which kernel credential envelope runs the tool.

Without this cut, the first lane could still depend on:

- root or device-domain credentials inherited from the launcher,
- supplementary groups such as operator, wheel, storage, or device-administration groups,
- saved-ID regain or privilege-preserving exec behavior,
- setuid/setgid binaries inside the pinned runtime closure,
- login-class or ambient privilege affordances that are not visible in the preopen map.

Those are authority under another name.
For the first lane, the honest rule is: **the launcher fixes an unprivileged credential envelope before handoff, and the receipt stack records it.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Credential envelope is launcher-fixed and unprivileged

The later worker records `launcher-fixed-unprivileged-credential-envelope-no-supplementary-groups`.
The launcher drops or spawns into the reviewed worker principal before tool mainline code runs.
The canonical first-lane example records:

```text
derive-rm-worker:derive-rm-worker
```

Those labels are reviewed contract labels; host-local numeric UID/GID realization remains an implementation detail that must satisfy the same non-elevating posture.

### 2) Supplementary groups are absent

The later worker records `no-supplementary-groups`.
Parent login groups, operator/device/storage groups, and wheel-like groups do not cross into the worker.
If a later compatibility lane needs a non-empty group vector, that vector is authority and must be explicitly declared and receipted.

### 3) Privilege regain is not available

The later worker records `no-setuid-setgid-saved-id-or-ambient-privilege-regain`.
Setuid/setgid binaries, saved-ID regain, ambient caps, privilege-preserving exec tricks, and login-class privilege are out of the first lane.
A tool that needs privileged helper behavior must use a later explicit broker/helper contract rather than smuggling it through worker credentials.

### 4) Plans, receipts, and preopen maps expose the envelope

The canonical examples now carry:

- `post_detach_credential_posture`
- `post_detach_worker_user`
- `post_detach_worker_group`
- `post_detach_supplementary_groups_posture`
- `post_detach_privilege_regain_posture`

The attach grant also carries:

- `post_detach_credential_receipt_posture`
  - canonical value: `receipt-records-worker-credential-envelope`
- `post_detach_credential_envelope_required`

The preopen map carries the same posture under launcher-focused names:

- `credential_posture`
- `worker_user`
- `worker_group`
- `supplementary_groups`
- `privilege_regain_posture`

Together with the descriptor set, launch context, executable digest, wrapper digest, and runtime dependency closure digest, these fields make the later worker's authority envelope reviewable without consulting launcher folklore.

## Canonical first-cut example stack

The credential-envelope cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- executable selection is launcher-owned and digest-pinned,
- wrapper contract identity is receipt-visible,
- runtime dependency closure is launcher-owned and digest-pinned,
- the worker credential envelope is launcher-fixed and unprivileged,
- supplementary groups are empty,
- setuid/setgid/saved-ID or ambient privilege regain is not available,
- and privileged helper behavior stays out unless a later explicit wrapper/broker lane admits and receipts it.

## Why this cut is worth making now

Without this decision, the archive could produce receipts that look precise but still hide a privileged worker:

- a sanitizer could accidentally keep root while only its file descriptors were reviewed,
- inherited storage/operator groups could authorize effects not visible in the preopen map,
- setuid or saved-ID behavior could recover privilege after the launcher thought it had dropped authority,
- and support would have to reconstruct the historical worker identity from host-local process-launch folklore.

This cut keeps the coding target honest: reviewed descriptors, reviewed launch context, reviewed executable identity, reviewed runtime dependency closure, and reviewed credential envelope.

## What remains open

Still intentionally open:

- the exact production format for mapping reviewed worker labels to numeric UID/GID on each host,
- whether profile A/D should require kernel-enforced no-new-privileges or verified-execution hooks for this lane,
- how to admit legacy tools that need privileged helpers through explicit broker contracts,
- and whether profile C should grow compatibility lanes for richer but still receipt-visible credential envelopes.

Last updated: 2026-05-18r497
