# Workstation working-copy reintegration stays explicit and new-version-shaped

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

`docs/605-workstation-file-open-import-and-bounded-document-roles.md` fixed the imported-document open boundary:
import first, route second, and keep ordinary handling inside bounded `document_viewing` / `document_editing` roles.
`docs/606-workstation-imported-foreign-documents-stay-view-first.md` then fixed the mutation floor:
foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of saving back over the imported original by default.
`docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` then made that transition typed and joinable through `content.working-copy.plan` / `content.working-copy.receipt` plus `working_copy_receipt_digest` on allow-path edit routes.
`docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` then fixed local save scope:
ordinary save stays on the working-copy output, and source write-back remains a separate explicit act.

This doc makes the next small but expensive cut:
**when locally edited working-copy bytes should count as the next candidate version of a known authoritative origin, that transition stays explicit, typed, and new-version-shaped rather than replace-in-place or app-folklore-shaped.**

See also:
- ADR: `adrs/ADR-0199-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- file-open floor: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- view-first mutation floor: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- typed working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- save-scope floor: `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- canonical schemas: `spec/content.reintegrate.plan.schema.json`, `spec/content.reintegrate.receipt.schema.json`
- immutable-candidate follow-on: `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`

## Why this needs a hard decision

Once the archive says **work on a copy** and **ordinary save stays local**, the next ambiguity is what the system means when the user really does want those edited bytes to become the next version of something authoritative.
If DeriveBSD leaves that vague, the easiest implementation path becomes the real product:

- editor-specific “save back” or “replace original” behaviors become source authority,
- cloud/document adapters decide version semantics ad hoc,
- support bundles cannot tell “edited derivative” from “candidate successor,”
- and the system loses a stable evidence join between imported origin, local edits, and later publication/check-in.

That is too much ambiguity for the ordinary workstation lane.
DeriveBSD needs one small, typed answer.

## Decision

The first official source-lineage act after local editing is now a narrow typed lane:

- `content.reintegrate.plan`
- `content.reintegrate.receipt`

This lane is for one thing only:
**register the exact working-copy output as an explicit local successor candidate of a known authoritative origin without pretending that local save already replaced the source.**

## The canonical join

### 1) Bind back to the exact local authoring act

A reintegration plan binds the exact local authoring chain through:

- `source.working_copy_receipt_digest`
- `source.working_copy_output_digest`
- `source.import_receipt_digest`
- `source.authoritative_origin_digest`

That means “this is the next version candidate” is not just a file path or app-side intention.
It is a digest-bound claim about one exact imported lineage, one exact working copy, and one exact authoritative origin.

### 2) Keep reintegration local-first

The v0 lane is intentionally **local-first**.
A reintegration receipt records that the edited bytes are now a typed **successor candidate** of the authoritative origin.
It does **not** by itself perform a remote check-in, overwrite, ticket attachment replacement, or cloud-version upload.
Those remain later adapter acts.

### 3) Forbid replace-in-place semantics in the official lane

`content.reintegrate.plan` and `content.reintegrate.receipt` now carry a required `boundary` object with three fixed v0 guarantees:

- `candidate_posture = local-successor-candidate`
- `replace_in_place = forbidden`
- `upstream_finalize = separate-adapter-required`
- `candidate_snapshot = immutable`
- `later_edits = new-candidate-required`

That means the official DeriveBSD lane does not say:

- “the source was already updated because the app saved,”
- “the imported original was replaced in place,”
- or “whatever the remote service did is now the source of truth.”

It says something narrower and more implementable:
**these exact locally edited bytes are now the explicit candidate successor of this exact authoritative origin.**

`docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then makes the next consequence explicit too: that candidate is an immutable snapshot of one digest, not a moving path, so later local edits require a new candidate. `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` then fixes the next multi-candidate rule: later candidates supersede earlier ones only by explicit digest through `supersession.supersedes_receipt_digest`, not by recency alone. `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` then fixes the next scope/evidence rule: that explicit supersession remains inside the same authoritative origin and carries the exact superseded candidate/origin digests too. `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` then fixes the next freshness rule: that supersession must still target the current unsuperseded candidate, and stale supersession attempts fail closed instead of being rebound. `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md` then fixes the next operability rule: those stale denials must also carry observed current-head denial evidence and the fresh explicit recovery target instead of a generic stale error. `docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md` then fixes the next retry rule too: that fresh recovery act must stay denial-joined and head-pinned through `stale_denial_receipt_digest` plus the exact `expected_current_*` digests instead of becoming a generic retry.

### 4) Keep the first target shape narrow

The v0 target stays intentionally small:

- `target.scope = same-authoritative-origin`
- `target.action = register-successor-candidate`

So the first accepted lane is not a giant document-management system.
It is just the minimal typed bridge from local authoring to later authoritative update workflows.

## Practical model

1. foreign content enters through `content.import.*`
2. ordinary viewing uses `document_viewing`
3. explicit editing uses `content.working-copy.*`
4. ordinary save updates the working-copy output
5. explicit reintegration uses `content.reintegrate.*`
6. later export/publish/check-in/upload adapters may finalize that successor candidate through separate policies and receipts

That is the smallest model that preserves provenance and still lets ordinary work eventually become authoritative.

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** emergency locally edited procedures or maintenance payloads can become typed successor candidates without letting shell/editor behavior act as source authority.
- **B / secure workstation:** the archive now has a boring exact answer for “I edited the working copy and now want it to count as the next version.”
- **C / general-purpose OS:** convenience adapters can still exist later, but the official Derive-managed lane stays explicit and evidence-bound.
- **D / appliance factory / regulatory:** revised SOPs, reports, manifests, or maintenance artifacts can become explicit successor candidates before later approval/publish/finalization flows, keeping revision history auditable.

## What remains intentionally open

This doc does **not** settle:

- remote DMS/VCS/cloud protocol specifics,
- collaborative locking/check-out semantics,
- how candidate supersession should interact with later approval/finalization lanes once `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` and `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` fix the no-latest-wins / same-origin floor,
- or which finalization adapters deserve first-class status.

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
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`

Last updated: 2026-03-20r345
