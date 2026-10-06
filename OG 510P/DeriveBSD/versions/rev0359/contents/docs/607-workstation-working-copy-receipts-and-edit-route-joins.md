# Workstation working-copy receipts and edit-route joins

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

`docs/605-workstation-file-open-import-and-bounded-document-roles.md` already fixed the broad workstation document path:
import first, route second, and keep document handling inside bounded `document_viewing` / `document_editing` roles.
`docs/606-workstation-imported-foreign-documents-stay-view-first.md` then fixed the next mutation boundary:
foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition rather than saving back over the imported original by default.

This doc makes the next small but expensive cut:
**the working-copy transition becomes a typed `content.working-copy.plan` / `content.working-copy.receipt` act, and allowed document-edit routes should carry `working_copy_receipt_digest` so the edit lane stays provably separate from the imported original.**

See also:
- ADR: `adrs/ADR-0197-workstation-working-copy-receipts-and-edit-route-joins.md`
- file-open floor: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- view-first mutation floor: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- canonical schemas: `spec/content.working-copy.plan.schema.json`, `spec/content.working-copy.receipt.schema.json`, `spec/intent.route.receipt.document-edit-allow.schema.json`
- save-scope follow-on: `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- reintegration follow-on: `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- immutable-candidate follow-on: `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`

## Why this needs a hard decision

Once the archive says **work on a copy**, the next ambiguity is whether that phrase is only UX prose or an actual typed system act.
If DeriveBSD leaves it informal, the easiest implementation path will quietly become the real product:

- the viewer or editor silently clones the imported artifact,
- the user cannot later prove when the copy was made,
- support/export surfaces cannot tell which writable file came from which imported source,
- and an allowed edit route can only prove that *a* file opened, not that it was the explicit working copy rather than the foreign original.

That is too much ambiguity for the ordinary workstation lane.
The archive needs one small, typed answer.

## Decision

The explicit authoring transition is now its own narrow typed lane:

- `content.working-copy.plan`
- `content.working-copy.receipt`

This lane is for one thing only:
**make an imported document or inspection derivative editable as a separate working artifact without pretending the imported original became ordinary mutable state.**

## The canonical join

### 1) Bind back to the exact imported source

A working-copy plan points at the exact imported lineage through:

- `source.import_receipt_digest`
- `source.source_output_digest`

That means “make editable copy” is not just a file-system copy request.
It is a digest-bound transition from a specific imported original or inspection derivative.

### 2) Emit a separate writable artifact

A working-copy receipt records a distinct output digest/path for the new writable artifact.
The imported source remains what it was:

- imported foreign original, or
- inspection-oriented sanitized/converted derivative.

The new output is the first ordinary writable document in this chain. `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` now fixes the next local rule too: ordinary save targets that working-copy output (`default_save_target = working-copy-output`) rather than the imported source lineage, and `source_writeback = separate-act-required` keeps source write-back out of ordinary editor save. `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` then fixes the next source-lineage rule: if those edited bytes should count as the next version, the explicit act is `content.reintegrate.receipt`, which registers a local successor candidate instead of replacing the source in place. `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then fixes the next evidence rule too: that candidate is frozen to one digest, so later edits require a new candidate rather than silently mutating the old one.

### 3) Keep edit routes joinable to the copy act

`intent.route.receipt` now grows optional `working_copy_receipt_digest`.
When the system allows `document_editing` for an imported-document workflow, it should emit that digest so support/export surfaces can answer:

- which imported artifact was inspected?
- which explicit working-copy act issued the writable file?
- and which exact edit route opened that working copy?

That is the minimal evidence chain needed to keep **view** and **author** meaningfully separate.

## Why this is not a new giant subsystem

This does **not** create a document-management framework.
The archive still refuses to standardize:

- collaborative editing stacks,
- cloud-sync semantics,
- a full application taxonomy,
- or a giant mutable document database.

The lane is deliberately narrow:
plan the copy, receipt the copy, and let edit routes prove they used it.

## Practical model

### View path

1. foreign content enters through `content.import.*`
2. ordinary viewing uses `document_viewing`
3. route evidence points back to the exact import via `import_receipt_digest`

### Edit path

1. a trusted broker or explicit user/admin action requests a working copy
2. `content.working-copy.plan` / `content.working-copy.receipt` creates the writable artifact
3. the later `document_editing` route carries `working_copy_receipt_digest`
4. the imported original remains separate from the writable working state

That is the smallest model that preserves provenance and still lets a normal workstation edit a document.

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** imported maintenance artifacts can still become editable only through an explicit receipted copy act when exceptional local authoring is needed.
- **B / secure workstation:** the archive now has a concrete boring answer for “work on a copy” that is typed enough to build and support.
- **C / general-purpose OS:** broader compatibility adapters can still exist later, but the official Derive-managed lane stays explicit and audit-friendly.
- **D / appliance factory / regulatory:** imported procedures, reports, and maintenance payloads can become local working material only through a receipted transition that keeps the original evidence chain intact.

## What remains intentionally open

This doc does **not** settle:

- collaborative/version-control semantics,
- exact storage placement policy for working copies,
- local ordinary-save scope once the working copy is open,
- which MIME/risk classes default to disposable vs persistent viewing,
- or profile-`C` compatibility adapters beyond this explicit official lane.

Those are future RFC/ADR topics.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- `spec/content.working-copy.plan.schema.json`
- `spec/content.working-copy.receipt.schema.json`
- `spec/intent.request.schema.json`
- `spec/intent.route.receipt.schema.json`
- `spec/intent.route.receipt.document-edit-allow.schema.json`

Last updated: 2026-03-20r340
