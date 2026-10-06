# LLM runbook (amnesia-resistant workflow)

This archive is designed to be edited by humans *and* automation. When using an LLM in the loop, treat this file as the
**operational contract** that prevents “design drift.”

## Non-negotiable invariants

DeriveBSD must preserve **all** of these pillars:

1. **Reproducible / derivation-first** builds and upgrades (explicit inputs; content-addressed identity; deterministic-by-default; impurity is policy-controlled and receipted).
2. **Strong runtime isolation** (jails + microVMs; least authority; capability-brokered operations; bounded interop).
3. **Supply-chain integrity / provenance** (signatures; trust roots; quarantine→promote; transparency lanes where applicable; long-term rebuildability & availability).
4. **Operability + forensics UX** (receipts everywhere; explainability; queryable evidence; deterministic exports / support bundles).

DeriveBSD must remain viable for all product shapes **without forks**:

- **A:** secure fleet host
- **B:** secure workstation
- **C:** general-purpose OS
- **D:** appliance factory / regulatory

Letters A–D are shorthands; canonical profile ids are in `spec/examples/product.profiles.json` (mapping in `spec/product.profile_aliases.json`).

If something only fits a subset, implement it as a **profile**, **tiered feature**, **optional lane**, or **adapter**.

## Mandatory refresh before editing

Re-read these before making changes:

- `docs/00-index.md`
- `docs/00-vision.md`
- `docs/01-glossary.md`
- `docs/02-derive-core.md`
- `docs/97-non-negotiable-behaviors.md`
- `docs/229-evidence-spine-overview.md`
- `docs/397-pattern-catalog.md`
- `docs/422-invariant-registry-and-design-invariants.md` (invariants as a stable diff surface)
- `docs/401-v0-cutline-and-feature-tiers.md`
- `docs/402-adapter-lanes-and-strangler-discipline.md`
- `docs/348-design-review-rubric-and-feature-intake.md`
- `docs/98-archive-hygiene.md` (repo growth rules + checks)
- `docs/411-product-profiles-as-compilation-target.md` (A–D as first-class artifacts)
- `docs/412-product-profile-matrix.md` (generated A–D summary)
- `docs/420-context-pack.md` (generated short refresh + JSON pack)
- `docs/414-doc-catalog.md` (generated navigation map + JSON index)
- `docs/418-artifact-index.md` (generated artifact→schema→example index + JSON)
- `docs/266-open-questions-and-risk-register.md`
- `docs/415-risk-register-index.md` (generated risk index + JSON)

## Editing rules (keep it tight)

- Prefer **small, composable changes**. One concept per doc.
- Docs >=397 must include a tiny metadata block near the top: **Tier / Profiles / Pillars / Patterns** (enforced by `tools/check_doc_metadata.py` and `tools/check_doc_patterns.py`).
- New work must fit an existing **pattern** (see `docs/397-pattern-catalog.md`), or add *exactly one* new pattern and justify the entropy cost.
- Every change must declare:
  - **tier** (A/B/C/D/E from `docs/401-v0-cutline-and-feature-tiers.md`)
  - **profile applicability** (A/B/C/D from `docs/411-product-profiles-as-compilation-target.md`)
- Any interop / compatibility must follow **Adapter → Shadow → Replace** and remain *killable* (`docs/402-adapter-lanes-and-strangler-discipline.md`).
- In `docs/266-open-questions-and-risk-register.md`, tag decided items with **[DECIDED]** and pin them to an ADR (guardrail: `tools/check_open_questions_decisions.py`).
- MicroVM Plan→Receipt examples must be mechanically consistent: receipt `plan_digest` is `sha256(JCS(plan))` (guardrail: `tools/check_microvm_example_plan_digests.py`).
- MicroVM lifecycle receipts must include stable reason codes on non-success outcomes (guardrail: `tools/check_microvm_receipt_reason_requirements.py`).
- MicroVM receipt example reason codes must be drawn from the central registry (guardrail: `tools/check_microvm_reason_code_registry.py`; registry: `docs/456-microvm-receipt-reason-code-registry.md`).

## Repo hygiene (must stay green)

Run:

- `python3 tools/hygiene.py`

Notes:
- If `tools/check_generated_docs.py` fails, regenerate generated docs (e.g., `python3 tools/gen_product_profile_matrix.py --write`, `python3 tools/gen_doc_catalog.py --write`, `python3 tools/gen_risk_register_index.py --write`, `python3 tools/gen_artifact_index.py --write`).

- If `tools/check_curated_references.py` fails, add the missing URLs to `docs/32-curated-references.md` (guardrail currently applies to docs >=397).

- If `tools/check_must_read_set.py` fails, restore any missing must-read entries in the runbook list (it is the source of truth for the generated context pack).

Recommended for “context refresh”:

- `python3 tools/gen_context_pack.py --write` (refreshes `docs/420-context-pack.md` + `docs/_generated/context_pack.json`)

## Output contract (per iteration)

Each iteration must include at least **one** of:

- an entropy-reducing refactor,
- a new guardrail/tool/check that prevents future drift,
- or a new integrated feature/idea that is explicitly tiered/profiled and wired into discovery surfaces.

And you must:

1. update wiring (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md` as applicable),
2. bump version stamps + `CHANGELOG.md`,
3. run hygiene checks,
4. package a new zip archive.


Last updated: 2026-03-04r184
