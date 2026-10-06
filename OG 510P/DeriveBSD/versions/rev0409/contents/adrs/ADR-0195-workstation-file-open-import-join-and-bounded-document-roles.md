# ADR-0195: Workstation file-open import join and bounded document roles

Date: 2026-03-20
Status: Accepted

## Context

`adrs/ADR-0129-workstation-intent-routed-uri-opening-floor.md` fixed the URI side of workstation crossing: risky `http` / `https` routes to a browsing compartment, `mailto` routes to communications, and `file://` does not smuggle cross-domain file authority through the URI lane.
`adrs/ADR-0130-workstation-role-bound-intent-targets-and-chooser-floor.md` then fixed chooser/default-app behavior onto trusted host-managed roles, and `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered target ownership as typed `intent.role.binding` state.
The generic safe-open lane already exists too: risky foreign content enters through `content.import.plan` / `content.import.receipt` rather than host-open folklore.

But one expensive everyday gap remained:

- people do not only click links; they also open PDFs, office documents, and other imported files
- the archive had no equally crisp baseline for **cross-compartment file open/view/edit**
- without that cut, the easiest implementation path would drift back toward host-side document rendering, generic “open with…” discovery, or one-off import/open helpers that lose provenance between the import act and the chosen viewer/editor

That would make profile **B** look coherent in theory while still falling back to ambient host document handling in daily life.

## Decision

1. Cross-compartment file `open` / `view` / `edit` on the workstation lane is a **two-stage act**:
   - explicit file authority transfer / safe-open intake on the existing `content.import.*` lane
   - then intent routing to a bounded viewer/editor target on the existing `intent.*` lane
2. The trusted host is **not** the default renderer/editor for imported untrusted document content. Ordinary document open should land in a designated document compartment lane rather than on the host.
3. The remembered role vocabulary is extended narrowly with optional document roles:
   - `document_viewing`
   - `document_editing`
4. Those roles are intentionally small. They standardize the workstation document floor without inventing a giant MIME/application registry or an office-suite taxonomy.
5. `intent.route.receipt` is extended with optional `import_receipt_digest` so a route can point back to the exact `content.import.receipt` that produced the imported artifact it is opening.
6. For cross-compartment document open/view/edit, implementations should emit that `import_receipt_digest` rather than relying only on portal grant lineage or side logs.
7. Trusted chooser/default behavior remains bounded inside the chosen role: the host may choose among pre-enrolled `document_viewing` targets or among pre-enrolled `document_editing` targets, but not fall back to arbitrary app discovery.
8. This ADR does **not** standardize rich media/editor taxonomies, collaboration semantics, or MIME-specific sanitization policy. Those remain future bounded work.

## Consequences

### What this locks now

- The archive gets a practical answer for the common “open this downloaded document” path without weakening the host/AppVM boundary.
- Imported document handling now stays on one proof chain:
  - `content.import.receipt` for intake / sanitization / provenance preservation
  - `intent.role.binding` for remembered viewer/editor targets
  - `intent.route.receipt.import_receipt_digest` for the exact join between the imported artifact and the chosen handler
- The workstation baseline can stay AppVM-first in real usage, not only for browsers/mail.

### What stays intentionally open

This ADR does **not** decide:

- exact MIME-to-role heuristics beyond the narrow viewer/editor split
- whether document open defaults to disposable or persistent targets for specific trust labels
- rich collaborative/editor workflows
- media-player / IDE / design-tool role families
- or whether profile **C** wants broader host-native compatibility adapters

Those remain future RFC/ADR territory.

## Why this is the smallest viable cut

The archive already had all the right primitives in pieces:

- explicit file transfer / import evidence
- intent routing and role-bound chooser/default behavior
- typed remembered role bindings

The missing move was simply to join them for document open instead of inventing a second document-open subsystem or pretending URLs were the whole problem.

So the archive now chooses the smallest durable answer:

- imported documents stay off the host by default
- file open/view/edit remains import-shaped first, route-shaped second
- and the route evidence can point back to the exact import evidence that made the open possible

## Wiring

- document-open boundary doc: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- role bindings: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- safe-open import lane: `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`, `spec/content.import.receipt.schema.json`
- route receipt schema: `spec/intent.route.receipt.schema.json`
