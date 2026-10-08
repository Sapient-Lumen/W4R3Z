# Cargo resolver explanation boundaries — feature origin, hidden aliases, and weak forwarding (2026-03-08)

## Main judgment

When a future pass touches **P-0468 Cargo Resolver Explanation Kit**, it should keep one more boundary explicit:

**feature resolution is not only about which feature ended up active; it is also about what kind of authored feature syntax produced that state.**

Cargo's current feature docs make three materially different cases explicit:

1. an optional dependency automatically creates an implicit feature alias,
2. any `dep:pkg` mention suppresses that implicit alias and makes the dependency an internal detail of some other feature,
3. `pkg/feat` forwards a dependency feature and also activates an optional dependency, while `pkg?/feat` forwards only if something else already activated that dependency.

Those are not the same user story, the same support burden, or the same artifact contract.

## What a worthy P-0468 bundle should preserve

At minimum it should be able to say:

- whether a subject feature name was explicitly authored or only exists as an implicit optional-dependency alias,
- whether a dependency name was intentionally hidden by `dep:` syntax,
- whether a clause activates an optional dependency directly,
- whether a clause only forwards a dependency feature if another path already activated that dependency,
- and whether a human-facing investigative surface flattened two of those cases together.

## Receiver-facing artifact to prefer

Freeze one compact artifact instead of burying the distinction inside notes:

- **`feature-origin.report.json`** — for each subject feature, record the authored token, the origin kind, the dependency activation rule, the user-visible/hidden status, and whether the answer is exact or conservative.

## Keep these separate

Do not flatten together:

- implicit optional-dependency feature aliases,
- explicit named features,
- hidden optional dependencies referenced with `dep:`,
- strong dependency feature forwarding with `pkg/feat`,
- weak dependency feature forwarding with `pkg?/feat`,
- and downstream surfaces that lost the original authoring intent.

## False-gap patterns to resist

1. “The dependency showed up in metadata, therefore the crate already knows whether it was public or hidden.”
2. “A dependency feature was forwarded, therefore that clause must also have activated the optional dependency.”
3. “If Cargo reported a feature-like `cfg`, then that name must correspond to a real public manifest feature.”
4. “This is just a parser quirk” when current docs, issue history, and changelog notes show that namespaced and weak feature syntax still produces receiver-facing confusion.

## What to do next

Good next passes should add tiny scenario bundles for:

- `dep:`-hidden optional dependencies,
- weak dependency forwarding that requires prior activation,
- and conservative/manual-review cases where metadata or emitted `cfg(feature = ...)` names do not preserve author intent cleanly.
