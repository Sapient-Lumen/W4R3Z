# cargo-config-layer-receipt-kit product plan — 2026-03-20

This note sharpens **P-0474 Cargo Config Layer Receipt Kit** into an implementation-ready `0.1` direction.

## Main judgment

A worthwhile `0.1` should **not** become:

- another generic config parser,
- another dotfile manager,
- another secret store,
- or a fuzzy “show me my Cargo config” shell wrapper.

It should become a **reviewable per-invocation config contract** that helps a project publish one boring, inspectable answer to two questions that an ordinary effective-config dump still leaves blurry:

1. **Was this bundle captured from one real Cargo invocation or reconstructed later from ambient files?**
2. **Is the exported bundle actually replayable by someone else, or only inspectable after redaction and missing ephemeral overrides?**

The missing value is the contract layer above Cargo’s current config substrate.

## Why this lane got stronger

Current Cargo substrate makes the gap more actionable than it used to be:

- Cargo’s config reference now explicitly documents hierarchical probing, merge rules, env overrides, command-line `--config` overrides, include graphs, and config-relative path rules.
- Cargo 1.94 stabilized the top-level `include` key, which makes shared config graphs and optional per-user includes more real in ordinary projects.
- Cargo’s docs are explicit that `--config` values take precedence over environment variables, which in turn take precedence over config files.
- Cargo’s path rules are explicit that env values and `--config KEY=VALUE` paths are relative to the current working directory, while config-file paths are relative to the config-definition root.
- Cargo’s credentials and credential-provider aliases make redaction more important: a bundle can explain which provider or token class won without remaining safe to replay publicly.
- Nightly `cargo config get` exists as inspection substrate, but it still is not a durable replayable artifact by itself.

That means the ecosystem no longer mainly lacks raw config primitives.
It lacks a **shared product-shape** for publishing invocation truth and replayability truth.

## What the crate should provide other people

For workspace maintainers, CI owners, release engineers, support responders, and tool authors, the crate should provide:

1. **One invocation-basis receipt** instead of letting a reconstructed file scan masquerade as one failing command’s exact config basis.
2. **One replayability report** instead of letting a redacted support bundle masquerade as something another machine can faithfully rerun.
3. **One effective-config and origin surface** that keeps env, `--config`, file, include, and credential classes visible.
4. **One path-root report** that makes cwd-relative versus config-relative path interpretation boring and inspectable.
5. **One compact contract-check report** that keeps imported facts, observed invocation facts, inferred facts, and redacted-away facts visibly separate.

## Two newly first-class review objects

### 1. `invocation-basis.receipt`

This artifact should answer:

- which Cargo command family was being described,
- whether capture happened live, wrapped, imported, or reconstructed,
- what current working directory and manifest/workspace anchor were in effect,
- which explicit `--config` fragments or extra config files were part of the basis,
- which env overrides were observed versus merely inferred,
- and whether the bundle should be read as `ambient_defaults`, `invocation_scoped`, or `mixed_basis`.

### 2. `replayability.report`

This artifact should answer:

- whether the bundle is replayable, inspectable-only, local-only, or redaction-broken,
- which missing or redacted facts prevent replay,
- whether replay requires local secrets, private paths, or external credential providers,
- and whether path interpretation, optional includes, or cwd-sensitive overrides make replay conditional.

## Recommended `0.1` command surface

### `cargo config-receipt capture`
Capture the declared/observed contract and emit:
- `config-files.graph.json`
- `config-effective.json`
- `config-origins.json`
- `config-paths.report.json`
- `config-redaction.report.json`
- `invocation-basis.receipt.json`
- `replayability.report.json`

### `cargo config-receipt check`
Run conservative checks and emit:
- `config-receipt-check.report.json`

### `cargo config-receipt diff`
Compare two bundles and emit:
- `config-receipt-diff.report.json`

### `cargo config-receipt bundle`
Produce one compact `.configbundle.zip`.

## Recommended crate/workspace split

- `cargo_config_receipt_model`
- `cargo_config_receipt_capture`
- `cargo_config_receipt_redaction`
- `cargo_config_receipt_check`
- `cargo_config_receipt_pack`
- `cargo-config-receipt`

## Discovery order

1. **Invocation capture**
   - command family
   - current directory
   - workspace / manifest anchor
   - explicit `--config` arguments
2. **Graph discovery**
   - probed config files
   - include edges
   - optional include results
   - credentials participation
3. **Effective merge capture**
   - effective keys
   - origin traces
   - winning source classes
4. **Path-root capture**
   - cwd-relative values
   - config-relative values
   - suspicious mixed-root cases
5. **Redaction and replay classification**
   - token / provider / local path redaction
   - replay blockers
   - public-safe versus local-only exports
6. **Bundle and diff**
   - export one compact review bundle

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- config hierarchy and merge rules
- include graphs and optional include state
- env overrides
- `--config KEY=VALUE` and `--config <path>` overrides
- credential-provider aliases and credentials-file participation
- nightly `cargo config get` inspection when available

### Do not flatten into one fake verdict
- “effective config was captured”
- “the bundle is safe to share”
- “the bundle is enough to replay”
- “this is the project default config”
- “this failing run used the same config as local development”

Those are ingredients, not the contract.

## Preferred proving grounds

- a CI-heavy workspace using `--config` and env overrides,
- a project using per-user optional includes,
- a release workflow depending on registry credentials and credential-provider aliases,
- a docs/build workflow where `doc.browser`, target runners, or `build.analysis` are configured outside the repo,
- a support case where a public-safe bundle must stay useful without pretending to be fully replayable.

## Non-goals

- not a replacement for Cargo config itself,
- not a secret manager,
- not a policy DSL for org-wide config enforcement,
- not a promise that every invocation can be reconstructed losslessly after the fact,
- not a generic cross-tool dotfile framework.
