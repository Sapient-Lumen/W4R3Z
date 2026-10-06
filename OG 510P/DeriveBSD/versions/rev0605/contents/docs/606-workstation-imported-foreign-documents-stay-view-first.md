# Workstation imported foreign documents stay view-first

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/605-workstation-file-open-import-and-bounded-document-roles.md` already fixed the broad shape of cross-compartment document handling:
import first, route second, and keep ordinary document handling inside bounded `document_viewing` / `document_editing` roles instead of the host.
But one expensive ambiguity remained after that decision:
**what is the default edit posture for imported foreign/quarantined documents?**

This doc makes the next narrow cut:
**foreign imported documents stay view-first, and editing them requires an explicit working-copy transition rather than save back over the imported original by default.**

See also:
- ADR: `adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md`
- file-open floor: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- portals / powerbox: `docs/179-portals-and-powerbox.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- origin / quarantine metadata: `docs/280-origin-labels-and-quarantine-attributes.md`
- sanitization lane: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- typed working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- sanitized-derivative posture: `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- working-copy save scope / no implicit source write-back: `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- explicit reintegration / successor-candidate boundary: `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- immutable-candidate follow-on: `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`

## Why this needs a hard decision

Without this cut, the archive still leaves the easiest implementation path dangerously attractive:

- import a risky attachment
- open it directly in an editor compartment
- save back over the same imported bytes
- and let the user believe this was just a normal “safe open” flow

That is exactly where provenance and quarantine boundaries get laundered in practice.
The user did not merely inspect the imported artifact anymore; they started authoring or mutating it.
If the archive does not say so clearly, implementations will flatten those two acts together.

## Decision

For ordinary cross-compartment document handling:

- imported foreign/quarantined documents are **view-first**
- the default route for those bytes is `document_viewing`
- `document_editing` is **not** the baseline target for a newly imported foreign original
- editing requires an explicit **working copy** / authoring copy / promoted derivative act
- that copy act is now typed as `content.working-copy.plan` / `content.working-copy.receipt` instead of being left as UI prose
- baseline behavior is **work on a copy**, not **save back over the imported original**
- sanitized or converted inspection derivatives also stay view-first unless separately turned into a working copy

This keeps “inspect imported content” distinct from “start producing trusted local changes.”

## Practical state model

The archive can stay small while still distinguishing the states that matter:

### 1) Imported foreign original

Examples:
- downloaded PDF or office document
- email/chat attachment
- removable-media import
- foreign report or procedure dropped into the workstation

Default posture:
- keep provenance/quarantine joins intact
- allow `open` / `view` through `document_viewing`
- deny ordinary `edit` routing to `document_editing`
- route baseline foreign originals through a disposable `document_viewing` target by default; `docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md` now fixes that foreign-viewing posture explicitly
- keep persistent viewer fallback forbidden by baseline policy

### 2) Sanitized or converted derivative

Examples:
- render-to-safe-PDF output
- converted inspection copy
- normalized artifact produced by a safe-open pipeline

Default posture:
- safer inspection/export object
- still **not automatically an authoring workspace**
- ordinary route remains `document_viewing`
- `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md` now fixes the next viewing/trust cut too: the derivative remains inspection-shaped and disposable-first by baseline policy instead of silently becoming a trusted/local persistent-viewer document
- if a user wants to modify content, the system should still make that a separate working-copy step

### 3) Explicit working copy / authoring copy

Examples:
- a deliberate “work on a copy” act in trusted UI
- a locally authored derivative placed into a designated authoring area
- a future promote/clone lane accepted by later ADR

Default posture:
- may use `document_viewing` or `document_editing`
- remembered `document_editing` targets may apply here
- support/export surfaces can explain that the user started with imported bytes but intentionally crossed into a mutation lane

## What this means for chooser/default behavior

The chooser/default-app floor from `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md` still stands.
But remembered `document_editing` targets are **not** ambient permission to edit every file.
They are only eligible when policy says the subject is actually in the editing lane.

So the trusted host may remember:
- which viewer compartment should handle document inspection
- which editor compartment should handle working copies

while still refusing to send a newly imported foreign original straight into the editing lane.

## What this means for evidence

The core evidence chain stays small:

- `content.import.receipt` proves how the foreign artifact entered the system
- `intent.route.receipt.import_receipt_digest` keeps the viewing route joinable back to that exact imported artifact
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` now fixes the next hop too: allowed edit routes should carry `working_copy_receipt_digest` so the system can prove which explicit copy became writable
- `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` then fixes the local authoring interpretation too: ordinary save stays on that working-copy output, and source write-back is a separate explicit act
- `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` then fixes the next source-lineage interpretation too: explicit reintegration registers a successor candidate instead of replacing the source in place
- `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then fixes the next evidence interpretation too: that immutable successor candidate is frozen to one digest, so later edits require a new candidate
- remembered role/default state still lives in `intent.role.binding`

This doc does **not** add a new evidence object yet.
It simply fixes the interpretation boundary so support/export surfaces can say:

- the original imported artifact was viewed
- editing that original was denied by baseline policy
- and any later editable working copy must be explained as a separate act

## What is explicitly not baseline

The ordinary workstation lane does **not** require:

- editing imported foreign originals in place
- “edit in disposable and save back over the original” as the default path
- implicit source write-back hidden behind ordinary editor save behavior
- automatic promotion from sanitized inspection derivative to editable working file
- using app self-claims (“I am an editor”) to bypass provenance-based route policy
- widening the document role vocabulary beyond `document_viewing` / `document_editing`

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** imported maintenance artifacts remain inspectable, while edits stay exceptional and explicit.
- **B / secure workstation:** downloaded attachments and reports get a practical boring default: inspect first, work on a copy when you really mean to change something.
- **C / general-purpose OS:** the official Derive-managed lane remains view-first; broader in-place editing can exist only as an explicit compatibility adapter or later bounded ADR.
- **D / appliance factory / regulatory:** imported procedures, certificates, reports, and maintenance payloads remain auditable and offline-friendly because foreign originals do not silently become mutable working state.

## What remains intentionally open

This doc does **not** settle:

- which future explicit promotion/finalization lane, if any, should allow a narrow sanitized class to become persistent-viewer-friendly after `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- collaborative editing/version-control semantics
- profile-`C` compatibility adapters for in-place editing
- or media/IDE/design-tool role families

Those are future RFC/ADR topics.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- `docs/280-origin-labels-and-quarantine-attributes.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md`
- `spec/content.import.receipt.schema.json`
- `spec/intent.route.receipt.schema.json`
- `spec/intent.role.binding.schema.json`

Last updated: 2026-03-22r384
