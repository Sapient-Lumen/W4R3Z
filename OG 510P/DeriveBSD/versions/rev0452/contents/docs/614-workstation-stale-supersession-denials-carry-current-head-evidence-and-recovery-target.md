# Workstation stale supersession denials carry current-head evidence and recovery target

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
`docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` then fixed freshness: supersession must target the current unsuperseded candidate, and stale supersession attempts fail closed instead of being rebound.

This doc makes the next small but expensive cut:
**when that stale supersession denial happens, the receipt must also carry the observed current head and the boring recovery target instead of degrading into a generic stale error.**

See also:
- ADR: `adrs/ADR-0204-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md`
- stale-target fail-closed floor: `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md`
- canonical schemas: `spec/content.reintegrate.plan.schema.json`, `spec/content.reintegrate.receipt.schema.json`
- canonical stale-target denial profile: `spec/content.reintegrate.receipt.stale-target-denied.schema.json`
- fresh denial-joined retry follow-on: `docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md`

## Why this needs a hard decision

Once the archive says **explicit same-origin supersession** and **current-head exact stale-target failure**, one more support/export gap remains.
A denial can still be technically correct but operationally weak if it only says “stale” and forces everything else to rediscover the live head out-of-band.
Then the easiest implementation path becomes the real product:

- the denial has no portable answer for which candidate currently won,
- support bundles can prove the rejected target but not the current head that displaced it,
- retry tooling must reopen storage state and guess what to supersede next,
- and operators drift back toward path/name/timestamp folklore for recovery.

That is still too much ambiguity for DeriveBSD’s evidence spine.
If the archive treats stale supersession as a first-class denial, it should also treat the observed current head as first-class evidence.

## Decision

`content.reintegrate.plan.boundary` and `content.reintegrate.receipt.boundary` now carry two more required guarantees:

- `stale_target_evidence = observed-current-head-required`
- `stale_target_recovery = fresh-explicit-supersession-required`

`content.reintegrate.receipt.result` now also admits a typed stale-target denial profile:

- `status = deny`
- `reason_code = stale-supersession-target`
- `recovery_posture = fresh-explicit-supersession-required`
- `observed_current_receipt_digest`
- `observed_current_candidate_digest`
- `observed_current_authoritative_origin_digest`

When `supersession.mode = supersede-prior-candidate` loses because the named predecessor is no longer the current unsuperseded candidate, the denial must carry that exact observed current-head summary.

## What the boundary means

### 1) Stale denial stays a denial

The act is still rejected.
The receipt does **not** become an implicit success, silent retarget, or best-effort rebind.

### 2) The denial names what actually won

Detached readers can now answer one boring question without reopening live storage state:
**which current candidate/head made this supersession target stale?**

That answer is carried directly on the denial receipt through:

- `result.observed_current_receipt_digest`
- `result.observed_current_candidate_digest`
- `result.observed_current_authoritative_origin_digest`

### 3) Recovery stays explicit

The denial also carries one stable recovery answer:

- `result.recovery_posture = fresh-explicit-supersession-required`

That means the caller must build a new explicit supersession act against the observed current head.
The archive does **not** allow the original request to be silently rewritten around that winner.

### 4) Detached bundles become queryable enough

Support/export surfaces can now answer both sides of the race in one artifact:

- what stale predecessor the request tried to displace,
- and what current head actually blocked it.

That keeps the local lineage queryable away from ambient storage lookups.

## Practical model

1. import foreign bytes through `content.import.*`
2. view first in `document_viewing`
3. issue an explicit writable artifact through `content.working-copy.*`
4. save locally onto that working-copy output
5. register an immutable successor candidate through `content.reintegrate.*`
6. explicitly supersede the current predecessor by digest
7. if another candidate became current first, emit a stale-target denial that carries the observed current head and `fresh-explicit-supersession-required`
8. require a fresh explicit supersession act rather than rebinding the old one

## Why this is still small enough for v0

This doc does **not** invent branching, merge conflict resolution, collaborative locking, or automatic retry/orchestration machinery.
It only keeps one already-accepted denial boundary self-describing enough to support deterministic support bundles and boring operator recovery.

The archive still does **not** decide:

- branch/merge semantics,
- finalization/approval policy over candidate chains,
- or remote adapter conflict resolution.

It only says that stale-target denial must remain exact, portable, and recovery-targeted.

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
- `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`
- `spec/content.reintegrate.receipt.stale-target-denied.schema.json`

Last updated: 2026-03-20r345
