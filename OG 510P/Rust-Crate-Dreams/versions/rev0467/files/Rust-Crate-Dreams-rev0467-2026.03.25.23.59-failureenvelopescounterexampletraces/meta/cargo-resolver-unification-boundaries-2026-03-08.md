# Cargo resolver explanation — feature-unification policy and participant-scope boundaries (2026-03-08)

## Main judgment

The next missing receiver-facing layer for **P-0468 Cargo Resolver Explanation Kit** is not another graph export.
It is a compact way to freeze **which packages were allowed to participate in feature unification** and **which policy shaped the answer**.

Current Cargo substrate is explicit enough to justify that split:

- unstable Cargo docs define `resolver.feature-unification` with explicit `selected`, `workspace`, and `package` modes,
- resolver docs still say dependency features unify across multiple selected workspace packages,
- the workspace feature-unification tracking issue still has unresolved representation questions for package mode,
- and the long-running package-set sensitivity issue is still open.

So a worthy **P-0468** bundle should not just say “feature X is active.”
It should also be able to say:

- which packages were selected,
- which packages participated in feature unification,
- whether another out-of-selection member influenced the result,
- whether package mode intentionally preferred duplicate builds,
- and whether the answer is directly observed, conservative, or still manual-review-required.

## What future passes should freeze explicitly

For any serious resolver bundle, preserve:

1. the explanation subject (`-p`, `--bin`, workspace root, or equivalent),
2. selected-package scope versus participating-package scope,
3. the active `resolver.feature-unification` mode,
4. whether another package influenced the result,
5. whether package mode changed the duplicate-build story,
6. and whether the answer is exact, conservative, or manual-review-required.

## What this should hand other people

A worthy bundle in this seam should provide:

- one `unification-scope.report.json` that records selected packages, participating packages, and policy,
- one `resolve-why.lock` that freezes command subject and unification policy,
- and one `resolver-choice.receipt.json` that states whether the answer came from stable surfaces, nightly imports, issue-style repro capture, or conservative reconstruction.

## Keep these boundaries separate

Do **not** collapse this seam into:

- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — that crate is about tool workflow coverage and invocation topology, not dependency feature unification policy,
- **P-0505 Cargo Host/Target Scope Contract Kit** — that crate is about host/target config scope, not package participation in resolver answers,
- or a generic “workspace features are spooky” complaint.

The sharper claim is narrower:
**which packages were allowed to influence this answer, and which unification policy actually won?**

## Sources

- Cargo unstable docs: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo resolver docs: https://doc.rust-lang.org/cargo/reference/resolver.html
- Tracking issue for workspace feature-unification: https://github.com/rust-lang/cargo/issues/14774
- Long-running issue on feature selection depending on package set: https://github.com/rust-lang/cargo/issues/4463
