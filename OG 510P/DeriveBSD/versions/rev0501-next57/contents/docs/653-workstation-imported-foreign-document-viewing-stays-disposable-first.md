# Workstation imported foreign document viewing stays disposable-first

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/605-workstation-file-open-import-and-bounded-document-roles.md` already fixed the broad file-open floor: import first, route second, no quiet host-open fallback, and bounded `document_viewing` / `document_editing` roles.
`docs/606-workstation-imported-foreign-documents-stay-view-first.md` then fixed the mutation boundary: foreign imported originals stay **view-first**, and mutation requires an explicit working-copy step.

But one expensive ambiguity still remained after those cuts:
**when a newly imported foreign/quarantined document is only being viewed, should the ordinary baseline land it in a persistent viewer compartment or a disposable viewer lane?**

This doc makes the next narrow cut:
**newly imported foreign/quarantined document viewing is disposable-first, and the baseline must not silently fall back to a remembered persistent viewer target.**

See also:
- ADR: `adrs/ADR-0243-workstation-imported-foreign-document-viewing-stays-disposable-first.md`
- file-open floor: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- view-first mutation boundary: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- portals / powerbox: `docs/179-portals-and-powerbox.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- desktop viability: `docs/410-desktop-viability-checklist.md`
- typed role state: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- sanitized-derivative follow-on: `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`

## Why this needs a hard decision

Without this cut, the archive still leaves an implementation-shaped loophole:

- foreign imported bytes are technically “view-first”,
- but the remembered `document_viewing` default is often a persistent reader AppVM,
- so the real product quietly becomes “open risky foreign files in the long-lived reader by default”,
- and the disposable viewer becomes a convenience option instead of the ordinary posture.

That is exactly the kind of drift the archive is trying to prevent.
The workstation story becomes much less coherent if the risky imported-content path is nominally compartmentalized but still lands in a long-lived viewer by habit.

## Decision

For the ordinary foreign-document inspection lane:

- newly imported foreign/quarantined originals route to `document_viewing` through a **disposable** target
- that route is a **policy-shaped foreign-content decision**, not just the remembered persistent role default
- remembered persistent `document_viewing` targets do **not** silently win for foreign imported originals
- if no disposable viewing target is enrolled/healthy, baseline behavior is **deny** or require a separately typed stronger path
- silent fallback to a persistent viewer is **not** baseline

This keeps ordinary foreign-document inspection short-lived, no-network, and easier to reason about.

## Practical model

### 1) Import remains the first authoritative act

The archive still uses the existing intake lane:

- `content.import.plan`
- `content.import.receipt`

For the ordinary foreign-document viewing baseline, the canonical execution posture is:

- `isolation = microvm`
- `network = none`
- `lifetime = disposable`

That uses existing import execution fields rather than inventing a new viewer-policy subsystem.

### 2) Route the imported artifact to `document_viewing`

The trusted host still routes the imported artifact on the existing intent lane.
But for a newly imported foreign original, the route interpretation is stricter:

- the allow-path viewing route should be treated as **policy-pinned** disposable viewing
- `intent.request.context.import_receipt_digest` keeps the request joined to the exact import act
- `intent.route.receipt.import_receipt_digest` keeps the allow-path route joined to that same foreign imported artifact
- a remembered persistent reader does not silently override this posture

In other words, the baseline foreign-document route is not “whatever `document_viewing` remembered last”.
It is “the disposable viewer lane for foreign imported content”.

### 3) Persistent viewers still exist, but not as the baseline foreign-import landing zone

Persistent `document_viewing` targets are still useful for:

- trusted/local reading workflows
- durable user-owned reading environments
- later future ADRs for specific sanitized or trusted-local classes
- explicit compatibility adapters in profile **C**

But they are not the ordinary answer for newly imported foreign originals.

## What this means for role/default state

`intent.role.binding` can still remember both:

- a persistent `document_viewing` target
- and an enrolled disposable `document_viewing` target

That typed remembered state remains useful.
This doc only fixes how the baseline foreign-import path interprets it:

- foreign imported originals should resolve to the disposable target
- the persistent target is not a fallback just because it is remembered
- missing disposable support should fail closed instead of quietly weakening the posture

This keeps remembered role state from becoming ambient authority for risky imported bytes.

## What this means for evidence

The archive can now tell one more coherent story with existing objects:

- `content.import.receipt` proves how the foreign bytes entered the system
- `intent.request.context.import_receipt_digest` keeps the later viewing request joined to that intake act
- `intent.route.receipt.import_receipt_digest` keeps the route joined too
- `resolution_mode = policy-pinned` expresses that ordinary foreign-document viewing is policy-shaped rather than just role-default convenience
- and `docs/606-workstation-imported-foreign-documents-stay-view-first.md` plus `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` still keep mutation on a separate explicit lane

This is enough to make the baseline inspection story implementable without adding a new artifact family.

## What is explicitly not baseline

The ordinary workstation foreign-document lane does **not** require:

- persistent-viewer fallback when a foreign original is opened
- “best effort” downgrade from disposable to persistent viewing because the reader is already warm
- treating a remembered persistent `document_viewing` target as ambient approval for risky imported bytes
- using sanitizer success as automatic permission to land the result in a persistent viewer by default; `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md` now makes the stricter follow-on cut that sanitized inspection derivatives stay inspection-shaped too
- broadening the role vocabulary beyond `document_viewing` / `document_editing`

## Product-shape fit (A–D without forks)

- **A / secure fleet host:** risky maintenance/support artifacts can reuse the same disposable-first inspection posture instead of teaching a separate fleet-only reader story.
- **B / secure workstation:** downloaded attachments and reports now have a more concrete boring default: import, inspect in a disposable viewer, and only cross into mutation through a separate working-copy step.
- **C / general-purpose OS:** the official Derive-managed lane stays strong and coherent, while any persistent-viewing compatibility path remains explicit adapter territory.
- **D / appliance factory / regulatory:** imported procedures, certificates, and maintenance documents can stay offline/auditable because the baseline foreign-document path is short-lived and does not normalize long-lived mutable reader state.

## What remains intentionally open

This doc does **not** settle:

- which trusted/local document classes should prefer persistent vs disposable viewing
- whether some future explicit promotion/finalization lane should let a narrow sanitized class or trusted/local class escape the now-accepted disposable-first inspection posture from `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- media-player / IDE / design-tool role families
- exact health probing for enrolled disposable viewer targets
- or any specific profile-`C` compatibility adapter

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
- `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- `spec/content.import.plan.schema.json`
- `spec/content.import.receipt.schema.json`
- `spec/intent.request.schema.json`
- `spec/intent.route.receipt.schema.json`
- `spec/examples/content.import.document-view.plan.json`
- `spec/examples/content.import.document-view.receipt.json`
- `spec/examples/intent.request.document-view.json`
- `spec/examples/intent.route.receipt.document-view.json`

Last updated: 2026-03-22r384
