# Air-gap mirror kits + sneakernet updates (offline “happy path”)

**Tier:** C (Optional lane)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability, reproducibility

DeriveBSD already supports offline signed update bundles (`docs/138-offline-signed-update-bundles.md`).
This doc tightens the *ecosystem ergonomics*:

- air-gapped and intermittently connected environments need a **boring** workflow
- operators should not have to build bespoke rsync scripts and “trust the USB stick” rituals
- importing updates must be **verifiable, receipt-emitting, and quarantine-first**

This is a greenfield feature worth baking in because “offline” is where update systems get most fragile.

Related:
- TUF-shaped channel metadata: `docs/61-channel-metadata-tuf-inspired.md`, `adrs/ADR-0016-tuf-inspired-channel-metadata.md`
- Uptane director role separation: `docs/127-uptane-director-targets.md`
- ZFS send distribution lane: `docs/126-zfs-send-distribution.md`
- bandwidth-efficient deltas lane: `docs/139-bandwidth-efficient-deltas.md`
- export + consent + transport policies: `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/255-policy-constrained-transports.md`
- long-term source availability + SWHID fallback: `docs/403-swhid-fallback-and-long-term-source-availability.md`

## Concept: a Mirror Kit

A **mirror kit** is a portable, content-addressed snapshot of “everything required to update a host” for a set of channels.
Think: a USB SSD, a signed file tree, or a removable disk image.

It contains:
- a typed kit index (self-describing contents): `mirror.kit.manifest` (`spec/mirror.kit.manifest.schema.json`)
- channel metadata (timestamp/snapshot/targets, delegations as applicable)
- required artifacts (store objects, host images, microVM bundles)
- optional sources/distfiles needed for local rebuilds (hash-verified; may carry SWHID hints)
- optional delta packs (OSTree-style static deltas or equivalent)
- optional transparency proofs / witness statements

A mirror kit is not “trusted because it’s on a disk”. It is trusted only after:
- signatures verify
- metadata freshness/expiry rules pass
- monotonic version constraints pass
- quarantine import receipts exist

## Two-phase import: quarantine → promote

The flow is **Plan → Receipt** at each phase.

### Phase 1: import into quarantine
`derive mirror import /media/mirrorkit --channel stable --to quarantine`

Plan/receipt artifacts:
- Plan: `mirror.import.plan` (`spec/mirror.import.plan.schema.json`)
- Receipt: `mirror.import.receipt` (`spec/mirror.import.receipt.schema.json`)

Rules:
- import is performed in a *disposable sandbox* where feasible
- nothing is “active” after import
- everything is verified and recorded

Outputs:
- `mirror.import.receipt` (what was imported, what verified, what failed)
- the kit manifest digest is recorded in the receipt when present (`source.kit_manifest_digest`)
- updated local cache state (**still not promoted**)

### Phase 2: promote into a local channel
`derive mirror promote --from quarantine --into stable`

Plan/receipt artifacts:
- Plan: `mirror.promote.plan` (`spec/mirror.promote.plan.schema.json`)
- Receipt: `mirror.promote.receipt` (`spec/mirror.promote.receipt.schema.json`)

Rules:
- promotion is policy-gated (trust policy, cohort policy, allowlists)
- promotion is reversible (**promote is a transaction**)

Outputs:
- `mirror.promote.receipt`
- optional publication into local transparency log

## Mirror kit layouts (boring by design)

### A) “Channel snapshot” tree
A directory layout that is easy to inspect and copy:
- `/channels/<name>/metadata/...`
- `/channels/<name>/artifacts/<digest>...`
- `/channels/<name>/deltas/...` (optional)

### B) “Bundle file” (single signed blob)
A single file that can be carried via ticket systems and emailed around (policy permitting).
This is conceptually closer to RAUC-style bundles.

DeriveBSD can support both:
- the tree is great for large media and diffing
- the bundle is great for controlled transports

## Policy: freshness without internet

The tricky part for air-gapped flows is **timestamped metadata**.
DeriveBSD should explicitly support “manual metadata transfer”:

- mirror kits always include *all required metadata objects*, including timestamp/snapshot equivalents
- the importer enforces expiry, but policy can define:
  - maximum acceptable staleness window for specific environments
  - manual “I accept this stale metadata” breakglass with receipts

This avoids the worst failure mode: “we turned off freshness checks to make it work.”

## Delta packs for sneaker nets

Large updates over removable media benefit from “single-file deltas”:
- store object deltas (where applicable)
- OSTree-style static deltas for image-mode hosts
- ZFS send streams for dataset replication lanes

The mirror kit can carry a mix:
- if the target can apply a delta: fast path
- if not: fallback to full objects

## UX requirements (make the secure path easy)

- `derive mirror verify` prints:
  - what channels are present
  - what versions are included
  - what will change (blast radius summary)
  - whether metadata is near expiry
- `derive mirror import` is idempotent and resumable
- every operation emits receipts suitable for incident/support bundles

## Non-goals (v1)

- inventing a new generic artifact transport
- assuming removable media is safe (it is only a carrier)

## References (primary)

- OSTree: static deltas for offline updates (USB/apply workflow):
  - https://ostreedev.github.io/ostree/copying-deltas/
- RAUC: signed update bundles (artifact-as-bundle ergonomics):
  - https://rauc.readthedocs.io/en/latest/basic.html
- TUF specification (freshness/roles/metadata model):
  - https://theupdateframework.github.io/specification/latest/
- Uptane Standard (compromise-resilient update workflows built on TUF concepts):
  - https://uptane.org/docs/2.1.0/standard/uptane-standard

Last updated: 2026-02-28r168
