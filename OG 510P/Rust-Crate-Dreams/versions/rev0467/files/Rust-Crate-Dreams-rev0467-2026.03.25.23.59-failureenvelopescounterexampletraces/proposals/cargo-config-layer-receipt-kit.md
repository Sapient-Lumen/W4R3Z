---
id: P-0474
title: Cargo Config Layer Receipt Kit — effective-config traces, include graphs, override explanations, and redacted support bundles
status: idea
domains: [cargo, config, workspaces, ci, devtools, release-engineering]
last_reviewed: 2026-03-20
evidence:
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
---

# Problem

Cargo’s configuration surface has become powerful enough that the missing pain is no longer “can Cargo be configured?”

Cargo now has real substrate for serious config workflows:

- hierarchical probing across project, ancestor, root, and `$CARGO_HOME` config files,
- deterministic merge rules for scalars and arrays,
- environment-variable and `--config` overrides with higher precedence than config files,
- first-class include support that stabilized in Cargo 1.94, including optional includes,
- a growing ecosystem of config-controlled workflow seams like `doc.browser`, credential providers, target runners, unstable flags, and build-analysis switches,
- and an unstable `cargo config get` command for viewing config values.

But ordinary teams still lack a boring answer to questions like:

- which file, include, env var, or `--config` override actually won,
- which effective value was inherited versus injected at invocation time,
- whether the bundle was captured from one real Cargo invocation or reconstructed later from files,
- which paths were interpreted relative to which config root,
- whether an optional include was absent, ignored, or shadowed by a later override,
- which config facts are safe to attach to CI or support tickets without leaking tokens,
- whether another machine could actually replay the same config from the exported bundle,
- and whether a docs/build/publish failure is really a config drift problem instead of a source-code problem.

So the missing crate is not another config parser.

The missing crate is a **Cargo config layer receipt kit**: a small crate and cargo subcommand that capture the effective Cargo configuration as a reviewable, redacted, precedence-aware artifact.

# What it provides

- `config-profile.toml` — pins capture mode, redaction policy, env import policy, and whether unstable keys should be recorded.
- `config-files.graph.json` — discovered config files, include edges, optional-include results, and relative-path anchors.
- `config-effective.json` — normalized effective config values after merge/precedence resolution.
- `config-origins.json` — per-key origin trace showing winning source, shadowed sources, and override class (`file`, `include`, `env`, `--config`, `credentials`).
- `config-paths.report.json` — explains path interpretation roots for path-bearing keys and flags suspicious relative-path situations.
- `config-redaction.report.json` — says which secrets, tokens, provider arguments, or local paths were redacted and why.
- `invocation-basis.receipt.json` — captures whether the bundle came from a live invocation, what cwd/manifest anchor was in effect, and which explicit `--config` fragments or env overrides were part of the basis.
- `replayability.report.json` — says whether the exported bundle is replayable, inspectable-only, local-only, or redaction-broken, and why.
- `cargo config-receipt capture` — emit one effective-config bundle for the current invocation context.
- `cargo config-receipt diff <old> <new>` — compare effective config, origin traces, include graphs, and redaction-sensitive drift.
- `cargo config-receipt doctor` — flag suspicious precedence, missing optional includes, unsupported env overrides, and config-root path traps.
- `*.configbundle.zip` — portable artifact for CI debugging, docs/build/publish support, onboarding, and release review.

# What the crate should provide other people

1. **A boring effective-config receipt** instead of folklore about which `.cargo/config.toml` “must have won”.
2. **A precedence trace** for file, include, env, credentials, and `--config` overrides.
3. **An invocation-basis receipt** so a file reconstruction cannot masquerade as one failing command’s exact config context.
4. **A replayability report** so a redacted support bundle cannot masquerade as something another machine can faithfully rerun.
5. **A path-interpretation report** for tricky runner/browser/credential/provider/path settings.
6. **A bridge** between Cargo’s expanding config substrate and ordinary team support workflows.

# Persona / who it’s for

- workspace maintainers with layered project/user config
- CI owners debugging environment-sensitive failures
- release engineers dealing with registry, credential-provider, or publish config
- docs/build maintainers whose workflows depend on config more than source changes
- tool authors who need one stable artifact instead of reverse-engineering Cargo config precedence

# Users & user stories

- **Workspace maintainer**: “Show me every config file and include that affected this run, in winning order.”
- **CI owner**: “Tell me whether this failure came from an env override, a missing optional include, or a project config change.”
- **Support engineer**: “Attach one redacted bundle that explains why Cargo chose this runner, browser, registry, or unstable knob.”
- **Tooling author**: “Consume one effective-config artifact instead of scraping `cargo config get` text and probing the filesystem manually.”

# Prior art (and why it’s insufficient)

- Cargo’s config reference already documents precedence, includes, environment variables, credentials, and path rules.
- Cargo 1.94 stabilized config includes, and the current changelog also records recent fixes around `--config` precedence and related path/config edge cases.
- Nightly Cargo has `cargo config get` for viewing values.

That is strong substrate, but it is still mostly **documentation plus ad-hoc inspection**, not a compact **receipt / origin trace / redacted support bundle**. The unstable `cargo config` command helps inspect values, but it does not by itself create a durable artifact that explains origin, redaction, path anchoring, or drift between runs.

# Design goals

1. **Precedence-explicit** — every effective key should show what won and what lost.
2. **Invocation-honest** — the bundle must say whether it came from a live command capture or a later reconstruction.
3. **Redaction-first** — exported bundles must be safe enough for CI artifacts and issue filing.
4. **Replayability-explicit** — safe-to-share should not automatically imply safe-to-replay.
5. **Path-honest** — path interpretation and config-root anchoring must be visible.
6. **Include-aware** — optional and nested includes must remain first-class data.
7. **Stable-first** — useful on stable Cargo today, while optionally recording unstable keys without depending on nightly-only output.

# MVP surface

- Minimal types: `ConfigProfile`, `ConfigFileNode`, `EffectiveConfig`, `ConfigOrigin`, `ConfigPathReport`, `RedactionReport`, `InvocationBasisReceipt`, `ReplayabilityReport`, `ConfigBundle`
- Minimal functions:
  - `capture_config_bundle()`
  - `discover_config_graph()`
  - `compute_effective_config()`
  - `diff_config_bundles()`
  - `run_config_doctor()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `redaction`
  - `env-snapshot`
  - `markdown`

# Compatibility story

- Works in a stable-first mode by reading discovered config files, selected environment variables, and explicit `--config` overrides supplied to the tool.
- Can optionally enrich bundles with nightly `cargo config get` output when available.
- Must preserve the difference between “documented Cargo rule”, “observed local file”, “observed invocation fact”, and “best-effort inference about an invocation”.
- Must keep “inspectable support bundle” separate from “replayable invocation bundle”, especially when tokens, provider arguments, or private paths are redacted.
- Should stay useful even if Cargo later stabilizes richer config inspection, because the invocation-basis and replayability bundle still matters.

# Conformance & fixtures

- One fixture with project + user config plus nested includes.
- One fixture with optional include present on one machine and absent on another.
- One fixture with env overrides for target runner, browser, and registry settings.
- One fixture with credentials and provider aliases requiring redaction.
- One fixture where `--config` wins and the bundle must stay invocation-scoped.
- One fixture where cwd-relative `--config KEY=VALUE` paths must not masquerade as config-root-relative replay.
- Goldens for `override_shadowed`, `optional_include_missing`, `relative_path_surprise`, `redaction_applied`, `invocation_scoped`, and `inspectable_not_replayable`.

# Path to boring stability

- Stabilize the effective-config / invocation-basis / replayability schemas before adding UI features.
- Start with read-only capture and diffing.
- Keep the first redaction vocabulary small and conservative.
- Treat nightly `cargo config` integration as an adapter, not the product itself.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 28/30**

# Minimum lovable MVP

A library and cargo subcommand that discover all applicable Cargo config files and includes, record effective values plus winning origins, classify invocation basis and replayability, redact sensitive fields, and emit one diffable support bundle.

# De-risk plan

1. Start with stable config files, env precedence, and `--config` capture before relying on nightly `cargo config`.
2. Keep redaction aggressive by default, especially for tokens, provider arguments, and local path details.
3. Treat credentials as “presence and source class” data unless the caller explicitly opts into local-only raw capture.
4. Mark bundles `inspectable_only` unless the tool has enough evidence to justify `replayable`.
5. Validate on one multi-user workspace setup and one CI-oriented repo with heavy `--config` usage.

# Non-goals

- Not a replacement for Cargo’s own config system.
- Not a general-purpose secret manager.
- Not a new project policy DSL.
- Not a promise that every invocation context can be reconstructed perfectly after the fact.

# Architecture & API sketch

```rust
pub struct ConfigOrigin {
    pub key: String,
    pub winner: String,
    pub losers: Vec<String>,
    pub source_class: String,
}

pub fn capture_config_bundle(root: &Path) -> Result<ConfigBundle>;
pub fn discover_config_graph(root: &Path) -> Result<Vec<ConfigFileNode>>;
pub fn compute_effective_config(bundle: &ConfigBundle) -> Result<EffectiveConfig>;
pub fn classify_invocation_basis(bundle: &ConfigBundle) -> InvocationBasisReceipt;
pub fn classify_replayability(bundle: &ConfigBundle) -> ReplayabilityReport;
pub fn diff_config_bundles(old: &ConfigBundle, new: &ConfigBundle) -> ConfigDiff;
```

Bundle draft: `config-profile.toml`, `config-files.graph.json`, `config-effective.json`, `config-origins.json`, `config-paths.report.json`, `config-redaction.report.json`, `invocation-basis.receipt.json`, `replayability.report.json`, `notes.md`.

# Security / safety model

- Treat all imported env vars, config files, and provider arguments as sensitive until classified.
- Redact token values, credential-provider secrets, and local-user path segments by default.
- Preserve enough metadata to explain precedence without leaking raw credentials.
- Never pretend an inferred invocation context is identical to Cargo’s internal state when it was reconstructed indirectly.
- Never label a bundle `replayable` if redaction removed a required token, provider argument, or path anchor.

# Maintenance & governance plan

- Track Cargo config precedence, include semantics, and future `cargo config` stabilization work.
- Keep schemas compact and versioned.
- Maintain fixtures for include graphs, env overrides, credential redaction, invocation-basis capture, and relative-path surprises.
- Publish guidance for CI systems on safe bundle retention and redaction expectations.

# Milestones

## 0.1
- config graph discovery
- effective-config capture
- invocation-basis receipt
- replayability report
- origin trace and redaction report

## 0.2
- bundle diffing
- doctor checks
- optional nightly `cargo config get` adapter
- public-safe versus local-only export modes

## 1.0
- stable receipt schema
- CI/support integrations
- curated precedence edge-case corpus

# Open questions

- How much of `--config` invocation context can be captured automatically without wrapping Cargo itself?
- What is the smallest useful origin vocabulary that still works for env/file/include/credentials sources?
- Which path-bearing keys deserve first-class doctor checks in the first release?
- What is the smallest replayability vocabulary that keeps `safe_to_share` distinct from `safe_to_replay`?

# Sources

- Cargo configuration reference: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features (`cargo config`, unstable table behavior): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog (1.94 include stabilization; 1.93 `--config` precedence/path fixes): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo 1.93 development-cycle notes (`config-include` design, optional includes): https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
