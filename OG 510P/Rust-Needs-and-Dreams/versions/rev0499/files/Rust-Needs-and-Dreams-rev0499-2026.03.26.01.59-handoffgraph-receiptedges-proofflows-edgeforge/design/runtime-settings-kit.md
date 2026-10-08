# Design: Runtime Settings Kit (`cargo settings`, `settings-pack/v0`)

## Goal
Define a portable contract for declaring, validating, documenting, diffing, and reviewing Rust runtime configuration: settings, defaults, source precedence, secret classification, migration aliases, example files, and evidence that the documented settings surface still matches the program.

This should **not** replace `config`, `figment`, `confique`, `envy`, `clap`, `schemars`, or JSON Schema validators.
It should make them compose better and make runtime-settings support claims reviewable.

## References (signals)
- `config` explicitly organizes hierarchical/layered configuration and supports defaults, explicit values, files, and environment variables.
  https://docs.rs/config/latest/config/
  https://docs.rs/config/latest/config/struct.Config.html
  https://docs.rs/config/latest/config/struct.Environment.html
- `figment` combines providers and tracks value provenance through metadata and source information.
  https://docs.rs/figment/latest/figment/
  https://docs.rs/figment/latest/figment/struct.Metadata.html
  https://docs.rs/figment/latest/figment/enum.Source.html
- `confique` is explicitly type-safe, layered, serde-based configuration with derive-driven defaults and layered loading.
  https://docs.rs/confique
  https://docs.rs/confique/latest/confique/trait.Config.html
- `envy` covers env-variable extraction into typesafe structs.
  https://docs.rs/envy
- `clap` already treats environment variables as part of CLI parsing when the `env` feature is enabled, which means many Rust apps already mix CLI and runtime-setting surfaces.
  https://docs.rs/clap/latest/clap/_features/index.html
  https://docs.rs/clap/latest/clap/struct.Arg.html
- `schemars` derives JSON Schema from Rust types; `jsonschema` validates both schema documents and instances.
  https://docs.rs/schemars
  https://docs.rs/jsonschema
- `figment_file_env_provider` exists because file-backed secret/env conventions matter operationally.
  https://docs.rs/figment_file_env_provider
- `config-rs` users are explicitly asking for generated user-facing configuration references and transition paths for renamed/refined settings.
  https://github.com/rust-cli/config-rs/discussions/661_
  https://github.com/rust-cli/config-rs/discussions/629

## Core components

### 1) `settings-schema/v0`
A design-time declaration of the runtime settings an application/workspace/release claims to support.

Required ideas:
- subject identity (crate / workspace / binary / service / deployment profile)
- setting catalog:
  - key/path identity
  - type and cardinality
  - default mode (`none`, literal default, computed default, derived default)
  - required/optional status
  - doc string / operator-facing description
  - stability posture (`official`, `best-effort`, `experimental`, `deprecated`, `internal`)
- source eligibility:
  - file
  - env
  - CLI passthrough/override
  - secret-file / `_FILE`
  - provider/remote lane when relevant
- secrecy / sensitivity classification:
  - `plain`
  - `secret`
  - `file-secret`
  - `redacted-report-only`
- mutability / reload semantics:
  - startup-only
  - reloadable
  - session-only
- compatibility metadata:
  - renamed-from
  - alias-of
  - split-from
  - removal target / sunset note
- schema attachment pointers:
  - derived JSON Schema / raw schema / validation rules
  - allowed value ranges and enum/value-hint metadata where relevant

Design rule: **`settings-schema` must separate the setting model from the source-precedence plan and from observed validation runs.**
A struct definition alone is not the whole runtime-settings contract.

### 2) `settings-source-plan/v0`
A machine-readable plan describing where settings may come from and how precedence is resolved.

Should record:
- linked `settings-schema/v0`
- ordered source layers
  - compiled defaults
  - profile defaults
  - file formats
  - environment
  - CLI overrides
  - secret-file shims
  - provider/remote fetch lanes
- profile selection rules
- normalization rules:
  - env-key casing/prefix/separator rules
  - path/base-directory rules
  - structured env parsing conventions
  - duplicate/unknown key policy
- per-setting source restrictions
- redaction/reporting policy for secret values
- source provenance expectations and whether they are preserved in adapters
- skip/waiver reasons such as:
  - `provider-not-available`
  - `secret-material-not-captured`
  - `profile-selection-external`
  - `legacy-key-accepted-during-transition`

This is the missing answer to “where can this setting legitimately come from, and in what order?”

### 3) `settings-example-catalog/v0`
An inventory of checked and illustrative runtime-settings examples.

Should record:
- source location (README, mdBook, docs.rs example, sample TOML/YAML/JSON, Helm values snippet, `.env.example`, integration fixture)
- example kind:
  - `checked-config-file`
  - `checked-env-set`
  - `checked-secret-file-lane`
  - `checked-composed-example`
  - `illustrative-only`
- selected profile / deployment mode
- expected normalization/source assumptions
- required external context (filesystem, network provider stub, container secret mount)
- whether secrets are real, fake, or redacted placeholders
- links to supporting validators or harnesses

This is the missing answer to “which examples are promises versus prose?”

### 4) `settings-check-report/v0`
Report artifact capturing what was actually validated.

Should record:
- referenced schema and source plan ids
- validators used (`serde`, `jsonschema`, custom loader, CLI/env adapter, integration test)
- checked examples / fixtures / profile lanes
- provenance observations when available
- unknown-key results
- missing-required-value results
- deprecated/aliased-key results
- source-precedence conflicts and how they resolved
- drift reason codes such as:
  - `default-drift`
  - `unknown-key-accepted`
  - `unknown-key-rejected`
  - `deprecated-key-used`
  - `source-precedence-drift`
  - `secret-redaction-gap`
  - `env-name-drift`
  - `example-out-of-date`
  - `schema-validation-gap`
- raw attachment pointers (sample files, env fixtures, rendered docs tables, schemas, validation errors)

This is the missing answer to “what part of the runtime-settings surface did we really check?”

### 5) `settings-transition-report/v0` (optional but important)
Focused artifact for settings evolution between versions.

Should record:
- source release / destination release ids
- renamed, split, merged, or removed settings
- alias and fallback policy
- migration hints and auto-rewrite availability
- changed defaults and precedence changes
- sunset status / future removal date if known
- affected example/docs/deployment-template pointers

This keeps settings-level compatibility changes from being buried inside general migration notes.

### 6) `settings-pack/v0`
Bundle format containing:
- `settings-schema/v0`
- `settings-source-plan/v0`
- optional `settings-example-catalog/v0`
- one or more `settings-check-report/v0`
- optional `settings-transition-report/v0`
- optional attached schemas, examples, docs tables, and raw validator outputs

This is the unit that should travel through CI, release review, deployment templates, docs, and later archaeology.

### 7) `cargo settings`
Reference UX:
- `cargo settings init`
- `cargo settings schema`
- `cargo settings check`
- `cargo settings diff`
- `cargo settings docs`
- `cargo settings pack`

`cargo settings` should begin as an explainer / adapter / packer.
It should not pretend to be the one true configuration crate.

## Default policy
- **Separate declared settings from source precedence and from run evidence.**
- **Treat secrets/file-secrets as first-class source classes** instead of undocumented deployment folklore.
- **Preserve raw source truth** for example files, env snippets, and schemas.
- **Record deprecations and rename aliases explicitly** rather than hiding them in changelogs.
- **Distinguish checked examples from illustrative examples** so docs can be honest.
- **Prefer redacted evidence over omitted evidence** for secret-bearing settings.

## What the kit should provide to others
- **Command Surface Kit:** connect CLI flags/env overrides to broader runtime settings without collapsing the two contracts.
- **DocProof Kit:** consume settings examples and generated config references as checked learning surfaces.
- **Credentials Kit:** provide a place to say which settings are secrets and which lanes are secret-file or keychain backed without taking over secret storage itself.
- **Support Envelope Kit:** connect settings profiles and provider assumptions to platform/runtime baselines.
- **Migration Kit:** attach settings transition reports to broader release/toolchain/dependency migrations when settings compatibility is part of the change program.
- **Database Contract Kit / Release Pipeline Kit / Observability Kit:** declare how runtime settings activate migrations, endpoints, exporters, or deployment behavior without each kit inventing a separate config story.

## Overlap boundaries
- **Not `config` / `figment` / `confique`:** those are loaders/combiners/derive systems; this kit packages the declared settings interface and evidence across them.
- **Not Command Surface Kit:** CLI flags are one way to influence runtime settings, but the command interface and runtime settings contract should stay distinct.
- **Not Credentials Kit:** secret storage, keychain/OIDC, and leak prevention remain a separate concern; this kit only classifies which settings are secret-bearing and how they are reported.
- **Not Schema Contract Kit:** this is about application runtime settings, not wire protocols or public service schemas.
- **Not Migration Kit:** Migration Kit captures broader change programs; this kit captures settings-surface evolution specifically.
- **Not a hosted control plane:** the value is the artifact and review workflow, not a central settings service.

## Hard problems (explicitly scoped)
1. **Configuration sources are heterogeneous**
   - file, env, CLI, secret-file, and provider lanes do not behave identically.
   - v0 should model them explicitly instead of flattening them.

2. **Rust types are not the whole contract**
   - Serde structs tell only part of the story; precedence, deprecation aliases, env-key mapping, and docs generation matter too.

3. **Secrets complicate evidence**
   - teams need proof that secret-bearing settings exist and are wired correctly without capturing the secret values.

4. **Examples are often half the operator interface**
   - `.env.example`, sample TOML, and deployment snippets are often more operationally relevant than API docs.
   - the kit must include them without pretending every example is executable.

5. **Config evolution is compatibility-sensitive**
   - renamed, split, or newly required settings are real compatibility changes.
   - they deserve explicit transition artifacts.

## Minimal adoption path
1. Publish schemas + validators for `settings-schema/v0` and `settings-check-report/v0`.
2. Add adapters for `config`, `figment`, `confique`, `envy`, and `clap` env-aware settings where possible.
3. Support JSON Schema attachments through `schemars` + `jsonschema`.
4. Add docs/example generation so generated setting references and sample config surfaces can be checked.
5. Add transition/diff support to make release review aware of settings-surface changes.

## Why this is an ecosystem contribution, not just repo hygiene
Rust applications already have enough configuration machinery that the missing piece is no longer “yet another loader.”
The missing piece is a portable runtime-settings contract that can travel through docs, CI, deployment templates, release review, and operational archaeology.
That is a substrate contribution, not a convenience wrapper.
