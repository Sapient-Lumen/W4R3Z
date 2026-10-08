# Gap: Manifest truth across authored, published, and consumed Cargo metadata

## Summary
Rust’s package/workspace manifest has become a strategic boundary, not just a config file.
`Cargo.toml` and embedded script frontmatter now sit at the junction of:
- package identity,
- feature and optional-dependency intent,
- publish restrictions,
- workspace inheritance and discovery,
- script execution,
- machine-readable external-tool imports,
- and increasingly, user-facing metadata that other tools want to render or diff.

But the ecosystem still lacks one portable, reviewable layer that answers:
- what the author actually wrote,
- what Cargo inferred or defaulted,
- what `cargo package` rewrote for publication,
- what external consumers like `cargo metadata`, `cargo info`, registries, docs hosts, or script runners actually import,
- and what changed between those views.

Today those questions are spread across:
- raw `Cargo.toml` diffs,
- `cargo metadata` output,
- package tarball inspection,
- docs.rs / registry rendering,
- `cargo info` screens,
- workspace/config discovery lore,
- and single-file-script frontmatter rules.

That is the gap: **Rust has manifest ingredients, but not yet a shared manifest-truth substrate.**

## Why this gap is sharper now
### Cargo and manifest evolution signal
Cargo 1.94 makes it unusually clear that manifest behavior is still evolving at a strategic layer: Cargo is handling TOML 1.1 transition issues, experimenting with `cargo-cargofmt` because manifest style itself affects compatibility and expectations, and actively discussing workspace/config discovery behavior.
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

### Publish rewrite signal
`cargo package` explicitly rewrites and normalizes the published `Cargo.toml`, removes `[patch]`, `[replace]`, and `[workspace]`, and includes `Cargo.lock` by default. That means the authored manifest and the published manifest are already materially different artifacts, but the ecosystem still lacks a first-class diff/report layer for that boundary.
https://doc.rust-lang.org/cargo/commands/cargo-package.html

### Feature metadata signal
RFC 3416 argues that feature descriptions, visibility, and deprecation metadata are currently under-expressed in Cargo manifests, and Cargo’s current planning keeps that work alive through visibility/deprecation follow-on RFCs. That means the manifest is becoming more consumer-facing, not less.
https://rust-lang.github.io/rfcs/3416-feature-metadata.html
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

### Workspace-inheritance signal
The workspaces reference now keeps `workspace.package`, `workspace.dependencies`, and `workspace.lints` visibly separate and explicit, and it is clear that Cargo will search parent directories for a workspace root while `package.workspace` can override that search. That means package-local authored text and inherited/defaulted/discovered interpretation are already different lanes in ordinary workflows.
https://doc.rust-lang.org/cargo/reference/workspaces.html

### Script/frontmatter signal
The accepted cargo-script/frontmatter direction means manifests can now live inside `.rs` files, with explicit defaulting and disallowed-field rules. That widens the manifest problem from package roots to lightweight execution lanes.
https://rust-lang.github.io/rfcs/3502-cargo-script.html
https://rust-lang.github.io/rfcs/3503-frontmatter.html

### External-tool / consumer-lane signal
Cargo’s external-tools guidance says `cargo metadata` is the stable, versioned machine-readable interface for package structure, and the command docs still recommend pinning `--format-version`. Cargo 1.94 also changed `cargo info` to default to inspecting the local package when no registry is explicitly specified. That is valuable, but it is direct evidence that machine-readable imports and human-readable projections are distinct consumer lanes, and neither one answers authored-vs-published differences, frontmatter/defaulting truth, or registry/docs lossiness by itself.
https://doc.rust-lang.org/cargo/reference/external-tools.html
https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
https://doc.rust-lang.org/cargo/CHANGELOG.html

## What a worthy contribution would look like
A worthy contribution is **not** just another formatter, editor, metadata wrapper, or registry page.

It would instead provide:
- a canonical subject model for one manifest-bearing thing,
- an authored-manifest report with explicit/defaulted/inferred fields,
- a publish-rewrite diff for authored vs packaged manifest truth,
- a feature catalog with visibility/deprecation/documentation posture,
- consumer-import reports for `cargo metadata`, `cargo info`, registry/docs/script consumers,
- and a portable pack/diff layer for reviews, releases, migrations, and policy handoffs.

That would let teams:
- review manifest changes without guessing which ones survive packaging,
- keep feature-surface changes separate from activated-feature/runtime results,
- stop rediscovering workspace/config/frontmatter edge cases,
- and import the same manifest facts into publish, support, trust, and migration workflows.

## Why existing approaches are still insufficient
- **Raw `Cargo.toml` diffs are not semantic reports.**
  They do not say what was defaulted, stripped, normalized, or ignored.
- **`cargo metadata` is necessary but not enough.**
  It gives stable machine-readable structure, not authored/published/consumer-lane comparisons.
- **`cargo info` is presentation, not a review substrate.**
  It is helpful for humans but does not define a portable attachment model.
- **Publish/package behavior is easy to forget.**
  `cargo package` normalization means consumer-visible truth can differ from repo truth.
- **Script/frontmatter and workspace discovery widen the problem.**
  The active manifest may not even be a normal package-root `Cargo.toml`.

## Archive decision
Add a new **Manifest Surface Kit** centered on:
- `manifest-subject/v0`
- `manifest-authored-report/v0`
- `manifest-publish-diff/v0`
- `feature-catalog/v0`
- `manifest-consumer-report/v0`
- `manifest-pack/v0`

Then promote an explicit **Manifest Truth Stack** plus a **Manifest Surface lane map** that keeps authored-manifest truth, inherited/defaulted/discovered interpretation, published-manifest truth, script/frontmatter subject truth, machine-consumer imports, human projections, feature-surface watch posture, and downstream package/install/policy conclusions separate instead of letting every consumer silently tell a different story.
