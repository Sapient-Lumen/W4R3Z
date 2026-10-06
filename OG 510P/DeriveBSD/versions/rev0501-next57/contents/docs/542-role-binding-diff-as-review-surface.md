# Role-binding diff as a review surface

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Registry→Diff→Gate, Bundles  

`docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` already decided that remembered browsing/communications defaults live in a typed `intent.role.binding` object.
That fixed *where the truth lives*.
This doc fixes the next practical question:

> when trusted settings/admin UX changes remembered role/default state, what compact artifact do humans and policy review?

The answer should not be “diff two random settings files” or “inspect the desktop registry database.”
Role-binding changes are high leverage: they change where risky `http` / `https` and `mailto` requests land.
So the archive standardizes a compact posture diff:

- `intent.role.binding.diff`

See also:
- ADR: `adrs/ADR-0132-role-binding-diff-as-review-surface.md`
- authoritative state object: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- chooser/default-app floor: `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- drift bundles: `docs/395-drift-bundles-and-review-summaries.md`

## The artifacts

### `intent.role.binding`

The remembered state snapshot:
- which target currently holds `browsing` or `communications`
- which additional same-role targets are enrolled for the trusted chooser

Schema: `spec/intent.role.binding.schema.json`  
Example: `spec/examples/intent.role.binding.json`

### `intent.role.binding.diff`

The compact review surface:
- compares old/new binding snapshots by digest
- summarizes per-role default-target changes
- summarizes enrolled target additions/removals
- emits stable `risk_flags` suitable for trusted settings UX, drift bundles, and policy gates

Schema: `spec/intent.role.binding.diff.schema.json`  
Example: `spec/examples/intent.role.binding.diff.json`

## Noise rule (keep this surface small)

This diff is intentionally **not** a full settings-operation log.
It should stay focused on the posture questions that matter for routing and trusted-host policy:

- did the default browsing target change?
- did the default communications target change?
- was a new same-role target enrolled for chooser use?
- was an enrolled target removed?

If later work needs actor attribution, approver chains, or settings-transaction replay, add a separate typed receipt family.
Do not overload this diff into a universal settings journal.

## Where it plugs in

### 1) Trusted settings/admin review

Trusted settings/admin UX should review role/default changes through `intent.role.binding.diff` rather than through raw settings blobs or desktop-registry deltas.
That keeps the human question legible:

- which role changed?
- did the default target move?
- did chooser enrollment broaden or narrow?

### 2) Drift bundles

When remembered role-binding state changes, attach `intent.role.binding.diff` next to other posture diffs in `drift.bundle`.
That keeps workstation routing/default drift reviewable without needing a special desktop-only review path.

See: `docs/395-drift-bundles-and-review-summaries.md` and `docs/430-diff-surface-registry.md`.

### 3) Evidence spine

The evidence story for ordinary URI handling now becomes:

- `intent.role.binding` — authoritative remembered state snapshot
- `intent.role.binding.diff` — compact change summary when that snapshot changes
- `intent.role.binding.event` — durable mutation trace for those remembered changes
- `intent.route.receipt.role_binding_digest` — proof of which remembered snapshot actually routed the request

That is enough to keep support/export surfaces honest before a richer settings-receipt lane exists. `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` now carries the same review-surface handle into spent-authority retry evidence through `consumed_diff_digest`, so detached bundles can still name which reviewed change actually landed. The durable mutation trace alongside that review surface is now `intent.role.binding.event`, so time-ordered remembered-role changes can land in the event journal without bloating this diff.

See: `docs/229-evidence-spine-overview.md`.

## Product-shape fit without forks

- **A / secure fleet host:** often compiles to no ordinary interactive bindings, but if a maintenance surface exists, the same diff shape works.
- **B / secure workstation:** this is the primary beneficiary; browser/mail target changes become reviewable instead of folklore.
- **C / general-purpose OS:** can still reuse the same typed diff even if later host-native adapters exist.
- **D / appliance factory / regulatory:** production images may have thin or absent role bindings, but maintenance/operator images can still use the same artifact family.

## Risk flags

Diff generators should emit conservative, stable reason codes:

- `role-binding-default-changed`
- `role-binding-target-enrolled`
- `role-binding-target-removed`

These are canonical ids in `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## References

- Android RoleManager (browser/home/SMS and other explicit system roles): https://developer.android.com/reference/android/app/role/RoleManager
- XDG AppChooser backend (chooser from a provided list): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.AppChooser.html
- XDG Settings backend (read-only; not for general purpose settings): https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Settings.html

## Related docs

- `docs/395-drift-bundles-and-review-summaries.md`
- `docs/430-diff-surface-registry.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`
- `spec/intent.role.binding.schema.json`
- `spec/intent.role.binding.diff.schema.json`

Last updated: 2026-03-18r289
