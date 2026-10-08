# Gap: runtime settings and configuration contracts

## What is missing
Rust has many good ways to **load** configuration, but it still lacks a **shared runtime-settings contract**.

Today there is no standard way to describe, exchange, and diff:
- which runtime settings an application actually exposes,
- which settings are ordinary values versus secrets,
- which sources are allowed to provide each setting,
- what the precedence rules and profile/layer semantics are,
- which defaults, examples, and deprecations are part of the supported interface,
- which settings were validated or migrated in CI/release review,
- and what evidence exists that documentation, examples, env vars, config files, and secret-file lanes still agree.

That missing layer matters because Rust now has strong point tools for loading config, but deployable applications still ship configuration truth as a mixture of struct definitions, README snippets, Helm values, `.env` conventions, example TOML files, and maintainer memory.

Sources:
- https://docs.rs/config/latest/config/
- https://docs.rs/config/latest/config/struct.Config.html
- https://docs.rs/config/latest/config/struct.Environment.html
- https://docs.rs/figment/latest/figment/
- https://docs.rs/figment/latest/figment/struct.Metadata.html
- https://docs.rs/figment/latest/figment/enum.Source.html
- https://docs.rs/confique
- https://docs.rs/confique/latest/confique/trait.Config.html
- https://docs.rs/envy
- https://docs.rs/clap/latest/clap/struct.Arg.html
- https://docs.rs/clap/latest/clap/_features/index.html
- https://docs.rs/schemars
- https://docs.rs/jsonschema
- https://docs.rs/figment_file_env_provider
- https://github.com/rust-cli/config-rs/discussions/661_
- https://github.com/rust-cli/config-rs/discussions/629

## The current seam is awkward
The ecosystem clearly has ingredients:
- `config` explicitly supports prioritized configuration repositories, layered sources, defaults, files, and environment variables,
- `figment` already combines providers and tracks value provenance,
- `confique` provides type-safe layered configuration with derive-driven defaults,
- `envy` provides straightforward env-to-struct extraction,
- `clap` can already treat env variables as part of argument parsing,
- `schemars` can derive JSON Schema from Rust types,
- `jsonschema` can validate schema documents and instances,
- and `figment_file_env_provider` exists because file-backed secret/env lanes are a real operational need in containerized deployments.

But each real project still hand-assembles its runtime-settings story out of:
- Serde structs,
- default implementations,
- loader precedence code,
- CLI/env overrides,
- example config files,
- README or wiki tables,
- Kubernetes/Compose/Systemd snippets,
- secret-file conventions,
- validation wrappers,
- and ad hoc migration notes when settings are renamed or split.

The result is not that Rust lacks config crates.
The result is that there is no portable way to say:
- “these are the supported runtime settings,”
- “these are their sources and precedence rules,”
- “these settings are secret/materialized-through-file only,”
- “these examples and docs were actually checked,”
- or “these renamed/deprecated settings still have an intentional transition path.”

The open requests around generated config references and transitions for renamed/refined settings in the `config-rs` project are especially revealing here: even mature users want a canonical, generated description of keys, defaults, sources, and migration behavior, but the ecosystem still lacks a common artifact for it.

Sources:
- https://docs.rs/config/latest/config/
- https://docs.rs/config/latest/config/struct.Config.html
- https://docs.rs/config/latest/config/struct.Environment.html
- https://docs.rs/figment/latest/figment/
- https://docs.rs/figment/latest/figment/struct.Metadata.html
- https://docs.rs/confique
- https://docs.rs/confique/latest/confique/trait.Config.html
- https://docs.rs/envy
- https://docs.rs/clap/latest/clap/struct.Arg.html
- https://docs.rs/clap/latest/clap/_features/index.html
- https://docs.rs/figment_file_env_provider
- https://docs.rs/schemars
- https://docs.rs/jsonschema
- https://github.com/rust-cli/config-rs/discussions/661_
- https://github.com/rust-cli/config-rs/discussions/629

## Why this matters
This gap is bigger than “nicer config files.”
It affects:
1. **deployment truthfulness** — application behavior depends on runtime settings just as much as on CLI flags or supported targets;
2. **operational safety** — secrets, file-backed secrets, and ordinary settings should not be documented, logged, or diffed the same way;
3. **reviewability** — teams need to know whether a release changed defaults, precedence, accepted keys, or deprecation aliases;
4. **migration ergonomics** — setting renames/splits and source-precedence changes are real compatibility events, but they are often buried in changelogs or code comments;
5. **docs quality** — generated config references, examples, and environment-variable tables drift unless they share one declared settings model;
6. **cross-tool composition** — Command Surface Kit, DocProof Kit, Credentials Kit, Support Envelope Kit, and Deployment-oriented workflows all need a shared story about runtime knobs.

Rust applications increasingly span CLIs, daemons, services, operators, web apps, and embedded-adjacent tools. All of them still need a coherent answer to “what can I configure, where can it come from, and what is the support promise?”

Sources:
- https://docs.rs/figment/latest/figment/
- https://docs.rs/figment/latest/figment/struct.Metadata.html
- https://docs.rs/confique
- https://docs.rs/clap/latest/clap/struct.Arg.html
- https://docs.rs/figment_file_env_provider
- https://github.com/rust-cli/config-rs/discussions/661_
- https://github.com/rust-cli/config-rs/discussions/629

## What “good” looks like
A worthy contribution here is **not** another config loader, another env parser, or another schema crate.

It is a shared runtime-settings boundary:
- one `settings-schema/v0` describing supported settings, types, defaults, stability/deprecation, secret classification, and source eligibility,
- one `settings-source-plan/v0` describing precedence, profiles/layers, file/env/CLI/provider lanes, and normalization rules,
- one `settings-example-catalog/v0` inventorying checked and illustrative config examples, env snippets, secret-file examples, and docs tables,
- one `settings-check-report/v0` recording validation, unknown-key drift, deprecated-key use, missing required values, secret-leak hazards, and example/documentation status,
- one optional `settings-transition-report/v0` for renamed/split/merged settings and upgrade guidance,
- and one `settings-pack/v0` bundle for CI, docs, release review, deployment templates, and archaeology.

That would let Rust applications expose a reviewable runtime configuration interface the same way API surfaces, command surfaces, and release surfaces increasingly deserve reviewable artifacts.
