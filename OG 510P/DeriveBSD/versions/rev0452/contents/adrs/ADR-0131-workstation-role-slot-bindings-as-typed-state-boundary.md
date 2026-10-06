# ADR-0131: Workstation role-slot bindings as a typed state boundary

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0130-workstation-role-bound-intent-targets-and-chooser-floor.md` already decided that profile **B** resolves URI-like routing through a small set of trusted host-managed target roles, that chooser scope stays bounded to pre-enrolled targets of the same role, and that first-open prompts from untrusted context do not silently rewrite defaults.

That still left one important boundary too fuzzy:

- where does the trusted host actually remember which compartment currently holds the `browsing` or `communications` role?
- what is the authoritative object that a support bundle, export surface, or drift review should inspect?
- how does an `intent.route.receipt` prove which remembered role/default state it resolved through?

If we leave that unanswered, the archive will drift back toward desktop folklore:

- desktop-entry caches or package registries becoming the real default-app database,
- ad-hoc settings files that are hard to diff or explain,
- and route receipts that can say *which handler ran* but not *which remembered state selected it*.

Portal practice and role-based handler practice both push toward a narrower answer: user-facing chooser/default behavior can stay on the trusted host, but the remembered assignment state itself should be an explicit, typed host-owned object rather than an ambient registry side effect. See `docs/32-curated-references.md` for the Android RoleManager, XDG OpenURI, and XDG AppChooser references that motivated this cut.

## Decision

For the workstation baseline, the authoritative remembered role/default state is now a typed artifact:

- `intent.role.binding`

This is the host-owned, reviewable state object for remembered target-role bindings.

The baseline boundary is:

1. Trusted role/default state is represented as `intent.role.binding`, not inferred from application registries, desktop-entry associations, or unstructured settings files.
2. `intent.role.binding` is written only by trusted settings/admin workflows. Untrusted callers cannot mutate it as a side effect of `intent.request` handling.
3. The v0 role vocabulary remains intentionally small:
   - `browsing`
   - `communications`
4. The v0 target-kind vocabulary is also intentionally small:
   - `persistent-compartment`
   - `disposable-template`
5. An allow-path `intent.route.receipt` must bind back to the remembered state it used via `role_binding_digest`.
6. This ADR fixes the **typed state boundary**, not the full mutation workflow. Fine-grained mutation receipts, durable diff objects, and richer role vocabularies remain future work.

## Consequences

- The archive now has one obvious place to answer “what currently owns the browsing role on this host?”
- Route evidence can now answer both:
  - which role resolved the request,
  - and which remembered binding snapshot was used.
- The workstation lane gets closer to implementation because trusted settings/admin UX now has a concrete authoritative object to read and write.
- A/C/D remain coherent without forks because they can compile to the same object shape while using stricter or thinner role populations.

## What this ADR does **not** decide

This ADR does **not** yet decide:

- the exact mutation receipt family for settings/admin changes,
- whether remembered changes need a dedicated `*.diff` artifact,
- whether document-viewer/editor/media roles are worth standardizing,
- or whether profile **C** gets a broader host-native handler adapter lane.

Those should land only when the smaller baseline object is already useful.

## Related

- `adrs/ADR-0130-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/199-intent-routing-and-plumbing.md`
- `spec/intent.role.binding.schema.json`
- `spec/intent.route.receipt.schema.json`
