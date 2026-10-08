# Design: Rollout Surface Kit (`cargo rolloutcheck`, `rollout-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust program’s supported rollout surface: flags, variants, prerequisites, targeting/rule posture, exposure and impression expectations, cleanup posture, and evidence that the declared rollout surface still matches the program.

This should **not** replace OpenFeature, Unleash, GrowthBook, Flipt, or provider-specific SDKs.
It should make them compose better and make support claims reviewable.

## References (signals)
- OpenFeature’s evaluation API already defines vendor-neutral typed evaluation and detailed evaluation metadata.
  https://openfeature.dev/specification/sections/flag-evaluation/
- OpenFeature also defines hooks and tracking semantics.
  https://openfeature.dev/specification/sections/hooks/
  https://openfeature.dev/specification/sections/tracking/
- OpenFeature now publishes an experimental CLI with a `flags.json` manifest and generated typed accessors, which is strong prior art but still narrower than the whole rollout surface.
  https://openfeature.dev/docs/tutorials/open-feature-cli/
- OpenFeature also now publishes OFREP work, which is a useful signal that feature-flag interoperability is moving beyond just local SDK APIs.
  https://openfeature.dev/specification/appendix-c/
- The OpenFeature Rust SDK already supports providers, targeting, hooks, logging hooks, and named clients, but marks eventing as not yet available.
  https://openfeature.dev/docs/reference/sdks/server/rust/
- Unleash already exposes flag lifecycle state, stale-flag handling, impression data, and Rust SDK support.
  https://docs.getunleash.io/concepts/feature-flags
  https://docs.getunleash.io/concepts/impression-data
  https://docs.getunleash.io/sdks/rust
  https://docs.getunleash.io/concepts/technical-debt
- GrowthBook already supports environment-specific rules, forced values, percentage rollouts, experiments, safe rollouts, prerequisite features, JSON schema validation, and Rust tracking callbacks.
  https://docs.growthbook.io/features/rules
  https://docs.growthbook.io/quick-start
  https://docs.growthbook.io/lib/rust
- Flipt already provides server-side evaluation APIs/SDKs, which shows that Git-native and API-native control planes are both real deployment lanes.
  https://docs.flipt.io/v2/integration/server/rest

## Core components

### 1) `rollout-surface/v0`
A design-time declaration of the supported rollout boundary for a binary/service/workspace.

Required ideas:
- system/service identity
- environments in scope
- release-control families in scope:
  - release flag
  - kill switch
  - entitlement/plan gate
  - beta/internal gate
  - experiment
  - safe rollout / guarded rollout
  - remote-config value
- support classes:
  - official
  - best-effort
  - experimental
  - deprecated
  - internal
- linked attachments:
  - service surfaces
  - identity/access surfaces
  - runtime settings refs
  - observability/diagnostic ids
  - provider-specific raw manifests or exports

Design rule: preserve rollout/control semantics separate from runtime settings. A feature flag that changes over time and carries targeting/variant semantics is not just “another config key.”

### 2) `flag-catalog/v0`
Stable identities for the flags a program supports.

Each entry should support:
- stable flag id
- provider flag key(s)
- human-facing name + summary
- role/class:
  - release
  - experiment
  - ops kill switch
  - entitlement
  - remote-config
  - migration bridge
  - internal-only
- expected lifetime posture:
  - transient
  - medium-lived
  - long-lived
  - permanent-interface
- owning team / review owner
- linked prerequisite flags
- linked variant profile id(s)
- linked targeting profile id
- default/fallback posture
- support level
- deprecation / cleanup target

Design rule: keep stable archive identities even when provider keys or backends move. A rollout surface should survive provider churn.

### 3) `variant-profile/v0`
What values or variants a flag can resolve to.

Each profile should support:
- stable variant-profile id
- linked flag id
- value kind:
  - boolean
  - string
  - number
  - structured/object
  - named variant set
- declared variants / allowed value ranges
- default variant/value
- schema refs for structured values
- compatibility notes
- linked experiment profile(s) when relevant

Design rule: keep variant truth separate from targeting/rules. “What values exist?” and “who gets them?” are different questions.

### 4) `targeting-profile/v0`
The allowed rule/targeting surface.

Each profile should capture:
- stable targeting-profile id
- linked flag ids
- supported context attributes/classes
- environment posture
- prerequisite posture
- rule families in use:
  - forced value
  - percentage rollout
  - experiment
  - safe rollout / guarded rollout
  - schedule-based activation
  - prerequisite-dependent rule
- precedence notes
- known unsupported or unchecked lanes

Design rule: preserve provider-specific raw rules as attachments. Do not flatten every provider into one fake rule language.

### 5) `experiment-profile/v0`
What experiment semantics a rollout flag is expected to support.

Each profile should support:
- stable experiment-profile id
- linked flag id / variants
- cohort/allocation posture
- success metrics or analytics refs
- exposure-event requirements
- guardrail metrics refs when relevant
- stop/rollback notes
- support level

Design rule: keep experiments distinct from generic feature flags and from downstream analytics ownership.

### 6) `exposure-profile/v0`
What evaluation/exposure/impression/tracking behavior is expected.

Each profile should support:
- stable exposure-profile id
- linked flag ids / experiment ids
- event kinds expected:
  - evaluation detail only
  - impression event
  - exposure event
  - business tracking event
- required fields / attribute refs
- redaction/privacy notes
- idempotency / dedup notes
- linked observability schemas when relevant
- known provider/runtime limitations

Design rule: keep “flag evaluated” separate from “experiment exposed” and from generic product analytics. They may overlap, but they are not identical.

### 7) `rollout-check-plan/v0`
A plan for validating that the declared rollout surface still behaves as claimed.

A plan should capture:
- selected flags/variants/targeting profiles
- representative contexts/archetypes
- expected outputs / allowed result windows
- prerequisite and rule-order cases
- fallback/default cases
- provider-ready / provider-error / offline cases when relevant
- exposure/impression assertions when relevant
- cleanup/deprecation assertions
- unsupported or illustrative-only lanes

Design rule: keep simulated rule cases distinct from production analytics outcomes. A rollout check is not the same thing as a product experiment readout.

### 8) `rollout-check-report/v0`
Portable results from running the rollout checks.

A report should capture:
- artifact versions and environment
- flags/variants/targeting profiles exercised
- contexts/archetypes executed
- pass/fail/error outcomes
- mismatches and reason codes, e.g.:
  - `flag-missing`
  - `variant-missing`
  - `default-changed`
  - `rule-order-changed`
  - `prerequisite-changed`
  - `targeting-attribute-missing`
  - `exposure-event-missing`
  - `provider-not-ready`
  - `cleanup-overdue`
- optional diff summaries vs baseline

### 9) `flag-cleanup-report/v0`
A portable summary of stale/deprecated/transient-flag posture.

This should support:
- stable flag ids
- current lifetime state
- expected removal/review dates
- stale/cleanup warnings
- unresolved owners
- attached migration/remove-code notes

Design rule: keep cleanup posture explicit. A stale flag is a real interface risk, not just backlog trivia.

### 10) `rollout-pack/v0`
Bundle the rollout contract and its evidence.

Typical contents:
- `rollout-surface.json`
- `flag-catalog.json`
- `variant-profile/*.json`
- `targeting-profile/*.json`
- `experiment-profile/*.json`
- `exposure-profile/*.json`
- `rollout-check-plan.json`
- `rollout-check-report.json`
- optional `flag-cleanup-report.json`
- raw attachments:
  - OpenFeature manifests
  - provider exports/configs
  - bounded archetype/context fixtures
  - sample analytics mapping docs
  - screenshots or dashboard exports only when strictly necessary

## UX shape

### `cargo rolloutcheck init`
Bootstrap rollout artifacts from known adapters or a manual scaffold.

### `cargo rolloutcheck scan`
Inspect a project and emit a draft inventory:
- OpenFeature/OpenFeature CLI usage
- provider SDKs (Unleash, GrowthBook, Flipt, custom)
- hard-coded flag keys and contexts
- obvious stale/transient flag hints

### `cargo rolloutcheck doctor`
Explain problems in the declared rollout surface:
- undocumented flags
- missing default/fallback posture
- experiments without exposure profile
- missing cleanup owner/date
- provider/runtime mismatch

### `cargo rolloutcheck test`
Run declared check cases against local adapters, fixtures, or provider mocks.

### `cargo rolloutcheck diff`
Compare two revisions and explain rollout-surface changes.

### `cargo rolloutcheck pack`
Emit `rollout-pack/v0` for CI, release review, and incident bundles.

## Adapters, not empire
v0 should be adapter-heavy:
- OpenFeature manifest + generated-accessor adapters
- OpenFeature provider/hook adapters where possible
- Unleash export/impression-data adapters
- GrowthBook flag/rule/experiment adapters
- Flipt evaluation/export adapters
- fixture-only/manual adapters for in-house systems

The kit wins if it can describe mixed ecosystems, not if it demands one provider.

## Overlap boundaries
- **Runtime Settings Kit:** owns stable runtime configuration keys and precedence; Rollout Surface Kit only references the config values or control-plane endpoints it depends on.
- **Service Surface Kit:** owns routes/exchanges; Rollout Surface Kit owns the release-control semantics that may gate them.
- **Identity Surface Kit:** owns principals/claims and protected-surface requirements; Rollout Surface Kit references those attributes for targeting but does not redefine identity truth.
- **Observability Kit:** owns telemetry schemas/export contracts; Rollout Surface Kit declares which exposure/impression/tracking events are expected.
- **Migration Kit:** owns source→destination change programs; Rollout Surface Kit can attach cleanup/removal posture for temporary migration flags.
- **DocProof Kit:** owns user-facing documentation evidence; Rollout Surface Kit may supply typed/default/variant facts to docs but does not own guide validation.

## Why this could matter
A good v0 would make rollout drift reviewable:
- turning a release flag into a permanent entitlement flag,
- silently changing prerequisites or audience,
- losing exposure events for experiments,
- moving to a provider with weaker runtime hooks/events,
- or carrying transient flags for months after they should be deleted.

Rust already has enough building blocks that this missing layer looks strategic rather than premature.
