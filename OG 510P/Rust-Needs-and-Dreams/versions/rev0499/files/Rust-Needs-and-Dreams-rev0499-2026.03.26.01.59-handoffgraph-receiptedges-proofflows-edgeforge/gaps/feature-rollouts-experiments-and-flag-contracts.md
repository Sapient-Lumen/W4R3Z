# Gap: feature rollouts, experiments, and flag contracts

## What is missing
Rust now has credible building blocks for feature flags, staged rollouts, and experiments:
- vendor-neutral evaluation APIs,
- Rust SDKs for open-source flag systems,
- typed/defaulted flag access,
- targeting and rule evaluation,
- percentage rollouts and variants,
- experiment tracking callbacks,
- impression/exposure events,
- and even early flag-manifest/codegen work.

What it still lacks is a **boring, reviewable contract** for the rollout surface itself.

Today teams can separately:
- declare or create flags in a hosted system,
- evaluate them through Rust SDKs,
- feed evaluation context into targeting,
- turn variants into experiments,
- capture exposure/impression events,
- and eventually clean up stale flags.

What is still missing is the shared layer that answers:
- which flags/variants a Rust program officially supports,
- which flags are release toggles vs kill switches vs experiments vs remote-config values,
- what targeting/prerequisite/rollout rules callers are allowed to depend on,
- what exposure/impression/tracking events are expected,
- what cleanup/expiry/ownership posture exists,
- and what evidence shows the declared rollout surface still matches the program.

## Why it matters
Feature flags are no longer just a UI trick.

They are increasingly part of the **public operational interface** of applications and services:
- staged releases,
- emergency disable paths,
- plan/tenant gating,
- beta cohorts,
- pricing/entitlement switches,
- experiments and safe rollouts,
- and structured remote configuration.

Without a shared artifact layer, those truths get scattered across:
- provider dashboards,
- environment-specific flag rules,
- SDK initialization code,
- ad hoc evaluation-context structs,
- analytics wiring,
- incident runbooks,
- and tribal memory about which flags are temporary versus contractual.

That is the same pattern this archive keeps finding elsewhere: strong point tools, weak portable artifacts.

## Existing building blocks worth composing
- OpenFeature provides a vendor-neutral flag evaluation API, typed evaluation, detailed evaluation metadata, hooks, tracking, and provider/domain concepts.
  https://openfeature.dev/specification/sections/flag-evaluation/
  https://openfeature.dev/specification/sections/tracking/
  https://openfeature.dev/specification/sections/hooks/
- OpenFeature now also has an OFREP appendix and an experimental CLI with a `flags.json` manifest for typed accessors. That is promising prior art, but it is still much narrower than a full rollout/review surface.
  https://openfeature.dev/specification/appendix-c/
  https://openfeature.dev/docs/tutorials/open-feature-cli/
- The OpenFeature Rust SDK already supports providers, targeting, hooks, logging hooks, and named clients, but it explicitly marks eventing as not yet available. That is a useful signal that reviewable rollout artifacts should not depend on every runtime achieving feature parity at the same time.
  https://openfeature.dev/docs/reference/sdks/server/rust/
- Unleash already treats feature flags as lifecycle-managed objects with types, environments, variants, impression-data settings, and stale/potentially-stale states.
  https://docs.getunleash.io/concepts/feature-flags
  https://docs.getunleash.io/concepts/impression-data
  https://docs.getunleash.io/concepts/technical-debt
- GrowthBook already treats rules as environment-specific and supports forced values, percentage rollouts, experiments, and safe rollouts; it also supports prerequisite features, JSON-schema validation, and Rust-side tracking callbacks.
  https://docs.growthbook.io/features/rules
  https://docs.growthbook.io/quick-start
  https://docs.growthbook.io/lib/rust
- Flipt already exposes server-side REST evaluation SDKs and positions itself as a Git-native/open-source feature-management system, which is a strong signal that the Rust ecosystem is not limited to one provider model.
  https://docs.flipt.io/v2/integration/server/rest
  https://github.com/orgs/flipt-io/repositories

## Why existing tools are not yet the whole answer
The ecosystem has **control planes, SDKs, providers, and dashboards**, but not the **shared contract / capability / evidence layer**.

OpenFeature helps normalize evaluation APIs.
Unleash, GrowthBook, Flipt, and others help define and execute rollout logic.
Rust SDKs help evaluate values locally.
Analytics tools help count exposures.

But teams still have to invent their own answers for:
- stable flag identities and support classes,
- distinctions between short-lived release flags and long-lived entitlement/config flags,
- normalized variant and prerequisite metadata,
- explicit cleanup expectations,
- checked-vs-illustrative rollout cases,
- and diffable review artifacts when a flag changes audience, a safe rollout becomes a plain percentage rollout, exposure semantics change, or a flag that should be deleted silently becomes permanent infrastructure.

That is exactly the kind of missing substrate this archive is trying to identify.

## Target outcome
A project should be able to say:
- “these are the flags and variants we officially support,”
- “these are their intended roles, lifetimes, prerequisites, and targeting assumptions,”
- “these are the required exposure/impression/tracking semantics,”
- “these are the cleanup and ownership expectations,”
- and “this is the portable bundle CI, release review, operators, and later archaeology can consume.”

That is bigger than one SDK and smaller than a hosted flag platform.
