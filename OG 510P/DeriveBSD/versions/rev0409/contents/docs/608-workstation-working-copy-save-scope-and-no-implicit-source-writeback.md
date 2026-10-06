# Workstation working-copy save scope and no implicit source write-back

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

`docs/605-workstation-file-open-import-and-bounded-document-roles.md` fixed the imported-document open boundary:
import first, route second, and keep ordinary handling inside bounded `document_viewing` / `document_editing` roles.
`docs/606-workstation-imported-foreign-documents-stay-view-first.md` then fixed the mutation floor:
foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of saving back over the imported original by default.
`docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` then made that transition typed and joinable through `content.working-copy.plan` / `content.working-copy.receipt` plus `working_copy_receipt_digest` on allow-path edit routes.

This doc makes the next small but expensive cut:
**ordinary save within that imported-document authoring lane targets the issued working-copy output, and any source write-back remains a separate explicit act.**

See also:
- ADR: `adrs/ADR-0198-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- file-open floor: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- view-first mutation floor: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- typed working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- canonical schemas: `spec/content.working-copy.plan.schema.json`, `spec/content.working-copy.receipt.schema.json`
- reintegration follow-on: `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- immutable-candidate follow-on: `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`

## Why this needs a hard decision

Once the archive says **work on a copy**, the next leak is to leave normal editor save behavior undefined.
Then the implementation with the least friction becomes the real product:

- the editor treats the imported source and the working copy as morally the same file,
- disposable-edit flows quietly save modified bytes back over the imported original,
- support/export surfaces cannot tell whether the foreign evidence was preserved,
- and any future “replace upstream version” workflow starts from whatever the application happened to do.

That is too much ambiguity for the ordinary workstation lane.
DeriveBSD needs one boring answer that keeps imported evidence and local authoring separate.

## Decision

`content.working-copy.plan` and `content.working-copy.receipt` now carry a required `boundary` object with two fixed guarantees:

- `default_save_target = working-copy-output`
- `source_writeback = separate-act-required`

That means:

- ordinary **Save** writes to the issued working-copy artifact,
- the imported source lineage remains separate,
- and replacing or updating an authoritative source is not an implicit side effect of opening an editor.

## What the boundary means in practice

### 1) Saving stays local to the working copy

Once a writable artifact exists, the editor is operating on that artifact.
The baseline interpretation of ordinary save is therefore simple:
update the working-copy output already described by `content.working-copy.receipt`.

### 2) Imported evidence stays preserved as imported evidence

The imported source remains what it was:

- foreign original, or
- inspection-oriented derivative.

The archive now has a typed way to say that the authoring lane does **not** silently mutate that source lineage just because the user pressed save in an editor.

### 3) Source replacement becomes its own explicit reintegration boundary

There may eventually be a good typed answer for:

The newly accepted answer for the first source-lineage step is a **local successor candidate** through `content.reintegrate.plan` / `content.reintegrate.receipt`; `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then makes that candidate frozen and requires a **new candidate** for later edits, but ordinary save still does not finalize anything.


- publish back to a service,
- replace an attachment,
- check in to version control,
- or import a revised file as a new authoritative version.

But those are not the same thing as ordinary local save.
This doc keeps them separate so they can become reviewable acts later instead of piggybacking on app behavior.

## Why this is worth deciding now

The archive is trying to stay viable for all product shapes without forking.
Leaving save semantics mushy would hurt each one differently:

- **A / secure fleet host:** imported maintenance artifacts could quietly stop being preserved as evidence.
- **B / secure workstation:** the default edit path would drift toward convenience folklore instead of a supportable boring contract.
- **C / general-purpose OS:** compatibility adapters would silently redefine the official lane rather than layering on top of it.
- **D / appliance factory / regulatory:** imported procedures, reports, and payloads could lose clean provenance boundaries at the exact point humans begin editing them.

## Practical model

### Imported-document edit path

1. foreign content enters through `content.import.*`
2. ordinary inspection uses `document_viewing`
3. explicit authoring creates a `content.working-copy.receipt`
4. allow-path edit routing points at that receipt through `working_copy_receipt_digest`
5. ordinary save updates the working-copy output
6. any path back to an authoritative source is a separate explicit act, not implicit save-back

This is the smallest full story that now hangs together from intake to authoring.

## What is explicitly not baseline

The ordinary workstation lane does **not** require:

- “edit in disposable and save back over the original” as the default path
- automatic replacement of the imported source when a working copy is modified
- treating imported evidence and local authoring state as the same artifact
- a hidden check-in/publish subsystem smuggled into editor save behavior

## What remains intentionally open

This doc does **not** settle:

- the later adapter/finalization lanes that may consume a typed successor candidate for upstream replacement/check-in
- exact Save As / Export UI policy
- descendant-artifact retention/GC policy for working copies
- profile-`C` compatibility adapters beyond this official boundary

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
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `spec/content.working-copy.plan.schema.json`
- `spec/content.working-copy.receipt.schema.json`

Last updated: 2026-03-20r340
