# ADR-0196: Workstation imported foreign documents stay view-first and working-copy-shaped

Date: 2026-03-20
Status: Accepted

## Context

`adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md` already fixed the high-level shape of workstation document handling:

- cross-compartment file `open` / `view` / `edit` is import-shaped first and route-shaped second
- imported content should not quietly fall back to host rendering
- the baseline role vocabulary stays small: `document_viewing` and `document_editing`
- route evidence can point back to the exact `content.import.receipt` through `intent.route.receipt.import_receipt_digest`

That was the right first cut, but one expensive ambiguity remained:

- if a document came from a foreign/quarantined source, should the default “edit” path open that exact imported artifact in an editor and save back over it?
- should `document_editing` be treated as just another same-class target for any imported file once chooser/default state exists?
- should a sanitized derivative be considered equivalent to an authoring workspace simply because it is easier to implement that way?

If the archive leaves that open, the easiest product path will quietly become:

- foreign attachments open in an editor and save back over the original bytes,
- “view” and “edit” collapse into whichever handler is most convenient,
- quarantine/provenance boundaries become weaker precisely when users start changing risky files,
- and support/export surfaces lose the distinction between “we inspected imported bytes” and “we deliberately started authoring a working copy.”

Compartmentalized systems hint at a narrower answer. Qubes makes opening files in a disposable routine and also treats sanitization as a separate act that yields a safer derivative, while XDG’s Documents portal keeps sandbox file access on an exported controlled view instead of ambient path authority. Those patterns point toward explicit file-state transitions rather than “just let the editor have the original.”

We need one more hard boundary so the workstation story stays coherent without inventing a new subsystem.

## Decision

1. **Imported foreign/quarantined documents are view-first by default.**
   - Ordinary `open` / `view` should route them to `document_viewing`.
   - `document_editing` is not the baseline target for newly imported foreign bytes.
2. **Editing foreign imported bytes requires an explicit working-copy transition.**
   - The baseline archive does **not** treat “open in editor and save back over the imported original” as the ordinary path.
   - A user/admin workflow may create a separate working copy, promoted derivative, or authoring clone, but that is a distinct act from merely opening the imported artifact.
3. **Sanitized/converted derivatives stay view-first unless explicitly turned into working copies.**
   - Sanitization makes inspection/export safer.
   - It does not automatically mean the result should enter the ordinary `document_editing` lane.
4. **The trusted chooser/default layer stays role-bound, but provenance still constrains role eligibility.**
   - A remembered `document_editing` target does not imply every imported foreign document may route there.
   - Policy must still deny edit-in-place for foreign/quarantined originals unless an explicit compatibility/override lane applies.
5. **Profile `C` may later document a bounded compatibility adapter for local-admin in-place editing, but that is not the official workstation baseline and must not weaken `B`.**
6. This ADR still does **not** standardize a giant MIME taxonomy, collaborative authoring semantics, or a new “document promotion” artifact family. It fixes only the default boundary needed to keep imported files honest.

## Consequences

### What this locks now

- Imported attachments/downloads/reports can be inspected without silently becoming ambient authoring inputs.
- The archive now distinguishes three practical states even without inventing new artifact kinds:
  - imported foreign original,
  - sanitized/converted inspection derivative,
  - explicit working copy / authoring copy.
- `document_viewing` and `document_editing` remain useful without collapsing into “same thing, different app.”
- Profile **B** gets a safer boring default: **work on a copy** instead of **edit the imported original**.
- Profile **D** gets a more defensible regulatory/appliance story because foreign procedures/reports remain inspectable without unreviewed in-place mutation.

### What stays intentionally open

This ADR does **not** decide:

- the exact future artifact/receipt shape for the working-copy / promote act,
- MIME-specific heuristics beyond the new view-first rule,
- which classes should default to disposable vs persistent `document_viewing`,
- rich collaboration/version-control workflows,
- or whether specific profile-`C` compatibility adapters are worth standardizing.

## Why this is the smallest viable cut

The archive already had the pieces:

- import evidence,
- role-bound routing,
- bounded viewer/editor roles,
- quarantine/origin metadata,
- and sanitization lanes.

The missing move was simply to refuse the convenient-but-dangerous equivalence between **viewing imported foreign bytes** and **editing a trusted working document**.

That distinction is small, but it prevents a lot of future drift.

## Wiring

- file-open floor: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- new document-edit boundary doc: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- portals/powerbox: `docs/179-portals-and-powerbox.md`
- risk/open questions: `docs/266-open-questions-and-risk-register.md`
