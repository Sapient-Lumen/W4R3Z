---
id: P-0056
title: Cargo Install Policy & Cooldown Kit — lockfile stance, pubtime age-gates, and install receipts for Rust binary installs
status: idea
domains: [cargo, supply-chain, policy, devtools, ci, security, release]
last_reviewed: 2026-03-16
evidence:
  - https://doc.rust-lang.org/cargo/commands/cargo-install.html
  - https://doc.rust-lang.org/cargo/commands/cargo.html
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://doc.rust-lang.org/cargo/reference/registry-authentication.html
  - https://doc.rust-lang.org/cargo/reference/config.html
---

# Problem

Rust now has a much more concrete install-policy seam than this archive recognized when this proposal was first sketched.

The official substrate is sharper than it used to be:

- `cargo install` still ignores the packaged `Cargo.lock` by default unless `--locked` is used,
- `cargo install` has explicit installation-root precedence and explicit install tracking metadata,
- `--no-track` now has a very clear tradeoff: Cargo gives up its protection against concurrent installs and safe overwrite tracking,
- Cargo registry auth has a richer credential-provider model,
- and crates.io now publishes **`pubtime`** in index entries, explicitly enabling future cooldown-period workflows.

Those are not small details.
Together they create a real missing crate opportunity.

Teams increasingly need install decisions to be reviewable:

- should we require `--locked` for this install,
- when is an unlocked install acceptable,
- should freshly published versions be blocked for a cooldown window,
- what evidence did we have about publish age, lockfile availability, source, auth path, and install root,
- and how do we keep source installs, binary installs, and policy exceptions from degenerating into shell-script folklore?

The missing crate is not just a wrapper around `cargo install`.
The missing crate is a **Cargo Install Policy & Cooldown Kit**: a crate and cargo-adjacent tool that produces policy files, dry-run install plans, cooldown verdicts, and durable install receipts.

# Main judgment

This is worthy because it sits at a broad Rust ecosystem seam:

- contributor onboarding,
- CI/bootstrap flows,
- `cargo-*` plugin installation,
- enterprise allowlist policy,
- release hygiene,
- and “don’t install the version published 30 seconds ago” risk management.

The missing value is not only faster installs or stricter defaults.
The missing value is **policy with receipts**.

# What it provides

- `install-policy.toml` — desired policy for lockfile stance, allowed sources, cooldown windows, allowed registries, install-root policy, tracking requirements, and exception classes.
- `install-request.json` — normalized request describing crate, version requirement, source kind, requested binary/example, target/profile/features, and execution environment.
- `install-plan.json` — dry-run plan showing selected version/source, whether packaged lockfile use is required, whether cooldown or allowlist rules apply, which auth path is expected, and where artifacts would be installed.
- `install-cooldown.report.json` — records publish-age evaluation using crates.io `pubtime` when available, including `age_unknown`, `age_below_minimum`, `age_satisfied`, or `not_applicable`.
- `install.receipt.json` — durable record of the exact command, selected version/source, lockfile mode, auth/provider path, install root, tracking mode, and policy hash.
- `install-exception.ledger.toml` — explicit waivers for cases like no packaged lockfile, git source, path source, mirror-only installs, or emergency pinning.
- `install-policy.diff.json` — compare two plans or receipts and classify `version_changed`, `lock_mode_changed`, `cooldown_blocked`, `source_changed`, `install_root_changed`, `tracking_changed`, and `auth_path_changed`.
- `cargo install-policy plan` — compute a dry-run install plan.
- `cargo install-policy check` — evaluate policy without mutating anything.
- `cargo install-policy run` — execute the install and emit a receipt.
- `*.installpolicy.zip` — portable artifact for CI, audit review, and support tickets.

# What the crate should provide other people

1. **A boring policy file** for Rust binary installs.
2. **A dry-run plan** that explains lockfile, age-gate, source, and root decisions before mutation.
3. **A cooldown report** that uses published registry facts instead of vague “wait a bit” folklore.
4. **An install receipt** that captures source, version, root, tracking mode, and policy inputs.
5. **A waiver ledger** so exceptions are explicit rather than hidden in shell scripts.
6. **A shared language** for source installs, binary installs, and install risk review.

# Persona / who it’s for

- CI and release engineers
- teams managing crate-shipped developer tools
- enterprises with installation policy requirements
- maintainers documenting recommended install commands
- security-conscious OSS projects

# Users & user stories

- **Maintainer**: “I want one recommended install policy for our tool, not a README that silently depends on defaults.”
- **CI owner**: “Reject freshly published versions for a cooldown window unless there is an explicit waiver.”
- **Enterprise**: “Require `--locked` when possible, approved registries, tracked installs, and written receipts.”
- **Developer**: “Tell me exactly why an install was blocked, allowed, or forced into a stricter mode.”
- **Support engineer**: “Attach one artifact that shows source, version, root, cooldown evaluation, and auth path.”

# Prior art (and why it’s insufficient)

- `cargo install` is the actual installer, but its docs intentionally describe command behavior rather than organizational policy.
- crates.io `pubtime` enables age-based policy, but Cargo does not yet provide a stable end-user cooldown workflow by itself.
- Cargo registry-auth docs describe provider behavior, but not install-stage policy artifacts.
- Teams can write shell wrappers, but those usually fail to preserve root choice, tracking mode, or publish-age reasoning in a reusable way.

What remains missing is the **policy + plan + cooldown + receipt** layer above install substrate.

# Design goals

1. **Dry-run first** — install plans should be reviewable before mutation.
2. **Policy explicitness** — lockfile stance, cooldowns, roots, and source rules must be encoded rather than implied.
3. **Registry-fact aware** — use `pubtime` and source metadata when available, while admitting when they are unavailable.
4. **Tracking-honest** — record when `--no-track` or similar choices reduce safety.
5. **Adapter-friendly** — leave room for source-install and binary-install backends without collapsing policy and execution.
6. **Support-bundle friendly** — optimize for audit and support use.

# MVP surface

- Minimal types: `InstallPolicy`, `InstallRequest`, `InstallPlan`, `InstallCooldownReport`, `InstallReceipt`, `InstallExceptionLedger`, `InstallPolicyDiff`, `InstallPolicyBundle`
- Minimal functions:
  - `evaluate_install_policy()`
  - `plan_install()`
  - `compute_cooldown_report()`
  - `execute_install_with_receipt()`
  - `diff_install_receipts()`
- Feature flags:
  - `cargo`
  - `serde`
  - `cooldown`
  - `registry-facts`
  - `ci`

# Compatibility story

- Stable Cargo first for install planning and receipts.
- Cooldown logic is optional and only authoritative when registry `pubtime` facts exist.
- Must preserve `not_applicable` or `age_unknown` for git/path/local installs rather than faking confidence.
- Should remain useful even if Cargo later adds first-class cooldowns, because organizations will still need waivers and receipts.

# Conformance & fixtures

- One fixture where packaged lockfile exists but policy requires `--locked` and the default install would have been looser.
- One fixture where a just-published version is blocked by a cooldown rule using crates.io `pubtime`.
- One fixture where a git install has `age_unknown` and must be judged by a different rule.
- One fixture where `--no-track` is disallowed because concurrent install protection matters.
- Goldens for `cooldown_blocked`, `age_unknown`, `tracking_changed`, and `lock_mode_changed`.

# Path to boring stability

- Freeze plan, cooldown, receipt, and waiver vocabulary before broad backend support.
- Start with source-install planning and report-only mode.
- Preserve unknown/unsupported cases explicitly instead of auto-approving them.
- Keep policy logic separable from installer backends.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that read an install-policy file, evaluate a requested Rust binary install, emit a dry-run plan and cooldown verdict, optionally execute the install, and write a durable receipt.

# De-risk plan

1. Start with dry-run plans and receipt-only wrappers around `cargo install`.
2. Add crates.io `pubtime`-based cooldown checks before more elaborate policy packs.
3. Keep git/path installs explicitly second-class in age evaluation until better source facts exist.
4. Treat auth/provider details as observed facts, not policy magic.

# Non-goals

- Not a replacement for Cargo’s installer.
- Not a general malware detector.
- Not a replacement for trusted publishing or post-publish receipts.
- Not a promise that every install source can be judged identically.

# Architecture & API sketch

```rust
pub struct InstallCooldownReport {
    pub source_kind: String,
    pub selected_version: String,
    pub minimum_age_hours: Option<u64>,
    pub status: String,
}

pub fn plan_install(req: &InstallRequest, policy: &InstallPolicy) -> Result<InstallPlan>;
pub fn compute_cooldown_report(plan: &InstallPlan) -> Result<InstallCooldownReport>;
```

# Maintenance & governance plan

- Keep policy and receipt schemas small and versioned.
- Preserve a strict distinction between registry facts, policy decisions, and backend execution.
- Maintain backend adapters as thin layers.
- Test cooldown and lockfile reasoning with frozen fixtures.

# Adoption plan

1. Start as a report-only cargo subcommand.
2. Integrate with workspace tool-manifest flows as an optional backend.
3. Add policy packs for common CI/bootstrap cases.
4. Only later broaden to richer binary-install adapters.

# Open questions

- What should the default cooldown stance be for developer laptops versus CI?
- How much policy should depend on crates.io-specific facts versus generic registry inputs?
- Should `--no-track` ever be allowed by default outside ephemeral environments?
- How much of binary-install strategy selection belongs in this crate versus sibling tool-manifest crates?

# Sources

See front matter links.
