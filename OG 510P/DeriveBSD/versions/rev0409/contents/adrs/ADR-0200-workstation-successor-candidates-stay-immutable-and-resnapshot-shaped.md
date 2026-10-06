# ADR-0200: Workstation successor candidates stay immutable and resnapshot-shaped

Date: 2026-03-20  
Status: Accepted

## Context

`ADR-0195` fixed the imported-document open floor:
import first, route second, and keep ordinary handling inside bounded `document_viewing` / `document_editing` roles.
`ADR-0196` then fixed the mutation floor:
foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of editing the imported original in place.
`ADR-0197` made that copy act typed as `content.working-copy.plan` / `content.working-copy.receipt` and made allow-path edit routes prove they opened the working copy via `working_copy_receipt_digest`.
`ADR-0198` then fixed local save scope:
ordinary save stays on the working-copy output, and source write-back is a separate explicit act rather than an editor side effect.
`ADR-0199` then made source-lineage intent explicit:
`content.reintegrate.plan` / `content.reintegrate.receipt` register a local successor candidate of the same authoritative origin instead of replacing the source in place.

That leaves the next expensive ambiguity:
**once a successor candidate exists, does it keep meaning the exact bytes that were reviewed at registration time, or can later saves silently mutate that same candidate and turn the receipt into a moving file-path alias?**

If the archive leaves that vague, implementations drift back toward folklore:

1. “candidate registered” becomes a mutable pointer to whatever bytes happen to be on disk later,
2. local editors can keep changing the same supposed candidate without emitting new evidence,
3. support/export surfaces cannot tell which exact bytes were reviewed or approved,
4. and any future finalization/check-in adapter loses the stable digest-bound object it was supposed to promote.

## Decision

1. The v0 `content.reintegrate.*` lane now treats every successor candidate as an **immutable snapshot** of one exact working-copy output digest.

2. `content.reintegrate.plan` and `content.reintegrate.receipt` now carry two more required boundary guarantees:
   - `candidate_snapshot = immutable`
   - `later_edits = new-candidate-required`

3. Therefore, a successful `content.reintegrate.receipt` does **not** name a mutable working path, live editor buffer, or “current document state.”
   It names one exact digest-bound candidate snapshot at one point in time.

4. If the user keeps editing after that receipt exists, those later bytes are **not** part of the earlier candidate.
   They must first exist as a later working-copy output digest and then, if source-lineage intent still exists, get their **own** later `content.reintegrate.receipt`.

5. The v0 model stays intentionally narrow:
   - no mutable candidate records,
   - no in-place candidate rewrite,
   - no “latest candidate for this path” folklore,
   - and no adapter permission to silently retarget an earlier candidate at newer local bytes.

## Consequences

### Positive

- Review, approval, and finalization lanes now have a stable exact object to talk about.
- Support bundles can answer which exact bytes became candidate `N` without inferring state from file timestamps or paths.
- Profile `D` gets a cleaner revision-control story: each candidate is a frozen auditable object.
- Profile `B` gets a predictable implementation rule when users continue editing after an earlier candidate already exists.

### Trade-offs

- Ordinary authoring flows that keep iterating will emit more than one candidate over time.
- Future UX may want a friendly “candidate superseded by newer candidate” summary, but the archive no longer gets to hide that behind one mutable record.

## Not decided here

This ADR does **not** decide:

- how candidate supersession/review status should be summarized across multiple candidates,
- which approval lanes should gate promotion/finalization,
- or which remote adapters deserve first-class finalization support.

## Related

- `adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md`
- `adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md`
- `adrs/ADR-0197-workstation-working-copy-receipts-and-edit-route-joins.md`
- `adrs/ADR-0198-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- `adrs/ADR-0199-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`
