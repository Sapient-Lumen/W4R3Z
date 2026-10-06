# Removable-media local fallback attach receipts carry observed hints and keep them evidence-only

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/732-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp` admission, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, one selected regular-file subject, and present-device-instance-only approval.

This page closes the next smaller implementation seam:

> **the first local-ingest `device.attach.receipt` must carry a finite observed current-presence hint bundle, and those hints stay evidence-only rather than becoming durable trust anchors.**

See also:
- ADR: `adrs/ADR-0323-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md`
- previous cut: `docs/732-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- device authority: `docs/278-device-grants-and-devfs-rulesets.md`
- lease/revocation spine: `docs/249-lease-registry-and-cross-lane-revocation.md`

## Why this needs a hard decision

The archive now says approval is only for the currently present removable-storage instance.
But that still leaves an expensive ambiguity for the first implementation:
what exactly should the attach receipt preserve about the current attachment event?

Without one more cut, implementations drift in opposite bad directions:

- record too little, so support/operator tooling cannot explain what was actually attached,
- or record serial/path/provider hints and then slowly treat those hints as durable “same device” authority.

The first local fallback needs a safer middle:
**record the finite current-instance hints that FreeBSD can observe now, but mark them as evidence-only.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) The canonical attach receipt carries a finite observed-hint bundle

The canonical `device.attach.receipt` example for this lane carries a finite bundle under `runtime.mapping.observed_hints`.
The first example bundle includes:

- a current transport locator such as `ugenX.Y`,
- the selected storage provider node,
- and, when available, disk-ident and physical-path hints.

This is enough to answer “what did the host think it attached right now?” without pretending that every machine can always emit every hint.

### 2) Those hints are explicitly evidence-only

The same attach receipt must say that these hints are **current-presence evidence only**.
They are there for:

- operator review,
- receipt/query surfaces,
- detach correlation,
- and support/forensics.

They are **not** a durable trust root for later attach decisions.

### 3) Missing hints do not upgrade or synthesize authority

If a platform cannot surface one of the optional hints, the first lane records what it observed and stays honest about the gap.
It does not silently synthesize a stronger device identity story, and it does not widen authority because some convenience hint was missing.

### 4) Same hints on reattach still do not auto-resume

This page composes with `docs/732-*`.
Even when the next insertion shows the same serial/disk-ident/path-style hints, that is still only operator/support evidence.
It does **not** revive the previous grant.
A reattach still needs a fresh grant.

## Canonical first-cut example stack

The attach-evidence example stack is now explicit too:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/device.attach.receipt.removable-media-local-ingest.json`
- `spec/examples/devfs.view.plan.removable-media-local-ingest.json`
- `spec/examples/mount.view.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`

Together they say:

- the first lane still uses a lease,
- the attach receipt keeps a finite current-presence hint bundle,
- those hints are evidence-only,
- and same hints on later reattach do not silently reopen authority.

## Why this cut is worth making now

Without this decision, the archive still pays repeated implementation tax:

- support bundles cannot answer what the host actually saw when a removable-storage session started,
- coding teams can disagree about whether serial/path/provider observations belong in receipts at all,
- and “same observed hints” can quietly become the real remembered-device policy surface even though the archive already rejected that continuity model.

This page keeps the first coding target small and honest: capture the current evidence, keep it queryable, but do not let it become durable trust.

This page therefore keeps one rule explicit in plain language too: **same hints on reattach still do not auto-resume**.

## What remains open

Still intentionally open:

- whether a later richer lane should add stronger hardware-identity continuity,
- whether device-domain or microVM-backed lanes should record a different hint family,
- exact trusted-UI wording for how those hints are shown to operators,
- and whether later lanes should standardize richer detach-side correlation fields too.

Last updated: 2026-03-28r464
