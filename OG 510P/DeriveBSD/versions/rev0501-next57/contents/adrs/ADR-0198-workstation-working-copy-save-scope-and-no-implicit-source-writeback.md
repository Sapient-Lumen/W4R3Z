# ADR-0198: Workstation working-copy save scope and no implicit source write-back

- Status: Accepted
- Date: 2026-03-20

## Context

`ADR-0195` fixed the imported-document open boundary:
import first, route second, and keep ordinary handling inside bounded `document_viewing` / `document_editing` roles.
`ADR-0196` then fixed the mutation floor:
foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of saving back over the imported original by default.
`ADR-0197` then fixed the next implementation gap by making that transition typed as `content.working-copy.plan` / `content.working-copy.receipt` and by joining allowed edit routes back to the exact working-copy act through `working_copy_receipt_digest`.

That still left one practical ambiguity large enough to derail implementation:
**once an editor has the issued working copy open, what does ordinary “Save” mean, and may it quietly write back into the imported source lineage?**

If the archive leaves that answer to application behavior, the easiest path will quietly become the product:

1. editing in a disposable or helper app can overwrite the imported source by default,
2. support/export surfaces can no longer distinguish “modified local working copy” from “replaced imported original,”
3. implementations drift toward Qubes-style “edit in disposable and save back over the original” behavior because it is familiar,
4. and any future origin-reintegration workflow starts from folklore instead of a bounded explicit act.

## Decision

1. `content.working-copy.plan` and `content.working-copy.receipt` now carry a required `boundary` object with two fixed v0 guarantees:
   - `default_save_target = working-copy-output`
   - `source_writeback = separate-act-required`

2. Ordinary save within the imported-document working-copy lane means **save the issued working-copy artifact**.
   It does **not** mean “write back to the imported source,” “replace the imported attachment,” or “update the authoritative origin.”

3. Any act that pushes modified bytes back toward an authoritative origin remains a separate explicit boundary.
   It may later be standardized as export, publish, check-in, import-as-new-version, or another narrow act, but it is not implicit in `content.working-copy.*` and not bundled into ordinary editor save semantics.

4. `ADR-0197` still stands: allow-path edit routes use `working_copy_receipt_digest` to prove which writable artifact was opened.
   This ADR adds the next local guarantee: that the writable artifact has its own save scope and does not smuggle origin mutation back in through application convenience behavior.

5. This decision is intentionally narrow and applies to the **imported-document working-copy lane**.
   It does not prohibit direct local editing of already-trusted project files that never entered via `content.import.*`.

## Consequences

Good:

- editors get one boring baseline answer for imported-document authoring,
- support/export surfaces can distinguish imported evidence from locally mutated working state,
- future reintegration flows have room to become explicit typed acts instead of retrofitting application folklore,
- and profile **B** stays coherent without copying the most convenience-shaped disposable-edit patterns from other systems.

Trade-offs:

- some familiar “save back over the original” behavior is intentionally rejected,
- compatibility adapters for profile **C** may need extra explicit UX later,
- and future check-in / publish-back lanes still need separate ADR work.

## What this does not decide

Still open:

- version-control or collaborative check-in semantics,
- exact storage/retention policy for working-copy descendants,
- exact UI wording for Save As / Export / Replace-style actions,
- and any future typed lane that reintegrates locally edited content with an upstream origin.

## Pointers

- `adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md`
- `adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md`
- `adrs/ADR-0197-workstation-working-copy-receipts-and-edit-route-joins.md`
- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- `spec/content.working-copy.plan.schema.json`
- `spec/content.working-copy.receipt.schema.json`
