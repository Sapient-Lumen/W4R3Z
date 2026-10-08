# Cargo resolver explanation — feature intent and suppression boundaries (2026-03-08)

## Main judgment

The next missing receiver-facing layer for **P-0468 Cargo Resolver Explanation Kit** is not another graph view.
It is a compact way to freeze **what someone asked Cargo to keep on or off** and **why the effective feature state still differed**.

Current Cargo substrate is explicit enough to justify that split:

- Cargo features docs say `default-features = false` may still fail to keep defaults off if another dependency path enables them,
- the same docs say `--no-default-features` disables defaults for the selected packages, not for every dependency edge in the workspace,
- resolver docs still say features unify across multiple selected workspace packages,
- the workspace feature-unification tracking issue is still open,
- and open workspace issues still show command/subject selection changing the observed feature set.

So a worthy **P-0468** bundle should not just say “feature X is active.”
It should also be able to say:

- who explicitly asked for a feature,
- who explicitly asked for defaults to stay off,
- which command/package/target subject the explanation is about,
- whether another selected or participating package overrode that negative intent through unification,
- and whether the answer is directly observed, conservative, or still manual-review-required.

## What future passes should freeze explicitly

For any serious resolver bundle, preserve:

1. the explanation subject (`-p`, `--bin`, workspace root, or equivalent),
2. positive feature requests versus negative feature intent (`default-features = false`, `--no-default-features`),
3. whether the observed feature state came from the subject itself or from another selected/participating package,
4. whether the mismatch is about default features, named features, or both,
5. whether the investigative surface preserves subject scope or merges it away,
6. and whether the answer is exact, conservative, or manual-review-required.

## What this should hand other people

A worthy bundle in this seam should provide:

- one `feature-intent.report.json` that records requested enable/disable intent and the effective result,
- one `resolve-why.lock` that freezes command subject and unification policy,
- one `unification-scope.report.json` when other packages influenced the result,
- and one `resolver-choice.receipt.json` that states whether the answer came from stable surfaces, nightly imports, issue-style repro capture, or conservative reconstruction.

## Keep these boundaries separate

Do **not** collapse this seam into:

- **P-0494 Cargo Compile-Time-Deps Workflow Kit** — that crate is about tool workflow coverage and invocation topology, not dependency feature intent,
- **P-0505 Cargo Host/Target Scope Contract Kit** — that crate is about host/target config scope, not feature enable/disable intent,
- or a generic “workspace features are spooky” complaint.

The sharper claim is narrower:
**what did this subject ask for, what stayed on anyway, and who caused that?**

## Sources

- Cargo features docs: https://doc.rust-lang.org/cargo/reference/features.html
- Cargo resolver docs: https://doc.rust-lang.org/cargo/reference/resolver.html
- Tracking issue for workspace feature-unification: https://github.com/rust-lang/cargo/issues/14774
- Cargo issue on `--bin` versus `-p` feature behavior: https://github.com/rust-lang/cargo/issues/8157
- Cargo issue on `default-features = false` inside a workspace: https://github.com/rust-lang/cargo/issues/8366
- Cargo issue on too-few features masked by unification: https://github.com/rust-lang/cargo/issues/14021
- Cargo issue on `cargo tree` subject scope under workspace feature-unification: https://github.com/rust-lang/cargo/issues/16583
