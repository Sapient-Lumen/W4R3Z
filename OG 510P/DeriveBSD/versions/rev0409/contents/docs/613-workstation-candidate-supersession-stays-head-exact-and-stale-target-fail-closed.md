# Workstation candidate supersession stays head-exact and stale-target fail-closed

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
`docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` then kept that relationship same-origin and self-describing: the superseding receipt also carries the displaced candidate/origin digests.

This doc makes the next small but expensive cut:
**an explicit supersession claim must target the current unsuperseded candidate for that authoritative origin, and stale supersession attempts fail closed instead of being silently rebound or normalized.** `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md` then fixes the next consequence too: the denial must also carry the observed current head and the exact fresh-explicit recovery target. `docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md` then fixes the next follow-on too: the fresh recovery act must stay denial-joined and head-pinned instead of degrading into a generic retry.

See also:
- ADR: `adrs/ADR-0203-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md`
- same-origin self-describing supersession floor: `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`
- explicit supersession floor: `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`
- canonical schemas: `spec/content.reintegrate.plan.schema.json`, `spec/content.reintegrate.receipt.schema.json`

## Why this needs a hard decision

Once the archive says **immutable candidates**, **explicit supersession**, and **same-origin self-describing lineage**, the next leak is to leave the target freshness rule ambiguous.
Then the easiest implementation path becomes the real product:

- two later candidates can both claim to supersede the same earlier candidate,
- a stale supersession request can be silently rebound to whatever candidate currently looks latest,
- support/export tooling has to guess whether a supersession acted on the live predecessor or on stale history,
- and profile `B` quietly reopens branch/merge folklore without ever saying so.

That is still too much ambiguity for DeriveBSD’s evidence model.
If supersession exists at all, it should act on the current unsuperseded predecessor or fail.

## Decision

`content.reintegrate.plan` and `content.reintegrate.receipt` now carry two more required boundary guarantees:

- `supersession_target_posture = current-unsuperseded-candidate-only`
- `stale_target_handling = fail-closed`

When `supersession.mode = supersede-prior-candidate`, the named `supersedes_receipt_digest` / `superseded_candidate_digest` pair must still describe the **current unsuperseded candidate** for that same authoritative origin at apply time.

If that earlier candidate has already been superseded, or if some other candidate became current first, the act must **deny/fail**.
It must not silently:

- retarget to a newer candidate,
- register a sibling candidate as though supersession succeeded,
- or reinterpret the act as a merge/rethread operation.

That means the official reintegration lane stays **head-exact compare-and-swap-shaped**, not merely **some-earlier-candidate-shaped**.

## What the boundary means

### 1) Supersession targets the live predecessor, not any historical candidate

A newer candidate may explicitly displace the current unsuperseded predecessor for that authoritative origin.
It may not reach back and supersede an already-displaced historical candidate.

### 2) Stale intents stay stale

If another candidate became current after the superseding plan was prepared, the older supersession intent does not get “helpfully” rebound.
The system should force a fresh explicit act against the now-current predecessor.

### 3) Sibling drafts remain possible, but supersession stays linear

The archive is **not** forbidding multiple sibling candidates.
It is only saying that the explicit **displace-this-candidate** act is linear and current-head exact.
If the product ever wants first-class branch/merge semantics, that is a later explicit topic.

### 4) Support/export surfaces get a boring answer

Detached tooling can now answer a simple question without reading operator minds:
**did this candidate successfully displace the current predecessor, or was the request stale and rejected?** When the request is stale, `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md` now also requires the receipt to carry the observed current head directly rather than leaving that answer to external storage lookup.

## Practical model

1. import foreign bytes through `content.import.*`
2. view first in `document_viewing`
3. issue an explicit writable artifact through `content.working-copy.*`
4. save locally onto that working-copy output
5. register an immutable successor candidate through `content.reintegrate.*`
6. if a later candidate should displace the current predecessor, name that exact current unsuperseded candidate by digest
7. if the predecessor changed first, deny/fail and require a fresh explicit supersession act
8. keep any later review/finalization/publish adapter as a separate act

## Why this is still small enough for v0

This doc does **not** invent a full branch/merge or collaborative editing subsystem.
It only prevents the already-accepted explicit-supersession lane from collapsing back into stale-target retries, best-effort rebinding, or branch folklore.

The archive still does **not** decide:

- branch/merge semantics,
- approval/finalization policy over candidate chains,
- or remote version-upload/check-in adapters.

It only says that the local supersession act is exact enough to race safely and explain later.

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
- `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`

Last updated: 2026-03-20r345
