# Workstation successor candidates stay immutable and resnapshot-shaped

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

`docs/605-workstation-file-open-import-and-bounded-document-roles.md` fixed the imported-document open boundary:
import first, route second, and keep ordinary handling inside bounded `document_viewing` / `document_editing` roles.
`docs/606-workstation-imported-foreign-documents-stay-view-first.md` then fixed the mutation floor:
foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of saving back over the imported original by default.
`docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` then made that transition typed and joinable through `content.working-copy.plan` / `content.working-copy.receipt` plus `working_copy_receipt_digest` on allow-path edit routes.
`docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` then fixed local save scope:
ordinary save stays on the working-copy output, and source write-back remains a separate explicit act.
`docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` then fixed the first source-lineage act:
`content.reintegrate.plan` / `content.reintegrate.receipt` register a local successor candidate of the same authoritative origin instead of replacing the source in place.

This doc makes the next small but expensive cut:
**that successor candidate must itself stay an immutable snapshot of one exact digest, and any later local edits must mint a new candidate rather than silently mutate the earlier one.** `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` then fixes the next follow-on: explicit supersession is required before one immutable candidate displaces another.

See also:
- ADR: `adrs/ADR-0200-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`
- file-open floor: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- view-first mutation floor: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- typed working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- save-scope floor: `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- explicit reintegration floor: `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- canonical schemas: `spec/content.reintegrate.plan.schema.json`, `spec/content.reintegrate.receipt.schema.json`

## Why this needs a hard decision

Once the archive says **explicit reintegration** and **local successor candidate**, the next leak is to leave that candidate mutable in practice.
Then the easiest implementation path becomes the real product:

- a receipt names a file path while the file keeps changing,
- approval/review acts accidentally refer to “whatever the working copy looked like later,”
- finalization adapters can no longer prove which bytes they promoted,
- and support bundles cannot distinguish candidate-1 from candidate-2 without reopening editor state or guessing from timestamps.

That is too much ambiguity for DeriveBSD’s evidence model.
A candidate needs to be a frozen thing.

## Decision

`content.reintegrate.plan` and `content.reintegrate.receipt` now carry two more required boundary guarantees:

- `candidate_snapshot = immutable`
- `later_edits = new-candidate-required`

Those fields mean the official reintegration lane stays **snapshot-shaped**, not **live-document-shaped**.

## What the boundary means

### 1) A candidate is one exact digest-bound snapshot

A successful `content.reintegrate.receipt` already binds:

- the exact `content.working-copy.receipt`,
- the exact `working_copy_output_digest`,
- the exact `content.import.receipt`,
- and the exact authoritative origin digest.

This doc now makes that interpretation explicit:
that receipt names **one immutable candidate snapshot**, not a mutable pointer to a working path.

### 2) Later local edits do not mutate the earlier candidate

If the user keeps editing after candidate registration, those later bytes are not secretly “the same candidate but newer.”
They are just later local bytes.
If those later bytes should count as source-lineage intent, they need:

1. their own later working-copy output digest,
2. and their own later `content.reintegrate.receipt`.

### 3) Re-snapshot beats retarget

The v0 lane intentionally prefers **re-snapshot** over **retarget**.
It does not support:

- mutable candidate records,
- candidate overwrite,
- “latest candidate for this file path,”
- or adapter-specific silent retargeting of an earlier candidate toward newer bytes.

That keeps review/finalization authority tied to one exact object.

## Practical model

1. import foreign bytes through `content.import.*`
2. view first in `document_viewing`
3. issue an explicit writable artifact through `content.working-copy.*`
4. save locally onto that working-copy output
5. register a frozen successor candidate through `content.reintegrate.*`
6. if more edits happen later, produce another candidate rather than mutating the old one
7. let later approval/finalization adapters pick which exact candidate to accept, after any explicit same-origin supersession relationships are clear, after `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` has ruled out stale-target rebinding in the local supersession lane, and after `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md` has made stale denial recovery/observed-head evidence queryable too through `fresh-explicit-supersession-required`, and after `docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md` has kept the fresh follow-on act denial-joined and head-pinned through `stale_denial_receipt_digest` plus `expected_current_*`

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** emergency edits or field-authored procedures can stay evidence-bound even when several candidate drafts are produced in sequence.
- **B / secure workstation:** ordinary “keep editing after I already marked this as candidate” behavior now has a boring exact answer.
- **C / general-purpose OS:** convenience adapters can still present a friendlier UX, but the official Derive-managed lane remains immutable underneath.
- **D / appliance factory / regulatory:** frozen candidate snapshots fit approval, sign-off, and audit trails better than mutable document-path records.

## What remains intentionally open

This doc does **not** settle:

- how later approval/finalization lanes should consume the explicit supersession chains that `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` and `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` now standardize,
- which approval lanes should gate promotion/finalization,
- or which remote adapters deserve first-class support.

Those remain future RFC/ADR work.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`
- `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`

Last updated: 2026-03-20r345
