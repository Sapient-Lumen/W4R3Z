# Workstation candidate supersession stays same-origin and self-describing

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

`docs/605-workstation-file-open-import-and-bounded-document-roles.md` fixed the imported-document open boundary: import first, route second, and keep ordinary handling inside bounded `document_viewing` / `document_editing` roles.
`docs/606-workstation-imported-foreign-documents-stay-view-first.md` then fixed the mutation floor: foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of editing the imported original in place.
`docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` then made that transition typed and joinable through `content.working-copy.plan` / `content.working-copy.receipt` plus `working_copy_receipt_digest` on allow-path edit routes.
`docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` then fixed local save scope: ordinary save stays on the working-copy output, and source write-back remains a separate explicit act.
`docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` then fixed the first source-lineage act: `content.reintegrate.plan` / `content.reintegrate.receipt` register a local successor candidate of the same authoritative origin instead of replacing the source in place.
`docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then made each candidate immutable: the receipt names one exact snapshot, and later edits require a fresh candidate.
`docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` then made candidate ordering explicit: one candidate does not automatically win by recency or label, and supersession must point at the exact earlier receipt digest.

This doc makes the next small but expensive cut:
**an explicit supersession claim must stay within the same authoritative origin, and the supersession object must carry enough digest evidence to name the exact prior snapshot being displaced without reopening earlier receipts.**

See also:
- ADR: `adrs/ADR-0202-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`
- explicit supersession floor: `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`
- explicit reintegration floor: `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- canonical schemas: `spec/content.reintegrate.plan.schema.json`, `spec/content.reintegrate.receipt.schema.json`
- stale-denial follow-on: `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md`

## Why this needs a hard decision

Once the archive says **same authoritative origin**, **immutable candidates**, and **explicit supersession**, the next leak is to let a supersession claim stay under-specified in practice.
Then the easiest implementation path becomes the real product:

- a new candidate can claim to supersede an unrelated prior candidate just by pointing at some earlier receipt digest,
- support bundles must reopen that earlier receipt just to learn which candidate snapshot was actually displaced,
- cross-origin or cross-document replacement pressure sneaks back in through a superficially explicit but still under-specified supersession lane,
- and profile `B` ends up depending on adapter folklore instead of one digest-bound candidate lineage story.

That is still too much ambiguity for DeriveBSD’s evidence model.
Supersession needs to stay same-origin and self-describing.

## Decision

`content.reintegrate.plan` and `content.reintegrate.receipt` now carry one more required boundary guarantee:

- `supersession_scope = same-authoritative-origin-only`

When `supersession.mode = supersede-prior-candidate`, the `supersession` object must now also carry:

- `supersedes_receipt_digest`
- `superseded_candidate_digest`
- `superseded_authoritative_origin_digest`

The prior authoritative-origin digest must equal the current `source.authoritative_origin_digest`.
A mismatch must not silently downgrade to `mode = none` or to an unrelated sibling candidate registration.

That means the official reintegration lane stays **same-origin digest-lineage-shaped**, not merely **some-earlier-receipt-shaped**. `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` then fixes the next freshness/race rule too: explicit supersession must still target the current unsuperseded candidate, and stale supersession attempts fail closed instead of being rebound or normalized later.

## What the boundary means

### 1) Supersession cannot hop authoritative origins

A candidate for origin X may not supersede a prior candidate from origin Y.
Explicit supersession does not relax the original `same-authoritative-origin` rule from `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`.

### 2) The superseded snapshot must be named exactly

Naming only the earlier receipt digest is no longer enough.
The newer receipt must also carry `superseded_candidate_digest`, so detached support/export surfaces can answer which exact prior immutable snapshot was displaced.

### 3) Same-origin proof travels with the act

The newer receipt must also carry `superseded_authoritative_origin_digest`.
That keeps same-origin intent self-describing at the act boundary instead of forcing downstream tooling to reopen the earlier receipt body just to recover origin scope.

### 4) Mismatch stays fail-closed

If the claimed earlier receipt, earlier candidate digest, and authoritative-origin digest do not line up, the operation is not silently normalized into:

- `mode = none`,
- a fresh unrelated sibling candidate,
- or any other “best effort” latest-wins fallback.

The supersession claim is wrong and should deny/fail.

## Practical model

1. import foreign bytes through `content.import.*`
2. view first in `document_viewing`
3. issue an explicit writable artifact through `content.working-copy.*`
4. save locally onto that working-copy output
5. register an immutable successor candidate through `content.reintegrate.*`
6. if a later candidate should displace an earlier one, name the exact earlier receipt digest, the exact earlier candidate digest, and the same authoritative-origin digest
7. keep any later review/finalization/publish adapter as a separate act

## Why this is still small enough for v0

This doc does **not** invent a full document-management subsystem.
It only prevents the already-accepted explicit-supersession lane from collapsing back into vague cross-document replacement folklore.

The archive still does **not** decide:

- review/approval/finalization policy over candidate chains,
- remote version-upload/check-in adapters,
- or any “preferred candidate” status beyond explicit local supersession.

It only says that the local candidate lineage must remain exact enough to reason about without path or timestamp folklore.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`
- `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`

Last updated: 2026-03-20r344


`docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md` then fixes the stale-denial side of the same detached evidence story too: if that same-origin supersession loses its current-head race later, the denial must carry `observed_current_receipt_digest` and the other observed current-head digests directly instead of sending support bundles back to ambient storage lookup.
