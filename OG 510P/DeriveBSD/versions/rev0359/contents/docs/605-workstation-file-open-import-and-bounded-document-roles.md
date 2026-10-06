# Workstation file-open import join and bounded document roles

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/539-workstation-intent-routed-uri-opening-floor.md` fixed the URI side of workstation routing: `http` / `https` goes to browsing, `mailto` goes to communications, and `file://` does not bypass explicit file authority lanes.
`docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md` then fixed chooser/default-app behavior onto trusted host-managed roles, while `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered target ownership as typed host-owned state.
The archive already had a safe-open intake lane too: risky foreign content enters through `content.import.plan` / `content.import.receipt` instead of host-open folklore.

This doc makes the next small but expensive cut:
**cross-compartment file open/view/edit is import-shaped first, route-shaped second, and the workstation baseline standardizes only two additional document roles: `document_viewing` and `document_editing`.**

See also:
- ADR: `adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md`
- workstation URI floor: `docs/539-workstation-intent-routed-uri-opening-floor.md`
- trusted chooser/default-app floor: `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- typed remembered role state: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- generic import lane: `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`
- imported-foreign-document edit boundary: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- working-copy receipts and edit-route joins: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- working-copy save scope / no implicit source write-back: `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`

## Why this needs a hard decision

Browsers and mail are not the only daily workstation crossings.
Users also open:

- downloaded PDFs
- office documents
- exported reports
- support artifacts
- untrusted attachments that are *files*, not links

If the archive does not choose a boundary here, the easiest implementation path will quietly become the real product:

- open imported files directly on the host for convenience
- let generic “open with…” discovery pick any installed handler
- or run one-off import helpers that lose the join between the imported artifact and the viewer/editor that actually opened it

That would make profile **B** look principled while still rendering risky document content on the host in normal use.

## Decision

For the ordinary workstation lane:

- cross-compartment file `open` / `view` / `edit` is a **two-stage act**
- stage 1 is explicit transfer / safe-open intake on the existing `content.import.*` lane
- stage 2 is intent routing to a bounded target on the existing `intent.*` lane
- the trusted host is **not** the default renderer/editor for imported untrusted document content
- the standardized remembered document roles are:
  - `document_viewing`
  - `document_editing`
- chooser/default behavior stays bounded inside those roles rather than reopening arbitrary app discovery
- route evidence should point back to the exact import evidence through `intent.route.receipt.import_receipt_digest`

This keeps the file-open path coherent with the already accepted host/AppVM and safe-open boundaries.

## Practical model

### Stage 1: import first

When a file needs to cross compartments, the first authoritative act is import / intake, not handler execution.
That means using the existing `content.import.plan` / `content.import.receipt` family for:

- provenance preservation
- quarantine / sanitization / normalization steps
- execution-boundary recording
- and output artifact labeling

This avoids turning file open into a hidden path move or a host-side convenience open.

### Stage 2: route the imported artifact

Once the imported artifact exists, the trusted host routes *that artifact* to a handler compartment under the existing intent-routing lane.
The route decision remains role-bound and host-owned:

- `document_viewing` for read-only / inspect / preview / safer-open posture
- `document_editing` for explicit authoring or mutation posture

That role split is no longer symmetric for foreign imported bytes: `docs/606-workstation-imported-foreign-documents-stay-view-first.md` now fixes the next boundary too, so imported foreign/quarantined documents stay **view-first** and baseline workstation behavior becomes **work on a copy** rather than **edit the imported original in place**. `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` then makes that copy act typed and receipted, so allowed edit routes can point at the exact `content.working-copy.receipt` through `working_copy_receipt_digest` instead of leaving “editable copy” as UI folklore. `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` fixes the next local authoring rule too: ordinary save on that lane stays on the working-copy output, and source write-back remains a separate explicit act. `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` then fixes the next source-lineage rule too: when edited bytes should count as the next version, the official lane registers a successor candidate instead of replacing the source in place. `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then fixes the next evidence rule too: that immutable successor candidate is frozen to one digest, so later edits require a new candidate instead of silently mutating the earlier one. `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`, `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`, and `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` then close the local multi-candidate story: supersession is explicit, same-origin, self-describing, and current-head exact rather than latest-wins or stale-target folklore. `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md` then fixes the support/export tail too by requiring stale denials to carry the observed current head instead of a generic stale message. `docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md` then fixes the next retry tail too: the fresh answer to that denial must stay denial-joined and head-pinned instead of becoming a generic retry.

The viewer/editor target may be:

- a persistent compartment
- or a disposable template

But the chooser still stays within the same role instead of becoming a registry of every installed application.

## Evidence tightening worth taking now

The important new proof join is small:

- `intent.route.receipt` now grows `import_receipt_digest`

That field is optional at the schema level because not every route is a file-open route.
But for cross-compartment document open/view/edit it should be emitted so support/export surfaces can answer:

- which exact imported artifact was opened?
- what intake/sanitization/provenance path produced it?
- was it routed to a viewing role or an editing role?
- which remembered role-binding snapshot selected the target?

This is better than relying only on portal-grant digests, file paths, or side logs.

## Why only two document roles

The archive should not jump from “two roles” to a full desktop ontology.
The smallest durable addition is just:

- `document_viewing`
- `document_editing`

That is enough to distinguish:

- safer preview/read lanes
- from explicit mutation/authoring lanes

without standardizing office-suite brands, MIME taxonomies, media players, IDEs, or creative-tool classes.

## What is explicitly not baseline

The ordinary workstation lane does **not** require:

- host-side opening of imported untrusted documents as the default path
- generic “open with…” discovery across all installed host/guest handlers
- silently treating every file open as equivalent to URI routing
- a giant built-in MIME/application registry
- automatic promotion from `document_viewing` to `document_editing` because an app asked nicely

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** usually has little ordinary document-open activity, but maintenance/support artifacts can still reuse the same import-first, route-second evidence chain.
- **B / secure workstation:** finally gets a practical answer for downloaded documents without falling back to host rendering.
- **C / general-purpose OS:** may later add broader compatibility adapters, but the principled Derive-managed lane still has a small viewer/editor split instead of ambient handler discovery.
- **D / appliance factory / regulatory:** imported procedures, reports, and maintenance artifacts can stay offline/auditable by reusing the same typed intake and bounded document-role routing model.

## What remains intentionally open

This doc does **not** settle:

- MIME-specific sanitization policy or default disposable heuristics
- media-player / IDE / design-tool role families
- collaborative editing semantics
- bounded host-native compatibility adapters for profile **C**
- the exact storage placement policy for issued working copies now that the typed receipt family exists
- or the typed reintegration lane for revised content that should first register an explicit successor candidate of an authoritative source

Those are future RFC/ADR topics.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`
- `docs/539-workstation-intent-routed-uri-opening-floor.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `spec/content.import.receipt.schema.json`
- `spec/intent.request.schema.json`
- `spec/intent.route.receipt.schema.json`
- `spec/content.working-copy.plan.schema.json`
- `spec/content.working-copy.receipt.schema.json`
- `spec/intent.role.binding.schema.json`

Last updated: 2026-03-20r345
