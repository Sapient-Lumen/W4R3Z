# Origin label authority and anti-laundering boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain, isolation  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

DeriveBSD already wanted origin labels, quarantine state, sanitize-first imports, and queryable metadata.
The hard decision this archive was missing was **which layer is authoritative**.

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD uses a **dual-layer provenance model**:

1. **Authoritative record:** `content.origin`
   - content-addressed, queryable, bundle-carryable
   - binds a subject digest to capture context
   - the semantic source of truth for provenance
2. **Local filesystem pointer/cache:** quarantine/origin label
   - lives next to the file for fast local UX
   - carries current state plus a pointer to the authoritative record
   - may be stripped by some filesystems/tools, so it is not authoritative

`content.import.receipt` is the join object that tells operators which path occurred for a given import result.
It must record:

- the authoritative `content.origin` digest,
- whether the file-local metadata was **preserved**,
- **rehydrated** through an approved portal/bundle lane,
- **cleared-by-policy** on purpose,
- or **laundering-suspected** because the workflow lost provenance.

## Why this is the right narrow decision

Treating xattrs/ADS/labels as the whole provenance story makes the archive brittle.
Treating provenance as only sidecars/CAS records makes everyday UX weak and slows incident response.

The small, coherent compromise is:

- keep the semantic truth in `content.origin`,
- keep the local label tiny and cheap,
- require import/export portals to preserve or rehydrate labels when the transport is lossy,
- and never silently pretend stripped metadata is intact.

## Contract details

### `content.origin` is the authority

The authoritative provenance object is `content.origin`.
It is the object incidents, exports, support bundles, and query/index layers should join against.

### The filesystem label is pointer-only

A label/xattr/attribute may carry:

- current quarantine state,
- an `origin_id`,
- an `origin_digest`,
- or another tiny pointer form.

It should **not** be treated as the only meaning-bearing provenance record.
If the label is lost, the system can still explain provenance when the authoritative record is available.

### `content.import.receipt` records metadata survival

`content.import.receipt` now carries a `metadata` block.
The important fields are:

- `authority`
- `transport`
- `status`
- `authoritative_origin_digest`

This is the smallest typed surface that makes “preserved vs rehydrated vs laundered” implementable.

### Official preservation lanes

DeriveBSD only promises provenance preservation across lossy transports through official lanes:

- portal copy / file transfer
- deterministic export / bundle lanes
- archive extraction paths that emit derived origin chains and receipts

Raw `cp`, ad-hoc `zip`, or foreign filesystems without the preserving lane are compatibility territory, not the guaranteed provenance-preserving story.

## Operational meaning

### Safe success case

- file arrives from download, USB, share, or attachment
- `content.origin` is created
- file gets a local quarantine/origin pointer
- import/sanitize/open path emits `content.import.receipt`
- receipt says `status=preserved` or `status=rehydrated`

### Suspicious case

- labeled content is copied/repacked/exported outside approved lanes
- the destination bytes arrive without a trustworthy pointer
- the system can still match parent receipts or bundle evidence, or it cannot
- if it cannot, the result stays quarantined and `content.import.receipt.metadata.status` becomes `laundering-suspected`

This prevents the archive from laundering mystery bytes into trusted-looking files.

## Relationship to query/index work

This decision intentionally does **not** make query/index services authoritative.
Indexes remain derivative convenience surfaces built from:

- current file-local pointers,
- authoritative `content.origin` records,
- and other evidence joins.

That keeps query privacy/governance open while unblocking the core provenance contract.

## Related docs

- `adrs/ADR-0074-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/280-origin-labels-and-quarantine-attributes.md`
- `docs/293-attribute-indexed-metadata-and-live-queries.md`
- `docs/251-export-policies-and-support-bundle-portal.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `spec/content.origin.schema.json`
- `spec/content.import.receipt.schema.json`
- `spec/examples/content.origin.json`
- `spec/examples/content.import.receipt.json`

Last updated: 2026-03-07r213
