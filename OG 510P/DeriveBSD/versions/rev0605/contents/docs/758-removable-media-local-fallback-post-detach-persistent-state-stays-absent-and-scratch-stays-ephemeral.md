# Removable-media local fallback post-detach persistent state stays absent and scratch stays ephemeral

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, reviewed environment/argv/cwd, launcher-pinned executable identity, launcher-pinned runtime dependency closure, launcher-fixed unprivileged credentials, launcher-supervised daemon-free lifecycle, a launcher-enforced resource envelope, a launcher-isolated peer-interaction envelope, a launcher-sealed ambient-input envelope, and receipt-visible absence of network egress.

This page closes the next persistent-state seam:

> **the later worker must not let user-home state, host cache/config/history, reusable scratch, crash dumps, lock files, or tool-local durable state become hidden derivative inputs, side outputs, or post-run leftovers.**

See also:
- ADR: `adrs/ADR-0347-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md`
- previous cut: `docs/757-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md`
- resource envelope: `docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use:

- `persistent-state-absent-no-home-cache-or-host-state-writes`
- `receipt-records-persistent-state-absence-and-scratch-cleanup`
- `launcher-created-empty-scratch-nonauthoritative`
- `scratch-destroyed-before-derivative-receipt`
- `no-user-home-cache-config-or-history-state`

These strings do not require one specific filesystem primitive. They require that ordinary derivative work has no user-home, host-cache, host-config, history, crash-dump, durable tool-state, or reusable temporary-state authority; that any scratch visible to the worker is launcher-created, empty, scoped to this run, nonauthoritative, bounded by the resource envelope, and destroyed before derivative receipt authority; and that the absence/cleanup posture is receipt-visible.

## Boundary rules

### 1) Persistent host/tool state is absent

The later worker records `persistent-state-absent-no-home-cache-or-host-state-writes`. `$HOME`, XDG cache/config/state directories, desktop thumbnail databases, fontconfig caches, tool history, crash dumps, lock files, license databases, mutable tool profiles, and reusable temporary directories are not admitted into the first lane.

This is separate from network egress absence. A fully offline sanitizer can still be stateful if it reads or writes local caches and config. The ordinary lane stays one-shot.

### 2) Scratch is launcher-created and nonauthoritative

The later worker records `launcher-created-empty-scratch-nonauthoritative`. Scratch is empty when handed to the worker, scoped to the run, and useful only as execution plumbing. It is bounded by `scratch_bytes` in the resource envelope, but that byte limit is not the authority story by itself.

Scratch does not become a second output channel. The only authoritative derivative bytes still leave through the one declared append-open derivative slot that the broker collects and remeasures.

### 3) Scratch cleanup is receipt-visible

The later worker records `receipt-records-persistent-state-absence-and-scratch-cleanup` and `scratch-destroyed-before-derivative-receipt`. Cleanup must be complete before a derivative locator becomes authoritative. A reviewer should not need to inspect host-local temp directories, crash directories, or tool caches to know whether subject-derived leftovers remain.

If cleanup fails, the ordinary lane fails closed or withholds derivative receipt authority until the failure is explicitly represented.

### 4) Cache/config/history channels stay out

The later worker records `no-user-home-cache-config-or-history-state`. Environment review and network absence are not enough if tools can still use home directories, `XDG_CACHE_HOME`, `XDG_CONFIG_HOME`, `XDG_STATE_HOME`, browser/profile stores, history files, plugin caches, font caches, or reusable TMPDIR locations. Those channels are out of the first lane unless a future compatibility lane declares and receipts them.

### 5) Canonical examples carry the posture

Canonical examples carry persistent-state posture through:

- `post_detach_persistent_state_posture`
- `post_detach_persistent_state_receipt_posture`
- `post_detach_scratch_posture`
- `post_detach_scratch_cleanup_posture`
- `post_detach_cache_config_posture`

The preopen map carries launcher-facing equivalents:

- `persistent_state_posture`
- `persistent_state_receipt_posture`
- `scratch_posture`
- `scratch_cleanup_posture`
- `cache_config_posture`

Together with descriptors, launch context, executable/runtime closure identity, credentials, lifecycle, resources, peer interaction, ambient inputs, and network absence, these fields make the worker's durable-state boundary reviewable without relying on a remembered disposable-jail template.

## Canonical first-cut example stack

The persistent-state cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- no user-home/cache/config/history state is admitted,
- scratch is launcher-created, empty, bounded, nonauthoritative, and per-run,
- scratch cleanup is recorded before derivative receipt authority,
- durable tool caches and profile stores stay out of ordinary derivative authority,
- and any future compatibility lane that needs persistent state must declare, scope, invalidate, and receipt it explicitly.

## Why this cut is worth making now

Without this decision, the archive could produce receipts that look complete but still hide durable local state:

- identical preserved subjects could produce different derivatives based on stale tool caches,
- subject-derived filenames could leak through history, thumbnails, crash dumps, or lock files,
- mutable config could change sanitizer behavior without appearing in the receipt,
- reusable scratch could let one removable-media subject influence the next,
- and support could confuse leftover temp files with authoritative evidence.

This cut keeps the first lane boring: one preserved subject, one declared bounded derivative slot, no durable worker state, and receipt-visible cleanup.

## Compatibility impact

Some tools genuinely benefit from caches, profiles, persistent policy state, or reusable temporary directories. Those tools are not rejected forever; they require a future explicit compatibility lane that:

- declares the persistent-state authority,
- scopes it by profile/tool/subject family,
- states cache invalidation and cross-subject separation rules,
- records cleanup or retention posture in receipts,
- preserves one-subject and derivative-egress invariants unless separately reviewed.

The current first lane remains persistent-state-absent and scratch-ephemeral.

## r504 contract-closure continuation

The persistent-state posture is now consumed by the schema-backed post-detach contract in `docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md`. The posture strings remain the human labels, but the ordinary lane now also carries `schema-backed-positive-and-negative-fixture-guarded`, `receipt-must-bind-freebsd-launch-evidence-to-contract`, and `known-bad-authority-shapes-must-fail-validation` so home/cache/config/history absence and scratch cleanup cannot survive only as prose.

Last updated: 2026-05-21r504
