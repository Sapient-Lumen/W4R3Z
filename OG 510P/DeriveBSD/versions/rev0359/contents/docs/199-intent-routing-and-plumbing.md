# Intent routing (“plumbing”) as a capability-mediated service

Modern systems want a simple primitive for:
- “open this file” / “view this URL” / “share this blob”
- “pick the best handler for this MIME type”
- “let the user choose a default app”

If apps do this by spawning arbitrary handlers or probing global registries, sandboxing collapses.

This doc proposes a DeriveBSD primitive: an **intent router** (Plan 9 “plumber” / Android intents shaped) that is:
- capability-mediated
- policy-gated
- evidence-bearing

## Lessons to steal

- **Plan 9 plumber**: a message routing service whose behavior is defined by a rules file; unusually, it is a *file server*, so sending is just writing to a file.
- **Android intents**: components declare intent filters; the system resolves implicit intents to handlers, optionally presenting a chooser and letting users set defaults.

References:
- Plan 9 plumbing design notes: https://9p.io/sys/doc/plumb.html
- plumb(7) rules and ports: https://9fans.github.io/plan9port/man/man7/plumb.html
- Android intents and intent filters: https://developer.android.com/guide/components/intents-filters

## What “intent routing” means in DeriveBSD

An **intent request** is a typed message:

- action: `open` / `view` / `edit` / `share` / `print` / …
- subject: a file capability, URL, or blob capability
- context: caller identity + plan/generation digests + reason
- constraints: UI requirements, redaction profile, time budget, etc.

The **intent router**:
1) evaluates rules + policy
2) selects a handler component
3) brokers the handoff using DeriveBSD’s capability substrate (portals + ocap RPC)
4) emits a signed **route receipt**

## Why bake this in early

- It avoids “xdg-open as ambient authority.”
- For the workstation lane, `docs/539-workstation-intent-routed-uri-opening-floor.md` now fixes the baseline URI answer: risky `http` / `https` opens go to a designated browsing compartment, `mailto` goes to a designated communications compartment, and `file://` does not bypass explicit file authority lanes. `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md` then keeps chooser/default-app behavior on trusted host-managed target roles instead of arbitrary app discovery, while `docs/605-workstation-file-open-import-and-bounded-document-roles.md` fixes the file-shaped companion path: cross-compartment document open/view/edit stays import-shaped first, route-shaped second, and route evidence can point back to the exact `content.import.receipt` via `import_receipt_digest`. `docs/606-workstation-imported-foreign-documents-stay-view-first.md` then tightens the mutation side: a newly imported foreign document may be view-routed, but baseline policy should deny edit-in-place and require an explicit working-copy transition before the `document_editing` lane applies. `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` then makes that transition typed through `content.working-copy.receipt` and lets allow-path edit routes carry `working_copy_receipt_digest` so the writable artifact stays evidence-bound. `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` now fixes the next local authoring rule too: ordinary save stays on that working-copy output, and source write-back is a separate explicit act rather than an editor-side side effect. `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` then fixes the next source-lineage rule: when those edited bytes should count as the next version, the official lane is a typed `content.reintegrate.receipt` act that registers a local successor candidate rather than replace-in-place folklore. `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then keeps that candidate evidence exact too: the receipt is an immutable snapshot, not a moving file pointer, and later edits require a new candidate. `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` then fixes the next multi-candidate rule: explicit supersession by digest is required before one candidate can displace another; recency alone carries no authority. `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` then fixes the next scope/evidence rule: that supersession remains `same-authoritative-origin-only`, and the newer receipt carries `superseded_candidate_digest` plus `superseded_authoritative_origin_digest` so the displaced snapshot stays queryable without reopening earlier receipts.
- It provides a single place to enforce UX + safety constraints (e.g. "open untrusted PDF" defaults to a hardened viewer compartment).
- It makes inter-app integration compatible with capability mode.

## Proposed contract (v0)

### `intent.request`

Schema: `spec/intent.request.schema.json`.

Key fields:
- `action`
- `subject` (by-value digest metadata, plus an optional handle reference)
- `mime_type` / `uri_scheme`
- `caller` identity
- `context` digests

### Resolution outputs

The router produces one of:
- deny (default)
- allow (explicit handler)
- ask (interactive chooser)

On allow, it returns:
- a handler endpoint (ocap RPC capability)
- the trusted `target_role` used for routing
- the `resolution_mode` (`role-default`, `trusted-chooser`, `policy-pinned`)
- the `role_binding_digest` for the remembered target-role snapshot used
- and/or a portal-derived file/socket capability for the handler

### Evidence: `intent.route.receipt`

Schema: `spec/intent.route.receipt.schema.json`.

Binds:
- request digest
- chosen handler identity (service digest)
- trusted `target_role`, `resolution_mode`, and `role_binding_digest`
- optional `import_receipt_digest` when a cross-compartment file-open route should point back to the exact safe-open/import evidence it depends on
- policy decision digest
- any portal grants minted as part of the routing
- optional consent receipt digest if interactive

The remembered chooser/default state behind that digest is now explicit too: `intent.role.binding` keeps trusted role-slot bindings out of ambient application registries and lets route receipts point at the exact snapshot they used. When trusted settings/admin UX changes that remembered state, `intent.role.binding.diff` is the compact snapshot-plus-diff review artifact rather than a grab bag of settings deltas, and `intent.role.binding.event` is the durable mutation trace for event journals and support bundles.

## Rules model (non-normative)

DeriveBSD can support a Plan 9-ish rules file:
- match on action + MIME type + scheme + tags
- rewrite/annotate intent
- dispatch to a handler class

But unlike Plan 9, dispatch must go through portals/leases so the handler receives only the minimum capability set.

## Threat model notes

- Prevent “confused deputy” by making the router the only component allowed to:
  - resolve implicit handlers
  - invoke interactive chooser UI
- Bind route receipts to a policy snapshot digest (avoid silent rule changes).
- For "open" actions on host files, prefer `fs.bookmark` claims or portal file picks rather than raw path strings.

## Integration points

- Portals: `docs/179-portals-and-powerbox.md`
- Object-capability RPC substrate: `docs/183-object-capability-rpc.md`
- Consent receipts: `docs/185-portal-consent-and-audit-receipts.md`
- Deterministic redaction transforms (safe sharing): `docs/195-deterministic-redaction-transforms.md`
- Role-slot binding boundary: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- Role-slot binding diff surface: `docs/542-role-binding-diff-as-review-surface.md`

Last updated: 2026-03-20r342
