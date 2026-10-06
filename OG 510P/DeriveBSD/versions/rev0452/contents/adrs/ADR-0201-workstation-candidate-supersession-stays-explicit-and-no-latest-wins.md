# ADR-0201: Workstation candidate supersession stays explicit and no latest-wins

Date: 2026-03-20  
Status: Accepted

## Context

`ADR-0195` fixed the imported-document open floor: import first, route second, and keep ordinary handling inside bounded `document_viewing` / `document_editing` roles.
`ADR-0196` then fixed the mutation floor: foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of editing the imported original in place.
`ADR-0197` made that copy act typed as `content.working-copy.plan` / `content.working-copy.receipt` and made allow-path edit routes prove they opened the working copy via `working_copy_receipt_digest`.
`ADR-0198` then fixed local save scope: ordinary save stays on the working-copy output, and source write-back is a separate explicit act rather than an editor side effect.
`ADR-0199` then made source-lineage intent explicit: `content.reintegrate.plan` / `content.reintegrate.receipt` register a local successor candidate of the same authoritative origin instead of replacing the source in place.
`ADR-0200` then made each candidate immutable: the receipt names one exact snapshot and later edits require a fresh candidate rather than mutating the earlier one.

That leaves the next expensive ambiguity:
**if several immutable candidates now exist for the same authoritative origin, does the newest one automatically become "the current candidate" by recency, version label, or path folklore, or must the archive say exactly when one candidate supersedes another?**

If the archive leaves that vague, implementations drift back toward ambient document-manager behavior:

1. the newest receipt silently wins because it is later in time,
2. human `version_label` text starts acting like hidden authority,
3. support/export surfaces cannot distinguish siblings from explicit successor relationships,
4. approval/finalization adapters lose the exact candidate chain they were supposed to review,
5. and product shapes A–D start answering "which candidate is current?" differently.

## Decision

1. The v0 `content.reintegrate.*` lane now treats candidate ordering as **explicit supersession only**.
   Later candidates do **not** automatically supersede earlier ones just because they are newer.

2. `content.reintegrate.plan` and `content.reintegrate.receipt` now carry two more required boundary guarantees:
   - `candidate_ordering = explicit-supersession-only`
   - `recency_precedence = forbidden`

3. The same artifacts now also carry a required `supersession` object:
   - `mode = none`, or
   - `mode = supersede-prior-candidate` plus `supersedes_receipt_digest` naming the exact earlier `content.reintegrate.receipt` being superseded.

4. Therefore, a successful later `content.reintegrate.receipt` does **not** become preferred/current by timestamp, path, or label alone.
   It becomes an explicitly related successor candidate only when the receipt itself says so.

5. The v0 lane stays intentionally narrow:
   - no ambient "latest candidate for this path" rule,
   - no auto-current pointer by recency,
   - no silent promotion because a human version label looked newer,
   - and no adapter permission to infer supersession without a digest-bound declaration.

## Consequences

### Positive

- Candidate chains stay digest-bound and queryable.
- Review/finalization lanes can talk about "candidate B supersedes candidate A" without guessing from timestamps.
- Profile `B` gets a boring exact answer when several drafts exist.
- Profile `D` gets cleaner audit trails because sibling candidates remain distinct unless supersession is declared.

### Trade-offs

- Friendly UX must surface explicit supersession instead of assuming newest-wins.
- Some integrations will have to emit one more digest join when the user means "this draft supersedes that earlier candidate."

## Not decided here

This ADR does **not** decide:

- how approval/finalization lanes choose among explicit candidates,
- whether a later adapter should be able to mark one candidate as preferred without superseding another,
- or which remote document/version adapters deserve first-class support.

## Related

- `adrs/ADR-0199-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `adrs/ADR-0200-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`
- `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`
- `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`
