# RFC-0194: Reviewed finite collection handoff session

- Status: draft
- Author(s): OpenAI / archive maintenance pass
- Created: 2026-03-22
- Last updated: 2026-03-22

## Summary

Design a first richer workstation transfer lane for a **reviewed finite collection handoff**:
a session-bounded way to hand a finite selected set of files and/or directories from one compartment to one receiving lane without widening ordinary `ui.datatransfer.*` into persistent tree authority, ambient shared mounts, or quiet source writeback.

This RFC is explicitly downstream of:
- `adrs/ADR-0261-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `adrs/ADR-0262-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`

## Motivation

The ordinary workstation `ui.datatransfer.*` lane is now coherent enough to implement, but it is intentionally narrow:
- one-shot by default
- payload-bounded
- exact-payload-bound under reviewed retry continuity
- not a general file-set or directory authority lane

The next practical pressure is usually a user or operator wanting to move a **small selected set of filesystem objects** across the compartment boundary:
- a few screenshots,
- several attachments,
- a selected project folder snapshot,
- or a bounded drag/drop-like handoff.

That need is real, but the archive should answer it with a lane that remains visibly separate from ordinary `ui.datatransfer.*` and that stays much narrower than persistent tree or bookmark-style authority.

## Goals / Non-goals

### Goals

- finite selected set of files and/or directories
- one reviewed handoff session to one receiving lane
- distinct artifact family from ordinary `ui.datatransfer.*`
- session-bounded authority
- single-retrieve by default
- auto-stop after the first successful retrieve
- read-only only in the first cut
- explicit collection membership / review surface
- explicit per-member manifest for snapshot membership
- a small exact per-member manifest floor
- regular-file manifest entries plus explicit directory entries only in the first cut
- explicit receipt/evidence surface
- compatibility with later import / working-copy / reintegration lanes rather than quiet source writeback

### Non-goals

- persistent document-tree authority
- ambient shared folders or shared mounts
- background sync / watcher semantics
- silent writeback to the source lineage
- symlink/device/special-object handoff as part of the first cut
- multi-recipient broadcast as the first richer lane
- retrofitting the ordinary `ui.datatransfer.*` family with “one more mode”

## Proposal

### 1) Keep the richer lane visibly distinct

The accepted archive rule already requires a distinct artifact family. This RFC should therefore avoid ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt` reuse.

Provisional names may be introduced during the RFC, but the final accepted family must remain visibly separate from ordinary `ui.datatransfer.*`.

### 2) Start with finite collection handoff, not persistent authority

The first richer lane should hand off a **finite selected collection**.
The sender chooses a bounded set of objects.
The collection membership then becomes part of the reviewed session story rather than something the receiver can expand later by browsing outward.

For directory-shaped members, the first cut should use **finite reviewed directory snapshot semantics**. Selecting a directory means reviewed snapshot membership at handoff creation time, not live outward traversal of a source tree and not later source-tree growth visibility.

### 2b) Keep snapshot membership manifest-first

The first cut should require an **explicit per-member manifest** for the reviewed finite set.
For directory-shaped members, reviewed snapshot membership should expand into explicit descendant-member entries at handoff creation time rather than staying represented only by a directory handle or only by an aggregate digest.

A tree/collection digest may still be useful as **supplementary summary evidence**, but it should not replace the explicit reviewed member manifest in the first cut.
tree-digest-only or summary-only membership representation should come back only as a later explicit RFC decision, not as the ordinary first-cut surface.

### 2c) Keep the first member-kind vocabulary narrow

The first cut should allow only **regular-file manifest entries** and **explicit directory manifest entries**.
No symlink, device-node, FIFO, or socket member semantics are part of the first cut.
unsupported member kinds must fail closed instead of being silently followed, preserved for later resolution, or omitted.


### 2d) Keep the first manifest floor content-identity-first and stat-light

The first cut should keep the explicit per-member manifest **small and exact**.
Every manifest entry should carry a **normalized review path** that is unique within the reviewed collection and an exact **member kind**.
In plain terms, every entry must carry a normalized review path and exact member kind.
Every regular-file entry should also carry exact **payload digest** and exact **byte length**.
Explicit directory entries remain reviewed members but do not need file-style payload digest / byte-length fields in the first cut.

MIME type, display labels, last-modified time, owner/group, mode bits, xattrs, thumbnails, and other platform-specific stat fidelity should stay **out of the required first-cut manifest floor**.
If such metadata appears later, it should stay clearly advisory rather than replacing path/kind/payload identity as the authoritative review/export surface.
Richer stat fidelity should come back only as a later explicit RFC decision rather than quietly inflating the first reviewed handoff lane.

### 3) Keep the first cut read-only only

The first richer lane should be **read-only only** in its first cut.
No write-enabled receive exception is part of the first cut.
If writable receive is ever worth designing later, it should arrive only as a **follow-on RFC/ADR decision**, not as an option quietly retained inside this first lane.

### 4) Keep the lane session-bounded

Authority should die with the handoff session.
The first richer lane should not act like a bookmark, a remembered grant, or a background mount that outlives the session unless a later, separate decision proves that value outweighs the added laundering and support cost.

### 5) Re-enter existing authoring lanes on mutation

If the receiver wants to edit the handed-off material, the design should prefer re-entry into existing import / working-copy / reintegration lanes rather than turning the richer handoff lane itself into quiet source-authority writeback.

### 6) Keep the first cut single-retrieve by default and auto-stopping

The first cut should keep retrieve semantics boring:
- **single-retrieve by default**
- **auto-stop after the first successful retrieve**
- no repeated-retrieve posture in the first cut

If repeated retrieve is ever worth standardizing later, it should come back as an explicit follow-on RFC decision rather than hiding inside the default richer lane.

## Alternatives considered

### Make multi-delivery clipboard history the first richer lane

Rejected as first priority because it mainly widens replay convenience without addressing the more common selected-files / selected-folder handoff pressure.

### Make persistent document-tree authority the first richer lane

Rejected as first priority because it is broader, more stateful, and harder to keep audit-friendly than a reviewed finite collection handoff.

### Make the first richer lane write-enabled from day one

Rejected because the first cut should learn collection membership, retrieve semantics, and bounded lifetimes before it also takes on mutation and conflict semantics.

### Keep a narrowed write-enabled exception inside the first RFC

Rejected because it preserves a standing scope-creep seam inside the first cut and blurs the boundary between handoff lanes and existing import / working-copy / reintegration lanes.

### Keep repeated-retrieve posture open in the first cut

Rejected for now because the first richer lane is already broader than ordinary `ui.datatransfer.*` by being collection-shaped; adding replay-friendly retrieve semantics at the same time would make the first cut harder to reason about and easier to launder into convenience authority.

## Backwards compatibility

None yet. This RFC does not change accepted schema families or accepted examples.

## Security considerations

- collection membership must be explicit and reviewable
- the receiver must not gain ambient discovery outside the finite selected set
- directory members should not silently become live open-ended tree grants
- snapshot-shaped directory membership should stay reviewable as a finite selected set, not a browse-later authority story
- explicit per-member manifest is the first-cut review/export surface; aggregate digests are supplementary summary evidence, not a substitute
- first-cut member kinds stay regular-files-plus-explicit-directories only; symlinks and special objects are out of scope unless a later RFC explicitly reopens them
- the first-cut manifest floor stays path/kind/payload identity first: normalized review path + member kind for every entry, plus exact payload digest + exact byte length for regular files
- richer stat fidelity stays out of the required first-cut manifest floor unless a later RFC explicitly standardizes it
- write-enabled receive is deferred out of the first cut and should be treated as a separate future risk family, not a standing option inside the first lane
- session lifetime must be explicit so the lane does not decay into a hidden persistent mount or bookmark
- repeated retrieve is a separate replay-width risk and should not quietly ride along in the first cut

## Open questions

- Should aggregate tree/collection digests become mandatory alongside the explicit manifest, or remain optional summary evidence?
- Should advisory MIME type become mandatory later, or remain optional descriptive metadata?
- Is any owner/mode/mtime/xattr fidelity worth standardizing later, or should richer filesystem metadata stay out of this lane entirely?
- What is the smallest review surface that makes collection membership legible without turning the trusted UI into a file-manager clone?
- Which profiles should treat the eventual lane as supported: B/C/D only, or A too under explicit operator posture?
