# AnonSync rev0952 revision notes

## Mission

AnonSync remains one practical C++ replacement for the personal Resilio Sync
workflow: continuous authenticated folder convergence over direct TCP, Tor, and
I2P, with ordinary setup, recovery, lifecycle, and bounded resource behavior.
This revision improves bounded progress and truthful settlement on that shipping
spine; it does not introduce another daemon or synchronization model.

## Product correction

Rev0951 bounded and rotated remote effects but still rooted-inspected the complete
sole-visible projection in one pass. Rev0952 separates inspection work from apply
work with `maximum_remote_inspection_paths` (default 4,096). Catalog schema v5
persists a remote inspection sweep containing:

- a SHA-256 basis over the exact catalog digest and replica visible-state digest;
- the fairness cursor at which that sweep began;
- the number of paths acknowledged on that basis;
- the last acknowledged canonical path; and
- a cumulative unresolved-path flag.

A same-basis restart must reproduce the cursor implied by origin plus count. A
changed basis starts a new sweep. The complete projection is still hard-validated
before any rooted effect. Selected applies complete before optimistic progress
publication, and selection invalidates an incomplete pre-effect sweep. Missing
payloads, conflicts, tombstone conflicts, and local absence awaiting adjudication
remain explicit unresolved scheduling state rather than false completion.

The final `sync-once` pass is settled only after a complete local scan epoch and
a complete clean remote inspection sweep with no deferred payload, apply, or
absence work and `end_of_projection`. Configuration, provisioning, status, and
process JSON expose the independent limit and durable/report sweep state.

## Audit and refactor

`SyncReplicaModel::visible_paths()` previously copied all distinct paths and then
called `visible_path()` once per path. Since `visible_path()` rescanned every
active operation, the bulk projection repeated the complete active-set walk for
each path. Rev0952 groups model-owned operation pointers once by borrowed
canonical path and routes single-path and bulk materialization through one helper.
A 512-path reverse-insertion test proves canonical ordering, exact primary IDs,
value kind, and conflict list shape. The refactor preserves the public owned
result while removing duplicate path ownership and repeated global scans.

The source audit now contains 74 checks and binds the one-pass grouping seam, the
borrowed active lookup, sweep basis/origin/count persistence, schema migration,
settlement fencing, and process diagnostics. It remains a lexical structural
audit, not semantic proof.

## Validation

- GCC 14.2 Debug: fresh configured graph completed all 511 build steps across
  retained continuation; a final no-work invocation re-attested bundled SQLite
  3.53.3.
- GCC registry: 253 other registered tests passed in the aggregate invocation;
  inherited `anonsync_core_sync_domain_model_selftest` then passed in isolation
  with 611/611 internal checks, covering all 254 entries without claiming one
  uninterrupted aggregate run.
- GCC product lane: 35/35 passed in 28.19 seconds real time.
- Focused: 92 network-model checks, 321 folder-owner checks, 99 sync-once checks,
  and 164 payload-store checks.
- Structural source audit: 74/74 passed.
- Clang 17 ASan/UBSan: the already configured full product graph rebuilt all 20
  affected steps for the exact final source; a no-work invocation re-attested the
  dependency state.
- Sanitizer product set: 35/35 passed as isolated invocations with leak detection;
  no AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or leak
  diagnostic was retained.

## Honest boundary

The inspection frontier does not make the remote projection incremental. Every
pass still restores and hard-validates the complete visible state. Same-path
causal maximality remains pairwise. The sweep is an asynchronous coverage
witness, not a point-in-time filesystem snapshot; a mutation behind a cursor is
next-epoch work. Local scanning still restarts at the retained root and
reclassifies its skipped prefix, immediate directories are fully buffered and
sorted, cold payload snapshots traverse the entire private namespace, and
catalog/replica/payload/filesystem cutpoints are not one transaction.

Identity-preserving rename, empty-directory and metadata semantics, friendly
conflict/restore behavior, selective synchronization, changed-block production
transfer, bounded history and garbage collection, multi-share device ownership,
cross-platform qualification, and the named first uninstall workload remain
open.

## Package

Declared publication name: `AnonSync-rev0952-2026.07.30.14.40-rootedsweep-linearprojection-settlement-aquamarine.zip`

Parent: `AnonSync-rev0951-2026.07.30.10.55-cyclicreproof-payloadsnapshot-crashdecoupling-fireopal.zip`

Parent SHA-256: `1d26f0e16afbacef5594bf88b1887c6448def8d86372afaa4d3d05001cf07806`
