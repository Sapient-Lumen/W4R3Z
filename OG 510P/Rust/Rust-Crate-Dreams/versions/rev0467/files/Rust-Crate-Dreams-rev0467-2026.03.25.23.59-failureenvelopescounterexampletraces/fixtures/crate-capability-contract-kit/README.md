# Crate Capability Contract Kit fixtures

This fixture family exists to make **P-0510 Crate Capability Contract & Interop Profile Kit** concrete.

The goal is to standardize a very small producer-side contract bundle for a crate’s support and interop posture:

- what the crate claims,
- what tools can observe,
- which interop ecosystems it exposes publicly,
- where the claims conform,
- and where human review is still required.

## Intended first scenarios

1. `tokio_internal_runtime_neutral_public_api`
2. `no_std_alloc_with_docsrs_target_overlay`
3. `build_rs_links_proc_macro_hidden_obligations`
4. `support_drift_requires_review`

## Minimal bundle for 0.1

- `capability-contract.json`
- `observed-capabilities.receipt.json`
- `interop-exports.report.json`
- `profile-conformance.report.json`
- `claim-class.policy.json`
- `support-obligation.receipt.json`
- `profile-fidelity.report.json`
- `evidence-source.receipt.json`
- `notes.md`

Later overlays may add:
- capability diffs across releases
- imports from MSRV / public-API / trust slice tools
- CI verification overlays
- docs or README summary generation

## Design rule

This family should optimize for **small joined support artifacts**, not giant mirrors of manifest or docs data.
If the crate cannot justify a confident support claim, the fixture should say `manual_review_required` instead of flattening uncertainty into “supported”.

## Current planning stance

This family is **not** trying to replace pathfinder decision packs, cfg-availability ledgers, whole-project toolchain support contracts, or trust/health tooling.
It is trying to standardize the producer-side contract those surfaces still do not hand people by default.


## 2026-03-17 productization note

This family now treats three review objects as first-class:

- **claim class** (`declared`, `observed`, `inferred`, `manual_review_required`)
- **support obligations** (`build.rs`, `links`, proc macros, docs.rs overlays, MSRV, target overlays)
- **profile fidelity** (how complete the support story really is across manifest/docs/API imports)

Future revisions should avoid collapsing those into one fake “supported / unsupported” verdict.
