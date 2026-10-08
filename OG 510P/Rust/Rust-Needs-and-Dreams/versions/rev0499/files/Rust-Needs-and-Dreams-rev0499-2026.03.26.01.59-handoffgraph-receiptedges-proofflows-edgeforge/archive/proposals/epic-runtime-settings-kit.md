# Epic proposal: Runtime Settings Kit

## Thesis
Rust already has serious building blocks for runtime configuration.
The next high-leverage contribution is not another settings crate.
It is a **shared runtime-settings layer** that turns declared settings, source precedence, secret classifications, examples, validation, and transition notes into durable engineering artifacts.

That would be a worthy ecosystem contribution because it helps:
- application authors treat configuration as a supported interface rather than incidental loader code,
- operators review default/source/deprecation drift without reverse-engineering structs and examples,
- documentation and deployment templates stay tied to the same declared settings model,
- and release processes attach configuration compatibility evidence alongside binaries and other review surfaces.

## Why now
The timing is good because Rust already has the ingredients, but still not the contract:
- `config`, `figment`, and `confique` already cover layered loading and precedence semantics,
- `envy` and `clap` already make env-variable and CLI-driven configuration routine,
- `schemars` and `jsonschema` already cover schema generation and validation,
- file-backed secret/env adapters already exist because containerized deployments need them,
- and real users are explicitly asking for generated config references and transition paths for renamed/refined settings.

Sources:
- https://docs.rs/config/latest/config/
- https://docs.rs/config/latest/config/struct.Config.html
- https://docs.rs/figment/latest/figment/
- https://docs.rs/figment/latest/figment/struct.Metadata.html
- https://docs.rs/confique
- https://docs.rs/envy
- https://docs.rs/clap/latest/clap/_features/index.html
- https://docs.rs/schemars
- https://docs.rs/jsonschema
- https://docs.rs/figment_file_env_provider
- https://github.com/rust-cli/config-rs/discussions/661_
- https://github.com/rust-cli/config-rs/discussions/629

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `settings-schema/v0`, `settings-source-plan/v0`, `settings-example-catalog/v0`, `settings-check-report/v0`, optional `settings-transition-report/v0`, and `settings-pack/v0`
2. adapters for popular Rust settings crates and env/CLI sources
3. generated docs/reference support so settings tables and sample files can be derived and checked
4. validation/reporting support for secrets, deprecations, default drift, source-precedence changes, and example freshness
5. release/CI examples showing settings packs attached to binaries, deployment templates, docs, and migration reviews

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s crates legible together rather than trying to replace them.

## Initial pilots
- one CLI application with config files + env overrides + checked sample config docs
- one service using layered file/env/secret-file settings in containers
- one app with explicit setting deprecations or rename aliases between releases
- one library or framework adapter that emits `settings-schema/v0` without mandating one runtime loader

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve setting identity, defaults, deprecations, and source eligibility
2. **v0.2 adapters**
   - support `config`, `figment`, `confique`, `envy`, `clap` env-aware inputs, and schema attachments
   - capture source precedence and redaction/report policy honestly
3. **v0.3 cross-kit integration**
   - integrate with Command Surface, DocProof, Credentials, Migration, Support Envelope, and Release Pipeline workflows
   - support diff/baseline workflows across releases and deployment modes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact loader stack

## Success metrics
- Teams can review runtime-settings changes as explicit interface and evidence artifacts rather than README diffs and hand-inspected structs.
- Default/preference/deprecation drift becomes visible in CI and release review.
- Generated config references and checked sample files stay aligned with actual loaders.
- Secret-bearing settings become auditable without leaking the secret values.
- Rust application deployment stories become easier to explain across services, CLIs, daemons, and operators.

## Archive fit
This proposal adds an underrepresented but important domain to the concise archive: **runtime configuration as a supported interface**.
It also fills a deliberate hole left by Command Surface Kit, DocProof Kit, Credentials Kit, and Migration Kit. Those proposals touch configuration from adjacent angles, but none of them tries to become the portable contract for declared runtime settings, source precedence, checked examples, and settings evolution themselves.
Runtime Settings Kit is the missing substrate that can travel alongside docs, releases, deployments, and operational review without being absorbed by any one of them.
