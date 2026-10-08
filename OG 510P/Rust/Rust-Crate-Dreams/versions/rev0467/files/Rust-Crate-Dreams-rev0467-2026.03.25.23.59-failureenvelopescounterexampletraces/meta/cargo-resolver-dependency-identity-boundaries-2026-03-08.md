# Cargo resolver explanation boundaries — dependency identity, rename surface, and registry truth (2026-03-08)

## Main judgment

When a future pass touches **P-0468 Cargo Resolver Explanation Kit**, it should keep one more boundary explicit:

**resolver explanation is not only about why a dependency participated; it is also about which name surface actually referred to it.**

Current Cargo substrate makes that materially real:

1. dependency-spec docs say renamed optional dependencies use the **dependency name**, not the original package name, for feature syntax,
2. the same docs say transitive dependency-feature forwarding also follows the renamed dependency key,
3. `cargo metadata` docs say package definitions are meant to reproduce manifest information while the resolve graph may be target-filtered,
4. registry-index docs say renamed dependencies swap fields across publish API / index / `cargo metadata`,
5. the original rename-dependency tracking issue explicitly called out metadata support and command-line ambiguity as real implementation work,
6. issue history says inherited workspace dependencies still cannot simply be renamed from the member side,
7. and recent private-registry issues show renamed + gated dependencies can still produce misleading missing-package failures.

So a worthy **P-0468** bundle should not just say “feature X is active” or “dependency Y is present.”
It should also be able to say:

- which local dependency key referred to the dependency in the subject manifest,
- which original package name was being requested from the registry,
- which token a human would actually use in manifest feature references,
- how `cargo metadata` represented the rename,
- how registry / publish surfaces represented the rename,
- and whether inheritance or registry publication made the answer conservative or manual-review territory.

## Receiver-facing artifact to prefer

Freeze one compact artifact instead of burying the distinction inside notes:

- **`dependency-identity.report.json`** — for each dependency under discussion, record the local dependency key, original package name, rename state, feature-reference token, metadata/index identity fields, and exactness level.

## Keep these boundaries separate

Do not flatten together:

- local dependency key,
- original package name,
- `cargo metadata` `name` / `rename`,
- registry-index `name` / `package`,
- publish-surface alias fields,
- and workspace-inherited declarations that ignored `package = ...`.

## False-gap patterns to resist

1. “The package is called `foo`, therefore `foo` must also be the feature token.”
2. “`cargo metadata` and the index use the same fields for renamed dependencies, so cross-surface comparison is trivial.”
3. “A workspace member wrote `package = ...`, therefore the inherited dependency was definitely renamed.”
4. “This is just a private-registry quirk” when current issue history shows renamed + gated dependencies can still fail in receiver-facing workflows.

## What to do next

Good next passes should add tiny scenario bundles for:

- a renamed optional dependency whose feature namespace follows the local dependency key,
- a workspace-inherited dependency whose attempted rename is ignored,
- and conservative/manual-review cases where registry or publish surfaces describe the same rename with different field vocabularies.

## Sources

- Cargo specifying dependencies docs: https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- Cargo metadata docs: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo registry-index docs: https://doc.rust-lang.org/cargo/reference/registry-index.html
- Cargo rename-dependency tracking issue: https://github.com/rust-lang/cargo/issues/5653
- Cargo issue on inherited dependency renames: https://github.com/rust-lang/cargo/issues/12546
- Cargo issue on renamed + gated dependency in private registry: https://github.com/rust-lang/cargo/issues/14365
- Cargo issue on renamed crates.io dependency through different registry: https://github.com/rust-lang/cargo/issues/14399
