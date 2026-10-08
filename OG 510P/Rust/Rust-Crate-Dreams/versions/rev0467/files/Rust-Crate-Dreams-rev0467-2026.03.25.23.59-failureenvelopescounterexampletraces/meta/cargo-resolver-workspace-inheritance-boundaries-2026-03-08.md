# Cargo resolver explanation — workspace dependency inheritance and manifest-origin boundaries (2026-03-08)

## Main judgment

The next missing receiver-facing layer for **P-0468 Cargo Resolver Explanation Kit** is not another graph view.
It is a compact way to freeze **where an effective dependency policy actually came from** when `[workspace.dependencies]`, member manifests, and target-specific inherited edges all participate.

Current Cargo substrate is explicit enough to justify that split:

- workspace docs say features declared in `[workspace.dependencies]` are additive with member dependency features,
- dependency-spec docs still say inherited dependencies cannot use keys other than `optional` and `features`, with `default-features` named as an example,
- a current docs issue says that wording is easy to misread against real behavior,
- issue history shows member `default-features = false` can be neutralized unless the workspace dependency also disables defaults,
- release notes document the converse case where a member inherited dependency with `default-features = true` re-enables defaults,
- and target-specific inherited dependencies still have enough bug history to justify conservative or manual-review boundaries.

So a worthy **P-0468** bundle should not just say “feature X is active” or “defaults are on.”
It should also be able to say:

- whether the effective policy came from the workspace root, the member manifest, or both,
- whether default features were disabled, neutralized, or re-enabled,
- whether a target-specific inherited edge changed the story,
- and whether the answer is directly observed, conservative, or manual-review-required.

## What future passes should freeze explicitly

For any serious resolver bundle, preserve:

1. the explanation subject (`-p`, `--bin`, workspace root, or equivalent),
2. the dependency package being explained,
3. manifest origin (`workspace.dependencies`, member dependency, or target-specific member dependency),
4. declared feature additions versus default-feature switches,
5. the effective default-feature outcome (disabled, neutralized by workspace pressure, re-enabled by member, or manual-review-required),
6. and whether the answer is exact, conservative, or still manual-review-required.

## What this should hand other people

A worthy bundle in this seam should provide:

- one `dependency-origin.report.json` that records manifest origin and effective inherited policy,
- one `resolve-why.lock` that freezes the command subject and selection scope,
- one `feature-intent.report.json` when a subject explicitly requested defaults on or off,
- and one `resolver-choice.receipt.json` that states whether the answer came from stable docs/manifests, issue-style repro capture, or conservative reconstruction.

## Keep these boundaries separate

Do **not** collapse this seam into:

- **P-0505 Cargo Host/Target Scope Contract Kit** — that crate is about host-vs-target configuration application, not manifest-origin truth for inherited dependencies,
- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — that crate is about tool workflow coverage and invocation topology, not who authored the effective dependency policy,
- or a generic “workspace dependencies are confusing” complaint.

The sharper claim is narrower:
**where did this effective dependency policy come from, and which inherited/default-feature rule actually won?**

## Sources

- Cargo workspaces docs: https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo specifying dependencies docs: https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- Cargo issue on inherited `default-features = false`: https://github.com/rust-lang/cargo/issues/11329
- Cargo issue on poor default-features interaction in workspace dependencies: https://github.com/rust-lang/cargo/issues/12162
- Cargo docs issue on inherited `default-features` wording: https://github.com/rust-lang/cargo/issues/14841
- Rust release notes documenting member-side re-enable behavior: https://doc.rust-lang.org/beta/releases.html
- Cargo issue on target-specific inherited dependency behavior: https://github.com/rust-lang/cargo/issues/11779
