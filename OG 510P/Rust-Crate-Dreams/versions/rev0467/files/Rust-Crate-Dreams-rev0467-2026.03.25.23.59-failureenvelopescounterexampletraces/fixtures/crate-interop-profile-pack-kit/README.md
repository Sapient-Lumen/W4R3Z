# Crate Interop Profile Pack Kit fixtures

This fixture pack exists to make **P-0511 Crate Interop Profile Pack Kit** concrete.
It is intentionally small and focused on Rust-internal library ecosystem boundaries rather than domain protocols.

## Included schema drafts

- `interop-profile-pack.schema.json`
- `static-conformance.receipt.schema.json`
- `behavioral-probe.report.schema.json`
- `pair-compatibility.report.schema.json`
- `migration-hazards.report.schema.json`
- `witness-source.receipt.schema.json`
- `profile-class.policy.schema.json`
- `boundary-obligation.receipt.schema.json`
- `pair-fidelity.report.schema.json`

## Scenario families

- `runtime_neutral_async_library/` — internal Tokio use is allowed but public API stays futures-oriented
- `tower_http_middleware/` — middleware/service boundary over `tower-service` + `http`
- `serde_boundary_models/` — model crates stay format-neutral while adapters live elsewhere
- `public_tokio_type_leaks_runtime_neutral_profile/` — public Tokio exposure quietly breaks the claimed runtime-neutral boundary
- `tower_http_pair_matches_service_but_misses_body_shape/` — `Service` alignment alone is not enough when body/error shapes are still ambiguous
- `serde_models_expose_format_specific_helpers/` — public format-specific helpers quietly erode a supposedly neutral Serde model boundary

## Minimal bundle for 0.1

- `interop-profile-pack.json`
- `static-conformance.receipt.json`
- `behavioral-probe.report.json`
- `pair-compatibility.report.json`
- `migration-hazards.report.json`
- `witness-source.receipt.json`
- `profile-class.policy.json`
- `boundary-obligation.receipt.json`
- `pair-fidelity.report.json`
- `notes.md`

Later overlays may add:
- richer behavioral probes
- imports from capability contracts or semver/public-API slice tools
- CI verification overlays
- documentation summary generation

## Design rule

This family should optimize for **small shared boundary artifacts**, not giant mirrors of manifest or rustdoc data.
If the profile cannot justify a confident pairwise verdict, the fixture should say `manual_review_required` instead of flattening uncertainty into “compatible”.

## Current planning stance

This family is **not** trying to replace pathfinder decision packs, producer-side capability contracts, semver/public-API tools, or domain-specific conformance suites.
It is trying to standardize the shared ecosystem boundary those surfaces still do not hand people by default.

## 2026-03-17 productization note

This family now treats three review objects as first-class:

- **profile class** (`shared_baseline`, `ecosystem_boundary`, `adapter_bridge`, `behavior_probe_required`, `manual_review_required`)
- **boundary obligations** (required surfaces, forbidden couplings, adapter paths, runtime/body/error expectations)
- **pair fidelity** (how complete a provider/consumer verdict really is)

Future revisions should avoid collapsing those into one fake “these crates are compatible” verdict.
