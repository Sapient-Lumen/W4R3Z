# Frontier salience snapshot — 2026-03-19 (81)

This pass did **not** add another test runner, another snapshot crate, another compile-fail harness, or another container helper.
It sharpened a top-ranked support-surface lane:

- **P-0523 Crate Test Surface Pack Kit** — because Rust now has real runner / fixture / replay / compile-fail / mock / snapshot substrate, but still lacks one boring receiver-facing contract for support level, topology honesty, witness lineage, and normalization boundary.

## Main judgment

The next worthy move here was **not** more testing substrate.
That substrate already exists.

The sharper missing layer is the **joined downstream testing contract** above today’s substrate, especially once four facts stay explicit:

- **support-level truth** — which fixtures and recipes are actually supported,
- **topology-honesty truth** — which scenarios are really in-process, loopback, containerized, or host-dependent,
- **witness-lineage truth** — whether scenario evidence came from direct runs, compile-fail harnesses, or imported/portable recordings,
- **normalization-boundary truth** — which redactions/sorting rules stabilize snapshots and which can hide semantic review.

That move is better grounded now because:

- the Rust vision-doc work explicitly calls for **supportive interfaces from crates**;
- the 2025 State of Rust survey still says online docs and code are the main learning surfaces;
- Tokio’s current testing docs still make paused time real, but bounded by runtime and feature requirements;
- `cargo-nextest` now documents record/replay plus portable recordings for cross-machine replay;
- `assert_cmd` still documents integration-test-only Cargo-binary helpers;
- `wiremock` still documents isolated per-test mock servers;
- `testcontainers` still documents Docker-API-compatible runtime requirements and weaker guarantees for alternative setups;
- `trybuild` still gives Rust a real compile-fail/diagnostic harness;
- `insta` still documents redactions and sorted redactions as stability tools, not semantic proofs.

So the gap is no longer “Rust lacks testing tools”.
The gap is that teams still rarely get a **reviewable crate-authored downstream testing promise** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because start/stop truth is so often missing.
3. **P-0522 Crate Persistence Surface Pack Kit** — still one of the sharpest support-surface lanes now that durable-state promises are specific.
4. **P-0521 Crate Resource Surface Pack Kit** — still a strong support lane because waiting-room truth is concrete now.
5. **P-0524 Crate Example Surface Pack Kit** — still a strong first-success lane.
6. **P-0523 Crate Test Surface Pack Kit** — now much stronger because the missing value is clearly support-level / topology / witness-lineage truth above real testing substrate.
7. **P-0525 Crate Diagnosis Surface Pack Kit** — still a strong first-diagnosis lane.
8. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
9. **P-0483 Public API Readiness Bundle Kit** — still a strong joined release-review lane.
10. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest adoption-trust lanes.
11. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
12. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.

## Why this won over adjacent candidates right now

- It beat a deeper **P-0518** pass because the support stack still needed a more concrete answer for “what testing recipe is actually supported?” before another observability-support refinement.
- It beat a deeper **P-0519** pass because trust about offline/sandbox posture matters, but today’s test substrate makes official downstream test contracts unusually buildable right now.
- It beat more **foreign-package shipping** work because the archive already has many fresh release-contract passes and still needed a stronger core supportiveness lane.
- It beat more **pathfinder** work because ecosystem choice is already strong enough that the archive now benefits more from tightening what happens *after* a crate is chosen and integrated into tests.

## What changed in the archive

Added:
- `entries/2026-03-19-261.md`
- `meta/frontier-salience-2026-03-19-81.md`
- `meta/crate-test-surface-product-plan-2026-03-19.md`
- `fixtures/crate-test-surface-pack-kit/README.md`
- `fixtures/crate-test-surface-pack-kit/witness-lineage.receipt.schema.json`
- `fixtures/crate-test-surface-pack-kit/nextest_portable_recording_replays_ci_failure_locally/README.md`
- `fixtures/crate-test-surface-pack-kit/nextest_portable_recording_replays_ci_failure_locally/witness-lineage.receipt.example.json`
- `fixtures/crate-test-surface-pack-kit/trybuild_compile_fail_contract_is_not_runtime_recipe/README.md`
- `fixtures/crate-test-surface-pack-kit/trybuild_compile_fail_contract_is_not_runtime_recipe/witness-lineage.receipt.example.json`
- `fixtures/crate-test-surface-pack-kit/assert_cmd_recipe_needs_integration_test_context/README.md`
- `fixtures/crate-test-surface-pack-kit/assert_cmd_recipe_needs_integration_test_context/test-environment.requirements.example.json`
- `fixtures/crate-test-surface-pack-kit/insta_sorted_redaction_stabilizes_set_snapshot_but_not_order_semantics/README.md`
- `fixtures/crate-test-surface-pack-kit/insta_sorted_redaction_stabilizes_set_snapshot_but_not_order_semantics/snapshot-normalization.report.example.json`
- `fixtures/crate-test-surface-pack-kit/paused_time_requires_current_thread_and_test_util/deterministic-seam.report.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-test-surface-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
