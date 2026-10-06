# Workstation role-slot bindings as a typed state boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Registry→Diff→Gate, Broker→Lease→Receipt  

`docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md` already fixed the chooser/default-app floor for the secure workstation lane:
DeriveBSD uses trusted host-managed target roles, keeps chooser scope bounded, and does not let untrusted first-open prompts silently rewrite global defaults.

This doc makes the next small but important cut:

> remembered role/default state is a typed host-owned artifact, not desktop-registry folklore.

See also:
- ADR: `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md`
- chooser/default-app floor: `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`

## Why this needs a hard decision

Once chooser/default-app behavior is constrained to trusted roles, the next likely drift point is the remembered state behind those roles.
If DeriveBSD does not make that state explicit, it will tend to leak into whatever is easiest to implement first:

- package-manager metadata,
- desktop-entry or MIME-association caches,
- ad-hoc settings files,
- or caller-driven “always use this” shortcuts.

That would recreate the same old problem in slower motion.
Support surfaces would have to guess where defaults really live, and route receipts could explain the chosen handler without proving which remembered state produced the choice.

## Accepted boundary

The authoritative remembered role/default object is now:

- `intent.role.binding`

This object is:

- host-owned
- trusted-settings/admin-written
- reviewable and exportable
- suitable for digest-binding from routing evidence

The workstation baseline uses it to answer:

- which target currently holds the `browsing` role?
- which target currently holds the `communications` role?
- which target currently holds the optional `document_viewing` / `document_editing` roles when the accepted file-open boundary is in use?
- and, once `docs/606-workstation-imported-foreign-documents-stay-view-first.md` is accepted, how do we keep remembered `document_editing` targets from being misread as permission to edit every imported foreign original?
- and, once `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` is accepted, how do allowed edit routes prove they used an explicit receipted working copy rather than the imported source?
- and, once `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`, `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`, `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`, `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`, `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` are accepted, how do remembered `document_editing` targets avoid being misread as authority to save modified bytes back into the imported source lineage, replace the authoritative origin in place, silently mutate an already registered candidate, let the newest candidate win without explicit supersession, or claim cross-origin supersession through a vague older receipt pointer?
- which additional targets are enrolled for chooser use inside the same role?

## Small vocabulary on purpose

### Roles stay small

The baseline role vocabulary remains intentionally small:

- `browsing`
- `communications`
- optional `document_viewing`
- optional `document_editing`

The first two keep the accepted URI-opening floor coherent.
The latter two keep the accepted file-open floor coherent without turning `intent.role.binding` into a giant systemwide application-role taxonomy.

### Target kinds stay small

The baseline target kinds are also intentionally narrow:

- `persistent-compartment`
- `disposable-template`

That gives the archive a practical answer for the already-accepted chooser scope:

- the stable daily target can be a persistent browser/mail compartment,
- and the safer one-shot alternative can be a disposable template of the same role.

Anything richer should wait for a later ADR.

## What `intent.role.binding` owns

`intent.role.binding` owns only the remembered role/default state boundary.
In v0 it should be able to say, for each supported role:

- the current default target
- the enrolled targets eligible for the trusted chooser
- the host/profile scope the binding belongs to
- the policy snapshot it was derived under, when applicable
- and the previous binding digest, when the implementation wants stable continuity across reviewed changes
- and enough metadata for callers to compile through the right authority lane without inventing transport-specific trigger vocabulary

That is enough to make settings UX, support exports, and route receipts point at the same source of truth.
When that source changes, the compact review surface is now `intent.role.binding.diff`, and the durable event-journal trace is now `intent.role.binding.event`, so trusted settings/admin implementation can start from a small snapshot-plus-diff-plus-event model instead of inventing a giant settings journal. `intent.role.binding.diff.from_binding.digest` is also the compare-and-swap apply precondition, so reviewed role-binding writes cannot silently stomp newer state.

## What it does **not** own

`intent.role.binding` does **not** turn into a universal application registry.
It does **not** own:

- arbitrary app discovery
- ambient MIME/desktop-entry handler truth
- caller-supplied app ids
- media-player / IDE / creative-tool role taxonomies by default
- mutation semantics for every future profile and product shape

The object should stay small enough that people can reason about it without reconstructing a whole desktop shell.

## Evidence tightening

The main new evidence join is simple:

- `intent.route.receipt` now carries `role_binding_digest`

That means an allow-path route can answer all three of these questions together:

- which handler ran?
- which target role resolved the request?
- which remembered role-binding snapshot did the decision use?
- and, for imported-document editing, which `content.working-copy.receipt` made the writable artifact exist through `working_copy_receipt_digest`?
- and, once ordinary save semantics are fixed, which typed boundary said the default save target was the working-copy output rather than the imported source (`default_save_target` / `source_writeback`)?
- and, once explicit reintegration is fixed, which typed boundary said later source-lineage intent had to register a successor candidate through `content.reintegrate.receipt` rather than replace the origin in place, which typed boundary said later edits require a new candidate rather than silently retargeting the old one, and which typed boundary said candidate-to-candidate replacement must use explicit supersession instead of newest-wins folklore, and which typed boundary said stale supersession denials must also carry observed current-head evidence plus a fresh explicit recovery target?

This is the right granularity for now.
We do **not** need to standardize every role-binding mutation receipt before the router can start producing better evidence.
For v0, snapshot-plus-diff-plus-event is enough: `intent.role.binding` remains the authoritative remembered state, `intent.role.binding.diff` is the compact review surface when trusted settings/admin UX changes that state, and `intent.role.binding.event` is the durable mutation trace for the event journal and support bundles. For profile **B** interactive changes, that event can also join to the generic consent lane through `consent_receipt_digest`, so the archive can prove not only what changed and when, but that a trusted-UI approval happened. For non-interactive reconcile/import changes, the same event family can instead join to `policy.decision` through `policy_decision_digest`, so A / C / D do not inherit a workstation prompt model by accident. `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md` further narrows that boundary: local admin or remote tooling may still invoke the write, but the event `trigger` must name the authority/apply lane instead of the transport.

## Product-shape fit without forks

- **A / secure fleet host:** usually compiles to no ordinary interactive role bindings, but the shape still fits if a management UI or maintenance workstation needs the same artifact family.
- **B / secure workstation:** this is the primary baseline; remembered browsing/comms/document-view/document-edit targets become typed and supportable.
- **C / general-purpose OS:** may later allow broader host-native adapters, but the remembered state can still compile to the same typed binding object instead of escaping into ambient desktop caches.
- **D / appliance factory / regulatory:** production images may compile to a very thin or absent role set, but maintenance or operator surfaces can still reuse the same object family.

## Future bounded lane

Later work may still decide:

- the full mutation-receipt family for role-binding changes,
- whether more role families are worth standardizing beyond the current browsing/comms/document floor,
- whether profile **C** wants a bounded host-native handler adapter lane,
- and how much chooser history or “last used” state deserves durable evidence.

Those are worth deciding later.
For now, the important hard cut is that remembered role/default state is explicit, typed, and digest-bindable.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/542-role-binding-diff-as-review-surface.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `spec/intent.role.binding.schema.json`
- `spec/intent.role.binding.diff.schema.json`
- `spec/intent.route.receipt.schema.json`
- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`, `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`, `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`, `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`, `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`

Last updated: 2026-03-20r342
