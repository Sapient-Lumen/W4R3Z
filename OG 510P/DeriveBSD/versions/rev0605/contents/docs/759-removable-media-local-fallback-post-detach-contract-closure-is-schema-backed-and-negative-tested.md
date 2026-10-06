# Removable-media local fallback post-detach contract closure is schema-backed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt, Registry→Diff→Gate, Quarantine→Promote

The removable-media local fallback already has a narrow first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, finite filesystem-family admission, one selected regular-file subject, capture-first into the authoritative quarantine store, early detach, a fresh post-detach worker, one digest-bound preserved-subject delivery, one broker-collected derivative slot, capability-mode entry, reviewed descriptors, reviewed process launch, launcher-pinned executable/runtime closure, fixed unprivileged credentials, launcher-supervised lifecycle, bounded resources, isolated peers, launcher-sealed ambient inputs, no network egress, no persistent host/tool state, and ephemeral scratch.

This page closes the next review seam:

> **the first post-detach worker contract is not closed until its posture strings are represented by a typed object, a positive fixture, negative fixtures, a checker, receipt fields, backend evidence vocabulary, and failure semantics.**

See also:
- ADR: `adrs/ADR-0348-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.contract.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.contract.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-contract/`
- previous cut: `docs/758-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md`

## Decision

The ordinary first lane now carries:

- `schema-backed-positive-and-negative-fixture-guarded`
- `receipt-must-bind-freebsd-launch-evidence-to-contract`
- `known-bad-authority-shapes-must-fail-validation`
- `sha256:4848484848484848484848484848484848484848484848484848484848484848`

The new typed contract object is `removable.media.local.post_detach.contract`. It is deliberately narrower than a future general launcher profile. It names the first removable-media post-detach lane only: B/C local fallback, one selected regular file, post-detach later worker, preserved capture as the only input authority, one declared derivative sink, no path reopen, no persistent state, no network, no ambient peer/session/control surface, and receipt-bound backend evidence.

## Contract-closure rule

A security posture is not complete when it has a phrase. For this lane, a posture is considered closed only when it has all of the following:

1. a schema field or typed object;
2. closed vocabulary for ordinary-lane values;
3. a canonical positive example;
4. at least one negative fixture for the known-bad shape;
5. a checker that proves positives pass and negatives fail;
6. a receipt field or receipt-binding posture;
7. a backend evidence source; and
8. a fail-closed or downgrade rule when evidence is missing.

The pilot implementation of that rule is `tools/check_removable_media_local_post_detach_contract_closure.py`.

## Positive contract object

The positive example `spec/examples/removable.media.local.post_detach.contract.json` binds these previously separate surfaces:

- lane shape: `removable-media-local-fallback`, `post-detach-later-worker`, `single-selected-subject-first-cut`;
- worker boundary: capability mode, reviewed fds, no path reopen, reviewed env/argv/cwd, pinned executable/runtime closure, fixed credentials, supervised lifecycle, resource envelope, peer isolation, ambient-input sealing, network absence;
- authority boundary: persistent-state absence, cache/config/history absence, no crash-dump/tool-profile/reusable-temp authority, and no authoritative-store browse authority;
- scratch boundary: launcher-created, empty, single-run, nonauthoritative, bounded, cleanup-before-receipt, memory-backed or key-discarded;
- output boundary: one declared derivative slot, no readback/truncate/rebind, broker collection and remeasurement before receipt;
- backend evidence: FreeBSD jail/Capsicum posture, fd table/rights posture, devfs/pf posture, no Casper services, no network descriptors, scratch backend and teardown evidence, and output-slot identity.

## Negative fixtures

The red corpus starts with six fixtures under `spec/examples/invalid/removable-media/post-detach-contract/`:

- `home-preopen-present.json`
- `reusable-scratch-present.json`
- `casper-network-service-present.json`
- `path-reopen-allowed.json`
- `scratch-cleanup-best-effort.json`
- `undeclared-output-surface-present.json`

Each fixture is intentionally close to the canonical object and must fail schema validation. This makes regression visible when someone widens a vocabulary, changes a `const`, or quietly treats an authority leak as another allowed mode.

## Backend evidence vocabulary

The first backend vocabulary is intentionally FreeBSD-shaped but not yet tied to one implementation log format. The receipt must be able to bind evidence for:

- jail/profile identity;
- devfs ruleset posture;
- pf/no-network posture;
- capability-mode entry;
- fd table after close/attenuation;
- fd rights per reviewed descriptor;
- absence of Casper services and network descriptors;
- scratch backend and cleanup evidence;
- resource envelope posture; and
- output slot identity.

The phrase `receipt-must-bind-freebsd-launch-evidence-to-contract` means these are not comments. A successful derivative receipt should be able to point to the evidence bundle, digest, or structured receipt that proves the worker launched under this contract.

## Mount flags are evidence, not the execution boundary

The first lane still wants read-only, `nodev`, `nosuid`, `noexec`, `nosymfollow`, and finite filesystem-family admission on the host-controlled mount. The r504 contract adds a sharper rule: mount flags are defense-in-depth evidence, not the primary no-execution guarantee.

The primary execution boundary is descriptor-only launch, capability-mode entry before tool mainline, no post-entry path reopen, launcher-pinned executable identity, launcher-pinned runtime dependency closure, no ambient loader/plugin/helper discovery, no network descriptors/Casper network service, no user-home/cache/config/history state, and broker-collected output.

## Scratch semantics

The ordinary lane admits memory-backed scratch or encrypted/key-discarded scratch. Disk-backed scratch without key discard is not admitted in the first lane. If a future compatibility lane wants durable scratch, it must name the storage backend, crash behavior, cleanup proof, retention posture, and receipt downgrade semantics explicitly.

For this first lane, failure to evidence cleanup before derivative receipt authority is not a warning. It withholds the derivative receipt or fails closed.

## Implementation target

The next runtime prototype should treat `spec/removable.media.local.post_detach.contract.schema.json` as the launch target. A launcher does not have to emit every final receipt format immediately, but it should be able to produce enough structured evidence to answer:

- Which fds existed after closefrom/attenuation?
- Which rights did each fd retain?
- Did the approved shim enter capability mode before tool mainline?
- Which jail/devfs/pf posture was active?
- Were Casper services absent?
- Was scratch memory-backed or key-discarded?
- Was scratch destroyed or otherwise made nonpersistent before derivative receipt visibility?
- Did the derivative come only from the declared append-open output slot?

## First-run check

Run:

```sh
python3 tools/check_removable_media_local_post_detach_contract_closure.py
```

Then run:

```sh
python3 tools/validate_spec_examples.py
python3 tools/check_generated_docs.py
```

`tools/hygiene.py` includes the new guardrail so release hygiene will catch drift.

## r505 launch-evidence closure

r505 turns the r504 backend-evidence posture into `spec/removable.media.local.post_detach.launch.evidence.schema.json` and `spec/examples/removable.media.local.post_detach.launch.evidence.json`. The contract now also binds `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded`, `sha256:4949494949494949494949494949494949494949494949494949494949494949`, and `known-bad-freebsd-launch-evidence-shapes-must-fail-validation` so a derivative receipt cannot merely say that FreeBSD evidence exists; it must point at a typed launch-evidence object whose bad shapes fail validation.


## r506 recovery-evidence closure

r506 extends the r504 contract and r505 launch-evidence stack with `spec/removable.media.local.post_detach.recovery.evidence.schema.json`. The contract now also binds `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded`, `sha256:5050505050505050505050505050505050505050505050505050505050505050`, and `known-bad-recovery-evidence-shapes-must-fail-validation` so `scratch-destroyed-before-derivative-receipt` survives crash, kill, timeout, and later audit semantics instead of remaining a clean-run assumption.

Last updated: 2026-05-21r506
