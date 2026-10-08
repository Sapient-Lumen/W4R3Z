# Meta: Kernel Fixture Pack Protocol (rev0487)

## Purpose
Use this protocol when the repo needs a thin shared answer to:
> what replayable scenario inputs, command recipes, and expected checks should bind witness artifacts to real proving-ground cases for the top-band kernels?

Read with:
- `design/epic-contribution-kernel-fixture-packs-2026Q1.md`
- `design/portfolio-proving-grounds-2026Q1.md`
- `meta/KERNEL_CONTRACT_WITNESS_PROTOCOL.md`
- `meta/KERNEL_INTERFACE_CONTRACT_PROTOCOL.md`

## Required assets
The first fixture-pack lane should include:
- `fixtures/README.md`
- `fixtures/top-band-v0/README.md`
- `fixtures/top-band-v0/fixture-pack-hygiene-checks.json`
- at least four `*.fixture.json` cards under `fixtures/top-band-v0/`
- `tools/check_kernel_fixture_packs.py`

## Required fixture fields
Every `*.fixture.json` card in the first corpus must include:
- `schema_family`
- `fixture_id`
- `kernel_id`
- `candidate_id`
- `scenario_id`
- `fixture_family`
- `substrate_lane`
- `required_tools`
- `input_assets`
- `command_recipe`
- `expected_artifacts`
- `expected_negative_states`
- `expected_checks`
- `refused_claims`
- `refresh_triggers`
- `related_contracts`
- `related_witnesses`

## Minimum corpus rules
The initial corpus must:
1. include at least four fixture cards;
2. keep `fixture_id` values unique;
3. cover exactly these first kernels:
   - `build-state-pack`
   - `debug-acceptance-matrix`
   - `package-intake-review-kit`
   - `safety-critical-readiness-cards`
4. include at least one fixture with an explicit `experimental_caveated` lane;
5. include at least one fixture with route-specific uncertainty;
6. include at least one fixture with stale-or-missing evidence posture;
7. bind every fixture to an existing contract0 and witness file.

## Required non-claims
The first corpus must **not** claim that:
- a fixture is the same thing as a witness;
- a passing fixture proves ecosystem-wide default readiness;
- a stable-only fixture silently covers experimental imports;
- one happy-path fixture proves the kernel is mature enough to widen;
- or a `hold` candidate deserves fixtures before its blocker changes.

## Checker duties
`tools/check_kernel_fixture_packs.py` should stay thin.
It may check:
- file presence;
- JSON parseability;
- required fields;
- unique fixture IDs;
- minimum kernel coverage;
- lane coverage for experimental/stale/route-specific cases;
- and linked-asset existence for related contract/witness paths.

It must **not** claim to validate seam-local semantics, current external facts, or implementation correctness.

## Revision rule
If a revision materially changes the kernel fixture corpus, it should update in the same revision:
- `design/epic-contribution-kernel-fixture-packs-2026Q1.md`
- `meta/KERNEL_FIXTURE_PACK_PROTOCOL.md`
- `fixtures/top-band-v0/README.md`
- `fixtures/top-band-v0/fixture-pack-hygiene-checks.json`
- the changed `*.fixture.json` cards
- and `tools/check_kernel_fixture_packs.py`

If no fixture changed, say so rather than silently leaving the corpus stale.
