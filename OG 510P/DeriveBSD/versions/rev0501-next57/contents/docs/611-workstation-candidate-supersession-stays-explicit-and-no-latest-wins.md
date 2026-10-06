# Workstation candidate supersession stays explicit and no latest-wins

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

This doc makes the next small but expensive cut:
**when several immutable candidates exist for the same authoritative origin, none automatically becomes current just because it is newer; candidate ordering stays explicit, and supersession must name the exact earlier receipt it supersedes.**

See also:
- ADR: `adrs/ADR-0201-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`
- explicit reintegration floor: `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- immutable-candidate floor: `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`
- same-origin self-description follow-on: `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`
- canonical schemas: `spec/content.reintegrate.plan.schema.json`, `spec/content.reintegrate.receipt.schema.json`

## Why this needs a hard decision

Once the archive says **explicit reintegration** and **immutable candidate snapshots**, the next leak is to leave multi-candidate ordering ambient in practice.
Then the easiest implementation path becomes the real product:

- the newest receipt silently wins because it is newer,
- a human `version_label` starts acting like hidden authority,
- support bundles cannot tell sibling candidates from explicit supersession,
- finalization/review lanes cannot prove which earlier candidate was superseded,
- and profile `B` ends up depending on document-manager folklore instead of typed evidence.

That is too much ambiguity for DeriveBSD’s evidence model.
Candidate ordering needs to be a typed act too.

## Decision

`content.reintegrate.plan` and `content.reintegrate.receipt` now carry two more required boundary guarantees:

- `candidate_ordering = explicit-supersession-only`
- `recency_precedence = forbidden`

They also now carry a required `supersession` object with one of two modes, and `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` then further tightens that object so explicit supersession remains same-authoritative-origin-only and names the exact prior candidate snapshot too:

- `mode = none`
- `mode = supersede-prior-candidate` plus `supersedes_receipt_digest` naming the exact earlier `content.reintegrate.receipt` being superseded

That means the official reintegration lane stays **digest-chain-shaped**, not **latest-wins-shaped**.

## What the boundary means

### 1) Newer does not mean current

A later `content.reintegrate.receipt` does not become preferred/current merely because it was created later.
Recency alone carries no authority here.

### 2) Supersession is a separate explicit relationship

If candidate B should supersede candidate A, candidate B must say so explicitly by digest through `supersession.mode = supersede-prior-candidate` and `supersession.supersedes_receipt_digest`.
That creates a typed candidate-to-candidate relationship instead of forcing tools to infer one.

### 3) Sibling candidates may exist

The v0 lane intentionally permits multiple sibling candidates against the same authoritative origin.
If `supersession.mode = none`, the archive does not pretend one sibling is current just because it happened later.

### 4) Human labels remain descriptive, not authority

`target.version_label` may still help humans, but it does not replace digest-bound supersession.
A nice-looking or lexically newer label does not supersede anything by itself.

## Practical model

1. import foreign bytes through `content.import.*`
2. view first in `document_viewing`
3. issue an explicit writable artifact through `content.working-copy.*`
4. save locally onto that working-copy output
5. register an immutable successor candidate through `content.reintegrate.*`
6. if a later candidate should replace an earlier candidate in the local lineage story, declare that exact earlier receipt digest explicitly
7. let later approval/finalization adapters consume the exact candidate chain they were given

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** field-authored revisions can remain auditably distinct until an operator explicitly supersedes an earlier candidate.
- **B / secure workstation:** "I made another draft" and "this new draft supersedes that earlier candidate" now have different typed answers.
- **C / general-purpose OS:** friendly adapters may still present a simpler UX, but the underlying Derive-managed lane stays explicit.
- **D / appliance factory / regulatory:** explicit candidate supersession yields cleaner sign-off and evidence review than ambient newest-wins behavior.

## What remains intentionally open

This doc does **not** settle:

- approval/finalization policy over explicit candidate chains,
- whether there should be a later typed "preferred candidate" status distinct from supersession,
- whether `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` should eventually grow into first-class branch/merge semantics,
- or which remote version/check-in adapters deserve first-class support.

Those remain future RFC/ADR work.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`
- `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`
- `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`

Last updated: 2026-03-20r343
