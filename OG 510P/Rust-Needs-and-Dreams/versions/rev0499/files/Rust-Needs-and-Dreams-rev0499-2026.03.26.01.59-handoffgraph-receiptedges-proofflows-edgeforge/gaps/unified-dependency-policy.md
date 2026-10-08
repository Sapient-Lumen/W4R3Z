# Gap: Unified, Explainable Dependency Policy

## Summary
Rust already has real building blocks for dependency and release policy:
- `cargo-deny` for licenses, bans, advisories, sources, target filtering, and machine-meaningful check classes,
- `cargo-audit` and `rustsec` for vulnerability scanning and advisory-database consumption,
- `cargo vet` for criteria, imported audit sets, publisher trust, and project-level policy customization,
- crates.io signals like the Security tab, Trusted Publishing posture, blocked risky CI triggers, and publication time,
- and a growing family of ecosystem evidence surfaces in this archive: Trust Signals, Lifecycle Ledger, SBOM Evidence, Signed Binaries, Typosquat Guard, Support Envelope, and more.

But the ecosystem still lacks one portable, reviewable layer that answers:
- what evidence was imported,
- what rules applied to which scope,
- what was missing or stale,
- why the result passed, warned, failed, or remained inconclusive,
- and what changed since the previous reviewed baseline.

Today that logic is usually spread across:
- multiple tool configs,
- CI scripts,
- shell wrappers,
- human interpretation of logs,
- and ad hoc local exception lists.

This is the gap: **Rust has policy ingredients, but not yet a shared policy decision substrate.**

## Why this gap is sharper now
The ecosystem is no longer starting from zero.
It now has enough evidence sources that the missing piece is mostly the **composition and explanation layer**.

### Upstream Rust signal
Rust’s 2026 flagships explicitly include **Secure your supply chain**, with milestones around stabilizing public/private dependencies and SBOM support. That is strong evidence that dependency and release controls are now core ecosystem work rather than niche enterprise add-ons.
https://rust-lang.github.io/rust-project-goals/2026/flagships.html

### Registry signal
crates.io now surfaces a **Security** tab based on RustSec advisories, supports GitLab Trusted Publishing in addition to GitHub Actions, has a Trusted-Publishing-only mode, blocks risky CI triggers like `pull_request_target` and `workflow_run`, and records `pubtime` in index entries. That means registries are already publishing policy-relevant facts; the ecosystem still lacks a common decision layer over them.
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

### Audit and trust signal
`cargo vet` is already more than a yes/no scanner: it has built-in criteria like `safe-to-run` and `safe-to-deploy`, allows custom criteria, project-specific policy tuning, imported audit sets, and date-bounded trusted-publisher entries. That is strong evidence that policy in Rust is already multi-dimensional and scope-sensitive.
https://mozilla.github.io/cargo-vet/audit-criteria.html
https://mozilla.github.io/cargo-vet/specifying-policies.html
https://mozilla.github.io/cargo-vet/trusted-entries.html
https://mozilla.github.io/cargo-vet/config.html

### Dependency hygiene signal
`cargo-deny` already models target-aware graph filtering, advisories including unmaintained crates, bans for specific crates or duplicate versions, SPDX-oriented license controls, and check-specific exit-code classes. That is precisely the kind of structured signal a better policy layer should consume rather than re-implement.
https://embarkstudios.github.io/cargo-deny/checks/cfg.html
https://embarkstudios.github.io/cargo-deny/checks/advisories/index.html
https://embarkstudios.github.io/cargo-deny/checks/bans/index.html
https://embarkstudios.github.io/cargo-deny/checks/licenses/cfg.html
https://embarkstudios.github.io/cargo-deny/cli/check.html

### Vulnerability signal
`cargo-audit` and the `rustsec` crate already provide advisory-database-backed scanning, and `cargo audit bin` can audit binaries directly, becoming fully accurate when used with `cargo auditable`. That means policy can increasingly operate at both workspace and shipped-artifact layers — but still lacks one standard output for doing so.
https://docs.rs/crate/cargo-audit/latest
https://docs.rs/rustsec/latest/rustsec/

## What a worthy contribution would look like
A worthy contribution is **not** “another security score” and **not** a monolithic replacement for cargo-deny or cargo-vet.

It would instead provide:
- a common subject model for workspace / lockfile / artifact slices,
- a common input catalog for imported evidence and freshness,
- a common rule catalog for explicit policy,
- a common decision report with reason-coded outcomes,
- durable waivers with ownership and expiry,
- and diffable reports for PRs, releases, and audits.

That would let organizations:
- keep existing tools,
- share results across CI and review workflows,
- and stop burying important policy decisions inside custom glue.

## Why existing approaches are still insufficient
- **Tool-specific configs are not the same as portable policy artifacts.**
  They are often tightly coupled to one CLI.
- **Exit codes are too lossy.**
  They tell CI that something failed, not what evidence led there or whether the result was waived.
- **Ad hoc scripts erase provenance.**
  They often flatten advisories, licenses, trust, and lifecycle into one opaque gate.
- **Local exceptions age badly.**
  Teams need reviewable waiver records with owners and expiry.
- **Different scopes need different policy.**
  Runtime, build, dev, proc-macro, and release-artifact concerns are not interchangeable.

## Archive decision
Deepen **Policy Kit** into a first-class policy-decision substrate centered on:
- `policy-subject/v0`
- `policy-input-catalog/v0`
- `policy-rule-catalog/v0`
- `policy-waiver/v0`
- `policy-decision-report/v0`
- `policy-diff-report/v0`
- `policy-pack/v0`

The contribution should be evaluated primarily as a **composition and explanation layer** over existing evidence sources, not as a new scanner or a new registry-controlled score.
