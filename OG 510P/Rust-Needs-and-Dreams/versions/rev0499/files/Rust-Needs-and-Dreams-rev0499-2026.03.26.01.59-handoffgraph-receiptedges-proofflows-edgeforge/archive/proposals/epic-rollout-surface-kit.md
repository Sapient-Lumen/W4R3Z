# Epic proposal: Rollout Surface Kit

## Thesis
Rust’s feature-flag and experimentation ecosystem is mature enough that the missing contribution is no longer “yet another SDK,” “yet another targeting DSL,” or “yet another hosted flag system.”
The higher-leverage missing piece is a **portable rollout-surface contract** that lets teams declare, diff, validate, and ship what release controls and experiments actually promise: flag identities, variants, prerequisites, targeting posture, exposure/impression expectations, cleanup posture, and checked behavior evidence.

In other words: Rust needs a boring, attachable `rollout-pack/v0` more than it needs one more provider-specific wrapper.

## Why now
The ecosystem signals line up:
- OpenFeature already normalizes evaluation APIs, hooks, and tracking semantics.
- OpenFeature now has OFREP work and an experimental CLI manifest/codegen lane.
- OpenFeature’s Rust SDK is real, but it still does not have full eventing parity.
- Unleash already models stale flags, impression data, variants, and lifecycle/technical-debt concerns.
- GrowthBook already treats percentage rollouts, experiments, safe rollouts, prerequisites, and schema-validated values as first-class.
- Flipt and related systems show the control-plane/provider side is not converging to one hosted model.

The hard part is increasingly not “can Rust evaluate a flag?” but “what exactly does this program promise about its rollout and experiment surface, and what evidence do we have that the promise still holds?”

Sources:
- https://openfeature.dev/specification/sections/flag-evaluation/
- https://openfeature.dev/specification/sections/hooks/
- https://openfeature.dev/specification/sections/tracking/
- https://openfeature.dev/specification/appendix-c/
- https://openfeature.dev/docs/tutorials/open-feature-cli/
- https://openfeature.dev/docs/reference/sdks/server/rust/
- https://docs.getunleash.io/concepts/feature-flags
- https://docs.getunleash.io/concepts/impression-data
- https://docs.getunleash.io/concepts/technical-debt
- https://docs.growthbook.io/features/rules
- https://docs.growthbook.io/quick-start
- https://docs.growthbook.io/lib/rust
- https://docs.flipt.io/v2/integration/server/rest

## What should be built
A first credible version should ship:
1. `rollout-surface/v0`, `flag-catalog/v0`, `variant-profile/v0`, `targeting-profile/v0`, `experiment-profile/v0`, `exposure-profile/v0`, `rollout-check-plan/v0`, `rollout-check-report/v0`, optional `flag-cleanup-report/v0`, and `rollout-pack/v0`
2. adapters for OpenFeature/OpenFeature CLI plus common Rust provider lanes (Unleash, GrowthBook, Flipt, custom/manual)
3. docs/reference generation for declared flags, variants, prerequisite posture, targeting assumptions, and cleanup expectations
4. validation/reporting support for rollout drift, missing exposures, flag-role changes, stale-flag debt, and checked-vs-illustrative archetype separation
5. examples showing rollout packs attached to API releases, incident bundles, beta-program rollouts, staged migrations, and experiment reviews

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one OpenFeature-only pilot proving typed/defaulted flag manifests are useful but insufficient without rollout/cleanup metadata
- one Unleash pilot proving stale-flag and impression-data posture belongs in the contract
- one GrowthBook pilot proving percentage rollout / experiment / safe-rollout distinctions belong in the support surface
- one Flipt or custom-provider pilot proving provider swaps should not force a complete rewrite of the review artifacts
- one internal app pilot where temporary migration flags must be removed on time and that removal gets tracked by the pack

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve flag identity, variant truth, targeting posture, exposure semantics, and cleanup posture as separate artifacts
2. **v0.2 adapters**
   - support OpenFeature manifests, one Rust provider SDK adapter, one experiment-heavy adapter, and one manual/custom adapter
3. **v0.3 cross-kit integration**
   - integrate with Runtime Settings, Service Surface, Identity Surface, Observability, Migration, and DocProof workflows
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact provider or control-plane model

## Success metrics
- Teams can review rollout changes as explicit artifacts instead of dashboard diffs, screenshots, SDK code, and tribal memory.
- Release flags, experiments, and permanent entitlement/config flags become easier to distinguish and clean up honestly.
- Exposure/impression expectations become attachable and testable rather than “best effort if analytics remembers.”
- Provider migrations become easier because support truth lives above one SDK.
- Rust services become easier to hand off because rollout inventory and flag debt stop living only in people’s heads.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Runtime Settings Kit covers declared runtime config and precedence,
- Service Surface Kit covers HTTP/service behavior,
- Identity Surface Kit covers principals/claims and access requirements,
- Observability Kit covers telemetry contracts,
- Migration Kit covers change programs,
- and DocProof Kit covers documentation trust.

But none of those is the portable contract for the **release-control / experiment boundary itself**.
Rollout Surface Kit is the missing substrate that keeps flags, variants, prerequisites, targeting, exposure semantics, and cleanup truth attached to one reviewable interface without absorbing the rest of the stack into one mega-format.
